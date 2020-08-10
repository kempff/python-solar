# Python reader for solar panel controller

from influxdb import InfluxDBClient
from threading import Thread
import logging
import time
import sys
from logging.handlers import RotatingFileHandler
import crc16
from datetime import datetime, date, timedelta
import pytz
from openpyxl import Workbook
import sys
import usb.core
import zmq
import json

# Internal imports
from constants import command_dictionary
import solar_config as config
from solar.struct_logger import StructLogger

APP_VERSION = "0.1.2"                               # Ensure this is the same as the Git release tag version
APP_NAME = "solar_monitor"

# Setup logging
logger = StructLogger()


class PythonSolar:
    '''
    Class to process data from either a file (debug mode) or USB.
    '''
    def __init__(self):
        # Configure DB
        self.influx_client = InfluxDBClient(config.INFLUX_HOST, config.INFLUX_PORT, database=config.INFLUX_DB)

        self.debug_data = config.DEBUG_MODE
        self.write_to_db = True
        self.request_ratings = True              # Flag to request ratings data, only when a command was sent and at startup
        self.processing = False
        self.errors = 0

        if self.debug_data:
            # Open the files for reading
            self.pigs_file = open("qpigs.txt","r")
            self.mod_file = open("qmod.txt","r")
            self.piri_file = open("qpiri.txt","r")
            self.piws_file = open("qpiws.txt","r")
        else:
            # Configure USB to Solar device
            vendorId = 0x0665
            productId = 0x5161
            interface = 0
            self.usb_dev = usb.core.find(idVendor=vendorId, idProduct=productId)
            if self.usb_dev.is_kernel_driver_active(interface):
                self.usb_dev.detach_kernel_driver(interface)
            self.usb_dev.set_interface_altsetting(0,0)

        self.mode_data = 'B'           # From QMOD command - start with battery mode as default
        self.status_data = None        # From QPIGS command
        self.ratings_data = None       # From QPIRI command
        self.error_data = None         # From QPIWS command

        logger.setLevel(logging.INFO)
        logger.info(f'Running {APP_NAME} version {APP_VERSION}')
        logger.info(f"Influx DB config: {config.INFLUX_HOST}, {config.INFLUX_PORT}, {config.INFLUX_DB}")
        if not self.debug_data:
            logger.info("USB info: {0}".format(self.usb_dev))
            # Read the port to clear it from data
            self.get_result()
        logger.setLevel(config.LOG_LEVEL)

    # Read next line from each file, if at end of the file loop to the beginning
    def read_file_data(self,input_file):
        return_data = []
        return_data = input_file.readline()
        if return_data is "":
            input_file.seek(0)
            return_data = input_file.readline()
        return return_data


    def format_data(self,cmd):
        cmd = cmd.encode('utf-8')
        crc = crc16.crc16xmodem(cmd).to_bytes(2,'big')
        cmd = cmd+crc
        cmd = cmd+b'\r'
        return cmd


    def send_command(self,cmd):
        bytes_to_send = len(cmd)
        byte_offset = 0
        while bytes_to_send:
            # Limit packet size to 8 bytes
            if bytes_to_send > 8:
                tx_data = cmd[byte_offset:byte_offset+8]
                the_bytes = 8
            else:
                tx_data = cmd[byte_offset:byte_offset+bytes_to_send]
                the_bytes = bytes_to_send
            # Pad up to 8 bytes with zeros
            while len(tx_data)<8:
                tx_data = tx_data+b'\0'
            self.usb_dev.ctrl_transfer(0x21, 0x9, 0x200, 0, tx_data)
            # Recalculate the offsets
            byte_offset += the_bytes
            bytes_to_send -= the_bytes


    def get_result(self,timeout=100):
        res=""
        i=0
        while '\r' not in res and i<20:
            try:
                res+="".join([chr(i) for i in self.usb_dev.read(0x81, 8, timeout) if i!=0x00])
            except usb.core.USBError as e:
                if e.errno == 110:
                    pass
                else:
                    raise
            i+=1
        return res


    def save_mode_data(self,the_data):
        self.mode_data = the_data

    
    def save_status_data(self, the_data):
        self.status_data = the_data

    
    def save_ratings_data(self, the_data):
        self.ratings_data = the_data


    def save_error_data(self, the_data):
        self.error_data = the_data


    def process_result(self,command, result_data):
        return_val = False
        result_dictionary = {'QMOD' : self.save_mode_data,
                            'QPIRI': self.save_ratings_data,
                            'QPIGS': self.save_status_data,
                            'QPIWS': self.save_error_data}
        hex_data = ":".join("{:02x}".format(ord(c)) for c in result_data)
        logger.debug("Data length: {0} Hex: {1}".format(len(result_data),hex_data))
        if result_data:
            if result_data[0] is '(':
                check_data = result_data[:-3].encode('utf-8')
                rx_crc = bytes([ord(result_data[-3:-2]),ord(result_data[-2:-1])])
                crc = crc16.crc16xmodem(check_data).to_bytes(2,'big')
                if crc == rx_crc or self.debug_data:
                    if "(NAK" in result_data:
                        logger.warning(f"NAK received - {command} data not updated")
                    else:
                        result_dictionary[command](result_data[1:-3].split())
                        return_val = True
                else:
                    logger.error('Incorrect CRC for {0} command Calc: {1} - RX: {2}'.format(command, crc, rx_crc))
                    logger.error("Data length: {0} Hex: {1}".format(len(result_data),hex_data))
            else:
                logger.error(f'Incorrect start byte for {command} command: {result_data}')
        else:
            logger.error('No data for command {0}'.format(command))
        return return_val



    # Read data function (either from USB or file)
    def read_data(self):
        cyclic_commands = [ 'QMOD', 'QPIGS', 'QPIWS']
        if self.debug_data:
            the_data = self.read_file_data(self.mod_file)
            logger.info("Mode data: {0}".format(the_data))
            self.process_result('QMOD', the_data)
            the_data = self.read_file_data(self.pigs_file)
            logger.info("Status data: {0}".format(the_data))
            self.process_result('QPIGS', the_data)
            the_data = self.read_file_data(self.piri_file)
            logger.info("Ratings data: {0}".format(the_data))
            self.process_result('QPIRI', the_data)
            the_data = self.read_file_data(self.piws_file)
            logger.info("Fault data: {0}".format(the_data))
            self.process_result('QPIWS', the_data)
        else:
            try:
                for the_cmd in cyclic_commands:
                    for cnt in range(0,3):
                        self.send_command(self.format_data(the_cmd))
                        result = self.get_result()
                        logger.debug(f"{the_cmd}: {result}")
                        # If successful, continue with the next command
                        if self.process_result(the_cmd, result):
                            time.sleep(2)
                            break
                        # Retry time: a bit longer
                        time.sleep(5)
                # If the frontend configured something, request the ratings
                if self.request_ratings:
                    self.send_command(self.format_data('QPIRI'))
                    result = self.get_result()
                    logger.debug(result)
                    self.process_result('QPIRI', result)
                    self.request_ratings = False
                self.errors = 0
            except Exception as e:
                logger.error(f"Send command error {e}")
                self.errors+=1
                # Too many errors - exit app. 'systemctl' will reload
                if self.errors > 10:
                    exit(1)


    def populate_status_data(self, status_data, mode_data):
        mode_dictionary = { 'P': 'Power on', 'S': 'Standby', 'L': 'Line',
                            'B': 'Battery', 'F': 'Fault', 'H': 'Power saving'}
        status_body = [
        {
            "measurement": "system_status",
            "tags": {
                "installation": config.INSTALLATION,
                "mode": "unknown",
                },
            "fields": {
                "grid_voltage": 123.4,
                "grid_frequency": 50.0,
                "ac_output_voltage": 123.5,
                "ac_output_frequency": 50.1,
                "ac_output_va": 345,
                "ac_output_w": 456,
                "output_load_percent": 90,
                "bus_voltage": 10,
                "battery_voltage": 34.56,
                "battery_charge_current": 13,
                "battery_capacity": 80,
                "inverter_temperature": 60,
                "pv_input_current": 10,
                "pv_input_voltage": 20.3,
                "scc_battery_voltage": 23.45,
                "battery_discharge_current": 12,
                "load_status": 0,
                "battery_voltage_steady": 0,
                "charging_on": 0,
                "scc_charging_on": 0,
                "ac_charging_on": 0,
                "pv_input_w": 203,
                }
        }
        ]
        if mode_data[0] in mode_dictionary.keys():
            status_body[0]['tags']['mode'] = mode_dictionary[mode_data[0]]
        else:
            logger.error("Invalid mode {0}".format(mode_data[0]))
        status_body[0]['fields']['grid_voltage'] = float(status_data[0])
        status_body[0]['fields']['grid_frequency'] = float(status_data[1])
        status_body[0]['fields']['ac_output_voltage'] = float(status_data[2])
        status_body[0]['fields']['ac_output_frequency'] = float(status_data[3])
        status_body[0]['fields']['ac_output_va'] = float(status_data[4])
        status_body[0]['fields']['ac_output_w'] = float(status_data[5])
        status_body[0]['fields']['output_load_percent'] = float(status_data[6])
        status_body[0]['fields']['bus_voltage'] = float(status_data[7])
        status_body[0]['fields']['battery_voltage'] = float(status_data[8])
        status_body[0]['fields']['battery_charge_current'] = float(status_data[9])
        status_body[0]['fields']['battery_capacity'] = float(status_data[10])
        status_body[0]['fields']['inverter_temperature'] = float(status_data[11])
        status_body[0]['fields']['pv_input_current'] = float(status_data[12])
        status_body[0]['fields']['pv_input_voltage'] = float(status_data[13])
        status_body[0]['fields']['scc_battery_voltage'] = float(status_data[14])
        status_body[0]['fields']['battery_discharge_current'] = float(status_data[15])
        the_bits = list(status_data[16])
        status_body[0]['fields']['load_status'] = int(the_bits[3])
        status_body[0]['fields']['battery_voltage_steady'] = int(the_bits[4])
        status_body[0]['fields']['charging_on'] = int(the_bits[5])
        status_body[0]['fields']['scc_charging_on'] = int(the_bits[6])
        status_body[0]['fields']['ac_charging_on'] = int(the_bits[7])
        status_body[0]['fields']['pv_input_w'] = float(status_data[12]) * float(status_data[13])
        self.influx_client.write_points(status_body)


    def populate_ratings_data(self, ratings_data):
        battery_type_dictionary = { '0': 'AGM', '1': 'Flooded', '2': 'User'}
        input_voltage_dictionary = { '0': 'Appliance', '1': 'UPS'}
        output_source_dictionary = { '0': 'Utility first', '1': 'Solar first', '2': 'SBU first'}
        charger_source_dictionary = { '0': 'Utility first', '1': 'Solar first', '2': 'Solar and utility', '3': 'Only solar'}
        machine_type_dictionary = { '00': 'Grid tie', '01': 'Off grid', '10': 'Hybrid'}
        topology_dictionary = { '0': 'Transformerless', '1': 'Transformer'}
        output_mode_dictionary = { '0': 'Single machine', '1': 'Parallel', '2': 'Phase 1 of 3', '3': 'Phase 2 of 3', '4': 'Phase 3 of 3'}
        ratings_body = [
        {
            "measurement": "system_rating",
            "tags": {
                "installation": config.INSTALLATION,
                },
            "fields": {
                "grid_voltage": 123.4,
                "grid_current": 50.0,
                "ac_output_voltage": 123.5,
                "ac_output_frequency": 50.1,
                "ac_output_current": 10.1,
                "ac_output_va": 345,
                "ac_output_w": 456,
                "battery_voltage": 34.56,
                "battery_recharge_voltage": 12.5,
                "battery_under_voltage": 13,
                "battery_bulk_voltage": 80,
                "battery_float_voltage": 60,
                "battery_type": "AGM",
                "max_ac_charge_current": 20,
                "max_charge_current": 23.45,
                "input_voltage_range": "Appliance",
                "output_source_priority": "SBU first",
                "charger_source_priority": "Utility first",
                "machine_type": "Grid tie",
                "topology": "Transformer",
                "output_mode": "Single machine",
                "battery_redischarge_voltage": 12.3,
                "pv_ok_for_parallel": 0,
                "pv_power_balance": 0, 
                }
        }
        ]
        ratings_body[0]['fields']['grid_voltage'] = float(ratings_data[0])
        ratings_body[0]['fields']['grid_current'] = float(ratings_data[1])
        ratings_body[0]['fields']['ac_output_voltage'] = float(ratings_data[2])
        ratings_body[0]['fields']['ac_output_frequency'] = float(ratings_data[3])
        ratings_body[0]['fields']['ac_output_current'] = float(ratings_data[4])
        ratings_body[0]['fields']['ac_output_va'] = float(ratings_data[5])
        ratings_body[0]['fields']['ac_output_w'] = float(ratings_data[6])
        ratings_body[0]['fields']['battery_voltage'] = float(ratings_data[7])
        ratings_body[0]['fields']['battery_recharge_voltage'] = float(ratings_data[8])
        ratings_body[0]['fields']['battery_under_voltage'] = float(ratings_data[9])
        ratings_body[0]['fields']['battery_bulk_voltage'] = float(ratings_data[10])
        ratings_body[0]['fields']['battery_float_voltage'] = float(ratings_data[11])
        ratings_body[0]['fields']['battery_type'] = battery_type_dictionary[ratings_data[12]]
        ratings_body[0]['fields']['max_ac_charge_current'] = float(ratings_data[13])
        ratings_body[0]['fields']['max_charge_current'] = float(ratings_data[14])
        ratings_body[0]['fields']['input_voltage_range'] = input_voltage_dictionary[ratings_data[15]]
        ratings_body[0]['fields']['output_source_priority'] = output_source_dictionary[ratings_data[16]]
        ratings_body[0]['fields']['charger_source_priority'] = charger_source_dictionary[ratings_data[17]]
        # Skip 18 (parallel max num)
        ratings_body[0]['fields']['machine_type'] = machine_type_dictionary[ratings_data[19]]
        ratings_body[0]['fields']['topology'] = topology_dictionary[ratings_data[20]]
        ratings_body[0]['fields']['output_mode'] = output_mode_dictionary[ratings_data[21]]
        ratings_body[0]['fields']['battery_redischarge_voltage'] = float(ratings_data[22])
        ratings_body[0]['fields']['pv_ok_for_parallel'] = float(ratings_data[23])
        ratings_body[0]['fields']['pv_power_balance'] = float(ratings_data[24])
        self.influx_client.write_points(ratings_body)


    def populate_error_data(self, error_data):
        error_values = [int(d) for d in error_data[0]]

        for cnt,value in enumerate(error_values,start=1):
            if value != 0:
                logger.error(f"Error {config.ERROR_MESSAGES[cnt]['message']} ({config.ERROR_MESSAGES[cnt]['severity']}) active!")
                error_body = [
                                {
                                    "measurement": "system_error",
                                    "tags": {
                                        "installation": config.INSTALLATION,
                                        "appname": APP_NAME,
                                        "host": "raspberry",
                                        },
                                    "fields": {
                                        "message": config.ERROR_MESSAGES[cnt]['message'], 
                                        "severity": config.ERROR_MESSAGES[cnt]['severity'],
                                    }
                                }
                ]     
                self.influx_client.write_points(error_body)


    def populate_data(self):
        try:
            if self.write_to_db:
                logger.info("Writing to database...")
                if self.mode_data:
                    logger.debug(f"Mode data: {self.mode_data}")
                if self.status_data:
                    logger.debug(f"Status data: {self.status_data}")
                    self.populate_status_data(self.status_data, self.mode_data)
                if self.ratings_data:
                    logger.debug(f"Ratings data: {self.ratings_data}")
                    self.populate_ratings_data(self.ratings_data)
                if self.error_data:
                    logger.debug(f"Error data: {self.error_data}")
                    self.populate_error_data(self.error_data)
        except Exception as e:
            logger.error(str(e))


    def send_command_with_ack_reply(self,command):
        self.send_command(self.format_data(command))
        result = get_result()
        if result[0:4] == '(ACK':
            logger.info(f'Command {command} processed OK')
            self.request_ratings = True
            return_val = True
        else:
            logger.error(f'Command {command} error, reply {result}')
            return_val = False


    def convert_timestamp_to_datetime(self,in_time):
        # Remove nanoseconds and 'Z'
        in_time = in_time[:-4]
        the_time = datetime.strptime(in_time,"%Y-%m-%dT%H:%M:%S.%f")
        return the_time


    def write_row(self,the_sheet, the_data):
        # Add offset to time written to spreadsheet
        timestamp = self.convert_timestamp_to_datetime(the_data['time'])
        timestamp += timedelta(hours=config.TIME_OFFSET)
        the_row = [str(timestamp), the_data['mode'], the_data['ac_output_w'], the_data['pv_input_voltage']]
        # logger.debug(the_row)
        the_sheet.append(the_row)


    def calculate_total_time(self,start_time, end_time):
        end_time_dt = convert_timestamp_to_datetime(end_time)
        start_time_dt = convert_timestamp_to_datetime(start_time)
        time_diff = end_time_dt - start_time_dt
        return time_diff.total_seconds() 
    

    def perform_aggregations(self, start_date, end_date):
                
        heading_text = ['Time','Mode','AC output W','PV input V','','Total kW','Average kW','Total time','kWh']
        db_queries = {  "Battery" : "select * from system_status where (\"mode\" = \'Battery\') and time >= \'{0}\' and time <= \'{1}\'",
                        "Line" : 'select * from system_status where (\"mode\" = \'Line\') and time >= \'{0}\' and time <= \'{1}\'',
                        "All" : 'select * from system_status where time >= \'{0}\' and time <= \'{1}\''
        }
        total_time = { "Battery": 0,
                    "Line": 0,
                    "All": 0
        }
        columns = ['B','C','D','F','G','I']
        
        try:
            # Start from 0 hours util last hour for the selected dates
            start_date += " 00:00:00"
            valid_start_date = datetime.strptime(start_date, '%Y/%m/%d %H:%M:%S')
            end_date += " 23:59:59"
            valid_end_date = datetime.strptime(end_date, '%Y/%m/%d %H:%M:%S')
            valid_start_date = valid_start_date.replace(tzinfo=pytz.utc)
            valid_end_date = valid_end_date.replace(tzinfo=pytz.utc)
            filename = valid_start_date.strftime("%y-%m-%d") + " to " +  valid_end_date.strftime("%y-%m-%d") + ".xlsx"
            logger.info("Filename selected: {0}".format(filename))
            book = Workbook()
            # First calculate total time dictionary using the "All" query. Check times between elements, ignoring the last one (therefore [:-1]).
            query_results = list(self.influx_client.query(db_queries["All"].format(valid_start_date.isoformat(), valid_end_date.isoformat())).get_points())
            for i, results in enumerate(query_results[:-1]):
                the_time = calculate_total_time(results["time"], query_results[i+1]["time"])
                total_time[results["mode"]] += the_time
                total_time["All"] += the_time
            
            # Now filter according to mode and create separate sheets in spreadsheet
            for key in db_queries.keys():
                book.create_sheet(key)
                sheet = book.get_sheet_by_name(key)
                sheet.append(heading_text)
                query_results = list(self.influx_client.query(db_queries[key].format(valid_start_date.isoformat(), valid_end_date.isoformat())).get_points())
                total_watts = 0
                if query_results:
                    for results in query_results:
                        write_row(sheet, results)
                        total_watts += int(results['ac_output_w'])
                    sheet['F2'] = str(total_watts/1000.0)
                    if len(query_results) is  not 0:
                        avg_kw = total_watts/1000.0/len(query_results)
                    else:
                        avg_kw = 0
                    sheet['G2'] = str(avg_kw)
                    sheet['H2'] = str(total_time[key])
                    # / 3600.0 to get from seconds to hours
                    if total_time is not 0:
                        kwh = avg_kw*total_time[key]/3600.0
                    else:
                        kwh = 0
                    sheet['I2'] = kwh
                # Set time columns wider than the other
                sheet.column_dimensions['A'].width = 20
                sheet.column_dimensions['H'].width = 15
                for column in columns:
                    sheet.column_dimensions[column].width = 12
                
            # Remove default sheet
            sheet = book.get_sheet_by_name("Sheet")
            book.remove_sheet(sheet)
            book.save(filename)

        except ValueError:
            mb = QMessageBox ("Error",'Start {0} or end {1} date incorrect'.format(start_date, end_date),QMessageBox.Warning,QMessageBox.Ok,0,0)
            mb.exec_()
            logger.error('Start {0} or end {1} date incorrect'.format(start_date, end_date))


    def process_function(self):
        logger.info('Processing thread entry')
    #    time.sleep(1)
    #    re_command =  "PBCV49.0"
    #    send_command_with_ack_reply(re_command)

        while self.processing:
            try:
                logger.info('Processing data...')
                self.read_data()
                self.populate_data()
                time.sleep(config.PROCESS_TIME)
            except Exception as e:
                logger.error(f"Error in process loop: {e}")
                time.sleep(config.PROCESS_TIME)
        logger.info('Processing thread exit')


    def zmq_reader(self):
        '''
        ZMQ thread to receive data from the frontend
        '''
        logger.info('ZMQ thread entry')
        while self.processing:
            try:
                message = self.socket.recv()
                # Message is in JSON
                message_data = json.loads(message)
                if self.send_command_to_inverter(message_data['command'],message_data['data']):
                    data = dict(result='OK')
                else:
                    data = dict(result='FAIL')
                self.socket.send_json(data)
            except Exception as e:
                logger.error(f'ZMQ error: {str(e)}')
                time.sleep(1)


    def start_processing(self):
        if not self.processing:
            logger.info('Creating threads...')
            # Create the ZMQ socket and thread
            context = zmq.Context()
            self.socket = context.socket(zmq.REP)
            self.socket.bind(f'tcp://*:{config.ZMQ_PORT}')
            # Create and start ZMQ read thread - Only applicable when not a Flask app
            self.zmq_thread = Thread(target=self.zmq_reader, args=())
            self.zmq_thread.setDaemon(True)
            self.zmq_thread.start()

            # Run reading of data and writing to DB as a background thread
            process_thread = Thread(target=self.process_function)
            self.processing = True
            process_thread.start()
            process_thread.join()
            self.processing = False
        else:
            logger.info('Thread already started')


    def send_command_to_inverter(self, command,value):
        the_command = f"{command_dictionary[command]}{value}"
        if self.debug_data:
            return_val = False
            logger.info(f'Sending \'{command}\' with value {value}')
            if command != 1:
                return_val = True
        else:
            return_val = self.send_command_with_ack_reply(the_command)
        return return_val


if __name__ == '__main__':
    '''
    Create the PythonSolar class and start the processing.
    '''
    solar_processor = PythonSolar()
    solar_processor.start_processing()

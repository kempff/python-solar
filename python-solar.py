# Python reader for solar panel controller

from influxdb import InfluxDBClient
from threading import Thread
import logging
import time
import solar_config as config
import sys
from logging.handlers import RotatingFileHandler
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QFileDialog
from PyQt4.QtCore import pyqtSlot
from ui.python_ui import Ui_MainWindow
import crc16
from datetime import datetime, date, timedelta
import pytz
from openpyxl import Workbook
import sys
import usb.core


# Configure DB
influx_client = InfluxDBClient(config.INFLUX_HOST, config.INFLUX_PORT, database=config.INFLUX_DB)

debug_data = config.DEBUG_MODE
write_to_db = True
request_ratings = True              # Flag to request ratings data, only when a command was sent and at startup


if debug_data:
    # Open the files for reading
    pigs_file = open("qpigs.txt","r")
    mod_file = open("qmod.txt","r")
    piri_file = open("qpiri.txt","r")
else:
    # Configure USB to Solar device
    vendorId = 0x0665
    productId = 0x5161
    interface = 0
    usb_dev = usb.core.find(idVendor=vendorId, idProduct=productId)
    if usb_dev.is_kernel_driver_active(interface):
        usb_dev.detach_kernel_driver(interface)
    usb_dev.set_interface_altsetting(0,0)

mode_data = []          # From QMOD command
status_data = []        # From QPIGS command
ratings_data = []       # From QPIRI command
# Setup logging, using the configuration to set the path and the level
log_file_path = config.LOG_FILE_PATH
file_handler = RotatingFileHandler(log_file_path + 'python_solar.log', maxBytes=2 * 1024 * 1024, backupCount=10)
logger = logging.getLogger('python_solar')
log_level_config = config.LOG_LEVEL
log_level = logging.WARNING
if log_level_config == 'INFO':
    log_level = logging.INFO
elif log_level_config == 'DEBUG':
    log_level = logging.DEBUG
file_handler.setLevel(log_level)
formatter = logging.Formatter(
    '\n\n** %(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Configure screen logging according to config
if config.PRINT_LOGS:
    logger = logging.getLogger('python_solar')
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    # add the handler to the root logger
    logger.addHandler(console)

# Read next line from each file, if at end of the file loop to the beginning
def read_file_data(input_file):
    return_data = []
    return_data = input_file.readline()
    if return_data is "":
        input_file.seek(0)
        return_data = input_file.readline()
    return return_data


def get_command(cmd):
    cmd = cmd.encode('utf-8')
    crc = crc16.crc16xmodem(cmd).to_bytes(2,'big')
    cmd = cmd+crc
    cmd = cmd+b'\r'
    while len(cmd)<8:
        cmd = cmd+b'\0'
    return cmd


def send_command(cmd):
    global usb_dev
    usb_dev.ctrl_transfer(0x21, 0x9, 0x200, 0, cmd)


def get_result(timeout=100):
    global usb_dev
    res=""
    i=0
    while '\r' not in res and i<20:
        try:
            res+="".join([chr(i) for i in usb_dev.read(0x81, 8, timeout) if i!=0x00])
        except usb.core.USBError as e:
            if e.errno == 110:
                pass
            else:
                raise
        i+=1
    return res


def write_mode_data(the_data):
    global mode_data
    mode_data = the_data
    
    
def write_status_data(the_data):
    global status_data
    status_data = the_data
    
    
def write_ratings_data(the_data):
    global ratings_data
    ratings_data = the_data
    

def process_result(command, result_data):
    global debug_data
    result_dictionary = {'QMOD' : write_mode_data,
                         'QPIRI': write_ratings_data,
                         'QPIGS': write_status_data}
    if result_data:
        if result_data[0] is '(':
            check_data = result_data[:-3].encode('utf-8')
            rx_crc = result_data[-3:-1].encode('utf-8')
            crc = crc16.crc16xmodem(check_data).to_bytes(2,'big')
            if crc == rx_crc or debug_data:
                result_dictionary[command](result_data[1:-3].split())
            else:
                logger.error('Incorrect CRC for {0} command {1} - {2}'.format(command, crc, rx_crc))
                logger.error('Data: {0}'.format(result_data[:].encode('utf-8')))
        else:
            logger.error('Incorrect start byte for {0} command'.format(command))
    else:
        logger.error('No data for command {0}'.format(command))


# Read data function (either from USB or file)
def read_data():
    global request_ratings
    if debug_data:
        get_command('(B')
        the_data = read_file_data(mod_file)
        logger.info("Mode data: {0}".format(the_data))
        process_result('QMOD', the_data)
        the_data = read_file_data(pigs_file)
        logger.info("Status data: {0}".format(the_data))
        process_result('QPIGS', the_data)
        the_data = read_file_data(piri_file)
        logger.info("Ratings data: {0}".format(the_data))
        process_result('QPIRI', the_data)
    else:
        send_command(get_command('QMOD'))
        result = get_result()  
        logger.debug(result)
        process_result('QMOD', result)
        time.sleep(1)
        send_command(get_command('QPIGS'))
        result = get_result()
        logger.debug(result)
        process_result('QPIGS', result)
        time.sleep(1)
        if request_ratings:
            send_command(get_command('QPIGS'))
            result = get_result()
            logger.debug(result)
            process_result('QPIGS', result)
            request_ratings = False


def populate_status_data(status_data, mode_data, client):
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
    client.write_points(status_body)


def populate_ratings_data(ratings_data, client):
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
    ratings_body[0]['fields']['max_ac_charge_current'] = float(status_data[13])
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
    client.write_points(ratings_body)


def populate_data():
    global mode_data
    global status_data
    global influx_client
    try:
        if write_to_db:
            logger.info("Writing to database...")
            if len(mode_data) > 0:
                logger.debug('Mode data: {0}'.format(mode_data))
            if len(status_data) > 0:
                logger.debug('Status data: {0}'.format(status_data))
                populate_status_data(status_data, mode_data, influx_client)
            if len(ratings_data) > 0:
                logger.debug('Ratings data: {0}'.format(ratings_data))
                populate_ratings_data(ratings_data, influx_client)
    except Exception as e:
        logger.error(str(e))


def send_command_with_ack_reply(command):
    global request_ratings
    send_command(get_command(command))
    result = get_result()
    if result is '(ACK':
        logger.info('Command {0} processed OK').format(command)
        request_ratings = True
    else:
        logger.error('Command {0} error, reply {1}'.format(command,result))


def convert_timestamp_to_datetime(in_time):
    # Remove nanoseconds and 'Z'
    in_time = in_time[:-4]
    the_time = datetime.strptime(in_time,"%Y-%m-%dT%H:%M:%S.%f")
    return the_time


def write_row(the_sheet, the_data):
    # Add offset to time written to spreadsheet
    timestamp = convert_timestamp_to_datetime(the_data['time'])
    timestamp += timedelta(hours=config.TIME_OFFSET)
    the_row = [str(timestamp), the_data['mode'], the_data['ac_output_w'], the_data['pv_input_voltage']]
    # logger.debug(the_row)
    the_sheet.append(the_row)


def calculate_total_time(start_time, end_time):
    end_time_dt = convert_timestamp_to_datetime(end_time)
    start_time_dt = convert_timestamp_to_datetime(start_time)
    time_diff = end_time_dt - start_time_dt
    return time_diff.total_seconds() 
    

def perform_aggregations(start_date, end_date):
    global influx_client
    
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
        query_results = list(influx_client.query(db_queries["All"].format(valid_start_date.isoformat(), valid_end_date.isoformat())).get_points())
        for i, results in enumerate(query_results[:-1]):
            the_time = calculate_total_time(results["time"], query_results[i+1]["time"])
            total_time[results["mode"]] += the_time
            total_time["All"] += the_time
        
        # Now filter according to mode and create separate sheets in spreadsheet
        for key in db_queries.keys():
            book.create_sheet(key)
            sheet = book.get_sheet_by_name(key)
            sheet.append(heading_text)
            query_results = list(influx_client.query(db_queries[key].format(valid_start_date.isoformat(), valid_end_date.isoformat())).get_points())
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

def process_function():
    global processing
    logger.info('Processing thread entry')
    while processing:
        read_data()
        populate_data()
        time.sleep(config.PROCESS_TIME)
    logger.info('Processing thread exit')


logger.info("Program starts: Debug {0}".format(debug_data))
if not debug_data:
    logger.info("USB info: {0}".format(usb_dev))


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.battery_recharge_v_button.clicked.connect(self.update_battery_recharge_v)
        self.output_source_button.clicked.connect(self.update_output_source)
        self.device_charge_button.clicked.connect(self.update_device_charge)
        self.battery_cutoff_button.clicked.connect(self.update_battery_cutoff)
        self.battery_constant_v_button.clicked.connect(self.update_battery_constant_v)
        self.battery_floating_v_button.clicked.connect(self.update_battery_floating_v)
        self.generate_report_button.clicked.connect(self.generate_report)
        
        
    @pyqtSlot()
    def update_battery_recharge_v(self):
        logger.info('Recharge Clicked: {0}'.format(self.battery_recharge_v_edit.text()))
        send_command_with_ack_reply('PBCV'+self.battery_recharge_v_edit.text())

    @pyqtSlot()
    def update_output_source(self):
        output_sources = { 'Utility first': '00', 'Solar first': '01', 'SBU priority': '02'}
        logger.info('Output source Clicked: {0}'.format(self.output_source_combo.currentText()))
        send_command_with_ack_reply('POP'+output_sources[self.output_source_combo.currentText()])
        
    @pyqtSlot()
    def update_device_charge(self):
        output_sources = { 'Utility first': '00', 'Solar first': '01', 'Solar and utility': '02', 'Solar only': '03'}
        logger.info('Device charge Clicked: {0}'.format(self.device_charge_combo.currentText()))
        send_command_with_ack_reply('PCP'+output_sources[self.device_charge_combo.currentText()])
        
    @pyqtSlot()
    def update_battery_cutoff(self):
        logger.info('Battery cutoff Clicked: {0}'.format(self.battery_cutoff_edit.text()))
        send_command_with_ack_reply('PSDV'+self.battery_cutoff_edit.text())
        
    @pyqtSlot()
    def update_battery_constant_v(self):
        logger.info('Battery constant V Clicked: {0}'.format(self.battery_constant_v_edit.text()))
        send_command_with_ack_reply('PCVV'+self.battery_constant_v_edit.text())
        
    @pyqtSlot()
    def update_battery_floating_v(self):
        logger.info('Battery floating V Clicked: {0}'.format(self.battery_floating_v_edit.text()))
        send_command_with_ack_reply('PBFT'+self.battery_floating_v_edit.text())
        
    @pyqtSlot()
    def generate_report(self):
        logger.info('Generate report Clicked: {0} - {1}'.format(self.report_from_edit.text(), self.report_to_edit.text()))
        perform_aggregations(self.report_from_edit.text(), self.report_to_edit.text())


if __name__ == "__main__":
    global processing
    # Run reading of data and writing to DB as a background thread
    process_thread = Thread(target=process_function)
    processing = True
    process_thread.start()
    process_thread.join()
    #app = QApplication(sys.argv)
    #main_window = MainWindow()
    #main_window.show()
    #sys.exit(app.exec_())
    processing = False



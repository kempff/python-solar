from influxdb import InfluxDBClient
import pytz
from datetime import datetime

# Load internal modules
from solar.struct_logger import StructLogger
from solar.settings import DATABASES, TIME_ZONE


the_logger = StructLogger()


class _InfluxInterface:

    def __init__(self):
        # Configure DB
        self.influx_client = InfluxDBClient(DATABASES['influx']['INFLUX_HOST'], DATABASES['influx']['INFLUX_PORT'], 
                database=DATABASES['influx']['INFLUX_DB'])
        self.installation = DATABASES['influx']['INSTALLATION']
        self.tz = pytz.timezone(TIME_ZONE)
        the_logger.info(f"Influx client: {self.influx_client}")


    def convert_time(self, input_value):
        '''
        Convert time to local timezone
        '''
        time_string = input_value + "+0000"
        utc_time = datetime.strptime(time_string,"%Y-%m-%dT%H:%M:%S.%f%z")
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(self.tz)
        return_val = local_time.strftime("%Y-%m-%d %H:%M:%S")
        return return_val


    def get_status_data(self):
        '''
        Performs the queries and return the result from InfluxDB. Can probably do it in 1 query...
        '''
        last_status_time = None
        ac_power_24h = None
        pv_power_24h = None
        ac_on = 0

        status_data = {
            'Battery': {'query_param': 'battery_capacity', 'result': None},
            'AC Power': {'query_param': 'ac_output_w', 'result': None},
            'PV Power': {'query_param': 'pv_input_w', 'result': None},
            'Charging On': {'query_param': 'charging_on', 'result': None},
            'AC Voltage': {'query_param': 'ac_output_voltage', 'result': None},
        }
        try:
            for key in status_data:
                db_data = self.influx_client.query(f"SELECT last(\"{status_data[key]['query_param']}\") FROM \"system_status\" WHERE (\"installation\" = '{self.installation}')")
                # Found this out by: print(db_data.raw)
                status_data[key]['result'] =  round(db_data.raw['series'][0]['values'][0][1])

            if status_data['AC Voltage']['result'] > 210:
                ac_on = 1

            # Retrieve AC and PV power for previous 24 hours. Get the average and multiply by 24.
            db_data = self.influx_client.query(f"""
                SELECT mean(\"ac_output_w\"), mean(\"pv_input_w\") FROM \"system_status\" WHERE (\"installation\" = '{self.installation}') 
                AND time > now() - 24h 
                """)
            
            # To view the data: print(db_data.raw['series'][0]['values'])
            last_status_time = self.convert_time(db_data.raw['series'][0]['values'][0][0][:-4])
            ac_power_24h = round(24 * db_data.raw['series'][0]['values'][0][1])
            pv_power_24h = round(24 * db_data.raw['series'][0]['values'][0][2])

        except Exception as e:
            the_logger.error(f'Influx status: {str(e)}')

        # Retrieve last 10 errors for previous 24 hours
        error_list = []
        try:
            db_data = self.influx_client.query(f"""
                SELECT \"severity\", \"message\" FROM \"system_error\" WHERE (\"installation\" = '{self.installation}') 
                AND time > now() - 24h 
                ORDER BY time DESC LIMIT 10
                """)
            for error in db_data.raw['series'][0]['values']:
            
                error_value = {
                    'timestamp': self.convert_time(error[0][:-4]),
                    'severity': error[1],
                    'error_message': error[2] 
                }
                error_list.append(error_value)
        except Exception as e:
            the_logger.error(f'Influx error retrieve: {str(e)}')

        solar_data = {
                "last_status_time": last_status_time,
                "battery_percentage": status_data['Battery']['result'],
                "ac_on": ac_on,
                "battery_charge": status_data['Charging On']['result'],
                "ac_power": {
                    "current": status_data['AC Power']['result'],
                    "24hours": ac_power_24h,
                },
                "pv_power": {
                    "current": status_data['PV Power']['result'],
                    "24hours": pv_power_24h,
                },
                "errors": error_list,
            }
        the_logger.debug(f'Status: {solar_data}')
        return solar_data


    def get_ratings_data(self):
        '''
        Performs the queries and return the result from InfluxDB. Can probably do it in 1 query...
        '''
        ratings_data = {
            'Max charge A': {'query_param': 'max_charge_current', 'result': None},
            'AC charge A': {'query_param': 'max_ac_charge_current', 'result': None},
            'Battery redischarge V': {'query_param': 'battery_redischarge_voltage', 'result': None},
            'Battery recharge V': {'query_param': 'battery_recharge_voltage', 'result': None},
            'Battery cutoff V': {'query_param': 'battery_under_voltage', 'result': None},
        }

        try:
            for key in ratings_data:
                db_data = self.influx_client.query(f"SELECT last(\"{ratings_data[key]['query_param']}\") FROM \"system_rating\" WHERE (\"installation\" = '{self.installation}')")
                # Found this out by: print(db_data.raw)
                ratings_data[key]['result'] =  round(db_data.raw['series'][0]['values'][0][1])
        except Exception as e:
            the_logger.error(f'Influx ratings retrieve: {str(e)}')


        solar_data = {
                "max_charge_current": ratings_data['Max charge A']['result'],
                "max_ac_charge_current": ratings_data['AC charge A']['result'],
                "battery_redischarge_voltage": ratings_data['Battery redischarge V']['result'],
                "battery_recharge_voltage": ratings_data['Battery recharge V']['result'],
                "battery_cutoff_voltage": ratings_data['Battery cutoff V']['result'],
            }
        the_logger.debug(f'Ratings: {solar_data}')
        return solar_data
    

# Create the InfluxDB interface object
_influx_interface = _InfluxInterface()

def InfluxInterface():
    '''
    Use this function to get the single instance to use.
    '''
    return _influx_interface
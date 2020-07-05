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
        the_logger.info(f"Influx client: {self.influx_client}")


    def get_status_data(self):
        '''
        Performs the queries and return the result from InfluxDB. Can probably do it in 1 query...
        '''
        status_data = {
            'Battery': {'query_param': 'battery_capacity', 'result': None},
            'AC Power': {'query_param': 'ac_output_w', 'result': None},
            'PV Power': {'query_param': 'pv_input_w', 'result': None},
            'Charging On': {'query_param': 'charging_on', 'result': None},
            'AC Voltage': {'query_param': 'ac_output_voltage', 'result': None},
        }

        for key in status_data:
            db_data = self.influx_client.query(f"SELECT last(\"{status_data[key]['query_param']}\") FROM \"system_status\" WHERE (\"installation\" = '{self.installation}')")
            # Found this out by: print(db_data.raw)
            status_data[key]['result'] =  round(db_data.raw['series'][0]['values'][0][1])

        ac_on = 0
        if status_data['AC Voltage']['result'] > 210:
            ac_on = 1

        # Retrieve AC and PV power for previous 24 hours

        # Retrieve last 10 errors for previous 24 hours
        tz = pytz.timezone(TIME_ZONE)
        db_data = self.influx_client.query(f"""
            SELECT \"severity\", \"message\" FROM \"system_error\" WHERE (\"installation\" = '{self.installation}') 
            AND time > now() - 24h 
            ORDER BY time DESC LIMIT 10
            """)
        error_list = []
        for error in db_data.raw['series'][0]['values']:
            # Convert time to local timezone
            time_string = error[0][:-4] + "+0000"
            utc_time = datetime.strptime(time_string,"%Y-%m-%dT%H:%M:%S.%f%z")
            local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(tz)
            error_value = {
                'timestamp': local_time.strftime("%Y-%m-%d %H:%M:%S"),
                'severity': error[1],
                'error_message': error[2] 
            }
            error_list.append(error_value)

        solar_data = {
                "battery_percentage": status_data['Battery']['result'],
                "ac_on": ac_on,
                "battery_charge": status_data['Charging On']['result'],
                "ac_power": {
                    "current": status_data['AC Power']['result'],
                    "24hours": 15000,
                },
                "pv_power": {
                    "current": status_data['PV Power']['result'],
                    "24hours": 10000,
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

        for key in ratings_data:
            db_data = self.influx_client.query(f"SELECT last(\"{ratings_data[key]['query_param']}\") FROM \"system_rating\" WHERE (\"installation\" = '{self.installation}')")
            # Found this out by: print(db_data.raw)
            ratings_data[key]['result'] =  round(db_data.raw['series'][0]['values'][0][1])


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
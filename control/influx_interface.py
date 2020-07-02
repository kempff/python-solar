from influxdb import InfluxDBClient

# Load internal modules
from solar.struct_logger import StructLogger
from solar.settings import DATABASES


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
                "errors": [
                    # TODO retrieve all errors of last 24 hours
                ],
            }
        the_logger.debug(f'Status: {solar_data}')
        return solar_data

# Create the InfluxDB interface object
_influx_interface = _InfluxInterface()

def InfluxInterface():
    '''
    Use this function to get the single instance to use.
    '''
    return _influx_interface
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
        the_logger.info(f"Influx client: {self.influx_client}")


    def get_status_data(self):
        '''
        Performs the queries and return the result from InfluxDB
        '''
        solar_data = {
                "battery_percentage": 70,
                "ac_power": {
                    "current": 120,
                    "24hours": 15000,
                },
                "pv_power": {
                    "current": 220,
                    "24hours": 10000,
                }
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
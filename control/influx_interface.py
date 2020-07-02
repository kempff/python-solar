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
        Performs the queries and return the result from InfluxDB
        '''
        db_data = self.influx_client.query(f"SELECT last(\"battery_capacity\") FROM \"system_status\" WHERE (\"installation\" = '{self.installation}')")
        # Found this out by: print(db_data.raw)
        battery_percentage = db_data.raw['series'][0]['values'][0][1]
        solar_data = {
                "battery_percentage": battery_percentage,
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
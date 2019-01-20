# python-solar

Alternative to WatchPower software for RS-232 based solar power inverter. Written using Python and runs on a Raspberry Pi 3+.

## Installation

The project requires InfluxDB and Graphana.

### Influx DB

* wget https://dl.influxdata.com/influxdb/releases/influxdb-1.7.3_linux_armhf.tar.gz
* tar xvfz influxdb-1.7.3_linux_armhf.tar.gz
* Copied all the files to the root folder
* sudo service influxdb start
* influx (should open the command prompt for the DB)
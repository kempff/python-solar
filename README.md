# python-solar

Alternative to WatchPower software for RS-232 based solar power inverter. Written using Python and runs on a Raspberry Pi 3+.

## Installation

The project requires Django, Postgres, (InfluxDB) and Grafana.

### Postgres

* sudo apt install postgresql libpq-dev postgresql-client postgresql-client-common 
* sudo su postgres
* createuser solar -P --interactive
* psql
* create database solar;
* \q 
* exit


### Influx DB

* wget https://dl.influxdata.com/influxdb/releases/influxdb-1.7.3_linux_armhf.tar.gz
* tar xvfz influxdb-1.7.3_linux_armhf.tar.gz
* Copied all the files to the root folder
* sudo service influxdb start
* influx (should open the command prompt for the DB)

### Grafana

* wget https://dl.grafana.com/oss/release/grafana_5.4.3_armhf.deb 
* sudo dpkg -i grafana_5.4.3_armhf.deb 
* Auto start at startup: sudo update-rc.d grafana-server defaults

Checking it out:
Browse to localhost:3000, username and password admin/admin

## Remote access

Using _remote.it_

# python-solar

Alternative to WatchPower software for RS-232 based solar power inverter. Written using Python and runs on a Raspberry Pi 3+.

## Installation

The project requires Django, Postgres, (InfluxDB) and Grafana.

Note: when python modules gave installation errors upon _pipenv install_ run _pipenv shell_ without them in the _Pipfile_ and then run _pip install <modulename>_. Thereafter the shell can be exit and the modules added to the _Pipfile_.

### Postgres

* sudo apt install postgresql libpq-dev postgresql-client postgresql-client-common 
* sudo su postgres
* createuser solar -P --interactive
* psql
* create database solar;
* ALTER USER postgres with password '<your-pass>';
* \q 
* exit

To connect thereafter:
* psql -U postgres -h 127.0.0.1

### Django

* In python-solar: pipenv shell
* django-admin startproject solar
* Move directory to one level up
* python manage.py startapp control
* Edit settings.py and select 'django.db.backends.postgresql' as ENGINE
* python manage.py migrate
* python manage.py createsuperuser
* python manage.py runserver

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

# python-solar

Alternative to WatchPower software for RS-232 based solar power inverter. Written using Python and runs on a Raspberry Pi 3+/ Pi 4.

## Installation

The project requires Django, Postgres, InfluxDB and Grafana.

Note: when python modules gave installation errors upon _pipenv install_ run _pipenv shell_ without them in the _Pipfile_ and then run _pip install <modulename>_. Thereafter the shell can be exit and the modules added to the _Pipfile_.

### First time installation on PC/Pi

* sudo apt-get install git git-flow
* sudo apt install python3-pip
* pip3 install pipenv
* Add path to .bashrc where pipenv is installed (e.g. export PATH="/home/pi/.local/bin:$PATH")
* git clone https://github.com/kempff/python-solar.git
* cd python-solar
* git flow init
* git checkout develop (or other feature branch)
* pipenv install --python /usr/bin/python3
* If crc16, zmq and psycopg fails: pipenv shell, pip install crc16==0.1.1, pip install psycopg2-binary==2.8.4, pip install pyzmq==19.0.0,
exit, pipenv install
* If django fails: pipenv shell, pip install django==3.0.8, exit, pipenv shell
* Enable SSH on the Pi for remote connection: Start menu -> Preferences -> Raspberry Pi Configuration -> Interfaces

### Python 3.7 (not required for latest Raspbian)

SSL:
* sudo apt-get install build-essential checkinstall libreadline-gplv2-dev libncursesw5-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
* cd /usr/src
* sudo curl https://www.openssl.org/source/openssl-1.0.2o.tar.gz | sudo tar xz 
* cd openssl-1.0.2o
* sudo ./config shared --prefix=/usr/local/
* sudo make
* sudo make install
* sudo mkdir lib
* sudo cp ./*.{so,so.1.0.0,a,pc} ./lib

Python:
* cd ~/Downloads
* sudo wget https://www.python.org/ftp/python/3.7.7/Python-3.7.7.tgz
* sudo tar xzf Python-3.7.7.tgz
* cd Python-3.7.7
* ./configure --with-openssl=~/Downloads/openssl-1.0.2o --enable-optimizations
* sudo make
* sudo make altinstall

### Postgres

* sudo apt install postgresql libpq-dev postgresql-client postgresql-client-common 
* sudo su postgres
* createuser solar -P --interactive
* psql
* create database solar;
* \password <enter new postgres password>
* \q 
* exit

To connect thereafter:
* psql -U postgres -h 127.0.0.1

### Django

* Setup DB connection in .env file (create file if it does not exist)
    * POSTGRES_PASSWORD=<postgres password>
* In python-solar: pipenv shell
* First time only:
    * django-admin startproject solar
    * Move directory to one level up
    * python manage.py startapp control
    * Edit settings.py and select 'django.db.backends.postgresql' as ENGINE
* python manage.py migrate
* python manage.py createsuperuser
* python manage.py runserver
* Open browser, login and browse to 'http://127.0.0.1:8000/admin/' and create users and groups

#### Static files

* _sudo mkdir /var/www/_
* _sudo mkdir /var/www/solar_
* _sudo mkdir /var/www/solar/static_
* sudo chown to user and group that has access to copy files: _sudo chown pi:pi /var/www/solar -R_
* Add environment variable: STATIC_ROOT='/var/www/solar/static'
* In project pipenv shell run: _python manage.py collectstatic_ to copy all the files for serving through Nginx

**Note: With DEBUG=True in the settings.py file Django serves the files from the project directory.** 

### Influx DB

* On Pi: 
    * wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
    * source /etc/os-release
    * sudo apt-get update && sudo apt-get install influxdb
    * sudo apt install influxdb-client

* On Ubuntu: 
    * wget https://dl.influxdata.com/influxdb/releases/influxdb_1.7.10_amd64.deb
    * sudo dpkg -i influxdb_1.7.10_amd64.deb

* sudo service influxdb start
* influx (should open the command prompt for the DB)
    * CREATE DATABASE solardb

### Grafana

* On Pi:
    * wget https://dl.grafana.com/oss/release/grafana-rpi_7.0.6_armhf.deb
    * sudo dpkg -i grafana-rpi_6.6.2_armhf.deb
* On Ubuntu:
    * sudo apt-get install -y adduser libfontconfig1
    * wget https://dl.grafana.com/oss/release/grafana_6.6.2_amd64.deb
    * sudo dpkg -i grafana_6.6.2_amd64.deb    
* Auto start at startup: 
    * sudo update-rc.d grafana-server defaults
    * sudo systemctl enable grafana-server.service
* To enable embedding in iframe (not used anymore - just for reference):
    * sudo geany /etc/grafana/grafana.ini
    * add allow_embedding=true under [security]
    * sudo service grafana-server restart
* To enable using subpath from nginx
    * sudo geany /etc/grafana/grafana.ini
    * root_url = http://localhost:3000/grafana/
    * serve_from_sub_path = true
    * sudo service grafana-server restart
* Browser to localhost:3000, username and password admin/admin
    * Enter a new admin password when prompted
    * Add the InfluxDB datasource
    * Add 'viewer' user with password 'grafana123' under 'Server admin' -> 'Users' menu
    * Add the connection to the solardb Influx database
    * Select 'Import' in the 'Create' menu and upload the JSON files in the 'grafana' directory of the project
    * Select each graph as a favorite by clicking on the star
    * Change the organisation name to reflect the installation
    * Default screen: Configuration > Preferences you can set the home dashboard for your organization.
* Disable the login in Grafana and change user to view only:
    * sudo geany /etc/grafana/grafana.ini
    * Edit the values in the _[auth.anonymous]_ section
    * sudo service grafana-server restart
    * Browse to localhost:3000 and the default page must be displayed

Note: a default _grafana.ini_ file is included in the _grafana_ directory of the code.

### USB

* lsusb:
    _Bus 001 Device 007: ID 0665:5161 Cypress Semiconductor USB to Serial_
* Add the vendor and product
    * _sudo nano /etc/udev/rules.d/99-solar.rules_
    * SUBSYSTEM=="usb", ATTR{idVendor}=="0665", ATTR{idProduct}=="5161", MODE="666"
* _sudo udevadm control --reload_
* _sudo udevadm trigger_


### Gunicorn

* _pipenv shell_
* _which gunicorn_
* Copy pathname to be use in Gunicorn service file (<gunicorn path> below)
* Create a Gunicorn systemd Service File

_sudo geany /etc/systemd/system/gunicorn.service_

```
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=pi
Group=pi
WorkingDirectory=/home/pi/python-solar
EnvironmentFile=/home/pi/python-solar/.env
ExecStart=<gunicorn path> --access-logfile - --workers 3 --timeout 600 --bind unix:/home/pi/python-solar/python-solar.sock solar.wsgi:application

[Install]
WantedBy=multi-user.target

```

* _sudo systemctl start gunicorn_
* _sudo systemctl enable gunicorn_
* _sudo systemctl status gunicorn_

### Nginx

* _sudo apt-get install nginx_
* _sudo geany /etc/nginx/sites-available/python-solar_

```
server {
    listen 80;
    access_log /home/pi/python-solar/logs/nginx-access.log;
    error_log /home/pi/python-solar/logs/nginx-error.log;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static {
        root /var/www/solar;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/pi/python-solar/python-solar.sock;
    }

    location /grafana/ {
        rewrite ^/grafana(.*) $1 break;
        proxy_pass http://localhost:3000/;
        proxy_set_header Host $http_host;
    }
}
```

* _sudo ln -s /etc/nginx/sites-available/python-solar /etc/nginx/sites-enabled_
* Test by: _sudo nginx -t_
* _pipenv shell_
* _python manage.py collectstatic_

If default nginx screen is displayed:

* _sudo rm /etc/nginx/sites-enabled/default_
* _sudo service nginx restart_


### Running pythonsolar (backend processing) from a service file

* _sudo geany /etc/systemd/system/solar.service_
```
[Unit]
Description=pythonsolar daemon
After=network.target

[Service]
User=pi
Group=pi
Restart=always
RestartSec=10
WorkingDirectory=/home/pi/python-solar
EnvironmentFile=/home/pi/python-solar/.env
ExecStart=/home/pi/.local/bin/pipenv run python /home/pi/python-solar/pythonsolar.py

[Install]
WantedBy=multi-user.target

```
* _sudo systemctl start solar_
* _sudo systemctl enable solar_

### Enable ask for password for 'pi' user



### Remote access

Options:
* Using _remote.it_ to add connections
    * _sudo apt install remoteit_
    * Broswe to location provided (e.g. http://raspberrypi.local:29999)
    * Setup SSH and HTTP
* Expost the HTTP port with _remote.it_ and use Gunicorn and Nginx

## Running the application

* To execute:
    * pipenv shell
    * python pythonsolar.py
    * In another terminal: 
        * pipenv shell 
        * python manage.py runserver

## Access from Virtualbox

* Power down Virtualbox
* Go to "Global Tools" and click on "Create"
* Go to the "Network" settings of the Virtualbox, select "Host network" and the created network. 

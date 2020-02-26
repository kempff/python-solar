# python-solar

Alternative to WatchPower software for RS-232 based solar power inverter. Written using Python and runs on a Raspberry Pi 3+/ Pi 4.

## Installation

The project requires Django, Postgres, (InfluxDB) and Grafana.

Note: when python modules gave installation errors upon _pipenv install_ run _pipenv shell_ without them in the _Pipfile_ and then run _pip install <modulename>_. Thereafter the shell can be exit and the modules added to the _Pipfile_.

### First time installation on PC

* sudo apt-get install git git-flow
* sudo apt install python3-pip
* pip3 install pipenv
* Add path to .bashrc where pipenv is installed (e.g. export PATH="/home/gkempff/.local/bin:$PATH")
* git clone https://github.com/kempff/python-solar.git
* cd python-solar
* git flow init
* git checkout develop (or other feature branch)
* pipenv install
* If crc16 and psycopg fails: pipenv shell, pip install crc16, pip install psycopg2-binary, exit, pipenv install

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

### Influx DB

* On Pi: 
    * wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
    * source /etc/os-release
    * sudo apt-get update && sudo apt-get install influxdb

* On Ubuntu: 
    * wget https://dl.influxdata.com/influxdb/releases/influxdb_1.7.10_amd64.deb
    * sudo dpkg -i influxdb_1.7.10_amd64.deb

* sudo service influxdb start
* influx (should open the command prompt for the DB)
    * CREATE DATABASE solardb

### Grafana

* On Pi:
    * wget https://dl.grafana.com/oss/release/grafana-rpi_6.6.2_armhf.deb
    * sudo dpkg -i grafana-rpi_6.6.2_armhf.deb
* On Ubuntu:
    * sudo apt-get install -y adduser libfontconfig1
    * wget https://dl.grafana.com/oss/release/grafana_6.6.2_amd64.deb
    * sudo dpkg -i grafana_6.6.2_amd64.deb    
* Auto start at startup: 
    * sudo update-rc.d grafana-server defaults
    * sudo systemctl enable grafana-server.service
* To enable embedding in iframe:
    * sudo geany /etc/grafana/grafana.ini
    * add allow_embedding=true under [security]
    * sudo service grafana-server restart
* Browser to localhost:3000, username and password admin/admin
    * Enter a new admin password when prompted
    * Add the InfluxDB datasource
    * Add 'viewer' user with password 'grafana123' under 'Server admin' -> 'Users' menu
    * Add the connection to the solardb Influx database
    * Select 'Import' in the 'Create' menu and upload the JSON files in the 'grafana' directory of the project

### Redis

* Installation:
    * wget http://download.redis.io/redis-stable.tar.gz
    * tar xvzf redis-stable.tar.gz
    * cd redis-stable
    * make
    * sudo make install
* Test by:
    * redis-server
    * In another terminal: redis-cli ping (returns 'PONG')
    * redis-cli shutdown (to stop server)
* Installing to use an init script:
    * sudo cp utils/redis_init_script /etc/init.d/redis_6379
    * sudo mkdir /etc/redis
    * sudo cp redis.conf /etc/redis/6379.conf
    * sudo mkdir /var/redis
    * sudo mkdir /var/redis/6379
    * sudo nano /etc/redis/6379.conf
        * Set __daemonize__ to yes (by default it is set to no)
        * Set __pidfile__ to /var/run/redis_6379.pid 
        * Set __logfile__ to /var/log/redis_6379.log
        * Set __dir__ to /var/redis/6379 (very important step!)
    * sudo update-rc.d redis_6379 defaults
    * sudo /etc/init.d/redis_6379 start
    * Testing installation:
        * redis-cli ping (returns 'PONG')
        * redis-cli save (DB saved to '/var/redis/6379/dump.rdb')

### Celery

* pipenv shell
* pip install Celery
* To execute (saving celery logs to _/tmp/solar.log_):
    * celery -A tasks worker --loglevel=info -f /tmp/solar.log

## Remote access

Options:
* Using _remote.it_ to add a VNC connection
* Expost the HTTP port with _remote.it_ and use Gunicorn and Nginx

### Gunicorn

* Create a Gunicorn systemd Service File

_sudo nano /etc/systemd/system/gunicorn.service_

```
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=sysadmin
Group=sysadmin
WorkingDirectory=/home/sysadmin/Projects/python-solar
EnvironmentFile=/home/sysadmin/Projects/python-solar/.env
ExecStart=/home/sysadmin/.local/share/virtualenvs/python-solar-DAj_LhDv/bin/gunicorn --access-logfile - --workers 3 --timeout 600 --bind unix:/home/sysadmin/Projects/python-solar/python-solar.sock solar.wsgi:application

[Install]
WantedBy=multi-user.target

```

* _sudo systemctl start gunicorn_
* _sudo systemctl enable gunicorn_
* _sudo systemctl status gunicorn_

### Nginx

* _sudo apt-get install nginx_
* _sudo nano /etc/nginx/sites-available/python-solar_

```
server {
    listen 80;
    server_name 127.0.0.1;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static {
        root home/sysadmin/Projects/python-solar;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/sysadmin/Projects/python-solar/python-solar.sock;
    }
}
```

* _sudo ln -s /etc/nginx/sites-available/python-solar /etc/nginx/sites-enabled_
* Test by: _sudo nginx -t_
* _python manage.py collectstatic_




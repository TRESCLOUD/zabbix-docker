FROM zabbix/zabbix-server-pgsql:ubuntu-5.0-latest

RUN apt-get update && apt-get upgrade && apt-get install curl -y

FROM zabbix/zabbix-server-pgsql:ubuntu-5.2-latest

USER root
RUN apt-get update && apt-get install -y curl \
    python3-pip
RUN pip3 install erppeek
USER zabbix
#!/bin/bash
#
# Autor: Trescloud Cia. Ltda., Patricio Rangles
#
# Script que instala el servicio para recuperar el servidor en caso de reinicio
# Se descarta el uso de restart: always en el archivo yaml por problemas con 
# el agente de Zabbix, al parecer por un bug en docker-compose no se puede levantar
# adecuadamente
#
# 2021-09-01: Agregado instalacion de Postgres directo en el servidor para uso de tablas
#             particionadas y mejora de performance.
#

#Verifico si Psql de postgres esta instalado
sudo psql --version
result=$?
if [ "${result}" -eq "0" ] ; then
    echo "`date`: Ya esta instalado postgres"
else
    echo "`date`: instalando Postgres 13 ..."
    sudo apt install wget ca-certificates
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
    sudo apt update
    sudo apt-get install -y postgresql-13 postgresql-contrib postgresql-13-partman
fi

# instalo librerias del sistema operativo y python requeridas
# por los scripts complemetarios

sudo apt install python3-pip -y
pip3 install docker

# construyo la imagen de TRESCLOUD con curl incluido
cd TRESCLOUD
docker build -t zabbix-server-pgsql:ubuntu-5.2-latest-trescloud .
cd ..

# copio el servicio
sudo cp docker-compose-zabbix.service /etc/systemd/system/

# habilito el servicio
sudo systemctl enable docker-compose-zabbix

#!/bin/bash
#
# Autor: Trescloud Cia. Ltda., Patricio Rangles
#
# Script que instala el servicio para recuperar el servidor en caso de reinicio
# Se descarta el uso de restart: always en el archivo yaml por problemas con 
# el agente de Zabbix, al parecer por un bug en docker-compose no se puede levantar
# adecuadamente

# instalo librerias del sistema operativo y python requeridas
# por los scripts complemetarios

sudo apt install python3-pip
pip3 install docker

# construyo la imagen de TRESCLOUD con curl incluido
cd TRESCLOUD
docker build -t zabbix-server-pgsql:ubuntu-5.2-latest-trescloud .
cd ..

# copio el servicio
sudo cp docker-compose-zabbix.service /etc/systemd/system/

# habilito el servicio
sudo systemctl enable docker-compose-zabbix

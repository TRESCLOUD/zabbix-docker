#!/bin/bash
#
# Autor: Trescloud Cia. Ltda., Patricio Rangles
#
# Script que instala el servicio para recuperar el servidor en caso de reinicio
# Se descrata el uso de restart: always en el archivo yaml por problemas con 
# el agente de Zabbix, al parecer por un bug en docker-compose no se puede levantar
# adecuadamente

sudo cp docker-compose-zabbix.service /etc/systemd/system/
sudo systemctl enable docker-compose-zabbix

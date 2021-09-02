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
# NOTA: Desde esta version se soporta multiarquitectura
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

# Verifico la arquitectura a usarse
arch_system=$(dpkg --print-architecture)

#Verifico si Docker esta instalado
sudo docker --version
result=$?
if [ "${result}" -eq "0" ] ; then
    echo "`date`: Ya esta instalado Docker"
else
    echo "`date`: instalando Docker ..."
	#Llave publica Docker
	#sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
	wget https://download.docker.com/linux/ubuntu/gpg
	sudo apt-key add gpg
	rm gpg
	
	# Verifico si es ubuntu o debian la distribucion
	check_ubuntu=$(cat /etc/issue | grep Ubuntu)
	check_debian=$(cat /etc/issue | grep Debian)
	
	if [[ -z $check_ubuntu ]]
	then
		if [[ -z $check_debian ]]
		then
			echo "Distribucion de Linux no soportada"
			exit 1
		else
			sudo su -c "echo 'deb [arch=$arch_system] https://download.docker.com/linux/debian $(lsb_release -cs) stable' > /etc/apt/sources.list.d/docker.list"
		fi
	else
		sudo su -c "echo 'deb [arch=$arch_system] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable' > /etc/apt/sources.list.d/docker.list"
	fi
	
	# instalacion de Docker 
	sudo apt-get update && sudo apt-get install -y docker-ce
	
	#Instalo Docker compose
	sudo pip3 install pip3
	sudo pip3 install docker-compose
	
    #Permisos de Docker
    sudo usermod -a -G docker $USER
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

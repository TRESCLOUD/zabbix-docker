#!/bin/bash
################################################################################################
# Nombre: vacuum_full_zabbix
# Fecha: 14/07/2021
# Autor: TRESCLOUD Cia. Ltda., Patricio Rangles
#
# Script para realizar VACUUM FULL y ANALIZE VERBOSE a la base de datos de Zabbix
#
################################################################################################

VACUUM_LOG="${HOME}/vacuum-full-zabbix.log"

# debido a que estamos usando un contenedor para Postgres se usa datos predefinidos
# accedemos al contenedor de postgres y desde dentro ejecutamos el vacuum
echo "Ejecucion actual: "`date`" ------------------------------------------" >> $VACUUM_LOG
echo "Ejecucion actual: "`date`" ------------------------------------------"
docker exec -u postgres zabbix-docker_postgres-server_1 psql -U zabbix -c "VACUUM FULL VERBOSE ANALYZE;" >> $VACUUM_LOG
echo "Tarea Finalizada." `date` >> $VACUUM_LOG
echo "" >> $VACUUM_LOG
echo "Tarea Finalizada." `date`
echo ""

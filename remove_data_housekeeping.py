# Autor: Trescloud Cia. Ltda., Patricio Rangles
#
# Fecha: 14-07-2021
#
# Basado en el script de esta web:
# https://www.zabbix.com/forum/zabbix-troubleshooting-and-problems/373410-zabbix-housekeeper-processes-more-than-75-busy#post386846
#
# Se ejecuta la eliminacion de datos antiguos de zabbix segun la configuracion personalizada para housekeeping
# en este caso las tablas afectadas son las de history que debido a su rapido crecimiento requieren eliminacion externa
# 
# - El script realiza la verificacion si hay una copia del mismo en ejecucion
# - A continuacion verifica la cantidad de registros que deben eliminarse por tabla y ejecuta la eliminacion
#   por cada una en secuencia hasta vaciarlas todas
# - Una vez que son eliminados los datos detectados el script finaliza y permite que el cron lo vuelva a ejecutar
#
# El script deberia ser ejecutado cada hora aproximadamente, con esto se evita acumular las tablas y complicar su gestion
#
# Identificacion de si existe un proceso ya corriendo
# https://stackoverflow.com/questions/4843359/python-lock-a-file
# 
# NOTA: se necesita completar con fcntl.LOCK_NB
#
# Librerias requeridas:
# pip3 install docker

import fcntl
import docker
import time
#import os


# Variables generales
lock_file = '/tmp/.remove_data_housekeeping_lockfile.LOCK'
container = 'zabbix-docker_postgres-server_1'
container_user = 'postgres'

#limites de eliminacion maximo por interaccion
#limit_trends_uint = 10000
limit_history_str = 1000
limit_history_text = 10000
limit_history = 30000
limit_history_uint = 50000

# Tiempo de espera entre eliminaciones
# esta en segundos
sleep_time = 10

#####################################################################################
# Funciones
def acquireLock():
    ''' acquire exclusive lock file access '''
    locked_file_descriptor = open(lock_file, 'w+')
    fcntl.lockf(locked_file_descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return locked_file_descriptor

def releaseLock(locked_file_descriptor):
    ''' release exclusive lock file access '''
    locked_file_descriptor.close()

def get_docker_client():
    """
    Carga como parte del environment los datos de conexion a docker
    """
    #os.environ["DOCKER_TLS_VERIFY"] = "1"
    #os.environ["DOCKER_HOST"] = "tcp://%s:2376"%(self.slave_host_ip)
    #os.environ["DOCKER_CERT_PATH"] = keys_path
    #os.environ["DOCKER_MACHINE_NAME"] = "slaveodoo"
    # cliente docker listo para usarse
    docker_client = docker.from_env()
    return docker_client

def container_exist(name):
    """
    Funcion que determina si existe el contenedor corriendo
    """
    docker_client = get_docker_client()
    list = docker_client.containers.list()
    for container in list:
        if container.name == name:
            return container
    return False

def container_exec_run(user, name, command):
    """
    Funcion que permite ejecutar un comando dentro del contenedor,
    en este caso retornamos tanto el codigo de salida
    como el resultado obtenido.

    parametros:
    name: indica el nombre del contenedor sobre el cual se ejceuta el comando enviado
    command: es el comando enviado para su ejecucion dentro del contenedor
    """
    if not command or not name:
        # Retorno False 2 veces por que siempre retorno 2 elementos
        return False, False
    container = container_exist(name)
    if container:
        return container.exec_run(command, user=user)
    return False, False

####################################################################################

# adquiero el bloqueo sobre el archivo
# si no lo logra sale con error
lock_fd = acquireLock()

# obtengo el total de datos que necesitamos eliminar y a partir de aqui 
# se controlara la eliminacion de todos

#TODO: eliminar los trends luego de 2 años
#Los trends no se eliminan aun, no existen aun
#echo "eliminacion trends_uint"
#docker exec -u postgres zabbix-docker_postgres-server_1 psql -U zabbix -c "DELETE FROM trends_uint t WHERE ctid IN ( SELECT t.ctid FROM trends_uint t LEFT JOIN items i ON i.itemid = t.itemid WHERE to_timestamp(t.clock) < (current_date - ((i.trends)::interval)) LIMIT $limit_trends_uint);"

# ### history_str
# command = 'psql -U zabbix -c "SELECT count(*) FROM history_str h WHERE ctid IN ( SELECT h.ctid FROM history_str h LEFT JOIN items i ON i.itemid = h.itemid WHERE to_timestamp(h.clock) < (current_date - ((i.history)::interval)));"'
# status, total_history_str = container_exec_run(container_user, container, command)
# if status != 0:
#     exit(1)
# # b' count  \n--------\n 120412\n(1 row)\n\n'
# total_history_str = int(total_history_str.split()[2])
# print("total_history_str: %s" % total_history_str)

# ### history_text
# command = 'psql -U zabbix -c "SELECT count(*) FROM history_text h WHERE ctid IN ( SELECT h.ctid FROM history_text h LEFT JOIN items i ON i.itemid = h.itemid WHERE to_timestamp(h.clock) < (current_date - ((i.history)::interval)));"'
# status, total_history_text = container_exec_run(container_user, container, command)
# if status != 0:
#     exit(1)
# # b' count  \n--------\n 120412\n(1 row)\n\n'
# total_history_text = int(total_history_text.split()[2])
# print("total_history_text: %s" % total_history_text)

# ### history_uint
# command = 'psql -U zabbix -c "SELECT count(*) FROM history_uint h WHERE ctid IN ( SELECT h.ctid FROM history_uint h LEFT JOIN items i ON i.itemid = h.itemid WHERE to_timestamp(h.clock) < (current_date - ((i.history)::interval)));"'
# status, total_history_uint = container_exec_run(container_user, container, command)
# if status != 0:
#     exit(1)
# # b' count  \n--------\n 120412\n(1 row)\n\n'
# total_history_uint = int(total_history_uint.split()[2])
# print("total_history_uint: %s" % total_history_uint)

# se cuenta la cantidad de items eliminados
total_history_str = total_history_text = total_history_uint = 0
# se indica cuando ya no hayan items que borrar, se inicia directamente la eliminacion pero se marca con False si se detecta que no se eliminaron registros
history_str = history_text = history_uint = True

while history_str or history_text or history_uint:
    if history_str:
        command = 'psql -U zabbix -c "DELETE FROM history_str h WHERE ctid IN ( SELECT h.ctid FROM history_str h LEFT JOIN items i ON i.itemid = h.itemid WHERE to_timestamp(h.clock) < (current_date - ((i.history)::interval)) LIMIT %s);"' % limit_history_str
        status, result = container_exec_run(container_user, container, command)
        if status != 0:
            exit(1)
        last_value = int(result.split()[1])
        total_history_str += last_value
        if last_value == 0:
            history_str = False
        print("history_str: %s, total_history_str: %s" % (history_str, total_history_str))
        time.sleep(sleep_time)

    if history_text:
        command = 'psql -U zabbix -c "DELETE FROM history_text h WHERE ctid IN ( SELECT h.ctid FROM history_text h LEFT JOIN items i ON i.itemid = h.itemid WHERE to_timestamp(h.clock) < (current_date - ((i.history)::interval)) LIMIT %s);"' % limit_history_text
        status, result = container_exec_run(container_user, container, command)
        if status != 0:
            exit(1)
        last_value = int(result.split()[1])
        total_history_text += last_value
        if last_value == 0:
            history_text = False
        print("history_text: %s, total_history_text: %s" % (history_text, total_history_text))
        time.sleep(sleep_time)

    if history_uint:
        command = 'psql -U zabbix -c "DELETE FROM history_uint h WHERE ctid IN ( SELECT h.ctid FROM history_uint h LEFT JOIN items i ON i.itemid = h.itemid WHERE to_timestamp(h.clock) < (current_date - ((i.history)::interval)) LIMIT %s);"' % limit_history_uint
        status, result = container_exec_run(container_user, container, command)
        if status != 0:
            exit(1)
        last_value = int(result.split()[1])
        total_history_uint += last_value
        if last_value == 0:
            history_uint = False
        print("history_uint: %s, total_history_uint: %s" % (history_uint, total_history_uint))
        time.sleep(sleep_time)

# libero el bloqueo del archivo para una
# futura ejecucion
releaseLock(lock_fd)

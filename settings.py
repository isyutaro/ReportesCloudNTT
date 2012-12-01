#nombres de servidores para generar reporte
LISTA_SERVIDORES = [
    'uno',
    ]

#correos donde se enviaran los reportes
MAIL_FROM = ''
MAIL_TO = [
    '',
    ]
MAIL_SERVER = ''
MAIL_PORT_SMTP = 25

#redondear BandWidth tipo floor yes|no
ROUND = 'no'

#porcentaje de ganancia
GANANCIA = 18

#Costos
cpuP = 0.0
RAMP = 0.0
StorageP = 0.0
BandWidthPI = 0.0
BandWidthPO = 0.0
cloudStorageP = 0.0

#SQL cacti
MySQL_USER = ''
MySQL_PW = ''
MySQL_DB = ''

#Datos CACTI graficas
USER_WEB_CACTI = ''
PASSWD_WEB_CACTI = ''

URL_CACTI = ''

#NTT datos
NTT_USER = ''
NTT_PW = ''
NTT_URL = ''

try:
    from local_settings import *
except ImportError:
    pass

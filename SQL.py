import MySQLdb
from settings import MySQL_USER, MySQL_PW, MySQL_DB

class SQL:
        def getListaCacti(self):
                db = MySQLdb.connect(user=MySQL_USER, db=MySQL_DB, passwd=MySQL_PW, host='localhost')
                cursor = db.cursor()
                #cursor.execute('select host.description, graph_local.id from host, graph_local, graph_templates where host.id=graph_local.host_id and graph_templates.id=graph_local.graph_template_id and graph_templates.id=33')
                cursor.execute('select host.description, graph_local.id from host, graph_local, graph_templates where host.id=graph_local.host_id and graph_templates.id=graph_local.graph_template_id and (graph_templates.id=32 or graph_templates.id=33) group by host.description')
                lista = cursor.fetchall()
                db.close()
                return lista

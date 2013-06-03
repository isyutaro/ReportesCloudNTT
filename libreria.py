# coding: utf-8
from twill.commands import *
from fecha import *
from settings import *
import os
import re
import locale

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch, landscape
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table
from reportlab.lib.styles import getSampleStyleSheet

import smtplib
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Encoders import encode_base64
from email import Encoders

class libreria:
	locale.setlocale(locale.LC_ALL,('es_MX','UTF8'))
	path = os.path.abspath(os.path.dirname(__file__)) + "/"
	listaServidores = LISTA_SERVIDORES
	hoy = datetime.datetime.now()
	reporteGeneral = 'csv/reporteCloud[' + hoy.strftime("%Y-%B") + '].csv'

	def connectCacti(self):
		#Nos conectamos al sitio
		go(URL_CACTI)
		fv("1", "login_username", USER_WEB_CACTI)
		fv("1", "login_password", PASSWD_WEB_CACTI)
		submit("None")

	def connectNTT(self):
		#nos conectamos a la nube NTT obteniendo los detalles del reporte al periodo anterior
		Fecha = fecha()
		hoy = Fecha.getNow()
		final = Fecha.getUltimoDia(hoy)
		primero = Fecha.getPrimerDia(final)
		START = str(primero.year) + '-' + str("%02d"%primero.month) + '-01'
		END = str(primero.year) + '-' + str("%02d" % (primero + datetime.timedelta(days=32)).month) + '-01'
		NTT_URL2 = NTT_URL.replace('START',START)
		NTT_URL2 = NTT_URL2.replace('END',END)
		go(NTT_URL2)
		#nos autenticamos
		fv("1", "userId", NTT_USER)
		fv("1", "password", NTT_PW)
		submit("None")

	def generarReporteGeneral(self):
		#cramos un archivo para guardar el reporte
		f = file(self.path + self.reporteGeneral, 'w')
		#guardamos
		f.write(show())
		f.close()

	def getReporteServidor(self, servidor):
		f = file(self.path + self.reporteGeneral, 'r')
		reporte = f.read()
		f.close()
		
		#dividimos el archivo en una lista por filas
		reporte = reporte.split('\n')

		aux = []
		#Agregamos la lista de servidores filtrada por los que estan Running y agregados en el archivo de configuracion
		for i in reporte:
			if (i.split(',')[0].replace("\"",'') == servidor and i.split(',')[4] == 'Running'):
				aux.append(i.split(','))

		return aux

	def getListaServidores(self):
		listaServidores = self.listaServidores

		#quitamos espacios de la lista
		for i in range(len(listaServidores)):
			listaServidores[i] = listaServidores[i].strip()
		
		return listaServidores

	def getTraffico(self,servidor):
		#servidor es una lista donde [0] = Nombre servidor, [1] = ID grafica de trafico
		#ID de la grafica
		ID = str(servidor[1])
		
		#Clase para obtener inicio y fin del mes anterior
		Fecha = fecha()
		hoy = Fecha.getNow()
		final = Fecha.getUltimoDia(hoy)
		primero = Fecha.getPrimerDia(final)
#		primero=datetime.date(primero.year,primero.month+1,primero.day)
#		final=datetime.date(final.year,final.month+1,final.day+1)
		
		#variable auxiliar
		auxOut = []
		auxIn = []
		
		#ciclo para obtener Ancho de banda de cada dia del mes
		
		for i in range(final.day):
			#variable general para la grafica de Kraft de ancho de banda bytes
			url = URL_CACTI + '/graph.php?action=properties&local_graph_id=<ID>&rra_id=0&graph_start=<START>&graph_end=<END>'
			#inicio del dia combertido a timestamp
			inicio = time.mktime(primero.timetuple())
			inicio = str(int(inicio))
			#incrementamos dia
			primero += datetime.timedelta(days=1)
			#restamos 1 segundo
			primero -= datetime.timedelta(seconds=1)
			#final del dia
			final = time.mktime(primero.timetuple())
			final = str(int(final))
			#sumamos un segundo
			primero += datetime.timedelta(seconds=1)
			
			#se reemplazan los identificadores para actualizar a la fecha señalada
			url = url.replace("<ID>", ID)
		        url = url.replace("<START>", inicio)
		        url = url.replace("<END>", final)
			#vamos a la URL
			go(url)
			out = show()
			#obtenemos solamente la parte donde muestra el codigo de la grafica
			out = out.split("<PRE>")[1].split("</PRE>")[0]
			out = out.replace("&quot;", "\"")
			#Seleccionamos la fila -6 donde encontramos al ancho de banda utilizado (IN)
			In = out.split('\n')[-6]
			#seleccionamos la ultima fila donde se encuentra el ancho de banda utilizado (OUT)
			out = out.split('\n')[-1]
			
			#GB, MB, KB
			tipoOut = out.split('\"')[1][-4:-2]
			tipoIn = In.split('\"')[1][-4:-2]
			#expresion regular para obtener el numero de la cadena
			match = re.search('\d+\.?\d*', out)
			out = match.group()
			match = re.search('\d+\.?\d*', In)
			In = match.group()
			
			#Cambio de GB >> MB o KB
			if(tipoOut == 'MB'):
				out = str(float(out) / 1000.0)
			if(tipoIn == 'MB'):
				In = str(float(In) / 1000.0)
			
			#Lo almacenamos en la lista
			auxOut.append(out)
			auxIn.append(In)

		#cambiamos a entero los datos
                if(ROUND == 'yes'):
			for i in range(len(auxOut)):
				auxOut[i] = str(int(float(auxOut[i])))

			for i in range(len(auxIn)):
				auxIn[i] = str(int(float(auxIn[i])))
			
		valor = []
		valor.append(auxOut)
		valor.append(auxIn)
		
		return valor

        #Obtenemos ultimo indice de la lista cuando se repiten fechas
        def get_last_index(self, date, dates):
            for i, d in enumerate(dates):
                if d == date:
                    return i
        #Funcion para sumar fechas repetidas
        def clean_list(self, _list):
            _list_original = list(_list)
            dates = []
            for i, x in enumerate(_list):
                    date = x[5].split(" ")[0]
                    if date in dates:
                        last_index = self.get_last_index(date, dates)
                        new_item = _list_original[last_index]
                        _sum = float(new_item[7]) + float(x[7])
                        new_item[7] = str(round(_sum, 2))
                        for it in range(11, 14):
                            _sum = float(new_item[it]) + float(x[it])
                            new_item[it] = str(round(_sum, 2))
                        _list_original.remove(_list[i])
                        dates.pop()
                    dates.append(date)
            return _list_original

	def genPDF(self, servidor, trafico, reporte):
                #revisamos si existen fechas repetidas
                reporte = self.clean_list(reporte)
		#Creamos documento
		doc = SimpleDocTemplate(self.path + "pdf/" + servidor + '[' + self.hoy.strftime("%Y-%B") + '].pdf', pagesize=landscape(letter))
		archivoComa = file(self.path + "csv/" + servidor + '[' + self.hoy.strftime("%Y-%B") + '].csv', "w")
		elements = []
		styleSheet = getSampleStyleSheet()
		
		aux = []
		data = []

		aux = ['Date','Duration\n(Hours)','CPU Count','RAM\n(GB)','Storage\n(GB)','CPU\n(Hours)','RAM\n(Hours)','Storage\n(Hours)','Bandwidth\nIN (GB)','Bandwidth\nOUT (GB)','Cloud\nStorage (GB)']
		data.append(aux)
		aux = []
#		data.append(aux)
		a = 0
                print len(reporte)
                print reporte
		for i in range(len(reporte)):
			aux = [reporte[i][5].split(' ')[0],
				reporte[i][7].split('.')[0],
				reporte[i][8],
				reporte[i][9],
				reporte[i][10].split('.')[0],
				reporte[i][13].split('.')[0],
				reporte[i][14].split('.')[0],
				reporte[i][15].split('.')[0],
				trafico[1][i],
				trafico[0][i],
				reporte[i][24].split('.')[0]]
			data.append(aux)

		aux = []
		data.append(aux)
		
		#Variables para las hr de uso
		cpuH = 0
		RAMH = 0
		StorageH = 0
		BandWidthHO = 0
		BandWidthHI = 0
		cloudStorageH = 0

		#se incrementa las hrs de cada servicio
		for i in reporte:
			cpuH += int(float(i[13]))
			RAMH += int(float(i[14]))
			StorageH += int(float(i[15]))
			cloudStorageH += int(float(i[24]))
		
		#Sumatoria del ancho de banda
		BandWidthHI = (eval('+'.join(trafico[1])))
		BandWidthHO = (eval('+'.join(trafico[0])))

		aux = ['Total Horas','','','','',cpuH,RAMH,StorageH,BandWidthHI,BandWidthHO,cloudStorageH]
		data.append(aux)
		aux = ['Costo por Hora','','','','', cpuP, RAMP, StorageP, BandWidthPI, BandWidthPO, cloudStorageP]
		data.append(aux)
		
		#Calculo total
		cpu = cpuH * cpuP
		RAM = RAMH * RAMP
		Storage = StorageH * StorageP
		BandWidthO = BandWidthHO * BandWidthPO
		BandWidthI = BandWidthHI * BandWidthPI
		cloudStorage = cloudStorageH * cloudStorageP

		aux = ['Neto','','','','','$ %.2f' % cpu, '$ %.2f' % RAM, '$ %.2f' % Storage, '$ %.2f' % BandWidthI, '$ %.2f' % BandWidthO, '$ %.2f' % cloudStorage]
		data.append(aux)
		aux = []
		data.append(aux)
		total = (cpu + RAM + Storage + BandWidthI + BandWidthO + cloudStorage)
		aux = ['Subtotal','','','','','','','','','','$ %.2f' % total]
		data.append(aux)
		aux = [str(int(float(GANANCIA)*100)) + '%','','','','','','','','','','$ %.2f' % (total * float(GANANCIA))]
		data.append(aux)
		aux = ['TOTAL','','','','','','','','','','$ %.2f' % (total * (float(GANANCIA)+1))]
		data.append(aux)

		archivoComa.write("Date,Duration (Hours),CPU Count,RAM (GB),Storage (GB),CPU (Hours),RAM (Hours),Storage (Hours),Bandwidth IN (GB),Bandwidth OUT (GB),Cloud Storage (GB)")
		for i in data[1:]:
			archivoComa.write(",".join(map(lambda x:str(x), i)))
			archivoComa.write("\n")

		archivoComa.close()

		t=Table(data,style=[
                    ('GRID',(0,0),(-1,0),2,colors.black),
		    		('BOX',(0,1),(-1,-1),1,colors.black),
                    ('GRID',(0,0),(-1,-9),0.5,colors.black),
                    ('GRID',(-1,-1),(-1,-1),0.5,colors.black),
                    ('BOX',(0,-1),(-2,-1),0.5,colors.black),
#                   ('BOX',(0,-5),(1,-3),0.4,colors.black),
                    ('BOX',(0,-7),(-7,-5),0.5,colors.black),
                    ('GRID',(5,-7),(-1,-5),0.5,colors.black),
				    ('ALIGN',(0,0),(-1,0),'CENTER'),
				    ('ALIGN',(0,1),(0,-1),'LEFT'),
                    ('ALIGN',(1,1),(-1,-1),'CENTER'),
                    ('FONT',(-1,-3),(-1,-1),'Times-Bold'),
                    ('ALIGN',(-1,-3),(-1,-1),'RIGHT'),
		])
		#Ajustamos ancho de la columna 1 y -1
		t._argW[0]=1.1*inch
		t._argW[-1]=1.01*inch
 
		elements.append(t)
		# write the document to disk
		doc.build(elements)

	def sendMail(self, validos):
		#Fecha
		date = datetime.datetime.utcnow()
		date = "%s -0000" % date.strftime('%a, %d %b %Y %H:%M:%S')
		# Creamos objeto Multipart, quien ser� el recipiente que enviaremos
	        msg = MIMEMultipart()
		msg['From']=MAIL_FROM
	        msg['Subject']="Reporte Mensual de consumo de trafico en NTT America"
	        msg['X-Mailer'] = "Python X-Mailer"
		msg['Date'] = date
        
	        texto = """
	        Reporte Mensual de los servidores en NTT America
        	"""
        
	        msg.attach(MIMEText(texto, 'plain', 'UTF-8'))
        
        	#adjuntamos PDF
	        for i in validos:
        		file = (self.path + "pdf/" + i + '[' + self.hoy.strftime("%Y-%B") + '].pdf')
            		part = MIMEBase('application', "pdf")
		        part.set_payload(open(file, "rb").read())
		        Encoders.encode_base64(part)
		        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
		        msg.attach(part)
		for i in validos:
                        file = (self.path + "csv/" + i + '[' + self.hoy.strftime("%Y-%B") + '].csv')
                        part = MIMEBase('Content-type', "text/csv")
                        part.set_payload(open(file, "rb").read())
                        Encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
                        msg.attach(part)
           	
		file = (self.path + self.reporteGeneral)
            	part = MIMEBase('application', "pdf")
		part.set_payload(open(file, "rb").read())
		Encoders.encode_base64(part)
		part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
		msg.attach(part)	
 
	        #conectamos
        	mailServer = smtplib.SMTP(MAIL_SERVER,MAIL_PORT_SMTP)
		# Enviamos
        	for correo in MAIL_TO:
			msg['To'] = correo.strip()
		        mailServer.sendmail(MAIL_FROM, correo.strip(), msg.as_string())
	                print "correo a: ", correo.strip()
                print "correo eviado"
	        # Cerramos conexi�n
        	mailServer.close()

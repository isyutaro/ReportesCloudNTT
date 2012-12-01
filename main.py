#!/usr/local/bin/python2.5
from libreria import *
from SQL import *

lib = libreria()
sql = SQL()

#nos conectamos a los sitios NTT y Cacti
lib.connectCacti()
lib.connectNTT()

#obteneoms el reporte General de NTT America del periodo anterior
lib.generarReporteGeneral()

#obtenemos la lista de servidores que necesitamos de NTT America
listaServidores = lib.getListaServidores()

#Obtenemos la lista de cacti para buscar el ID de la grafica del servidor que necesitamos de NTT
listaCacti = sql.getListaCacti()
##print listaCacti

#lista servidores validos
validos = []

#buscamos el servidor de NTT en cacti para obtener el ID de la grafica de traffic
for i in listaServidores:
	for j in listaCacti:
		#Verificamos que sea el mismo servidor
		if j[0].find(i)==0:
			#servidor es una lista donde j[0] = Nombre servidor, j[1] = ID grafica de trafico
			#En esta parte generamos todo, trafico, servidores y crear tabla
			#obtenemos el trafico de grafica para el servidor
			listaTrafico = lib.getTraffico(j)
			listaReporte = lib.getReporteServidor(j[0])
			lib.genPDF(j[0], listaTrafico, listaReporte)
			validos.append(j[0])

##print validos
lib.sendMail(validos)

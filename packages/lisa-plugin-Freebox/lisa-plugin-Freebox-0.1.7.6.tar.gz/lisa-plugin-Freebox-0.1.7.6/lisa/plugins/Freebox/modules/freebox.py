# -*- coding: UTF-8 -*-

#	"ids" : "donnes infos", 
#	"meth" : "switch",
#	"idx" : "ok|ok",
#	"idx_sec" : "2",
#	"boy" : "Voici les info du progamme"
# 
# # 	param à faire ip et port
# # 	param à faire multiplayer
#
from lisa.server.plugins.IPlugin import IPlugin
from twisted.python import log
import gettext
import inspect
import os
import requests
import json

# Code zappette
code_Fb= "35782633"
log.msg("*************  FREEBOX ****************")

class Freebox(IPlugin):
	def __init__(self):
		super(Freebox, self).__init__()
		self.configuration_plugin = self.mongo.lisa.plugins.find_one({"name": "Freebox"})
		self.path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(
		inspect.getfile(inspect.currentframe()))[0],os.path.normpath("../lang/"))))
		self._ = translation = gettext.translation(domain='freebox',
			localedir=self.path,
			languages=[self.configuration_lisa['lang']]).ugettext
#
	def switch(self, jsonInput):
		rangs = [] 
		bodies = ""
		if jsonInput['outcome']['entities']['location']['body'] :
			location = jsonInput['outcome']['entities']['location']['body']
		else:
			bodies = "pas de lieu"

		if jsonInput['outcome']['entities']['on_off']['value'] :
			on_off = jsonInput['outcome']['entities']['on_off']['value']
		else:
			bodies = "pas de on/off"
#
		idex= location + "_" + on_off
		log.msg("index :  %s" % (idex))	
		
	
		for rs in self.configuration_plugin['param_fb']:
			log.msg(" rs  :  %s" % (rs))
			log.msg("ids  :  %s" % (rs['ids']))
			if rs['ids'] == idex :
				log.msg("*************  TROUVé ****************")
				log.msg("idx  :  %s" % (rs['idx']))
				log.msg("idx sec :  %s" % (int(rs['idx_sec'])))
				log.msg(" boy  :  %s" % (rs['boy']))
				bodies = rs['boy']
				log.msg("BODIES  :  %s" % (bodies))
				if rs['idx_sec'] == "2":
					log.msg("*************  'idx_sec'] <> 1 ****************")
					# séparation de rs['idx'], nombre   len(maliste)
					lg=len(rs['idx'])		
					log.msg(" lg  :  %s" % (lg))
					for bar in range(lg):
##				#	while i = rs['idx_sec']:
##						for i in rs['idx_sec']:
						if rs['idx'][bar] == '|':
							log.msg(" bar  :  %s" % (bar))
#>>> for rang in range(len(mot)):  # La variable rang parcourt les entiers de 0 au rang de la dernière lettre du mot.
#...     if mot[rang] == 'i':
#...         rangs.append(rang)    # Si la lettre du mot est 'i', on stocke le rang dans notre liste.
#>>> rangs                         # On affiche le résultat.
#[5, 7]
##							# search position '|' dans rs['idx']	
##							# 'http://hd2.freebox.fr/pub/remote_control?code=35782633&key=%s' % (rs))
##							for rx in rs['idx_sec']:
##								log.msg(" rx  :  %s" % (rx))
##								log.msg("idx_sec  :  %s" % rs['idx_sec'])
##								log.msg("idx  :  %s" % (rs['idx']))
##
								resp = requests.get ('http://hd2.freebox.fr/pub/remote_control?code=%s&key=%s' % (code_Fb,rs['idx']))
							log.msg("resp  :  %s" % (resp))
				if rs['idx_sec'] == "1":
					log.msg("*************  'idx_sec'] = 1 ****************")
					resp = requests.get ('http://hd2.freebox.fr/pub/remote_control?code=%s&key=%s' % (code_Fb,rs['idx']))
					log.msg("resp unique   :  %s" % (resp))
				
				
		if bodies == "":
			bodies = "j'ai rien compris aux switch"
		return {"plugin": "Freebox",
			"method": "switch",
			"body": bodies
		}


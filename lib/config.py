# coding: gbk
import os
import ConfigParser

DEFAULT_CONFIG = 'config.ini'


class Config:
	def __init__(self):
		self.config = ConfigParser.ConfigParser()
		self.profile = os.getenv('COMPUTERNAME')
		self.load_config()

	def load_config(self):
		if os.path.exists(DEFAULT_CONFIG):
			self.config.read(DEFAULT_CONFIG)

	def put(self, option, value):
		self.config.set(self.profile, option, value)

	def get(self, option):
		return self.config.get(self.profile, option)

	def write(self):
		for profile in profiles:
			self.config.add_section(profile[0])
			self.config.set(profile[0], profile[1], profile[2])
		with open(CONFIG_PATH, 'w') as configfile:
			self.config.write(configfile)

global_config = Config()

IDM_PATH = global_config.get('idm_path')
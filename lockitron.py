'''
Example Usage

from lockitron import Lockitron
lock_controller = Lockitron(email="email@address.com", password="password")
lock_controller.locks
	#contains all the locks you control - [LockName]

#lock first door that you control
lock_controller.lock(lock_controller.locks[0])
#or
lock = lock_controller.locks[0]
lock.lock()

#unlock first door that you control
lock_controller.unlock(lock_controller.locks[0])
#or
lock = lock_controller.locks[0]
lock.unlock()

'''

import requests
try: import simplejson as json
except ImportError: import json

class Lock(object):
	def __init__(self, lock_controller):
		self.uuid = None
		self.app_id = None
		self.name = None
		self.controller = self
	
	def create_from_json(self, login_json):
		self.uuid = login_json['permission']['uuid']
		self.app_id = login_json['permission']['app_id']
		self.name = login_json['permission']['app']['name']

	def lock(self):
		self.controller.lock(self)
	def unlock(self):
		self.controller.unlock(self)

	def __repr__(self):
		return self.name

class Lockitron(object):
	def __init__(self, email=None, password=None):
		self.email = email
		self.password = password
		
		self.lockitron_id = 'dash' #"python-lockitron"

		if self.email is None or self.password is None:
			raise AttributeError("Email and Password need to be passed as parameters")
		self.api_endpoints = {}
		self.api_endpoints['root'] = "https://lockitron.com/"
		self.api_endpoints['endpoints'] = {}
		self.api_endpoints['endpoints']['login'] = 'api/mobile/login?id=%s'
		self.api_endpoints['endpoints']['lock'] = 'access/%s/lock'
		self.api_endpoints['endpoints']['unlock'] = 'access/%s/unlock'
		self.api_endpoints = {
								'root'		:	,
								'endpoints'	:	{
													'login'	: 'api/mobile/login?id=%s',
													'lock'	: 'access/%s/lock',
													'unlock': 'access/%s/unlock',
												}
							}
		self.headers = {'User-Agent': 'Appcelerator Titanium/1.7.2 (iPhone/5.0.1; iPhone OS; en_US;)', 
						'X-Requested-With': 'XMLHttpRequest'}

		self.locks = []
		
		self.cookies = None
		self.login()

	def login(self):
		payload = {'email' : self.email, 'password' : self.password}
		login = requests.post(self.api('login', self.lockitron_id), data=payload, headers=self.headers)
		if login.status_code is not 200:
			raise RuntimeError("Login Error")
		self.cookies = login.cookies
		resp = json.loads(login.content)
		self.gather_locks_from_login(resp)
	
	def gather_locks_from_login(self, locks):
		for lock in locks:
			new_lock = Lock(self)
			new_lock.create_from_json(lock)
			self.locks.append(new_lock)
	
	def lock(self, lock):
		response = requests.get(self.api('lock', lock.uuid), cookies=self.cookies, headers=self.headers)
		if response.status_code is not 200:
			raise RuntimeError("There was an unknown error while trying to lock; possibly logged out?")

	def unlock(self, lock):
		response = requests.get(self.api('unlock', lock.uuid), cookies=self.cookies, headers=self.headers)
		if response.status_code is not 200:
			raise RuntimeError("There was an unknown error while trying to unlock; possibly logged out?")

	def api(self, endpoint, param=None):
		return self.api_endpoints['root'] + self.api_endpoints['endpoints'][endpoint] % param

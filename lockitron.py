'''
Example Usage

from lockitron import Lockitron
lock_controller = Lockitron(email="email@address.com", password="password")
lock_controller.locks
	#contains all the locks you control - [LockName]

#lock first door that you control
lock_controller.lock(lock_controller.locks[0])

#unlock first door that you control
lock_controller.unlock(lock_controller.locks[0])
'''

import requests
try: import simplejson as json
except ImportError: import json

class Lock(object):
	def __init__(self):
		self.uuid = None
		self.app_id = None
		self.name = None
	
	def create_from_json(self, login_json):
		self.uuid = login_json['permission']['uuid']
		self.app_id = login_json['permission']['app_id']
		self.name = login_json['permission']['app']['name']

	def __repr__(self):
		return self.name

class Lockitron(object):
	def __init__(self, email=None, password=None):
		self.email = email
		self.password = password
		'''
			ATTN Lockitron: I want to set the id of my call to something other than 'dash'
							as I know it's rude to 100% emulate the iPhone app but, unfortunately
							requests to the login API return blank content (but, valid cookie?)
							which breaks the API as I can't get the list of locks and UUIDs. I would
							prefer to make the call with my own ID to be polite but, can't :-(
		'''
		self.lockitron_id = 'dash' #"python-lockitron"

		if self.email is None or self.password is None:
			raise AttributeError("Email and Password need to be passed as parameters")
		self.api_endpoints = {
									'root'		:	"https://lockitron.com/",
									'endpoints'	:	{
														'login'	: 'api/mobile/login?id=%s',
														'lock'	: 'access/%s/lock',
														'unlock': 'access/%s/unlock',
													}
							}
		# As with the login _id I'd rather not spoof user agents but, it won't function without it either :-(
		self.headers = {'User-Agent': 'Appcelerator Titanium/1.7.2 (iPhone/5.0.1; iPhone OS; en_US;)', 'X-Requested-With': 'XMLHttpRequest'}

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
			new_lock = Lock()
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

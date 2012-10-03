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
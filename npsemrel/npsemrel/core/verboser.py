import time
from time import gmtime, strftime

'''
Klasa do estymacji czasu potrzebnego do wykonania zadania.

Estymacja czasu odbywa sie poprzez uwzglednienie liczby wykonanych do danej
pory krokow do wszystkich krokow do wykonania jakie zostaly.

UWAGA! Czas poczatkowy liczony jest od momentu utworzenia obiektu
'''

class Testimator:
	def __init__(self, number_of_steps):
		self._number_of_steps = number_of_steps
		self._actual_step = 0
		self.starttime = time.time()
	
	def etl_autostep(self):
		self._step()
		left_min, left_sec = self._calculate_minsec_left()
		return '[%d/%d] estimated time left: %dm %ds' % (
				self._actual_step,
				self._number_of_steps,
				left_min,
				left_sec)
	
	def _step(self):
		self._actual_step += 1

	def _calculate_minsec_left(self):
		acttime = time.time()
		secperstep = (acttime - self.starttime) / self._actual_step
		leftsec = (self._number_of_steps - self._actual_step) * secperstep
		left_min = leftsec / 60
		left_sec = leftsec % 60
		return (left_min, left_sec)

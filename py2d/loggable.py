#common classes and defines

#TODO factor this out.

import logging
import sys

logger = None

class Loggable(object):
	def initLogging(self, fileLogging = False, level = logging.DEBUG):
		self.logger = logging.getLogger("py2d")
		std = logging.StreamHandler(sys.stdout)
		formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
		std.setFormatter(formatter)
		self.logger.addHandler(std)
		if fileLogging:
			self.logger.addHandler(logging.FileHandler('log.txt', 'w'))
		self.logger.setLevel(level)
		self.logger.debug("logger init")
		
	def debug(self, msg, *args, **kwargs):
		string = msg + " (from Class " + self.__class__.__name__ + ")"
		logger.debug(string)


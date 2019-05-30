#!/usr/bin/python

import re
from CString import *

class Printer:

	__alinea__       = 0
	__length__       = 80
	__width_label__  = 10
	__width_status__ = 8


	def __create_alinea__(self): return '  ' * self.__alinea__


	def __del__(self): print(' ') # prints an empty line upon program termination


	def __init__(self, line_length):
		if not isinstance(line_length, int) or line_length < 10:  raise Exception('invalid line length value')
		self.__length__ = line_length;


	def __print_msg__(self, msg, label=None, status=None):
		# Parse label
		if label == None: label_display = ' ' * self.__width_label__
		else:
			label = label.lower()
			label_display = '[' + label.upper().center(self.__width_label__-  2) + ']'
			if   label == 'info' : label_display = CString(label_display, fg='blue', style='bold')
			elif label == 'error': label_display = CString(label_display, fg='red' , style='bold')
			else: raise Exception('unsupported label \'' + label + '\'')
		# Parse status
		if status == None: status_display = ''
		else:
			status = status.lower()
			status_display = '[' + status.upper().center(self.__width_status__ - 2) + ']'
			if   status == 'ok'    : status_display = CString(status_display, fg='green', style='bold')
			elif status == 'failed': status_display = CString(status_display, fg='red'  , style='bold')
			else: raise Exception('unsupported status \'' + status + '\'')
		# Create the printed message
		out = label_display + ' ' + self.__create_alinea__() + msg.strip()
		# Append status
		if status != None:
			# If a status needs to be appended, cut the line shorter and add it
			length = self.__length__ - self.__width_status__ - 1
			if len(out) > length: out = out[:length-3] + '...'
			out = out.ljust(length) + ' ' + status_display
			# Do a quick check
			if len(out) != self.__length__: raise Warning('unexpected string length')
		print(out)

	
	def alinea_incr(self):
		# Increase alinea
		self.__alinea__ += 1
		return self
	

	def alinea_decr(self):
		# Decrease alinea
		self.__alinea__ = max(0, self.__alinea__ - 1)
		return self

	
	def alinea_del(self):
		# Completely delete alinea
		self.__alinea__ = 0
		return self

	
	def header(self, title):
		# Print a header
		line1 = '*' * self.__length__
		line2 = '*' * 10 + ' ' + title.strip() + ' '
		#line2 = tf.ljust(line2 , self.line_length, character='*')
		print(CString('\n' + line1 + '\n' + line2 + '\n', style='bold'))

	
	def info   (self, msg   ): self.__print_msg__(msg, label ='info'  ) # print info message
	def error  (self, msg   ): self.__print_msg__(msg, label ='error' ) # print error message
	def success(self, msg=''): self.__print_msg__(msg, status='ok'    ) # print success message
	def failure(self, msg=''): self.__print_msg__(msg, status='failed') # print failure message



####################### UNIT TESTS ########################################################""

def test():
	p = Printer(80);
	p.header     ('THIS IS A TITLE')
	p.header     ('THIS IS A TITLE THAT IS WAY TOO LONG FOR THE SELECTED OUTPUT LENGTH')
	p.info ('This is an information message')
	p.error('This is an error message')
	p.alinea_incr()
	p.info ('This is an information message with a 1st alinea level')
	p.alinea_incr()
	p.info ('This is an information message with a 2nd alinea level')
	p.alinea_decr()
	p.info ('Back to 1st alinea level!')
	p.error('Should apply to error messages too!')
	p.success('This is a success message with an alinea')
	p.alinea_decr()
	p.success('Same without alinea')
	p.failure('This is a failure message')

test()

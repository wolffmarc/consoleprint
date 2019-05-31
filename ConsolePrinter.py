#!/usr/bin/python

from RichText import RichText


class ConsolePrinter:

	def __init__(self, line_length):
		self._alinea = 0  # alinea level
		self._length = 80  # line length
		self._width_label = 10  # width of the line prefix label field
		self._width_status = 8  # width of the line suffix status field
		self._color_label = {'info': 'blue', 'warning': 'yellow', 'error': 'red'}  # label colors
		self._color_status = {'ok': 'green', 'failed': 'red'}  # status colors
		if not isinstance(line_length, int):
			raise TypeError('integer value expected for line length')
		min_valid_line_length = 2 * (self._width_label + self._width_status)
		if line_length < min_valid_line_length:
			raise ValueError('line length is too small, should be at least ' + str(min_valid_line_length))
		self._length = line_length

	def _create_alinea(self):
		"""
		Creates the alinea string according to the current alinea level
		:return: alinea string
		"""
		return '  ' * self._alinea

	def __del__(self):
		"""
		We overload the del operator to print an extra line when the object is deleted,
		which usually happens when the program terminates
		:return:
		"""
		print(' ')

	def _print_msg(self, msg, label=None, status=None):
		"""
		Print the input message with optional label and status
		:param msg: string or RichText object with the text message that should be displayed
		:param label: optional, should be 'info, 'warning' or 'error'
		:param status: optional, should be 'ok' or 'failed'
		"""
		# Parse label
		if label is None:
			label_display = ' ' * self._width_label
		else:
			label = label.lower().strip()
			if label not in ['info', 'warning', 'error']:
				raise ValueError('invalid label, should be \'info\', \'warning\' or \'error\'')
			label_display = '[' + label.upper().center(self._width_label - 2) + ']'
			label_display = RichText(label_display, fg=self._color_label[label], style='bold')
		# Parse status
		if status is None:
			status_display = ''
		else:
			status = status.lower().strip()
			if status not in ['ok', 'failed']:
				raise ValueError('invalid label, should be \'ok\' or \'failed\'')
			status_display = '[' + status.upper().center(self._width_status - 2) + ']'
			status_display = RichText(status_display, fg='black', bg=self._color_status[status], style='bold')
		# Create the printed message
		out = label_display + ' ' + self._create_alinea() + msg.strip()
		# Append status
		if status is not None:
			# If a status needs to be appended, cut the line shorter and add it
			length = self._length - self._width_status - 1
			if len(out) > length:
				out = out[: length - 3] + '...'
			out = out.ljust(length) + ' ' + status_display
			# Do a quick check
			if len(out) != self._length:
				raise Warning('unexpected string length')
		print(out)

	def alinea_incr(self):
		"""
		Increase alinea
		:return: self, modified
		"""
		self._alinea += 1
		return self

	def alinea_decr(self):
		"""
		Decrease alinea
		:return:  self, modified
		"""
		self._alinea = max(0, self._alinea - 1)
		return self

	def alinea_del(self):
		"""
		Completely delete alinea
		:return: self, modified
		"""
		self._alinea = 0
		return self

	def header(self, title):
		# Print a header
		line1 = '*' * self._length
		line2 = '*' * 10 + ' ' + title.strip() + ' '
		if len(line2) > self._length:
			line2 = line2[: self._length-3] + '...'
		else:
			line2 = line2.ljust(self._length, '*')
		print(RichText('\n' + line1 + '\n' + line2 + '\n', style='bold'))

	def info(self, msg):
		"""
		Print info message
		:param msg: message to print
		"""
		self._print_msg(msg, label='info')

	def error(self, msg):
		"""
		Print error message
		:param msg: message to print
		"""
		self._print_msg(msg, label='error')

	def success(self, msg):
		"""
		Print success message
		:param msg: message to print
		"""
		self._print_msg(msg, status='ok')

	def failure(self, msg):
		"""
		Print failure message
		:param msg: message to print
		"""
		self._print_msg(msg, status='failed')

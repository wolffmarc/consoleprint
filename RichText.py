#!/usr/bin/python


import copy
import math
try:
	import colors
	__flag_use_colors__ = True
except:
	__flag_use_colors__ = False
	raise Warning('ansicolors package is missing, string colors and styles will be disabled')


def __overlap__(a, b):
	"""
	Compute the overlap between 2 integers intervals
	Intervals are here defined as 2-element lists of integers [x,y] with x <= y
	The overlap is here defined as the number of integers present in both intervals
	Examples:
		overlap([1,3], [2,5]) = 2
		overlap([1,3], [3,6]) = 1
		overlap([1,3], [4,8]) = 0
		overlap([1,3], [1,3]) = 3
	"""
	if not isinstance(a, list) or len(a) != 2 or a[0] > a[1]:
		raise Exception('first input argument is not an interval')
	if not isinstance(b, list) or len(b) != 2 or b[0] > b[1]:
		raise Exception('second input argument is not an interval')
	return sum(1 for x in range(a[0], a[1]+1) if x in range(b[0], b[1]+1))


class StyleBox:
	"""
	The StyleBox class implements a style box object defining style options for a certain substring of a string
	It is defined by 3 properties
	- __start__: start index
	- __length__: length (i.e. number of characters in the style box)
	- __style__: style options
	"""

	def __init__(self, start, length, style):
		# TODO add tests to validate inputs
		self.start = start
		self.length = length
		self.__style__ = style

	def __str__(self):
		return 'start=' + str(self.start) + ' length=' + str(self.length) + \
			' fg=' + str(self.fg()) + ' bg=' + str(self.bg()) + ' style=' + str(self.style())

	def fg(self):
		""" Getter for the foreground color """
		return self.__style__['fg']

	def bg(self):
		""" Getter for the background color """
		return self.__style__['bg']

	def style(self):
		""" Getter for style options """
		return self.__style__['style']

	def interval(self):
		"""
		Return the integer interval over which the style box spans
		Example: if start index is 3 and length is 4, the interval is [3, 6]
		"""
		return [self.start, self.start + self.length - 1]


class RichText:
	"""
	The RichText class implements a formatted string object for display colored and formatted text in consoles
	It is defined by 2 properties:
	- __text__: the underlying unformatted text stored in a standard string
	- __sbox__: a list of style boxes, alxays stored in ascending order
	Style boxes may not overlap and are expected to partition the string
	Contrarily to native strings, RichText objects are mutable: most string methods that have been implemented
	to work with RichText objects therefore modify the current object instead of creating a new object
	"""

	def __init__(self, text, fg=None, bg=None, style=None):
		"""
		text: string of unformatted text
		fg: foreground color
		bg: background color
		style: font style (e.g. bold, underline, etc.)
		"""
		self.__text__ = text
		self.__sbox__ = []
		if len(text) > 0:
			# Formatting options are stored in a dictionary under the fg, bg and style keys
			self.__sbox__ = [StyleBox(0, len(text), {'fg': fg, 'bg': bg, 'style': style})]

	def __add__(self, other):
		if isinstance(other, str):
			other = RichText(other)
		# For the regular '+' operator, output should be a new object
		# Left and right hand side members of the operators should not be modified
		# --> Make a deepcopy of the current object
		out = copy.deepcopy(self)
		out.__rconcat__(other)
		return out

	def __iadd__(self, other):
		self = self.__add__(other)  # TODO: any way to remove this assignment to self?
		return self

	def __radd__(self, other):
		if not isinstance(other, str):
			# __radd__ may only be called with strings
			raise Exception('RichText objects may only be concatenated with strings')
		return RichText(other).__add__(self)

	def __apply_formatting__(self):
		"""
		Generate the formatted text string with ANSI color and style codes
		If another package were to be used for generating the formatted string,
		this is where changes would have to be made
		"""
		# Start with a few sanity checks to make sure the style boxes properties are properly set
		# - check all style boxes have strictly positive lengths
		if len(self) > 0 and sum(1 for sbox in self.__sbox__ if sbox.length <= 0) > 0:
			raise Exception('found style box(es) with negative length')
		# - check that the sum of style boxes lengths equals the overall string length
		if sum(sbox.length for sbox in self.__sbox__) != len(self):
			raise Exception('length mismatch')
		# - check that the first style box starts at index zero
		if len(self) > 0 and self.__sbox__[0].start != 0:
			raise Exception('start index of the first style box is not zero')
		# - check that each style box start index is equal to the start index of the previous + length
		if sum(1 for i in range(len(self.__sbox__)-1)
			   if self.__sbox__[i+1].start != self.__sbox__[i].start + self.__sbox__[i].length) > 0:
			raise Exception('invalid start indices')
		# If the RichText object is empty, just return an empty string
		if len(self) == 0:
			return ''
		# Otherwise create the output string with formatting blocks by joining the different pieces of the string
		if __flag_use_colors__:
			out = ''.join(colors.color(self.str()[sbox.start:sbox.start+sbox.length],
									   fg=sbox.fg(), bg=sbox.bg(), style=sbox.style()) for sbox in self.__sbox__)
			return out
		else:
			return self.str()

	def __clean_style_boxes__(self):
		"""
		After multiple transformations, we might end up in a situation where several consecutives style boxes
		actually share the same properties and could be merged
		This is the purpose of this method
		It is especially useful for ensuring that equality tests return the expected result
		Indeed, since equality tests compare formatted strings, formatted blocks have to be set the same way
		in the compared RichText objects
		:return: self, modified
		"""
		if len(self.__sbox__) <= 1:
			return self
		# Loop over style boxes
		i = 0
		is_finished = False
		while not is_finished:
			# Compare the current style box with the next one
			cur = self.__sbox__[i]
			nxt = self.__sbox__[i+1]
			# If they have the same style, delete the next one and add its length to the current one
			if cur.style() == nxt.style():
				cur.length += nxt.length
				self.__sbox__.remove(nxt)
				# Don't increase the index in this case
			else:
				# Increase it only if we have to move to the next style box
				i += 1
			# Computation is finished if we have reached the last style box
			is_finished = i == len(self.__sbox__) - 1
		return self

	def __lconcat__(self, other):
		"""
		Left-side concatenation (other + self) with another RichText object
		:param other: left hand side RichText object
		:return self
		"""
		# Here we want to modify the current object but not the other object
		# --> Make a deepcopy of the other object
		other_copy = copy.deepcopy(other)
		# Shift style boxes of the current object,
		# i.e. add the length of the other object to the start indices of the current object's style boxes
		for s in self.__sbox__:
			s.start += len(other)
		# Concatenate properties
		self.__text__ = other_copy.str() + self.str()
		self.__sbox__ = other_copy.__sbox__ + self.__sbox__
		return self

	def __rconcat__(self, other):
		"""
		Right-side concatenation (self + other) with another RichText object
		:param other: right hand side RichText object
		:return self
		"""
		# Here we want to modify the current object but not the other object
		# --> Make a deepcopy of the object object
		other_copy = copy.deepcopy(other)
		# Shift style boxes of the other object,
		# i.e. add the length of the current object to the start indices of the other object's style boxes
		for s in other_copy.__sbox__:
			s.start += len(self)
		# Concatenate properties
		self.__text__ += other_copy.str()
		self.__sbox__ = self.__sbox__ + other_copy.__sbox__
		return self

	def __eq__(self, other):
		"""
		Equality test
		:param other: RichText object
		:return: True if formatted strings of both objects are equal, false else
		"""
		return str(self.__clean_style_boxes__()) == str(other.__clean_style_boxes__())

	def __getitem__(self, key):
		"""
		Bracket operator, allows retrieving a substring of the current object with preserved formatting
		:param key: indices as single integer or slice
		:return: substring as a new RichText object
		"""
		# If the string is empty, return an empty RichText in any case
		if len(self) == 0:
			return RichText('')
		# Do a dummy call to the native string __getitem__ method just to validate input arguments
		_ = self.str()[key]
		# Transform key into a slice if it is an integer
		key_slice = key
		if isinstance(key, int):
			key_slice = slice(key, key+1)
		# Now check the step
		if key_slice.step is None or key_slice.step == 1:
			# If the step is None or 1, just crop the unnecessary leading and trailing characters
			start, stop = key_slice.indices(len(self))[0:2]
			out = copy.deepcopy(self)
			out.__lcrop__(start).__rcrop__((len(self) - stop) % len(self))
		else:
			# Otherwise we have to extract characters individually
			raise Exception('not implemented yet')
		return out

	def __len__(self):
		"""
		Return the length of the RichText object, defined as the length of the unformatted text string
		:return: string length
		"""
		return len(self.str())

	def __crop_edgecases__(self, numchars):
		"""
		This is a helper function for the lcrop and rcrop methods which deals with edge cases
		:param numchars: number of characters to remove
		:return: True if an edge case has been found, False otherwise
		"""
		# If numchars <= 0, don't modify the object
		if numchars <= 0:
			return True
		# If all characters are to be removed, reinitialize the current object to an empty RichText object
		if numchars >= len(self):
			self.__init__('')
			return True
		return False  # no edge case has been found

	def __lcrop__(self, numchars):
		"""
		Crop the first 'numchars' characters from the left end of the string
		:param numchars: number of characters to remove
		:return: self
		"""
		# Deal with edge cases
		if self.__crop_edgecases__(numchars):
			return self
		# Now deal with the 'normal' case
		# Actually remove the desired characters
		self.__text__ = self.str()[numchars:]
		# Then adjust style boxes
		i = 0  # index for looping over style boxes
		while numchars > 0:
			stb = self.__sbox__[i]
			# Compute the number of characters that can be removed from the current style box
			to_remove = min(numchars, stb.length)
			# Adjust length
			stb.length -= to_remove
			# Adjust start index of the current and subsequent style boxes
			# Don't do this for the 1st style box whose start index is already zero
			for j in range(max(i, 1), len(self.__sbox__)):
				self.__sbox__[j].start -= to_remove
			# If the current style box is now empty (length = 0), remove it
			# In this case, the index does not need to be increased
			if stb.length == 0:
				self.__sbox__.remove(stb)
			else:
				i += 1
			# Update the number of characters left to remove
			numchars -= to_remove
		return self

	def __rcrop__(self, numchars):
		"""
		Crop the last 'numchars' characters from the right end of the string
		:param numchars: number of characters to remove
		:return self
		"""
		# Deal with edge cases
		if self.__crop_edgecases__(numchars):
			return self
		# Now deal with the 'normal' case
		# Actually remove the desired characters
		self.__text__ = self.str()[:-numchars]
		# Then adjust style boxes
		i = len(self.__sbox__) - 1  # index for looping over style boxes, we start from the right here
		while numchars > 0:
			stb = self.__sbox__[i]
			# Compute the number of characters that can be removed from the current style box
			to_remove = min(numchars, stb.length)
			# Adjust length
			stb.length -= to_remove
			# If the current style box is now empty (length = 0), remove it
			if stb.length == 0:
				self.__sbox__.remove(stb)
			# Update index and number of characters left to remove
			i -= 1
			numchars -= to_remove
		return self	

	def __str__(self):
		"""
		Printable version of the RichText object: apply formatting options
		:return: string with ANSI color and style codes
		"""
		return self.__apply_formatting__()

	def capitalize(self):
		"""
		Extension of the built-in string capitalize() method
		"""
		self.replaceall(self.str().capitalize())
		return self

	def casefold(self):
		try:
			self.replaceall(self.str().casefold())
		except:
			# The casefold() method does not exist in Python 2, which will create errors
			# Try calling lower() as a replacement
			self.lower()			
		return self

	def center(self, width, fillchar=' ', fg=None, bg=None, style=None):
		"""
		Extension of the built-in string center() method
		:param width: width of the output string
		:param fillchar: character used to fill the string, whitespace by default
		:param fg: optional foreground color for fill characters
		:param bg: optional background color for fill characters
		:param style: optional font style options for fill characters
		:return: self, modified
		"""
		# Do a dummy call to the built-in method to validate input arguments
		_ = self.str().center(width, fillchar)
		# If the current object is longer than the desired width, don't do anything
		if width <= len(self):
			return self
		# Num characters to add at the left and right ends of the string
		num_chars_to_add = width - len(self)
		num_chars_left = int(math.ceil(num_chars_to_add * 0.5))
		num_chars_right = num_chars_to_add - num_chars_left
		# Append fill characters to both ends
		self.__lconcat__(RichText(fillchar * num_chars_left, fg, bg, style))
		self.__rconcat__(RichText(fillchar * num_chars_right, fg, bg, style))
		return self

	def expandtabs(self, tabsize=8):
		raise Exception('not implemented yet')  # TODO

	def ljust(self, width, fillchar=' ', fg=None, bg=None, style=None):
		"""
		Extension of the built-in string ljust() method
		:param width: width of the output string
		:param fillchar: character used to fill the string, whitespace by default
		:param fg: optional foreground color for fill characters
		:param bg: optional background color for fill characters
		:param style: optional font style options for fill characters
		:return: self, modified
		"""
		# Do a dummy call to the built-in method to validate input arguments
		_ = self.str().ljust(width, fillchar)
		# Deal with edge cases
		if width <= len(self):
			return self
		# Append fill characters to the right end
		self.__rconcat__(RichText(fillchar * (width - len(self)), fg, bg, style))
		return self

	def rjust(self, width, fillchar=' ', fg=None, bg=None, style=None):
		"""
		Extension of the built-in string rjust() method
		:param width: width of the output string
		:param fillchar: character used to fill the string, whitespace by default
		:param fg: optional foreground color for fill characters
		:param bg: optional background color for fill characters
		:param style: optional font style options for fill characters
		:return: self, modified
		"""
		# Do a dummy call to the built-in method to validate input arguments
		_ = self.str().rjust(width, fillchar)
		# Deal with edge cases
		if width <= len(self):
			return self
		# Append fill characters to the left end
		self.__lconcat__(RichText(fillchar * (width - len(self)), fg, bg, style))
		return self

	def lower(self):
		"""
		Extension of the built-in string lower() method
		:return: self, modified
		"""
		self.replaceall(self.str().lower())
		return self

	def replace(self, old, new, count=-1):
		"""
		Extension of the built-in string replace() method
		:param old: substring to replace
		:param new: replacement substring
		:param count: max number of times replacement should be done, by default all occurrences are replaced
		:return: self, modified
		"""
		# Do a dummy call to the built-in method to validate input arguments
		_ = self.str().replace(old, new, count)
		# Deal with edge cases
		if count == 0:
			return self
		if len(self) == 0 and len(old) != 0:
			return self
		if len(self) == 0 and len(old) == 0:
			# If the current object is empty and 'old' is empty too, just return 'new' without any formatting
			self.__init__(new)
			return self
		if len(old) == 0:
			# Deal with the special case where 'old' is an empty string
			# The expected behaviour with regular strings is the following:
			# 	'foo'.replace('', 'bar')     returns     'barfbarobarobar'
			# i.e. the replacement string has to be inserted everywhere:
			# at the start, the end and between all characters
			# The specificity for RichText objects is that we want to preserve formatting when the 'new'
			# string is inserted between 2 characters within the same style box
			# Start by initializing the output as the 'new' string without any formatting
			out = RichText(new)
			# Then append characters one by one, except the last one which will be appended later on
			for i in range(len(self)-1):
				out += self[i]
				# Check if the current character and the next one are in the same style box
				# This can be achieved by computing the overlap between the [i, i+1} interval and the style box
				# If the overlap equals 2, both characters are in the same style box
				flag_same_sbox = False
				for sbox in self.__sbox__:
					if __overlap__([i, i+1], sbox.interval()) == 2:
						flag_same_sbox = True
						# Append the 'new' string with the appropriate formatting
						out += RichText(new, fg=sbox.fg(), bg=sbox.bg(), style=sbox.style())
						break
				# If we haven't appended the 'new' string yet, do it now but without any formatting
				if not flag_same_sbox:
					out += RichText(new)
			# Add the last character and the 'new' string once again, this time without any formatting
			out += self[-1] + RichText(new)
			self = out
			return self
		# Deal with the standard case
		# We are going to look for occurrences of the 'old' string and replace them one by one
		string = self.str()
		num_iter = 0
		is_finished = False
		while not is_finished:
			# Look for the next occurrence of the 'old' string
			idx = string.find(old)
			if idx != -1:
				# If we found an occurrence, get the 'old' string's interval in the current object
				old_interval = [idx, idx + len(old) - 1]
				# Do the replacement
				string = string[0:idx] + new + string[idx+len(old):]
				# Update style boxes
				for sbox in self.__sbox__:
					# Compute the overlap between the old string and the style box
					overlap = __overlap__(old_interval, sbox.interval())
					# If the occurrence's index is within the style box, change only its length
					if __overlap__([idx, idx], sbox.interval()) == 1:
						sbox.length += len(new) - overlap
					# For all style boxes starting after the occurrence's index,
					# both the start index and the length have to be modified
					if sbox.start > idx:
						sbox.start += len(new) - len(old) + overlap
						sbox.length -= overlap
				# Remove style boxes that may be empty
				# To do so, we have to get the indices of empty style boxes and remove them in **reversed** order
				empty_sbox = list(i for i in range(len(self.__sbox__)) if self.__sbox__[i].length == 0)
				for i in reversed(empty_sbox):
					del self.__sbox__[i]
				# Update number of iterations
				num_iter += 1
			# Check if the computation is finished
			is_finished = idx == -1 or count == num_iter
		# Once the computation is complete, update the string and exit
		self.__text__ = string
		return self

	def replaceall(self, string):
		"""
		Replace the whole string in the current object with the input string
		:param string: replacement string
		:return: self, modified
		"""
		if not isinstance(string, str) or len(string) != len(self):
			raise Exception('replacement may only occur with another string of the same size')
		self.__text__ = string
		return self

	def str(self):
		"""
		Getter for the unformatted text string
		:return: string, unformatted
		"""
		return self.__text__

	def strip(self, chars=' '):
		"""
		Extension of the built-in string strip() method
		:param chars: characters to remove, whitespace by default
		:return: self, modified
		"""
		return self.lstrip(chars).rstrip(chars)

	def lstrip(self, chars=' '):
		"""
		Extension of the built-in string lstrip() method
		:param chars: characters to remove, whitespace by default
		:return: self, modified
		"""
		num_chars_to_remove = len(self) - len(self.str().lstrip(chars))
		self.__lcrop__(num_chars_to_remove)
		return self

	def rstrip(self, chars=' '):
		"""
		Extension of the built-in string rstrip() method
		:param chars: characters to remove, whitespace by default
		:return: self, modified
		"""
		num_chars_to_remove = len(self) - len(self.str().rstrip(chars))
		self.__rcrop__(num_chars_to_remove)
		return self

	def split(self, sep=' ', maxsplit=-1):
		"""
		Extension of the built-in string split() method
		:param sep: separator to use when splitting, whitespace by default
		:param maxsplit: how many splits to do, all occurrences of 'sep' by default
		:return: list of RichText objects
		"""
		# Call the built-in split method on the unformatted text string
		pieces = self.str().split(sep, maxsplit)
		# We now have to loop over the resulting pieces and to apply the right style boxes to them
		cursor = 0  # cursor in the input string
		for idx in range(len(pieces)):
			pc = pieces[idx]
			# If the current piece is empty, replace it with an empty RichText object and go to the next piece
			if len(pc) == 0:
				pieces[idx] = RichText('')
				cursor += len(sep)
				continue
			# At this point, we know the current piece is not empty
			# Get its interval in the input string
			interval = [cursor, cursor + len(pc) - 1]
			# For each piece, we have to create the list of style boxes
			# --> initialize an empty list of style boxes and set the start index to zero
			pc_sbox = []
			start_idx = 0
			# Look for style boxes than span over the current piece
			for sbox in self.__sbox__:
				overlap = __overlap__(interval, sbox.interval())
				if overlap > 0:
					# Copy the style box, adjust its properties and append it to the list of style boxes
					sbox_copy = copy.deepcopy(sbox)
					sbox_copy.start = start_idx
					sbox_copy.length = overlap
					pc_sbox.append(sbox_copy)
					# Increase the start index
					start_idx += sbox_copy.length
			# Finally replace the current piece with a RichText object
			pieces[idx] = RichText(pc)
			pieces[idx].__sbox__ = pc_sbox
			# Increase the cursor value
			cursor += len(pc) + len(sep)
		return pieces

	def swapcase(self):
		"""
		Extension of the built-in string swapcase() method
		:return: self, modified
		"""
		self.replaceall(self.str().swapcase())
		return self		

	def title(self):
		"""
		Extension of the built-in string title() method
		:return: self, modified
		"""
		self.replaceall(self.str().title())
		return self

	def upper(self):
		"""
		Extension of the built-in string title() method
		:return: self, modified
		"""
		self.replaceall(self.str().upper())
		return self

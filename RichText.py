#!/usr/bin/python

# Import standard packages
import copy, math
# Import the ansicolors package
try:
	import colors
	__flag_use_colors__ = True
except: 
	#raise Warning('ansicolors package is missing, string colors and styles will be disabled')
	__flag_use_colors__ = False


def __overlap__(a,b):
	if a[0] > a[1]: raise Exception('first input argument is not an interval')
	if b[0] > b[1]: raise Exception('second input argument is not an interval')
	a_unrolled = range(a[0], a[1]+1)
	b_unrolled = range(b[0], b[1]+1)
	return sum(1 for x in a_unrolled if x in b_unrolled)

def __apply_formatting__(cstring):
	string = cstring.__text__
	# Make sure the style boxes properties are properly set
	# - check all style boxes have strictly positive lengths
	if len(cstring) > 0 and sum(1 for sbox in cstring.__sbox__ if sbox.length <= 0) > 0:
		raise Exception('found style box with length <= 0')
	# - check that the sum of lengths equals the overall length
	if sum(stb.length for stb in cstring.__sbox__) != len(cstring):
		raise Exception('length mismatch')
	# - check that the first style box starts at index zero
	if len(cstring) > 0 and cstring.__sbox__[0].start != 0:
		raise Exception('start index of the first style box is not zero')
	# - check that each style box start index is equal to the cumulated length
	cum_length = 0
	for i in range(len(cstring.__sbox__)-1):
		cum_length += cstring.__sbox__[i].length
		if cstring.__sbox__[i+1].start != cum_length:
			raise Exception('invalid start index')
	# If string is empty, just return an empty string
	if len(cstring) == 0: return ''
	# Otherwise create the output string with formatting blocks
	if __flag_use_colors__:
		out = ''.join(colors.color( \
			string[elm.start : elm.start + elm.length], \
			fg=elm.fg(), bg=elm.bg(), style=elm.style()) \
			for elm in cstring.__sbox__)
		return out
	else:
		return string



class CString:

	__text__ = '' # unformatted text
	__sbox__ = [] # style boxes

	class StyleBox:
		start  = 0 # start index of the formatting element
		length = 0 # num characters in the style box
		__style__  = None # type of formatting applied

		def __init__(self, start, length, style):
			# TODO add tests to validate inputs		
			self.start     = start
			self.length    = length
			self.__style__ = style
		
		def __str__(self): 
			return 'start='    + str(self.start  ) + \
				' length=' + str(self.length ) + \
				' fg='     + str(self.fg   ()) + \
				' bg='     + str(self.bg   ()) + \
				' style='  + str(self.style())
		def fg    (self): return None if self.__style__ == None else self.__style__['fg']
		def bg    (self): return None if self.__style__ == None else self.__style__['bg']
		def style (self): return None if self.__style__ == None else self.__style__['style']
		def interval(self):
			# Return the interval over which the style box spans in [x, y] format
			return [self.start, self.start + self.length - 1]
		


	def __add__(self, other):
		if isinstance(other, str): other = CString(other)
		out = copy.deepcopy(self)
		out.__concat_trailing__(other)
		return out
	
	
	def __concat_leading__(self, other):
		# Left-side concatenation with another cstring
		other_copy = copy.deepcopy(other)
		# Increase the start indices of the current object's style boxes with the length of the other object
		for s in self.__sbox__: s.start += len(other)
		# Concatenate inner structures
		self.__text__ = other_copy.str() + self.__text__
		self.__sbox__ = other_copy.__sbox__ + self.__sbox__
		return self


	def __concat_trailing__(self, other):
		# Right-side concatenation with another cstring
		other_copy = copy.deepcopy(other)
		# Increase the start indices of the other object's style boxes with the length of the current object
		for s in other_copy.__sbox__: s.start += len(self)
		# Concatenate inner structures
		self.__text__ += other_copy.__text__
		self.__sbox__ = self.__sbox__ + other_copy.__sbox__
		return self


	def __getitem__(self, key):
		# If the string is empty, return an empty CString in any case
		if len(self) == 0: return CString('')
		# Transform key into a slice if necessary
		if isinstance(key, int): key = slice(key, key+1)
		# Now check the step
		if key.step == None or key.step == 1:
			# If the step is None or 1, just remove the unnecessary leading and trailing characters
			start, stop = key.indices(len(self))[0:2]
			out = copy.deepcopy(self)
			out.__remove_leading__(start).__remove_trailing__((len(self) - stop) % len(self))
		else:
			# Otherwise we have to extract characters individually
			raise Exception('not implemented yet')
		# Return result
		return out


	def __iadd__(self, other):
		self = self.__add__(other)
		return self


	def __init__(self, string, fg=None, bg=None, style=None):
		self.__text__ = string
		self.__sbox__ = []
		if len(string) > 0: self.__sbox__ = [self.StyleBox(0, len(string), {'fg' : fg, 'bg' : bg, 'style': style})]	


	def __len__(self): return len(self.str())


	def __radd__(self, other):
		# __radd__ may only be called with strings
		if not isinstance(other, str):
			raise Exception('CString objects may only be concatenated with strings')
		return CString(other).__add__(self)


	def __remove_edgecases__(self, numchars):
		# Deal with edge cases for character removal, return a True flag is the object has been processed
		# 1/ numchars <= 0
		if numchars <= 0: return True
		# 2/ all characters are removed
		if numchars >= len(self):
			self.__init__('')
			return True
		# Otherwise return False
		return False


	def __remove_leading__(self, numchars):
		# Deal with edge cases
		if self.__remove_edgecases__(numchars): return self
		# Now deal with the normal case
		# Actually remove characters
		self.__text__ = self.__text__[numchars:]
		# Then adjust style boxes
		i = 0
		while numchars > 0:
			stb = self.__sbox__[i]
			# Compute the number of characters that can be removed from the current style box
			to_remove = min(numchars, stb.length)
			# Adjust length
			stb.length -= to_remove
			# Adjust start index of the current and subsequent style boxes
			# Don't do anything for the 1st style box whose start index is already zero
			for j in range(max(i,1) ,len(self.__sbox__)): self.__sbox__[j].start -= to_remove
			# If the current style box is not empty (length = 0), remove it
			# In this case, the index does not need to be increased
			if stb.length == 0: self.__sbox__.remove(stb)
			else: i += 1
			# Update the number of characters
			numchars -= to_remove
		return self


	def __remove_trailing__(self, numchars):
		# Deal with the case where numchars <= 0
		if self.__remove_edgecases__(numchars): return self
		# Now deal with the normal case
		# Actually remove characters
		self.__text__ = self.__text__[:-numchars]
		# Then adjust style boxes
		i = len(self.__sbox__) - 1
		while numchars > 0:
			stb = self.__sbox__[i]
			# Compute the number of characters that can be removed from the current style box
			to_remove = min(numchars, stb.length)
			# Adjust length
			stb.length -= to_remove
			# If the current style box is not empty (length = 0), remove it
			if stb.length == 0: self.__sbox__.remove(stb)
                        # Update index and number of characters
			i -= 1
			numchars -= to_remove
		return self	


	def __str__(self): return __apply_formatting__(self)


	def capitalize(self):
		self.replacestr(self.str().capitalize())
		return self


	def casefold(self):
		try:
			self.replacestr(self.str().casefold())
		except:
			# The casefold() method does not exist in Python 2, which will create errors
			# Try calling lower() as a replacement
			self.lower()			
		return self


	def center(self, width, fillchar=' ', fillfg=None, fillbg=None, fillstyle=None):
		if width <= len(self): return self
		# Num characters to add as leading and trailing characters
		num_chars_to_add = width - len(self)
		num_chars_leading = int(math.ceil(num_chars_to_add * 0.5))
		num_chars_trailing = num_chars_to_add - num_chars_leading
		# Append fill characters
		self.__concat_leading__ (CString(fillchar * num_chars_leading , fillfg, fillbg, fillstyle))
		self.__concat_trailing__(CString(fillchar * num_chars_trailing, fillfg, fillbg, fillstyle))	
		return self


	def expandtabs(tabsize=8):
		raise Exception('not implemented yet') #TODO


	def ljust(self, width, fillchar=' ', fillfg=None, fillbg=None, fillstyle=None):
		if width <= len(self): return self
		self.__concat_trailing__(CString(fillchar * (width - len(self)), fillfg, fillbg, fillstyle))
		return self


	def lower(self):
		self.replacestr(self.str().lower())
		return self


	def lstrip(self):
		num_chars_to_remove = len(self) - len(self.str().lstrip())
		self.__remove_leading__(num_chars_to_remove)
		return self


	def replace(self, old, new, count=-1):
		# Call the string replace() method just to validate input arguments
		_ = self.str().replace(old, new, count)
		# Deal with edge cases
		if count == 0:
			 return self
		if len(self) == 0 and len(old) != 0:
			return self
		if len(self) == 0 and len(old) == 0:
			# If the current cstring is empty and 'old' is empty too, just return 'new'
			self = CString(new)
			return self
		if len(old) == 0:
			# Deal with the special case where 'old' is an empty string
			# In this case, 'new' has to be inserted at the start, at the end and between all characters
			# Formatting will be preserved only when 'new' is inserted between two characters within the same style box
			# Create the result with the 'new' string
			out = CString(new)
			# Append characters one by one
			for i in range(len(self)-1): 
				out += self[i]
				# If the current character and the next one are in the same style box, preserve formatting
				flag = False
				for sbox in self.__sbox__:
					if __overlap__([i,i+1], sbox.interval()) == 2:
						flag = True
						out += CString(new, fg=sbox.fg(), bg=sbox.bg(), style=sbox.style())
						break
				# Otherwise, add 'new' without any formatting
				if not flag: out += CString(new)
			# Add the last character and the 'new' string once again			
			out += self[-1] + CString(new)						
			self = out
			return self
		# Compute size difference between the new and the old string
		size_diff = len(new) - len(old)
		# Now do the actual replacement
		string = self.str()
		num_iter = 0
		is_finished = False
		while not is_finished:
			# Look for the next occurrence of the 'old' string
			idx = string.find(old)
			if idx != -1:
				# If we found an occurrence...
				# Get the 'old' string's interval in the string that is being processed
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
						sbox.start  += len(new) - len(old) + overlap
						sbox.length -= overlap
				# Remove style boxes that may be empty
				empty_sbox = list(i for i in range(len(self.__sbox__)) if self.__sbox__[i].length == 0)
				for i in reversed(empty_sbox): del self.__sbox__[i]
				# Update number of iterations
				num_iter += 1
			# Check if the computation is finished
			is_finished = idx == -1 or count == num_iter
		# Update the string and exit
		self.__text__ = string
		return self
					



	def rjust(self, width, fillchar=' ', fillfg=None, fillbg=None, fillstyle=None):
		if width <= len(self): return self
		self.__concat_leading__(CString(fillchar * (width - len(self)), fillfg, fillbg, fillstyle))
		return self


	def rstrip(self):
		num_chars_to_remove = len(self) - len(self.str().rstrip())
		self.__remove_trailing__(num_chars_to_remove)
		return self


	def str(self): return self.__text__


	def strip(self): return self.lstrip().rstrip()


	def replacestr(self, string):
		# Replace the object's string with another string of same size
		if not isinstance(string, str) or len(string) != len(self):
			raise Exception('string can only be replaced with another string of same size')
		self.__text__ = string
		return self


	def split(self, sep, maxsplit=-1):
		# Check that separator has been specified
		if sep == None: raise Exception('separator has to be specified')
		# Call the built-in string split method
		pieces = self.str().split(sep, maxsplit)
		pos_in_str = 0
		for idx in range(len(pieces)):
			p = pieces[idx]
			# If the current piece is empty, replace it with an empty cstring and continue
			if len(p) == 0:
				pieces[idx] = CString('')
				pos_in_str += len(sep)
				continue
			# Get the interval in the input string
			interval = [pos_in_str, pos_in_str + len(p) - 1]
			# For each piece, initialize an empty list of style boxes and reset the start index to zero
			p_stb = []
			start_idx = 0
			# Look for style boxes than span over the current piece
			for stb in self.__sbox__:
				overlap = __overlap__(interval, stb.interval())
				if overlap > 0:
					# Copy the style box, adjust start and length
					stb_copy        = copy.deepcopy(stb)
					stb_copy.start  = start_idx
					stb_copy.length = overlap
					# Append it to the list of style boxes
					p_stb.append(stb_copy)
					# Increase the start index for the current piece
					start_idx += stb_copy.length
			# Finally replace the current piece with a cstring
			pieces[idx] = CString(p)
			pieces[idx].__sbox__ = p_stb
			# Increase the position in the input string
			pos_in_str += len(p) + len(sep)
		return pieces
					
	
	def swapcase(self):
		self.replacestr(self.str().swapcase())
		return self		


	def title(self):
		self.replacestr(self.str().title())
		return self


	def upper(self):
		self.replacestr(self.str().upper())
		return self

	


        #maketrans()    Returns a translation table to be used in translations
        #partition()    Returns a tuple where the string is parted into three parts
        #replace()      Returns a string where a specified value is replaced with a specified value
        #rindex()       Searches the string for a specified value and returns the last position of where it was found
        #rpartition()   Returns a tuple where the string is parted into three parts
        #rsplit()       Splits the string at the specified separator, and returns a list
        #split()        Splits the string at the specified separator, and returns a list
        #splitlines()   Splits the string at line breaks and returns a list
        #translate()    Returns a translated string
        #zfill()

blue  = CString('blue' , fg='blue' )
red   = CString('red'  , fg='red'  )
green = CString('green', fg='green')

#test = CString('   lstrip test with 3 chars', fg='green')
#length = len(test)
#print(test.lstrip(), length - len(test) == 3)
#test  = CString('  ', bg='green') + CString('   harder lstrip ', bg='blue') + CString('test', bg='red')
#length = len(test)
#print(test)
#print(test.lstrip(), length - len(test) == 5)
test = red + blue + green
print(test)
print(test.replacestr('greenbluered'))
test = red + '*' + blue + '*' + green + '*'
for p in test.split('*'): print(p)
test = red + blue + green
for p in test.split('e'): print(p)
test = red + CString('***', fg='red') + CString('**', fg='blue') + green + CString('*', fg='red') + blue
print(test)
for p in test.split('*'): print(p)

tests = {}
cstr = red + blue + green

def printreturn(obj):
	print(obj)
	return obj

cstr  = red
cstr += green
cstr += blue
print('****************************************************************')
print('*** CONCATENATION TESTS ****************************************')
print('****************************************************************')
cstr  = red
cstr += green
cstr += blue
tests['concatenation'] = [ \
	printreturn(red   + green   + blue  ).str() == 'redgreenblue' and len(red   + green   + blue  ) == 12, \
        printreturn('000' + green   + blue  ).str() == '000greenblue' and len('000' + green   + blue  ) == 12, \
        printreturn(red   + '00000' + blue  ).str() == 'red00000blue' and len(red   + '00000' + blue  ) == 12, \
	printreturn(red   + green   + '0000').str() == 'redgreen0000' and len(red   + green   + '0000') == 12, \
	printreturn(cstr ).str() == 'redgreenblue' and len(cstr) == 12, \
        printreturn(red  ).str() == 'red'          and len(red  ) == 3, \
        printreturn(green).str() == 'green'        and len(green) == 5, \
	printreturn(blue ).str() == 'blue'         and len(blue ) == 4]

print('****************************************************************')
print('*** CHARACTER REMOVAL TESTS ************************************')
print('****************************************************************')
cstr = red + blue + green
tests['character_removal'] = [
	printreturn(copy.deepcopy(cstr).__remove_leading__ ( 3)).str() == 'bluegreen', \
        printreturn(copy.deepcopy(cstr).__remove_leading__ ( 5)).str() == 'uegreen', \
        printreturn(copy.deepcopy(cstr).__remove_leading__ ( 7)).str() == 'green', \
        printreturn(copy.deepcopy(cstr).__remove_leading__ ( 9)).str() == 'een', \
        printreturn(copy.deepcopy(cstr).__remove_leading__ (12)).str() == '', \
        printreturn(copy.deepcopy(cstr).__remove_leading__ (99)).str() == '', \
        printreturn(copy.deepcopy(cstr).__remove_leading__ ( 0)).str() == 'redbluegreen', \
        printreturn(copy.deepcopy(cstr).__remove_leading__ (-5)).str() == 'redbluegreen', \
        printreturn(copy.deepcopy(cstr).__remove_trailing__( 3)).str() == 'redbluegr', \
        printreturn(copy.deepcopy(cstr).__remove_trailing__( 5)).str() == 'redblue', \
        printreturn(copy.deepcopy(cstr).__remove_trailing__( 7)).str() == 'redbl', \
        printreturn(copy.deepcopy(cstr).__remove_trailing__( 9)).str() == 'red', \
        printreturn(copy.deepcopy(cstr).__remove_trailing__(12)).str() == '', \
        printreturn(copy.deepcopy(cstr).__remove_trailing__(99)).str() == '', \
        printreturn(copy.deepcopy(cstr).__remove_trailing__( 0)).str() == 'redbluegreen', \
        printreturn(copy.deepcopy(cstr).__remove_trailing__(-5)).str() == 'redbluegreen']
print('****************************************************************')
print('*** SUBSTRING TESTS ********************************************')
print('****************************************************************')
cstr = red + blue + green
tests['substring'] = [ \
	len(cstr)         == 12, \
	printreturn(cstr[ 0   ]).str() == 'r', \
	printreturn(cstr[ 2   ]).str() == 'd', \
	printreturn(cstr[ 3   ]).str() == 'b', \
	printreturn(cstr[ 7   ]).str() == 'g', \
	printreturn(cstr[ 11  ]).str() == 'n', \
	printreturn(cstr[-1   ]).str() == 'n', \
	printreturn(cstr[-2   ]).str() == 'e', \
	printreturn(cstr[-3   ]).str() == 'e', \
	printreturn(cstr[  : 3]).str() == 'red', \
	printreturn(cstr[ 0: 3]).str() == 'red', \
	printreturn(cstr[ 3: 7]).str() == 'blue', \
	printreturn(cstr[ 7:12]).str() == 'green', \
	printreturn(cstr[  :  ]).str() == 'redbluegreen', \
	printreturn(cstr[ 1: 5]).str() == 'edbl', \
	printreturn(cstr[-7:-2]).str() == 'uegre']
print('****************************************************************')
print('*** STRING TRANSFORMATION TESTS ********************************')
print('****************************************************************')
cstr = red + ' ' + green + ' ' + blue
tests['transform'] = [ \
        printreturn(cstr.replacestr('blue red green')).str() == 'blue red green', \
        printreturn(cstr.replacestr('red green blue')).str() == 'red green blue', \
	printreturn(cstr.capitalize()      ).str() == 'Red green blue', \
        printreturn(cstr.title()           ).str() == 'Red Green Blue', \
	printreturn(cstr.casefold()        ).str() == 'red green blue', \
        printreturn(cstr.upper()           ).str() == 'RED GREEN BLUE' and cstr.str().isupper(), \
        printreturn(cstr.lower()           ).str() == 'red green blue' and cstr.str().islower(), \
        printreturn(cstr.title().swapcase()).str() == 'rED gREEN bLUE', \
        printreturn(cstr.lower()           ).str() == 'red green blue', \
	printreturn(copy.deepcopy(cstr).center(10, fillchar='*')).str() == 'red green blue'.center(10, '*'), \
        printreturn(copy.deepcopy(cstr).center(20, fillchar='*')).str() == 'red green blue'.center(20, '*'), \
        printreturn(copy.deepcopy(cstr).center(19, fillchar='*')).str() == 'red green blue'.center(19, '*'), \
	printreturn(copy.deepcopy(cstr).ljust (10, fillchar='*')).str() == 'red green blue', \
	printreturn(copy.deepcopy(cstr).ljust (20, fillchar='*')).str() == 'red green blue******', \
	printreturn(copy.deepcopy(cstr).rjust (10, fillchar='*')).str() == 'red green blue', \
        printreturn(copy.deepcopy(cstr).rjust (20, fillchar='*')).str() == '******red green blue', \
	len(copy.deepcopy(cstr).ljust(150)) == 150, \
        len(copy.deepcopy(cstr).rjust(150)) == 150]
print('****************************************************************')
print('*** REPLACE TEST ***********************************************')
print('****************************************************************')
cstr = red + ' ' + green + ' ' + blue
tests['replace'] = [ \
	printreturn(copy.deepcopy(cstr).replace('e' , '0'  )).str() == cstr.str().replace('e' , '0'  ), \
	printreturn(copy.deepcopy(cstr).replace('e' , ''   )).str() == cstr.str().replace('e' , ''   ), \
	printreturn(copy.deepcopy(cstr).replace('e' , '---')).str() == cstr.str().replace('e' , '---'), 
	printreturn(copy.deepcopy(cstr).replace('ee', '*'  )).str() == cstr.str().replace('ee', '*'  ), \
	printreturn(copy.deepcopy(cstr).replace(''  , '%%' )).str() == cstr.str().replace(''  , '%%' ), 
	printreturn(copy.deepcopy(cstr).replace(cstr.str()  , '0123456789')).str() == '0123456789', \
	printreturn(copy.deepcopy(cstr).replace(cstr.str()  , '0123456789')).str() == '0123456789', \
	printreturn(copy.deepcopy(cstr).replace('ed gre'    , '0123456789')).str() == 'r0123456789en blue', \
	printreturn(copy.deepcopy(cstr).replace('ed green b', '0123456789')).str() == 'r0123456789lue', \
	printreturn(copy.deepcopy(cstr).replace('green bl'  , '0123456789')).str() == 'red 0123456789ue', \
	printreturn(copy.deepcopy(cstr).replace(' green blue', '0123456789')).str() == 'red0123456789']


print('****************************************************************')
print('*** SUMMARY ****************************************************')
print('****************************************************************')
for k in tests.keys():
	output_msg = ('TEST \'' + k + '\'').ljust(40) + ': '
	success = sum(1 for x in tests.get(k) if x) == len(tests.get(k))
	if success:
		output_msg += 'OK'.center(6)
	else:
		output_msg += 'FAILED'
	print(output_msg)	

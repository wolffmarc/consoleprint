from consoleprint import RichText, ConsolePrinter

"""
RichText is a class that implements formatted strings for the purpose of displaying 
nicely formatted messages in consoles and terminals. It supports most of the built-in
string methods.
"""

# RichText objects are initialized from a string with optional foreground/background colors
# and font style settings
foo = RichText('This is a colored', fg='red') + ' ' + RichText('string example', fg='blue')
print(foo)
# The main feature of RichText objects is that their length can be computed
print('\'' + foo + '\' is a ' + str(len(foo)) + '-character string')
# Which allows to do many things like centering and text justfication
foo = RichText('Left-justified example', fg='green')
print((foo + ' ').ljust(80, fillchar='*'))
foo = RichText('Right-justified example', fg='green')
print((' ' + foo).rjust(80, fillchar='*'))
foo = RichText('Right-justified example with colored fill characters', fg='green')
print((' ' + foo).rjust(80, fillchar='*', fg='blue'))
foo = RichText('This will hurt your eyes', fg='green')
print((' ' + foo).rjust(80, fillchar='*', fg='red', bg='yellow'))
foo = RichText('This is centered text', fg='red')
print((' ' + foo + ' ').center(80, fillchar='/'))
foo = RichText('This is centered and underlined text', fg='red', style='underline')
print((' ' + foo + ' ').center(80, fillchar='/'))
foo = RichText('This is a centered and underlined title', fg='red', style='underline')
print((' ' + foo + ' ').title().center(80, fillchar='/'))
# Splitting works too!
foo = RichText('This is a split%%', fg='red') + RichText('%%ting test', fg='blue')
print(foo)
print('Left  part: ' + foo.split('%%%%')[0])
print('Right part: ' + foo.split('%%%%')[1])

"""
ConsolePrinter is a utility to easily print well-formatted info/error/status messages
"""
# You initialize it with a max. line length that applies only to status messages
pt = ConsolePrinter(80)
# Now you can display a whole bunch of messages
pt.info('We are going to start this computation')
# Alinea can be increased and decreased
pt.alinea_incr()
pt.info('Here is some information about this computation')
pt.info('Some more information')
pt.info('Of course it works with ' + RichText('RichText objects too!', fg='red'))
pt.success('Computation successful')
pt.error('An error occured')
pt.failure('And led to a failure')
pt.alinea_decr()
pt.info('Let\'s start another computation')
pt.alinea_incr()
pt.success('I love success messages')
pt.success('Makes me feel good')
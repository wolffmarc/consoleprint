import sys
sys.path.append('../')

from consoleprint import ConsolePrinter

p = ConsolePrinter(60)
p.header('THIS IS A TITLE')
p.header('THIS IS A TITLE THAT IS WAY TOO LONG FOR THE SELECTED OUTPUT LENGTH')
p.info('This is an information message')
p.error('This is an error message')
p.alinea_incr()
p.info('This is an information message with a 1st alinea level')
p.alinea_incr()
p.info('This is an information message with a 2nd alinea level')
p.alinea_decr()
p.info('Back to 1st alinea level!')
p.error('Should apply to error messages too!')
p.success('This is a success message with an alinea')
p.alinea_decr()
p.success('Same without alinea')
p.failure('This is a failure message')

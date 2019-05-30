import copy
from RichText import RichText

red = RichText('red', fg='red')
blue = RichText('blue', fg='blue')
green = RichText('green', fg='green')

# Colored characters
# Red
rr = RichText('r', fg='red')  # red 'r'
re = RichText('e', fg='red')  # red 'e'
rd = RichText('d', fg='red')  # red 'd'
# Blue
bb = RichText('b', fg='blue')  # blue 'b'
bl = RichText('l', fg='blue')  # blue 'l'
bu = RichText('u', fg='blue')  # blue 'u'
be = RichText('e', fg='blue')  # blue 'e'
# Green
gg = RichText('g', fg='green')  # green 'g'
gr = RichText('r', fg='green')  # green 'r'
ge = RichText('e', fg='green')  # green 'e'
gn = RichText('n', fg='green')  # green 'n'
# Empty string
empty = RichText('')


test = red + blue + green
print(test)
print(test.replaceall('greenbluered'))
test = red + '*' + blue + '*' + green + '*'
for p in test.split('*'): print(p)
test = red + blue + green
for p in test.split('e'): print(p)
test = red + RichText('***', fg='red') + RichText('**', fg='blue') + green + RichText('*', fg='red') + blue
print(test)
for p in test.split('*'): print(p)

tests = {}
cstr = red + blue + green


def printreturn(obj):
    if isinstance(obj, list):
        for x in obj:
            print(x)
    else:
        print(obj)
    return obj


print('****************************************************************')
print('*** CONCATENATION TESTS ****************************************')
print('****************************************************************')
cstr = red
cstr += green
cstr += blue
tests['concatenation'] = [ \
    printreturn(red + green + blue).str() == 'redgreenblue' and len(red + green + blue) == 12,
    printreturn('000' + green + blue).str() == '000greenblue' and len('000' + green + blue) == 12,
    printreturn(red + '00000' + blue).str() == 'red00000blue' and len(red + '00000' + blue) == 12,
    printreturn(red + green + '0000').str() == 'redgreen0000' and len(red + green + '0000') == 12,
    printreturn(cstr).str() == 'redgreenblue' and len(cstr) == 12,
    printreturn(red).str() == 'red' and len(red) == 3,
    printreturn(green).str() == 'green' and len(green) == 5,
    printreturn(blue).str() == 'blue' and len(blue) == 4]

print('****************************************************************')
print('*** CHARACTER REMOVAL TESTS ************************************')
print('****************************************************************')
cstr = red + blue + green
tests['character_removal'] = [
    printreturn(copy.deepcopy(cstr).__lcrop__(3)).str() == 'bluegreen',
    printreturn(copy.deepcopy(cstr).__lcrop__(5)).str() == 'uegreen',
    printreturn(copy.deepcopy(cstr).__lcrop__(7)).str() == 'green',
    printreturn(copy.deepcopy(cstr).__lcrop__(9)).str() == 'een',
    printreturn(copy.deepcopy(cstr).__lcrop__(12)).str() == '',
    printreturn(copy.deepcopy(cstr).__lcrop__(99)).str() == '',
    printreturn(copy.deepcopy(cstr).__lcrop__(0)).str() == 'redbluegreen',
    printreturn(copy.deepcopy(cstr).__lcrop__(-5)).str() == 'redbluegreen',
    printreturn(copy.deepcopy(cstr).__rcrop__(3)).str() == 'redbluegr',
    printreturn(copy.deepcopy(cstr).__rcrop__(5)).str() == 'redblue',
    printreturn(copy.deepcopy(cstr).__rcrop__(7)).str() == 'redbl',
    printreturn(copy.deepcopy(cstr).__rcrop__(9)).str() == 'red',
    printreturn(copy.deepcopy(cstr).__rcrop__(12)).str() == '',
    printreturn(copy.deepcopy(cstr).__rcrop__(99)).str() == '',
    printreturn(copy.deepcopy(cstr).__rcrop__(0)).str() == 'redbluegreen',
    printreturn(copy.deepcopy(cstr).__rcrop__(-5)).str() == 'redbluegreen']
print('****************************************************************')
print('*** SUBSTRING TESTS ********************************************')
print('****************************************************************')
cstr = red + blue + green
tests['substring'] = [
    len(cstr) == 12,
    printreturn(cstr[0]).str() == 'r',
    printreturn(cstr[2]).str() == 'd',
    printreturn(cstr[3]).str() == 'b',
    printreturn(cstr[7]).str() == 'g',
    printreturn(cstr[11]).str() == 'n',
    printreturn(cstr[-1]).str() == 'n',
    printreturn(cstr[-2]).str() == 'e',
    printreturn(cstr[-3]).str() == 'e',
    printreturn(cstr[: 3]).str() == 'red',
    printreturn(cstr[0: 3]).str() == 'red',
    printreturn(cstr[3: 7]).str() == 'blue',
    printreturn(cstr[7:12]).str() == 'green',
    printreturn(cstr[:]).str() == 'redbluegreen',
    printreturn(cstr[1: 5]).str() == 'edbl',
    printreturn(cstr[-7:-2]).str() == 'uegre']
print('****************************************************************')
print('*** STRING TRANSFORMATION TESTS ********************************')
print('****************************************************************')
cstr = red + ' ' + green + ' ' + blue
tests['transform'] = [
    printreturn(cstr.replaceall('blue red green')).str() == 'blue red green',
    printreturn(cstr.replaceall('red green blue')).str() == 'red green blue',
    printreturn(cstr.capitalize()).str() == 'Red green blue',
    printreturn(cstr.title()).str() == 'Red Green Blue',
    printreturn(cstr.casefold()).str() == 'red green blue',
    printreturn(cstr.upper()).str() == 'RED GREEN BLUE' and cstr.str().isupper(),
    printreturn(cstr.lower()).str() == 'red green blue' and cstr.str().islower(),
    printreturn(cstr.title().swapcase()).str() == 'rED gREEN bLUE',
    printreturn(cstr.lower()).str() == 'red green blue',
    printreturn(copy.deepcopy(cstr).center(10, fillchar='*')).str() == 'red green blue'.center(10, '*'),
    printreturn(copy.deepcopy(cstr).center(20, fillchar='*')).str() == 'red green blue'.center(20, '*'),
    printreturn(copy.deepcopy(cstr).center(19, fillchar='*')).str() == 'red green blue'.center(19, '*'),
    printreturn(copy.deepcopy(cstr).ljust(10, fillchar='*')).str() == 'red green blue',
    printreturn(copy.deepcopy(cstr).ljust(20, fillchar='*')).str() == 'red green blue******',
    printreturn(copy.deepcopy(cstr).rjust(10, fillchar='*')).str() == 'red green blue',
    printreturn(copy.deepcopy(cstr).rjust(20, fillchar='*')).str() == '******red green blue',
    len(copy.deepcopy(cstr).ljust(150)) == 150,
    len(copy.deepcopy(cstr).rjust(150)) == 150]
print('****************************************************************')
print('*** REPLACE TEST ***********************************************')
print('****************************************************************')
cstr = red + ' ' + green + ' ' + blue
tests['replace'] = [
    printreturn(copy.deepcopy(cstr).replace('e', '0')).str() == cstr.str().replace('e', '0'),
    printreturn(copy.deepcopy(cstr).replace('e', '')).str() == cstr.str().replace('e', ''),
    printreturn(copy.deepcopy(cstr).replace('e', '---')).str() == cstr.str().replace('e', '---'),
    printreturn(copy.deepcopy(cstr).replace('ee', '*')).str() == cstr.str().replace('ee', '*'),
    printreturn(copy.deepcopy(cstr).replace('', '%%')).str() == cstr.str().replace('', '%%'),
    printreturn(copy.deepcopy(cstr).replace(cstr.str(), '0123456789')).str() == '0123456789',
    printreturn(copy.deepcopy(cstr).replace(cstr.str(), '0123456789')).str() == '0123456789',
    printreturn(copy.deepcopy(cstr).replace('ed gre', '0123456789')).str() == 'r0123456789en blue',
    printreturn(copy.deepcopy(cstr).replace('ed green b', '0123456789')).str() == 'r0123456789lue',
    printreturn(copy.deepcopy(cstr).replace('green bl', '0123456789')).str() == 'red 0123456789ue',
    printreturn(copy.deepcopy(cstr).replace(' green blue', '0123456789')).str() == 'red0123456789']
print('****************************************************************')
print('*** SPLITTING TESTS ********************************************')
print('****************************************************************')
teststr = red + ' ' + blue + ' ' + green
args_and_answer = [
    [[' '], [red, blue, green]],
    [['e'], [rr, rd + ' ' + bb + bl + bu, ' ' + gg + gr, empty, gn]],
    [['r'], [empty, re + rd + ' ' + blue + ' ' + gg, ge + ge + gn]],
    [['n'], [red + ' ' + blue + ' ' + gg + gr + ge + ge, empty]],
    [['ee'], [red + ' ' + blue + ' ' + gg + gr, gn]],
    [['red'], [empty, ' ' + blue + ' ' + green]],
    [['blue'], [red + ' ', ' ' + green]],
    [['green'], [red + ' ' + blue + ' ', empty]]
]


tests['splitting'] = list(printreturn(teststr.split(*(x[0]))) == x[1] for x in args_and_answer)




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


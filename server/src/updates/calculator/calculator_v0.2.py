#!/usr/bin/env python3

import os

CONST_VERSION = 'v0.2'

os.system('clear')
print('Welcome to calculator %s\n\nPlease enter your FIRST number:' % CONST_VERSION)
first = int(input())
print('Please enter your SECOND number:')
second = int(input())
result = first + second
os.system('clear')
print('Welcome to calculator %s\n\n' % CONST_VERSION)
print(' %d\n+%d\n---------------------------------------\n %d' % (first, second, result))
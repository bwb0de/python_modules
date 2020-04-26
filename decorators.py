#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# license: AGPL-3.0 
#

from os import system as sh
from sys import platform

def clear():
	if platform == 'win32':
		r = sh('cls')
	else:
		r = sh('clear')



def clear_screen(func):
	def wrapper(*args, **kargs):
		clear()
		return func(*args, **kargs)
	return wrapper


def only_tuple_and_list(func):
	def wrapper(*args, **kargs):
		if not isinstance(args, (tuple, list)):
			err = "Iterador não suportado, utilizar 'tuple' ou 'list' como argumento."
			raise ValueError(err)
		return func(*args, **kargs)
	return wrapper



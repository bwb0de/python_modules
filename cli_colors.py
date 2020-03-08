#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# license: AGPL-3.0 
#


from colored import fg, bg, attr

def branco(string):
	return "{}{}{}".format(attr(0), string, attr(0))

def vermelho(string):
	return "{}{}{}".format(fg(1), string, attr(0))

def azul_claro(string):
	return "{}{}{}".format(fg(12), string, attr(0))

def verde(string):
	return "{}{}{}".format(fg(2), string, attr(0))

def verde_limao(string):
	return "{}{}{}".format(fg(41), string, attr(0))

def verde_florescente(string):
	return "{}{}{}".format(fg(10), string, attr(0))

def verde_mar(string):
	return "{}{}{}".format(fg(35), string, attr(0))

def verde_agua(string):
	return "{}{}{}".format(fg(37), string, attr(0))

def amarelo(string):
	return "{}{}{}".format(fg(11), string, attr(0))

def rosa(string):
	return "{}{}{}".format(fg(5), string, attr(0))

def cinza(string):
	return "{}{}{}".format(fg(8), string, attr(0))

def salmao(string):
	return "{}{}{}".format(fg(9), string, attr(0))

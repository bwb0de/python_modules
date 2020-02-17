#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
#  Copyright 2019 Daniel Cruz <bwb0de@bwb0dePC>
#  Version 0.1
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
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


def saida_verde(rotulo, valor, referencia='', escalonamento=[]):
	if referencia != '':
		if escalonamento != []:
			partes = '('
			n = len(escalonamento)
			l_step = 0
			while l_step != n:
				if l_step == n-1:
					partes += str(escalonamento[l_step])
					partes += ')'
				else:
					partes += str(escalonamento[l_step])
					partes += '/'
				l_step += 1
			return str(verde(rotulo) + ' ({})'.format(referencia) +": {} ".format(valor) + partes)
		else:
			return str(verde(rotulo) + ' ({})'.format(referencia) +": {} ".format(valor))
	else:
		return str(verde('{}'.format(rotulo)) +": {} ".format(valor))




def saida_vermelha(rotulo, valor, referencia='', escalonamento=[]):
	if referencia != '':
		if escalonamento != []:
			partes = '('
			n = len(escalonamento)
			l_step = 0
			while l_step != n:
				if l_step == n-1:
					partes += str(escalonamento[l_step])
					partes += ')'
				else:
					partes += str(escalonamento[l_step])
					partes += '/'
				l_step += 1
			return str(vermelho(rotulo) + ' ({})'.format(referencia) +": {} ".format(valor) + partes)
		else:
			return str(vermelho(rotulo) + ' ({})'.format(referencia) +": {} ".format(valor))
	else:
		return str(vermelho('{}'.format(rotulo)) +": {} ".format(valor))




def saida_rosa(rotulo, valor, referencia='', escalonamento=[]):
	if referencia != '':
		if escalonamento != []:
			partes = '('
			n = len(escalonamento)
			l_step = 0
			while l_step != n:
				if l_step == n-1:
					partes += str(escalonamento[l_step])
					partes += ')'
				else:
					partes += str(escalonamento[l_step])
					partes += '/'
				l_step += 1
			return str(rosa(rotulo) + ' ({})'.format(referencia) +": {} ".format(valor) + partes)
		else:
			return str(rosa(rotulo) + ' ({})'.format(referencia) +": {} ".format(valor))
	else:
		return str(rosa('{}'.format(rotulo)) +": {} ".format(valor))
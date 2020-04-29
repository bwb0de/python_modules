#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# license: AGPL-3.0 
#


import time
import datetime


def convert_date_string(s, string_format='pt-br'):
	"""Converte uma string de data para um objeto 'datetime.datetime'
	
	Arguments:
		s {string} -- data em formato de string
	
	Keyword Arguments:
		string_format {string} -- faz a conversão conforme as convenções da localidade (default: {'pt-br'})
	
	Returns:
		{datetime.datetime} -- objeto 'datetime.datetime' para operações matemáticas com data
	"""
	
	assert isinstance(s, str), "O argumento A deve uma string de data correspondente ao argumento B..."
	
	try:
		if string_format == 'pt-br':
			return datetime.datetime.fromtimestamp(time.mktime(time.strptime(s, "%d/%m/%Y")))
		elif string_format == 'us':
			return datetime.datetime.fromtimestamp(time.mktime(time.strptime(s, "%m/%d/%Y")))
		elif string_format == 'ISO':
			return datetime.datetime.fromtimestamp(time.mktime(time.strptime(s, "%Y-%m-%d")))
		else:
			return "Formaro de string não reconhecido..."
	except ValueError:
		return "Data inválida ou em formato inválido..."


def create_period_pair(start_date, end_date, string_format='pt-br'):
	"""Recebe uma data de inínio e fim e retorna uma tupla com os respectivos 'datetime.datetime' representando o período

	Arguments:
		start_date {string} -- data de início do período
		end_date {string} -- data de fim do período

	Keyword Arguments:
		string_format {string} -- faz a conversão conforme as convenções da localidade (default: {'pt-br'})

	Returns:
		{tuple} -- tupla com dois objetos 'datetime.datetime'
	"""

	start_dt = convert_date_string(start_date, string_format=string_format)
	end_dt = convert_date_string(end_date, string_format=string_format)
	return (start_dt, end_dt)


def time_delta(start_date, end_date, string_format='pt-br', output_info='dias'):
	"""Calcula a variação de tempo, em dias, entre duas datas

	Arguments:
		start_date {string} -- data de início
		end_date {string} -- data de fim

	Keyword Arguments:
		string_format {string} -- informa a convenção da localidade para conversão da data (default: {'pt-br'})

	Returns:
		{int} -- número de dias entre a data de início e fim
		{float} -- número de anos entre a data de início e fim
	"""
	if isinstance(start_date, str) and  isinstance(end_date, str):
		period = create_period_pair(start_date, end_date)
	else:
		period = (start_date, end_date)

	if output_info == 'dias':
		return (period[1] - period[0]).days
	
	elif output_info == 'anos':
		return (period[1] - period[0]).days / 365



def today_date(string_format='pt-br'):
	"""Retorna uma string com a data do dia
	
	Keyword Arguments:
		string_format {string} -- informa a convenção da localidade para formatação da string (default: {'pt-br'})
	
	Returns:
		{string} -- data correspondente ao dia vigente
	"""

	if string_format == 'pt-br':
		return time.strftime('%d/%m/%Y', time.gmtime())
	elif string_format == 'us':
		return time.strftime('%m/%d/%Y', time.gmtime())
	elif string_format == 'ISO':
		return time.strftime('%Y-%m-%d', time.gmtime())


def years_since(date, string_format='pt-br'):
	"""Retorna um float com a diferença em anos desde a data especificada
	
	Arguments:
		date {string} -- data passada a ser verificada
	
	Keyword Arguments:
		string_format {string} -- informa a convenção da localidade da string (default: {'pt-br'})
	
	Returns:
		{float} -- número representando a distancia em anos desde a data especificada
	"""

	assert convert_date_string(date) <= convert_date_string(today_date()), "O argumento 'date' precisa ser uma data no passado"

	return time_delta(date, today_date(), string_format=string_format, output_info='anos')


def days_to(date, string_format='pt-br'):
	"""Retorna um inteiro com a quantidade de dias até a data especificada
	
	Arguments:
		date {string} -- data futura a ser verificada
	
	Keyword Arguments:
		string_format {string} -- informa a convenção da localidade (default: {'pt-br'})
	
	Returns:
		{int} -- número de dias
	"""

	assert convert_date_string(date) >= convert_date_string(today_date()), "O argumento 'date' precisa ser uma data no futuro"

	return time_delta(date, today_date(), string_format=string_format, output_info='dias') * -1


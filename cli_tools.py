#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# license: AGPL-3.0 
#


import sys
import itertools
import os
import io
import pickle
import json
import csv
import tempfile
import time
import re
import datetime
import heapq

from colored import fg, bg, attr
from subprocess import getoutput
from random import randrange, randint
from string import whitespace, punctuation, digits
from collections import OrderedDict
from copy import copy


from decorators import only_tuple_and_list

tmp_folder = tempfile.gettempdir()

class PK_LinkedList(list):
    def __init__(self, iterator=()):
        super(PK_LinkedList, self).__init__(iterator)
        self.sorted = False

    def __sub__(self, other):
        for element in other:
            self.remove(element)
        return self

    def append(self, element):
        if self.index(element) != None:
            print("Item já está na lista...")
            return

        super(PK_LinkedList, self).append(element)

    def index(self, element, self_list_nfo=False):
        check_element = bisect_search_idx(element, self, (0, len(self)))
        if not isinstance(check_element, bool): return check_element
        else: return None


class PK_OrderedLinkedList(list):
    def __init__(self, iterator=()):
        super(PK_OrderedLinkedList, self).__init__(iterator)
        self.sorted = False

    def __sub__(self, other):
        for element in other:
            self.remove(element)
        return self

    def append(self, element):
        if self.index(element) != None:
            print("Item já está na lista...")
            return

        try:
            if element > self[-1]:
                self.sorted = True
            else:
                self.sorted = False
        except IndexError:
            self.sorted = True
        
        super(PK_OrderedLinkedList, self).append(element)

        if not self.sorted:
            self.sort()

    def index(self, element, self_list_nfo=False):
        check_element = bisect_search_idx(element, self, (0, len(self)))
        if not isinstance(check_element, bool): return check_element
        else: return None
            
            

class ColisionDict(OrderedDict):
    def __add__(self, other):
        if len(self) > len(other):
            iterated_dict = other.items()
            copied_dict = self.copy()
        else:
            iterated_dict = self.items()
            copied_dict = other.copy()

        for item in iterated_dict:
            if copied_dict.get(item[0]):
                if type(copied_dict[item[0]]) == list:
                    copied_dict[item[0]].append(item[1])
                else:
                    copied_dict[item[0]] = [copied_dict[item[0]], item[1]]
            else:
                copied_dict[item[0]] = item[1]
        return copied_dict
    
    def append(self, key, value):
        if not self.get(key):
            self[key] = [value]
        else:
            self[key].append(value)


class Stack():
	def __init__(self, list_of_elements):
		assert isinstance(list_of_elements, list)
		self.stack = []

	def push(self, item):
		self.stack.append(item)

	def pull(self):
		if self.size() != 0:
			return self.stack.pop()

	def peek(self):
		if self.size() != 0:
			return self.stack[-1]

	def size(self):
		return len(self.stack)



class Queue():
	def __init__(self, list_of_elements):
		assert isinstance(list_of_elements, list)
		self.queue = list_of_elements

	def __repr__(self):
		output = str(self.queue).replace('[', '««').replace(']', '««')
		return output

	def enqueue(self, item):
		self.queue.append(item)

	def dequeue(self):
		if self.size() != 0:
			return self.queue.pop(0)

	def peek(self):
		if self.size() != 0:		
			return self.queue[0]

	def size(self):
		return len(self.queue)


class Heap():
	def __init__(self, list_of_elements):
		assert isinstance(list_of_elements, list)
		self.heap = []
		for element in list_of_elements:
			self.push(element)

	def push(self, element):
		return heapq.heappush(self.heap, element)

	def pull(self):
		if self.size() != 0:
			return heapq.heappop(self.heap)

	def peek(self):
		if self.size() != 0:		
			return self.heap[0]

	def size(self):
		return len(self.heap)
	




def create_lockfile(filename):
	"""Cria um arquivo vazio na pasta temporária para servir como trava
	
	Arguments:
		filename {string} -- o nome do arquivo vazio
	"""

	f = open(tmp_folder+os.sep+filename,'w')
	f.close()

def remove_lockfile(filename):
	"""Remove o arquivo alvo da pasta temporária
	
	Arguments:
		filename {string} -- the name of the file
	"""

	os.remove(tmp_folder+os.sep+filename)

def lockfile_name(path_to_file):
	"""Adciona um prefixo padrão a um arquivo alvo para criar um nome ao arquivo de trava
	
	Arguments:
		path_to_file {string} -- o caminho até o arquivo alvo/fonte
	
	Returns:
		{string} -- retorna o nome para o arquivo de trava
	"""

	lkf_name = path_to_file.split(os.sep)[-1]
	file_name = '~lock_'+str(lkf_name)
	return file_name


def list_folder(folder):
	"""Lista o conteúdo da pasta alvo

	Arguments:
		folder {string} -- caminho para a pasta a ser listada

	Returns:
		{list} -- lista com os nomes dos arquivos presentes na pasta
	"""
	return os.listdir(os.getcwd()+os.sep+folder)


def convert_date_string(s, string_format='pt-br'):
	"""Converte uma string de data para um objeto 'datetime.datetime'
	
	Arguments:
		s {string} -- data em formato de string
	
	Keyword Arguments:
		string_format {string} -- faz a conversão conforme as convenções da localidade (default: {'pt-br'})
	
	Returns:
		{datetime.datetime} -- objeto 'datetime.datetime' para operações matemáticas com data
	"""
	if string_format == 'pt-br':
		return datetime.datetime.fromtimestamp(time.mktime(time.strptime(s, "%d/%m/%Y")))
	elif string_format == 'us':
		return datetime.datetime.fromtimestamp(time.mktime(time.strptime(s, "%m/%d/%Y")))
	elif string_format == 'ISO':
		return datetime.datetime.fromtimestamp(time.mktime(time.strptime(s, "%Y-%m-%d")))


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


def add_list_elements(lista):
	"""Adiniona os elementos de uma lista numérica
	
	Arguments:
		lista {list|tuple} -- lista com números a serem adicionados
	
	Returns:
		{int|float} -- resultado da soma entre os elementos
	"""

	assert isinstance(lista, (list, tuple)), "Argumento deve ser do tipo 'list' ou 'tuple'"

	output = 0
	for item in lista:
		output += item
	return output



def list_col_responses(iterator, col_num=0, delimiter='\t'):
	"""Retorna os valores de uma tabela, linha à linha, para a coluna selecionada
	
	Arguments:
		iterator {table} -- é uma tabela NxN ou uma lista ou tupla com strings e um caractere delimiter
	
	Keyword Arguments:
		col_num {int} -- o numero correspondente à coluna desejada (default: {0})
		delimiter {str} -- o caractere/substring que demarca a separação das colunas (default: {'\t'})
	
	Yields:
		{string} -- each cell will be returned separatedly
	"""

	for item in iterator:
		yield item.split(delimiter)[col_num]


def concat_dict_values(dictionary, key, value):
	"""Verifica se um dicionário possui uma chave. Se possuir, cria uma lista no lado dos valores para preservar valores antigos
	
	Arguments:
		dictionary {dict} -- dicionário onde o par key-value deverá ser inserido
		key {any} -- qualquer chave de dicionário válida
		value {any} -- qualquer valor de dicionário válido
	
	Returns:
		{dict} -- retorna o dicionário modificado
	"""

	nested_list = False
	if dictionary.get(key):
		if isinstance(dictionary[key], list):
			if isinstance(dictionary[key][0], list):
				nested_list = True

		old_value = dictionary[key]
		dictionary[key] = [value]

		if nested_list:
			old_value.reverse()
			for sub_list in old_value:
				dictionary[key].insert(0, sub_list)
		else:
			dictionary[key].insert(0, old_value)
	return dictionary


def dict_from_table(iterator, col_num=0, delimiter='\t'):
	"""Converte uma tabela em um dicionário utilizando os valores da coluna selecionada como chaves
	
	Arguments:
		iterator {table} -- é uma tabela NxN ou uma lista ou tupla com strings e um caractere delimiter
	
	Keyword Arguments:
		col_num {int} -- número da coluna de referência (default: {0})
		delimiter {str} -- o caractere/substring que demarca a separação das colunas (default: {'\t'})
	
	Returns:
		{dict} -- retorna um OrderedDict

	Observation:
		Colisões serão aninhadas conforme a função 'concat_dict_values'
	"""

	assert isinstance(iterator, (tuple, list)), "Iterador não suportado, utilizar 'tuple' ou 'list' como argumento."
	assert isinstance(iterator[0], (list, str)), "As linhas da tabela devem ser to tipo 'list'."

	use_delimiter = check_table_type(iterator)

	output = OrderedDict()
	for item in iterator:
		if use_delimiter:
			num_of_cols = item.count(delimiter)+1
		else:
			num_of_cols = len(item)
		
		indexes = list(range(0,num_of_cols))
		indexes.remove(col_num)

		if use_delimiter:
			tmp_list = item.split(delimiter)
		else:
			tmp_list = item

		tmp_key = tmp_list[col_num]
		tmp_list.remove(tmp_list[col_num])
		tmp_value = tmp_list
		
		if output.get(tmp_key):
			output = concat_dict_values(output, tmp_key, tmp_value)
		else:
			output[tmp_key] = tmp_value

	return output


def create_col_index(iterator):
	"""Cria um índice para as colunas de uma tabela
	
	Arguments:
		iterator {list|tuple} -- lista com os nomes das colunas na mesma ordem da tabela original
	
	Returns:
		{dict} -- retorna um dicionário com rótulos apontando para os indexes
	"""

	assert isinstance(iterator, (tuple, list)), "Iterador não suportado, utilizar 'tuple' ou 'list' como argumento."

	output = ColisionDict()

	n = itertools.count()

	for col in iterator:
		idx = next(n)
		output.append(col, idx)
	
	return output


def create_line_index(iterator, col_num_list=[0], delimiter='\t'):
	"""Cria um dicionário a partir de uma tabela em que os valores das colunas selecionadas apontam para o número da linha da tabela original
	
	Arguments:
		iterator {table} -- é uma tabela NxN ou uma lista ou tupla com strings e um caractere delimiter
	
	Keyword Arguments:
		col_num_list {list} -- lista com o numero das colunas que serão indexadas (default: {[0]})
		delimiter {str} -- o caractere/substring que demarca a separação das colunas (default: {'\t'})
	
	Returns:
		{dict} -- retorna um dicionário com referências para as linhas da tabela original
	"""
	
	assert isinstance(iterator, (tuple, list)), "Iterador não suportado, utilizar 'tuple' ou 'list' como argumento."

	output = dict()
	
	use_delimiter = check_table_type(iterator)
	
	for col in col_num_list:
		idx = itertools.count()
		for line in iterator:
			n = next(idx)
			if use_delimiter:
				line = line.split(delimiter)
			if output.get(line[col]):
				output = concat_dict_values(output, line[col], n)
			else:
				output[line[col]] = n
	return output
		

def create_target_file(filename, target_filename, file_folder=os.curdir+os.sep, target_folder=os.getcwd()+os.sep):
	"""Cria um link simbólico para o arquivo alvo
	
	Arguments:
		filename {string} -- o nome do arquivo fonte ou de origem
		target_filename {string} -- o nome do arquivo de link que será criado
	
	Keyword Arguments:
		file_folder {string} -- a pasta onde o arquivo de origem está localizada (default: {os.curdir+os.sep})
		target_folder {string} -- a pasta onde o arquivo de link será criado (default: {os.getcwd()+os.sep})
	"""

	source = file_folder + filename
	destination = target_folder + target_filename
	
	try: os.remove(destination)
	except FileNotFoundError: pass
	
	os.symlink(source, destination)

def check_table_type(iterator):
	"""Verifica o tipo de tabela incluida no argumento
	
	Arguments:
		iterator {tabela} -- é uma tabela NxN ou uma lista ou tupla com strings
	
	Returns:
		{bool} -- retorna False se a tabela for uma lista/tupla aninhada com listas/tuplas
		{bool} -- retorna True se a tabela for uma lista/tupla com strings
	"""

	assert isinstance(iterator, (tuple, list)), "Iterador não suportado, utilizar 'tuple' ou 'list' como argumento."
	
	if isinstance(iterator[0], (tuple, list)):
		return False
	elif isinstance(iterator[0], str):
		return True

		


def ask_for_col_labels(num_of_cols, table_first_line, use_delimiter=True, delimiter='\t'):
	"""Retorna um dicionário com os nomes das colunas e indexes de referência
	
	Arguments:
		num_of_cols {int} -- quantidade de colunas da tabela
		table_first_line {table} -- matrix 1xN ou string com valores separados pelo delimitador
	
	Keyword Arguments:
		use_delimiter {bool} -- utiliza o delimitador no caso da amostra de dados ser uma string com delimitador (default: {True})
		delimiter {str} -- o caractere/substring que demarca a separação das colunas (default: {'\t'})

	Returns:
		{list} -- retorna uma lista
	"""

	assert isinstance(num_of_cols, int), "Número de colunas deve ser do tipo 'int'."
	assert isinstance(table_first_line, (list, str, tuple)), "Linha da tabela deve ser 'list', 'tuple' ou 'str'."

	output = []
	n = itertools.count() 
	
	if use_delimiter: table_first_line = table_first_line.split(delimiter)

	while True:
		idx = next(n)
		print('Indique o nome da coluna que armazena o dado: {}'.format(table_first_line[idx]))
		label = input(' :$')
		output.append(label)
		if len(output) == num_of_cols: break
	
	return output


def string_table_to_int_matrix(iterator, reference_data=False, reversed_reference_data=False, delimiter='\t'):
	"""Converte uma tabela com strings em uma matriz numérica a partir de uma referência prévia ou a partir da atribuição arbitrária de números aos valores dos campos textuais na ordem em que estes são apresentados
	
	Returns:
		{tupla} -- uma tupla com dois elementos, o primeiro a matriz com as respostas convertidas em números, o segundo uma lista de dicionários com as referências
	"""

	assert isinstance(iterator, (tuple, list)), "Iterador não suportado, utilizar 'tuple' ou 'list' como argumento."

	numeric_matrix = []

	use_delimiter = check_table_type(iterator)
	
	if use_delimiter:
		num_of_cols = len(iterator[0].split(delimiter))
	else:
		num_of_cols = len(iterator[0])

	if not reference_data:
		reference_list = create_reference_table(num_of_cols=num_of_cols)
	else:
		reference_list = reference_data
		assert len(reference_data) == num_of_cols, "A quantidade de dicionários na lista de referência de valores deve corresponder ao número de colunas da tabela"

	if not reversed_reference_data:
		reversed_reference_list = create_reference_table(num_of_cols=num_of_cols)
	else:
		reversed_reference_list = reversed_reference_data
		assert len(reversed_reference_data) == num_of_cols, "A quantidade de dicionários na lista de referência de valores deve corresponder ao número de colunas da tabela"


	for line in iterator:
		if use_delimiter:
			line = line.split(delimiter)
		
		n = itertools.count()
		numeric_matrix_line = []

		for col_idx in range(len(line)):
			ref_idx = next(n)
			print(line[col_idx])
			if not reference_list[ref_idx].get(line[col_idx]): 
				novo_escore = len(reference_list[ref_idx]) + 1
				reference_list[ref_idx][line[col_idx]] = novo_escore
				reversed_reference_list[ref_idx][novo_escore] = line[col_idx] 
				numeric_matrix_line.append(novo_escore)
			else:
				numeric_matrix_line.append(reference_list[ref_idx][line[col_idx]])

		numeric_matrix.append(numeric_matrix_line)

	return numeric_matrix, reference_list, reversed_reference_list
		


def create_reference_table(num_of_cols=0, zeros=False):
	"""Cria uma lista com dicionários vazios para referenciação de valores. Opcionalmente cria uma lista com zeros.
	
	Keyword Arguments:
		num_of_cols {int} -- número de colunas a serem inicializadas (default: {0})
		zeros {bool} -- se True, substitui os dicionários por zeros (default: {False})
	
	Returns:
		{list_of_dict} -- lista de dicionários vazios para referenciação de colunas
		{list_of_ints} -- lista com zeros para atualização de valores, exemplo: largura colunas de uma tabela
	"""

	output = []

	while num_of_cols:
		if zeros:
			output.append(0)
		else:
			output.append({})
		num_of_cols -= 1

	return output


def print_numeric_matrix(matrix_iterator, translator=False, col_wid=False, return_value=False, output_format='string'):
	"""Imprime uma matrix de inteiros reconvertida conforme as referencias apresentadas em 'translator'
	
	Arguments:
		matrix_iterator {table} -- lista/tupla de listas/tuplas
	
	Keyword Arguments:
		translator {list_of_dict} -- tabela de referência para conversão de valores (default: {False})
		col_wid {list_of_ints} -- lista de inteiros com as respectivas larguras das colunas (default: {False})
		return_value {bool} -- indica se a string de saída da tabela deve ser retornada ou impressa (default: {False})
	
	Returns:
		{string} -- se 'return_value' for True, retorna a string da tabela
	"""
	if output_format == 'string':
		output = ''
	
	elif output_format == 'list':
		output = []
	
	for list_obj in matrix_iterator:
		n = itertools.count()
		
		if output_format == 'string':
			line = ""
		elif output_format == 'list':
			line = []

		for cell in list_obj:
			if translator:
				col_idx = next(n)
				
				if output_format == 'string':
					if col_wid:
						line += translator[col_idx][cell].ljust(col_wid[col_idx])
					else:
						line += translator[col_idx][cell]
				elif output_format == 'list':
					line.append(translator[col_idx][cell])

		if not return_value:
			print(line)
		else:
			if output_format == 'string':
				output += line + os.linesep
			elif output_format == 'list':
				output.append(line)
	
	if return_value:
		return output




def read_all_text_json_file(filename):
	"""Retorna todas as linhas do arquivo tipo 'text_json_file'
	
	Arguments:
		filename {string} -- nome do arquivo de tipo text_json_file
	
	Yields:
		{pyObject} -- cada linha é retornada como um objeto python, conforme o formato JSON usado
	"""
	
	with open(filename) as f:
		for line in f:
			yield json.loads(line)


def read_target_line_on_text_json_file(filename, line_number):
	"""Retorna apenas a linha selecionada para o arquivo de tipo text_json_file
	
	Arguments:
		filename {string} -- nome do arquivo de tipo text_json_file
		line_number {int} -- nomero da linha que deve ser retornada
	
	Returns:
		{pyObject} -- retorna um objeto python, conforme o formato JSON usado
	"""

	assert isinstance(line_number, int)

	f = open(filename)
	output = itertools.islice(f, line_number, line_number+1)
	output = json.loads(next(output))
	f.close()
	return output



def read_all_text_table_file(filename, file_folder=os.curdir, delimiter='\t'):
	"""Ler todas as linhas de uma tabela em formato texto
	
	Arguments:
		filename {string} -- nome do arquivo da tabela
	
	Keyword Arguments:
		delimiter {string} -- caractere ou substring que delimita as colunas (default: {'\t'})
	
	Yields:
		{generator} -- retorna as linhas uma a uma...
	"""

	with open(file_folder + os.sep + filename) as f:
		for line in f:
			yield split_and_strip(line, delimiter=delimiter)



def split_and_strip(text, delimiter='\t'):
	"""Separa uma string com base no delimitador e retira espaços em branco no início e final dos elementos
	
	Arguments:
		texto {string} -- texto ou string de entrada
	
	Keyword Arguments:
		delimiter {string} -- caractere ou substring que delimita os campos (default: {'\t'})
	
	Returns:
		{list} -- retorna uma lista com os elementos
	"""

	assert isinstance(text, str)
	assert isinstance(delimiter, str)
	
	output = text.split(delimiter)
	idx = itertools.count()
	for i in output: output[next(idx)] = i.strip()
	return output



def read_target_line_on_text_table_file(filename, line_number, delimiter='\t'):
	"""Lê uma linha alvo de uma tabela em formato texto e retorna seu conteúdo, bem como o rótulo dos campos (primeira linha)
	
	Arguments:
		filename {string} -- nome do arquivo de tabela em formato texto
		line_number {int} -- linha alvo
	
	Keyword Arguments:
		delimiter {str} -- caractere ou substring que delimita os campos (default: {'\t'})
	
	Returns:
		{dict} -- retorna dicionário com nome/ordem dos campos e dados da linha selecionada
	"""
	assert isinstance(filename, str)
	assert isinstance(line_number, int)
	assert isinstance(delimiter, str)

	with open(filename) as f:
		fields = itertools.islice(f, 0, 1)
		fields = split_and_strip(next(fields), delimiter=delimiter) 
	
	with open(filename) as f:
		output = itertools.islice(f, line_number, line_number+1)
		output = split_and_strip(next(output), delimiter=delimiter)
		output = dict(zip(fields, output))

	return {'fields': fields, 'data': output}



def create_column_metainfo_file(text_table_filename, text_table_file_folder=os.curdir,  delimiter='\t', col_space=2):
	"""Cria, na pasta temporária, um arquico com informações da largura das colunas de uma tabela de texto
	
	Arguments:
		text_table_filename {string} -- nome do arquivo de tabela
	
	Keyword Arguments:
		delimiter {str} -- delimitador das colunas (default: {'\t'})
		col_space {int} -- espaço a ser colocado no final do arquivo (default: {2})

	"""
	
	assert isinstance(text_table_filename, str)
	assert isinstance(delimiter, str)
	assert isinstance(col_space, int)
	
	output_file = 'metainfo_'+text_table_filename
	
	text_table_generator = read_all_text_table_file(text_table_filename, delimiter=delimiter)
	
	fields = next(text_table_generator)
	fields_num = len(fields)

	output_col_size = []
	
	while fields_num:
		output_col_size.append(0)
		fields_num -= 1
	
	for line in text_table_generator:
		col_idx_count = itertools.count()
		for value in line:
			col_idx = next(col_idx_count)
			if len(value)+col_space > output_col_size[col_idx]:
				output_col_size[col_idx] = len(value)+col_space
	
	output_info = dict(zip(fields, output_col_size))
	save_json(output_info, output_file, file_folder=tmp_folder)



def print_text_table_file(text_table_filename, count_lines=True, delimiter='\t'):
	"""Imprime no console as informações de uma tabela no formato texto.
	
	Arguments:
		text_table_filename {string} -- nome do arquivo de tabela
	
	Keyword Arguments:
		count_lines {bool} -- ativa/desativa a contagem linha à linha (default: {True})
		delimiter {str} -- delimitador de campo, separador das colunas (default: {'\t'})
	"""
	
	text_table_generator = read_all_text_table_file(text_table_filename, delimiter=delimiter)

	fields = next(text_table_generator)
	line_num = itertools.count(start=1)

	if not os.path.isfile(tmp_folder+os.sep+'metainfo_'+text_table_filename):
		create_column_metainfo_file(text_table_filename)
	
	metainfo_file = 'metainfo_'+text_table_filename
	metainfo = load_json(metainfo_file, file_folder=tmp_folder)
	

	for table_line in text_table_generator:
		if count_lines: 
			line_to_print = str(next(line_num)).zfill(3) + '  '
		else: 
			line_to_print = ''
			next(line_num)
		
		col_idx_count = itertools.count()
		cells_values = ""
		for cell in table_line:
			col_idx = next(col_idx_count)
			cells_values += cell.ljust(metainfo[fields[col_idx]])
			
		print(line_to_print+cells_values)
	
	line_num = next(line_num) - 1
	if not count_lines:
		print('Total:', line_num)



def append_to_text_table_file(new_line, filename, file_folder=os.curdir, delimiter='\t', constrain_cols=True):
	"""Adiciona linha no final de uma tabela em texto
	
	Arguments:
		filename {string} -- arquivo de tabela em formato texto
		new_line {dict, tuple, list} -- novo conteúdo a ser inserido do arquivo
	
	Keyword Arguments:
		delimiter {str} -- caractere ou substring que delimita os campos (default: {'\t'})
		constrain_cols {bool} -- ativa/desativa validação de colunas e posição (default: {True})
	"""

	assert isinstance(filename, str)
	assert isinstance(delimiter, str)
	assert isinstance(constrain_cols, bool)

	if constrain_cols:
		assert isinstance(new_line, dict), "Para verificação das colunas é necessário passar os valores em um 'dict'"
		with open(filename) as f:
			fields = split_and_strip(next(f), delimiter=delimiter)
		assert len(fields) == len(new_line), "A quantidade de colunas no dicionário não corresponde à do arquivo"
		for key in new_line:
			assert key in fields, "O campo '{}' não existe no arquivo '{}'".format(key, filename)

	else:
		assert isinstance(new_line, (tuple, list)), "O argumento 'new_line' deve ser uma 'list' ou 'tuple'"
		new_line = delimiter.join(new_line) + os.linesep
	
	with open(file_folder+os.sep+filename, 'a') as f:
		if constrain_cols:
			new_line_ordered_info = []
			for field in fields:
				new_line_ordered_info.append(new_line[field])
			new_line = delimiter.join(new_line_ordered_info) + os.linesep
			f.write(new_line)
		else:
			f.write(new_line)
	

def return_bisect_lists(input_list):
	"""Divide uma lista e retorna uma tupla com o termo central e as metades direita e esquerda
	
	Arguments:
		input_list {list} -- lista a ser dividida
	
	Returns:
		{tuple} -- tupla contendo (fatia_esquerda, termo_central, fatia_direita)
		{string|int|float} -- se a lista for unitária retorna o elemento
		{NoneType} -- retorna None se a lista de entrada for vazia
	"""

	assert isinstance(input_list, list)

	input_size = len(input_list) 
	
	if input_size == 1:	return input_list[0]
	elif input_size == 0: return None

	left_side = input_list[:input_size//2]
	middle_element = input_list[input_size//2]
	right_side = input_list[(input_size//2)+1:]

	return left_side, middle_element, right_side



def bisect_search(search_value, input_list):
	"""Realiza pesquisa binária na lista de entrada e retorna True se o elemento existir
	
	Arguments:
		search_value {string|int|float} -- item a ser pesquisado
		input_list {list} -- a lista de entrada precisa conter elementos de um mesmo tipo
	
	Returns:
		{bool} -- retorna True se existir, False se não
	"""

	assert isinstance(search_value, (str, int, float))
	assert isinstance(input_list, list)

	input_size = len(input_list) 

	if input_list == []:
		return False
	elif input_size == 1:
		middle_element = return_bisect_lists(input_list)
		if search_value == middle_element: return True
		else:return False
	else:
		left_side, middle_element, right_side = return_bisect_lists(input_list)
		try:
			if search_value == middle_element: return True
			elif search_value < middle_element: return bisect_search(search_value, left_side)
			else: return bisect_search(search_value, right_side)	
		except TypeError:
			return False


def return_bisect_lists_idx(input_list, slice_ref, current_mid_idx=0):
	"""Retorna uma tupla com os índices de referencia para dividi-lá em termo central, fatias direita e esquerda
	
	Arguments:
		input_list {list} -- lista de entrada
		slice_ref {tuple} -- tupla contendo o index de início e fim da fatia
	
	Keyword Arguments:
		current_mid_idx {int} -- valor do índice para o termo do meio (default: {0})
	
	Returns:
		{tuple} -- retorna uma tupla com os indices da fatia esquerda, termo dentral e fatia direita
		{int} -- retorna um inteiro quando a lista é unitária
		{NoneType} -- retorna None se a lista estiver vazia
	"""

	assert isinstance(input_list, list)
	assert isinstance(slice_ref, (list, tuple))
	assert isinstance(current_mid_idx, int)
	
	init_idx, end_idx = slice_ref
	sliced_list = input_list[init_idx:end_idx]
	new_mid_idx = (init_idx + end_idx)//2 

	input_size = len(sliced_list) 
	
	if input_size == 1:	return new_mid_idx 
	elif input_size == 0: return None

	new_mid_idx = (init_idx + end_idx)//2 
	left_side_slice_idx = (init_idx, new_mid_idx)
	right_side_slice_idx = ((new_mid_idx)+1, end_idx) 

	return left_side_slice_idx, new_mid_idx, right_side_slice_idx



def bisect_search_idx(search_value, input_list, slice_ref, current_mid_idx=0):
	"""Retorna a posição do elemento pesquisado na lista fornecida, se não existir, retorna Falso
	
	Arguments:
		search_value {int|str|float} -- termo/elemento a ser pesquisado
		input_list {list} -- a lista de entrada precisa conter elementos de um mesmo tipo
		slice_ref {tuple} -- tupla contendo os indices de referência inicial e final da fatia
	
	Keyword Arguments:
		current_mid_idx {int} -- posição do termo central (default: {0})
	
	Returns:
		{int} -- retorna a posição do elemento na lista, se ele existir
		{bool} -- retorna False se o elemento não existir
	"""

	assert isinstance(search_value, (str, int, float)), "O argumento 'search_value' pode ser do tipo string, inteiro ou float"
	assert isinstance(input_list, list), "O argumento 'input_list' deve ser do tipo lista"
	assert isinstance(slice_ref, (tuple, list)), "O argumento 'slice_ref', deve ser uma tupla ou lista"
	assert isinstance(current_mid_idx, int), "O argumento 'current_mid_idx' deve ser um número inteiro"

	init_idx, end_idx = slice_ref
	sliced_list = input_list[init_idx:end_idx]
	sliced_list_size = len(sliced_list)

	if sliced_list == []:
		return False
	elif sliced_list_size == 1:
		new_mid_idx = return_bisect_lists_idx(input_list, slice_ref=slice_ref, current_mid_idx=current_mid_idx)
		if search_value == input_list[new_mid_idx]: return new_mid_idx
		else: return False
	else:
		left_side_slice_idx, new_mid_idx, right_side_slice_idx = return_bisect_lists_idx(input_list, slice_ref, current_mid_idx)
		try:
			if search_value == input_list[new_mid_idx]: 
				return new_mid_idx
			elif search_value < input_list[new_mid_idx]:
				return bisect_search_idx(search_value, input_list, slice_ref=left_side_slice_idx, current_mid_idx=new_mid_idx)
			else:
				return bisect_search_idx(search_value, input_list, slice_ref=right_side_slice_idx, current_mid_idx=new_mid_idx)	
		except TypeError:
			return False


def load_json(filename, file_folder=os.curdir):
	"""Carrega um arquivo JSON do disco rígido na memória
	
	Arguments:
		filename {string} -- nome do arquivo a ser carregado
		file_folder {string} -- local no sistema de arquivos onde o arquivo se encontra
	
	Returns:
		{pyObject} -- retorna um objeto python conforme a estrutura do arquivo JSON
	"""

	assert isinstance(filename, str)
	assert isinstance(file_folder, str)

	with open(file_folder+os.sep+filename) as f:
		data = f.read()
		return json.loads(data)



def save_json(info, filename, file_folder=os.curdir, tmp_folder=tmp_folder):
	"""Grava o um arquivo JSON no disco rígido
	
	Arguments:
		info {list|dict} -- informação a ser gravada em disco
		filename {string} -- nome do arquivo onde a informação será armazenada
	
	Keyword Arguments:
		file_folder {string} -- pasta onde o arquivo está localizado (default: {os.curdir})
		tmp_folder {string} -- pasta temporária do sistema (default: {tmp_folder})
	"""

	lockf = lockfile_name(filename)

	while True:
		if os.path.isfile(tmp_folder + os.sep + lockf):
			time.sleep(0.1)
		else:
			create_lockfile(lockf)
			break

	with open(file_folder + os.sep + filename, 'w') as f:
		f.write(json.dumps(info, ensure_ascii=False, indent=4))

	remove_lockfile(lockf)




def make_random_float_list(num_of_elements, min_val=0, max_val=10000):
	"""Retorna uma lista contendo a quantidade definida de floats gerados aleatoriamente
	
	Arguments:
		num_of_elements {int} -- a quantidade de elementos da lista de retorno
	
	Keyword Arguments:
		min_val {int} -- o valor de referencia mínimo para produção de números aleatórios (default: {0})
		max_val {int} -- o valor de referencia máximo para produção de números aleatórios (default: {10000})
	
	Returns:
		{list} -- o retorno contém pontos flutuantes com duas casas decimais
	"""

	assert isinstance(num_of_elements, int)
	assert isinstance(min_val, int)
	assert isinstance(max_val, int)
	assert min_val < max_val, "O argumento 'min_val' sempre deve ser menor que 'max_val'"
	
	output = []

	while num_of_elements:
		output.append(randint(min_val,max_val)/100)
		num_of_elements -= 1
			
	return output


def save_csv(list_of_dicts, filename, file_folder=os.curdir, header=[], file_method=False, delimiter='\t', lineterminator='\n', tmp_folder=tmp_folder):
	"""Função de criação de arquivos CSV, grava informações de matrizes NxN ou lista de dicionários
	
	Arguments:
		list_of_dicts {tables} -- lista ou tupla contendo dicionários ou outras listas/tuplas
		filename {string} -- nome do arquivo CSV onde informações serão gravadas
	
	Keyword Arguments:
		file_folder {string} -- pasta onde o arquivo está localizado (default: {os.curdir})
		header {list} -- lista de cabeçalho do arquivo (default: {[]})
		delimiter {str} -- delimitador de campos (default: {'\t'})
		lineterminator {str} -- delimitador de fim de linha (default: {'\n'})
		tmp_folder {[type]} -- pasta temporária do sistema (default: {tmp_folder})
	
	Raises:
		TypeError: formatos de dados inadequados implicarão erro
	"""

	if isinstance(list_of_dicts[0], (dict, OrderedDict)):
		fields = list_of_dicts[0].keys()
		write_method='dict'

	elif isinstance(list_of_dicts[0], (list, tuple)):
		if not header:
			num_of_cols = len(list_of_dicts[0])
			idx = itertools.count()
			fields = []
			while num_of_cols:
				print(list_of_dicts[0][next(idx)])
				label = read_input(input_label="Qual o rótulo deste campo?")
				fields.append(label)
				num_of_cols -= 1
		else:
			fields = header
		write_method='list'
	
	elif not file_method in [False, 'a']:
		raise ValueError("Metodo de escrita em arquivo inválido")
	
	else:
		raise TypeError("O objeto passado não corresponde ao aceito pela função")
	
	lockf = lockfile_name(filename)

	while True:
		if os.path.isfile(tmp_folder + os.sep + lockf):
			time.sleep(0.1)
		else:
			create_lockfile(lockf)
			break
	
	if file_method:
		if not os.path.isfile(file_folder + os.sep + filename):
			file_method_to_use = 'w'
		else:
			file_method_to_use = file_method
	else:
		file_method_to_use = 'w'

	with open(file_folder + os.sep + filename, file_method_to_use) as f:
		if write_method == 'dict':
			w = csv.DictWriter(f, fields, delimiter=delimiter, lineterminator=lineterminator)
			if file_method_to_use != 'a':
				w.writeheader()
			w.writerows(list_of_dicts)
		
		elif write_method == 'list':
			w = csv.writer(f, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)
			if file_method_to_use != 'a':
				w.writerow(fields)
			for line in list_of_dicts:
				w.writerow(line)
	
	remove_lockfile(lockf)



def load_csv(filename, file_folder=os.curdir, delimiter='\t', lineterminator='\n'):
	"""Função de leitura de arquivos CSV, retorna um gerador que apresenta as informações linha à linha.
	
	Arguments:
		filename {string} -- nome do arquivo CSV
	
	Keyword Arguments:
		delimiter {char} -- caractere delimitador (default: {'\t'})
		lineterminator {char} -- caractere de final de linha (default: {'\n'})
	
	Yields:
		{OrderedDict} -- as linhas são retornadas como dicionário ordenado
	"""

	fields = load_csv_head(filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator)

	try:
		with open(os.path.join(file_folder, filename), encoding="utf8") as f:
			rd = csv.DictReader(f, delimiter=delimiter, lineterminator=lineterminator)
			for row in rd:
				ordered_row = OrderedDict()
				for col in fields:
					ordered_row[col] = row[col]
				yield ordered_row

	except UnicodeDecodeError:
		with open(os.path.join(file_folder, filename), encoding="cp1252") as f:
			rd = csv.DictReader(f, delimiter=delimiter, lineterminator=lineterminator)
			for row in rd:
				ordered_row = OrderedDict()
				for col in fields:
					ordered_row[col] = row[col]
				yield ordered_row



def load_full_csv(filename, file_folder=os.curdir, delimiter='\t', lineterminator='\n'):
	"""Função de leitura de arquivos CSV, retorna todo o conteúdo do arquivo de uma vez.
	
	Arguments:
		filename {string} -- nome do arquivo CSV
	
	Keyword Arguments:
		file_folder {string} -- local onde o arquivo se encontra (default: {os.curdir})
		delimiter {char} -- caractere delimitador de campo (default: {'\t'})
		lineterminator {char} -- caractere delimitador de linha (default: {'\n'})
	
	Returns:
		{list} -- returna uma lista de dicionários ordenados
	"""

	full_csv_info = []
	
	fields = load_csv_head(filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator)
	
	try:
		with open(os.path.join(file_folder, filename), encoding="utf8") as f:
			rd = csv.DictReader(f, delimiter=delimiter, lineterminator=lineterminator)
			for row in rd:
				ordered_row = OrderedDict()
				for col in fields:
					ordered_row[col] = row[col]
				full_csv_info.append(ordered_row)
	
	except UnicodeDecodeError:
		with open(os.path.join(file_folder, filename), encoding="cp1252") as f:
			rd = csv.DictReader(f, delimiter=delimiter, lineterminator=lineterminator)
			for row in rd:
				ordered_row = OrderedDict()
				for col in fields:
					ordered_row[col] = row[col]
				full_csv_info.append(ordered_row)
	
	return full_csv_info




def load_csv_head(filename, file_folder=os.curdir, delimiter='\t', lineterminator='\n'):
	"""Carrega as informações de cabeçalho (nomes das colunas) de um arquivo CSV
	
	Arguments:
		filename {string} -- nome do arquivo CSV
	
	Keyword Arguments:
		file_folder {string} -- local onde o arquivo está (default: {os.curdir})
		delimiter {char} -- caractere delimitador de campo (default: {'\t'})
		lineterminator {char} -- caractere de fim de linha (default: {'\n'})
	
	Returns:
		{list} -- lista contendo os nomes das colunas
	"""

	with open(os.path.join(file_folder, filename)) as f:
		f_csv_obj = csv.DictReader(f, delimiter=delimiter, lineterminator=lineterminator)
		header = f_csv_obj.fieldnames
	return header



def load_csv_cols(filename, selected_cols=[], file_folder=os.curdir, delimiter='\t', lineterminator='\n', sort_by=False, reverse_sort=False, implict_convert=True):
	"""Retorna colunas selecionadas de um arquivo CSV
	
	Arguments:
		filename {string} -- nome do arquivo CSV
	
	Keyword Arguments:
		selected_cols {list} -- lista de colunas selecionadas, se vazio a linha de comando solicitará seleção (default: {[]})
		file_folder {string} -- local onde o arquivo CSV está (default: {os.curdir})
		delimiter {char} -- caractere de delimitação das colunas (default: {'\t'})
		lineterminator {char} -- caractere de fim de linha (default: {'\n'})
		sort_by {string} -- colona que servirá de referencia para ordenação (default: {False})
		reverse_sort {bool} -- se True, a ordem será invertida (default: {False})
		implict_convert {bool} -- tenta converter informações conforme o tipo (default: {True})
	
	Returns:
		{table} -- retorna uma matrix NxN com os valores do arquivo CSV

	Observations:
		Para ordenar a lista a partir de um campo numérico, será necessário manter o argumento 'implict_convert' como True.
	"""

	fields = load_csv_head(filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator)
	lines = load_csv(filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator)

	if not selected_cols:
		selected_cols = pick_options(fields, input_label="Selecione as colunas desejadas", max_selection=len(fields))
	

	output = []
	for line in lines:
		output_line = []
		for col in selected_cols:
			if implict_convert: output_line.append(try_implict_convert(line[col]))
			else: output_line.append(line[col])
		output.append(output_line)

	if not sort_by:
		return output

	else:
		col_idx = selected_cols.index(sort_by)
		print(col_idx)
		sort_by_col = lambda l: l[col_idx]
		output.sort(key=sort_by_col)
		if reverse_sort:
			output.reverse()
		return output



def try_implict_convert(value):
	"""Tenta converter as informações das colunas de um arquivo CSV conforme a máscara/pattern identificado
	
	Arguments:
		value {string} -- valor em formato string a ser convertido
	
	Returns:
		{int|float|string} -- tenta retornar 'int' ou 'float', se não for possível devolve o valor de entrada.
	"""

	if (value.find(',') != -1) or (value.find('.') != -1):
		if re.search(r'\d*,\d*', value):
			try:
				value = value.replace(',','.')
				value = float(value)
			except: pass
			return value

		elif re.search(r'\d*.\d*', value):
			try:
				value = float(value)
			except: pass
			return value

		else:
			return value


	elif re.search(r'\d*', value):
		try: value = int(value)
		except: pass
		return value

	else:
		return value
		


def seek_for_csv_gaps(filename, file_folder=os.curdir, reference_cols=[], target_col=[], target_col_ops=[], delimiter='\t', lineterminator='\n', print_reference_cols=True, fill_gaps=False):
	"""Procura por celulas vazias em um arquivo CSV
	
	Arguments:
		filename {string} -- nome do arquivo CSV alvo...
	
	Keyword Arguments:
		file_folder {string} -- local onde o arquivo CSV está (default: {os.curdir})
		reference_cols {list} -- lista com colunas de referencia que terão os valores impressos no console quando uma célula vazia for encontrada (default: {[]})
		target_col {list} -- lista especificando as colunas a serem verificadas, se "[]" buscará qualquer célula vazia (default: {[]})
		target_col_ops {list} -- lista/tabela de opções a serem usadas para o preenchimento do campo vazio conforme a posição da coluna alvo (default: {[]})
		delimiter {string} -- delimitador das colunas (default: {'\t'})
		lineterminator {string} -- delimitador de fim linha (default: {'\n'})
		print_reference_cols {bool} -- indicador para impressão ou não dos valores das células de referência (default: {True})
		fill_gaps {bool} -- se True, solicita a inclusão da informação pendente encontrada (default: {False})
	
	Returns:
		{table} -- Salva automaticamnte o arquivo de origem e retorna a tabela modificada ao final da edição.
	"""
	
	table = load_full_csv(filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator)
	#fields = load_csv_head(filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator)
	
	show_reference_cols = print_reference_cols
	lines_with_gaps = []

	for line in table:
		skip_save_dialog = True
		if target_col == []:
			for col in line:
				if line[col] == '':
					if show_reference_cols == True:
						show_reference_cols = False
						for ref_col in reference_cols:
							print(line[ref_col])
					if fill_gaps:
						line[col] = read_input(input_label=col)
					else: 
						line[col] = ' '
						skip_save_dialog = False
						lines_with_gaps.append(line)

		else:
			for selected in target_col:
				if line[selected] == '':
					if show_reference_cols == True:
						show_reference_cols = False
						for ref_col in reference_cols:
							print(line[ref_col])
					if fill_gaps:
						line[col] = read_input(input_label=col)
					else: 
						line[col] = ' '
						skip_save_dialog = False
						lines_with_gaps.append(line)

		if fill_gaps:
			if not skip_save_dialog:
				op = sim_ou_nao(input_label="Gravar alterações e sair?")
				if op == 's':
					save_csv(table, filename)
					return table

		show_reference_cols = print_reference_cols
	
	if fill_gaps:
		save_csv(table, filename)
		print("Trabalho concluído...")
		return table
	else:
		print_list_of_dict_as_table(lines_with_gaps)



def print_list_of_dict_as_table(list_of_dicts, col_space=2):
	"""Imprime no console uma lista de dicionários como uma tabela em formato texto
	
	Arguments:
		list_of_dicts {list with dics inside} -- dicionários devem ter a mesma estrutura
	
	Keyword Arguments:
		col_space {int} -- espaçamento definido entre as colunas (default: {2})
	"""

	assert isinstance(list_of_dicts, list)
	assert isinstance(list_of_dicts[0], (dict, OrderedDict))

	fields = list(list_of_dicts[0].keys())
	fields_num = len(fields)

	col_size = []
	
	while fields_num:
		col_size.append(0)
		fields_num -= 1

	for line in list_of_dicts:
		col_idx_count = itertools.count()
		for col in fields:
			col_idx = next(col_idx_count)
			if len(line[col]) + col_space > col_size[col_idx]:
				col_size[col_idx] = len(line[col]) + col_space
	
	fields_size = list(zip(fields, col_size))

	output = []

	for line in list_of_dicts:

		output_line = ''
		for info in fields_size:
			output_line += line[info[0]].ljust(info[1])
		output.append(output_line)
	print_list(output)



def print_list(iterator):
	"""Imprime os elementos de uma lista
	
	Arguments:
		iterator {list|tuple|iterator} -- objeto de entrada
	"""
	
	for element in iterator:
		print(element)


def load_data_file(filename, file_folder=os.curdir, delimiter='\t', lineterminator='\n', filemimetype='csv'):
	"""Carrega arquivo de dados conforme o tipo do arquivo
	
	Arguments:
		filename {string} -- nome do arquivo
	
	Keyword Arguments:
		file_folder {string} -- local onde o arquivo se encontra (default: {os.curdir})
		delimiter {char} -- caractere delimitador de campo, para arquivos CSV ou de texto (default: '\t')
		lineterminator {char} -- caractere delimitador de linha (default: {'\n'})
		filemimetype {string} -- tipo do arquivo de entrada, pode ser 'csv'|'json'|'txt' (default: {'csv'})
	
	Returns:
		{table} -- retorna o conteúdo do arquivo alvo como uma tabela
	"""
	
	assert filemimetype in ('csv', 'json', 'txt'), "Os únicos valores válidos para 'filemimetype' são: 'csv', 'json' ou 'txt'"

	if filemimetype == 'csv':
		conteudo = load_full_csv(filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator)
	elif filemimetype == 'json':
		conteudo = load_json(filename, file_folder=file_folder)
	elif filemimetype == 'txt':
		conteudo = read_all_text_table_file(filename, file_folder=file_folder, delimiter=delimiter)
	
	return conteudo



def save_data_file(data, filename, file_folder=os.curdir, delimiter='\t', lineterminator='\n', filemimetype='csv'):

	assert filemimetype in ('csv', 'json', 'txt'), "Os únicos valores válidos para 'filemimetype' são: 'csv', 'json' ou 'txt'"

	if filemimetype == 'csv':
		save_csv(data, filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator)

	elif filemimetype == 'json':
		save_json(data, filename, file_folder=file_folder)

	elif filemimetype == 'txt':
		append_to_text_table_file(data, filename, file_folder=file_folder, delimiter=delimiter)



def load_data_file_fields():
	pass


def seek_for_lines(filename, col, value, file_folder=os.curdir, filemimetype="csv", delimiter='\t', lineterminator='\n', extract=False, show_data=True):
	"""Retorna ou exclui as linhas de um arquivo em que o 'valor' existe na coluna 'col'.
	
	Arguments:
		filename {string} -- nome do arquivo alvo
		value {string|int|float} -- valor que deve ser verificado
		col {string} -- coluna onde o valor pode ser encontrado
	
	Keyword Arguments:
		file_folder {string}-- local onde o arquivo está localizado (default: {os.curdir})
		filemimetype {string} -- tipo do arquivo de entrada pode ser 'csv'|'json'|'txt' (default: {'csv'})
		delimiter {string} -- delimitador de campo, para arquivos CSV (default: {'\t'})
		lineterminator {string} -- delimitador de fim de linha, para arquivos CSV (default: {'\n'})
		extract {bool} -- indica se as informações devem ser extraídas do arquivo original (default: {False})
		show_data {bool} -- indica se as informações encontradas devem ser retornadas ou não (default: {True})
	
	Returns:
		{list} -- retorna uma lista de dicionários que pode ser manipulada ou salva como CSV ou JSON
	"""
	
	assert all([isinstance(filename, str), isinstance(col, str)]), "Os argumentos 'filename' e 'col' devem ser do tipo 'str'"
	assert isinstance(value, (str, int, float)), "O argumento 'valor' deve ser de em dos tipos: 'str', 'int' ou 'float'"
	assert all([isinstance(extract, bool), isinstance(show_data, bool)]), "Os argumentos 'extract' e 'show_data' devem ser boleanos"

	conteudo = load_data_file(filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator, filemimetype=filemimetype)

	keep_this = []
	remove_that = []
	
	for line in conteudo:
		if line[col] == value:
			remove_that.append(line)
		else:
			keep_this.append(line)
	
	if extract:
		save_data_file(keep_this, filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator)
		new_filename = time.ctime().replace(' ','_') + "removed_lines_from_" + filename
		save_data_file(remove_that, new_filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator)		
	
	if show_data:
		print_list_of_dict_as_table(remove_that)
		return remove_that
	

def copy_col(filename, source_col, destination_col, file_folder=os.curdir, filemimetype="csv", delimiter='\t', lineterminator='\n', preserve_existent_value=True):
	"""Copia as informações de 'source_col' para 'destination_col', cria a coluna de destino caso ela não exista
	
	Arguments:
		filename {string} -- nome do arquivo alvo
		source_col {string|iterator} -- coluna de origem
		destination_col {string} -- coluna de destino
	
	Keyword Arguments:
		file_folder {string} -- local onde o arquivo 'filename' está (default: {os.curdir})
		filemimetype {string} -- tipo do arquivo de entrada pode ser 'csv'|'json'|'txt' (default: {'csv'})
		delimiter {string} -- delimitador de campo, para arquivos CSV (default: {'\t'})
		lineterminator {string} -- delimitador de fim de linha, para arquivos CSV (default: {'\n'})
		preserve_existent_value {bool} -- indica se o valor no destino deve ser mantido ou substituído (default: {True})
	"""

	"Copia o conteúdo de uma coluna alvo para uma coluna de destino se a célula do destino ainda não estiver preechida"

	conteudo = load_data_file(filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator)

	#Sunstituir por 'load_data_file_fields', quando implementado
	cols = load_csv_head(filename)

	save_file = False
	if destination_col in cols:
		for line in conteudo:
			if line[source_col] != '' and line[destination_col] == '':
				save_file = True
				line[destination_col] = line[source_col]
	else:
		for line in conteudo:
			line[destination_col] = ''
			if line[source_col] != '' and line[destination_col] == '':
				save_file = True
				line[destination_col] = line[source_col]		
	
	if save_file:
		print("Cópia efetuada... Gravando informações no arquivo...")
		save_data_file(conteudo, filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator, filemimetype=filemimetype)
	else:
		print("Não há o que alterar...")



#### Refatorar
def add_line(filename, refcols=[]):
	conteudo = load_full_csv(filename)
	cols = load_csv_head(filename)
	nova_linha = OrderedDict()
	for c in cols:
		v = input(c+": ")
		nova_linha[c] = v
		
	conteudo.append(nova_linha)
	save_csv(conteudo, filename)
	v = input("Adicionar outro? (s/n) ")
	if v == "s" or v == "S":
		add_line(filename)


#### Refatorar
def convert_csv_type(filename, old_delimiter, new_delimiter, old_lineterminator=os.linesep, new_lineterminator=os.linesep):
	conteudo = load_csv(filename, delimiter=old_delimiter, lineterminator=old_lineterminator)
	save_csv(conteudo, filename, delimiter=new_delimiter, lineterminator=new_lineterminator)


#### Refatorar


#### Refatorar
def listagem_cli(linhas_selecionadas, cols):
	visual_count = len(linhas_selecionadas)
	for linha in linhas_selecionadas:
		visual_nfo = ""
		w = 0
		li = ""
		linha_sem_quebra = True
		for col in cols:
			if linha.get(col[0]):
				li += linha[col[0]].ljust(col[1])
				if linha[col[0]].find(';') == -1:
					w += col[1]
				else:
					linha_sem_quebra = False
					lii = li.split(';')
					if len(lii) > 1:
						pri = True
						for i in lii:
							if pri == True:
								visual_nfo += i + os.linesep
								pri = False
							else:
								visual_nfo += "".ljust(w-1) + i + os.linesep
								yield visual_nfo
			else:
				li += "".ljust(col[1])

		
		if linha_sem_quebra == True:
			visual_nfo += li 
			yield visual_nfo
	
	yield "Total: {}".format(visual_count)


#### Refatorar
def listagem_json(linhas_selecionadas, cols):
	selected_cols = []
	for linha in linhas_selecionadas:
		l = {}
		for col in cols:
			l[col[0]] = linha[col[0]]
		selected_cols.append(l)
	return json.dumps(selected_cols, ensure_ascii=False, indent=4)


#### Verificar diferenças com 'listar_dicionario'
def show_dict_data(dictionary, output_filename=False):
	'''Apenas retorna as chaves e os valores de um dicionário no formato de lista, obedecendo o layout "KEY » VALUE". '''
	o = u''
	for key in dictionary.keys():
		o += key + ' »» ' + str(dictionary[key]) + '\n'
		if type(dictionary[key]) == dict:
			show_dict_data(dictionary[key])
	
	if output_filename:
		with open(output_filename, 'w') as f:# f = open(output_filename,'w')
			f.write(o)
	
	print(o)



#### Verificar diferenças com 'show_dict_data'
def listar_dicionario(dicionario, cols, marcadores=[], tipo_output='cli'):
	'''
	Lista o conteúdo de um dicionário retornando uma tabela/string com colunas solicitadas.
	O parametro 'cols' é uma lista de tuplas (t) em que t[0] é o 'id' e t[1] um número.
	O número de t[1] representa a largura a ser definida para coluna id ou t[0].
	Exibe ao final o total de elementos no dicionário.
	'''

	r = []
	for linha in dicionario:
		select_this = True
		if marcadores != []:
			select_this = False
			try:
				for m in marcadores:
					if m in linha['marcador']:
						select_this = True
			except KeyError:
				pass

		if select_this == True:
			r.append(linha)


	if tipo_output == 'cli':
		visual_nfo = listagem_cli(r, cols)
	
	elif tipo_output == 'json':
		visual_nfo = listagem_json(r, cols)

	return visual_nfo

#### Refatorar, transferir este recurso para 'py_functions_calculation'
def obter_frq_abs_from_list_of_dicts(list_of_dicts, key=False):
	'''
	Retorna os diferentes valores existentes na chave 'key' para o 'list_of_dicts'.
	Retorna o valor absoluto das ocorrências de valores.

	'''
	
	#Assuming every dict on the list has the same structure...
	fields = list_of_dicts[0].keys()


	if key != False:
		selected_cols = [key]
	else:
		selected_cols = select_ops(fields, 2)
	
	o = OrderedDict()
	
	for f in selected_cols:
		query_list = []
		for line in list_of_dicts:
			query_list.append(line[f])
		query_list_entries = set(query_list)
		for itens in query_list_entries:
			o[itens]=query_list.count(itens)
	return o


#### Refatorar, transferir este recurso para 'py_functions_calculation'
def obter_frq_abs_e_rel_from_list_of_dicts(list_of_dicts, key=False):
	n = len(list_of_dicts)
	r = obter_frq_abs_from_list_of_dicts(list_of_dicts, key)
	o = OrderedDict()
	for k in r.keys():
		o[k] = (r[k], float((r[k]/n)*100.00))
	return o

#### Refatorar, transferir este recurso para 'py_functions_calculation'
def make_complete_stat_from_list_of_dicts(list_of_dicts, printout=True):
	fields = list_of_dicts[0].keys
	o = OrderedDict()
	for field in fields:
		colcount = obter_frq_abs_e_rel_from_list_of_dicts(list_of_dicts, field)
		o[field] = colcount
	
	for k in o.keys():
		print("Variável: "+k)
		for v in o[k].keys():
			print("  » "+v, o[k][v])
		print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-="+os.linesep)


#### Refatorar
def map_values_in_list_of_dicts_col(list_of_dicts):
	'''
	Retorna os diferentes valores existentes na coluna 'col' para a 'tabela' do mysql selecionada.
	'''

	output = obter_frq_abs_from_list_of_dicts(list_of_dicts)
	output = output.keys()
	return output



#### Refatorar e integrar a um recurso de listagem seletiva...
def show_each_dict_in_block(list_of_dicts, print_fields, index_pos):
	'''
	Apresenta bloco de informações de um 'list_of_dicts'.
	Apenas os campos definidos em 'print_fields' serão retornados.
	A cada impressão o programa aquarda pelo comando para prosseguir.
	Elementos iniciais da lista podem ser ignorados definindo-se o local de inicio 'index_pos'.
	'''

	for i in list_of_dicts[index_pos:]:
		print_nfo = ""
		for f in print_fields:
			print_nfo += i[f].replace('/','') + os.linesep
		print(print_nfo)
		input("Pressione enter para continuar...")



def join_list_of_dicts_intersection(list_of_dicts1, list_of_dicts2, joint_key):
	'''
	Realiza a junção de dois dicionários distintos que compartilhem uma mesma chave/col.
	Retorna as linhas em que os valores da chave selecionada correspondem nos dois dicionários.
	'''

	output = []
	tmpdict = {}
	for row in list_of_dicts1:
		tmpdict[row[joint_key]] = row
	list_of_dicts2_cols = list_of_dicts2[0].keys()
	for other_row in list_of_dicts2:
		if other_row[joint_key] in tmpdict: #tmpdict.has_key(other_row[col]):
			joined_row = tmpdict[other_row[joint_key]]
			for colz in list_of_dicts2_cols:
				if colz != joint_key:
					joined_row[colz] = other_row[colz]
			output.append(joined_row)
	return output



def join_list_of_dicts_union(list_of_dicts1, list_of_dicts2, joint_key):
	'''
	Realiza a junção de dois dicionários distintos que compartilhem uma mesma chave/col.
	Retorna as linhas em que os valores da chave selecionada correspondem nos dois dicionários.
	'''

	output = []
	tmpdict = {}
	list_of_dicts1_cols = list_of_dicts1[0].keys()
	list_of_dicts2_cols = list_of_dicts2[0].keys()
	for row in list_of_dicts1:
		tmpdict[row[joint_key]] = row
	new_row_col = merge_lists(list_of_dicts1_cols,list_of_dicts2_cols)
	new_row_skell = OrderedDict()
	for col_name in new_row_col:
		new_row_skell[col_name]=""
	
	key_2_skip = []
	for other_row in list_of_dicts2:
		if other_row[joint_key] in tmpdict:
			key_2_skip.append(other_row[joint_key])
			joined_row = tmpdict[other_row[joint_key]]
			for colz in list_of_dicts2_cols:
				if colz != joint_key:
					joined_row[colz] = other_row[colz]
			output.append(joined_row)
		
	linhas_n_comuns = len(list_of_dicts1) + len(list_of_dicts1) - len(key_2_skip)
	tabela_linhas_n_comuns = []
	while linhas_n_comuns != 0:
		linha_inteira = copy(new_row_skell)
		tabela_linhas_n_comuns.append(linha_inteira)
		linhas_n_comuns -= 1
	
	tabela_linhas_n_comuns=[]
	
	for linha in list_of_dicts1:
		linha_inteira = copy(new_row_skell)
		if not linha[joint_key] in key_2_skip:
			for colz in list_of_dicts1_cols:
				try: linha_inteira[colz] = linha[colz]
				except: pass
			tabela_linhas_n_comuns.append(linha_inteira)

	for linha in list_of_dicts2:
		linha_inteira = copy(new_row_skell)
		if not linha[joint_key] in key_2_skip:
			for colz in list_of_dicts2_cols:
					linha_inteira[colz] = linha[colz]
			tabela_linhas_n_comuns.append(linha_inteira)
		
	final_output = merge_lists(tabela_linhas_n_comuns, output)
	return final_output




def cruzar_variaveis(list_of_dicts):
	arquivo_de_saida = input("Salvar resultado como...: ")
	limpar_tela()
	fields = list_of_dicts[0].keys()
	selected_cols = select_ops(fields, 2)
	selected_cols_len = len(selected_cols)
	print("Selecionadas: ", selected_cols, selected_cols_len)
	set_of_values = []
	while selected_cols_len != 0:
		col_values = []
		for line in list_of_dicts:
			col_values.append(line[selected_cols[selected_cols_len-1]])
		set_of_values.append(set(col_values))
		selected_cols_len -= 1
	print("Valores encontrados: ", set_of_values)
	o = OrderedDict()
	set_of_values_len = []
	for i in set_of_values:
		set_of_values_len.append(len(i))
	print("Número de valores diferentes: ", set_of_values_len)

	r = []
	if len(selected_cols) == 1:
		print("É necessário escolher mais de uma coluna para efetuar o cruzamento...")
	elif len(selected_cols) == 2:
		for lines in list_of_dicts:
			r.append(" e ".join([lines[selected_cols[0]],lines[selected_cols[1]]]))
	elif len(selected_cols) == 3:
		for lines in list_of_dicts:
			r.append(" e ".join([lines[selected_cols[0]],lines[selected_cols[1]],lines[selected_cols[2]]]))
	elif len(selected_cols) == 4:
		for lines in list_of_dicts:
			r.append(" e ".join([lines[selected_cols[0]],lines[selected_cols[1]],lines[selected_cols[2]],lines[selected_cols[3]]]))
	elif len(selected_cols) == 5:
		for lines in list_of_dicts:
			r.append(" e ".join([lines[selected_cols[0]],lines[selected_cols[1]],lines[selected_cols[2]],lines[selected_cols[3]],lines[selected_cols[4]]]))
	elif len(selected_cols) == 6:
		for lines in list_of_dicts:
			r.append(" e ".join([lines[selected_cols[0]],lines[selected_cols[1]],lines[selected_cols[2]],lines[selected_cols[3]],lines[selected_cols[4]],lines[selected_cols[5]]]))
	elif len(selected_cols) == 7:
		for lines in list_of_dicts:
			r.append(" e ".join([lines[selected_cols[0]],lines[selected_cols[1]],lines[selected_cols[2]],lines[selected_cols[3]],lines[selected_cols[4]],lines[selected_cols[5]],lines[selected_cols[6]]]))
	elif len(selected_cols) == 8:
		for lines in list_of_dicts:
			r.append(" e ".join([lines[selected_cols[0]],lines[selected_cols[1]],lines[selected_cols[2]],lines[selected_cols[3]],lines[selected_cols[4]],lines[selected_cols[5]],lines[selected_cols[6]],lines[selected_cols[7]]]))
	elif len(selected_cols) == 9:
		for lines in list_of_dicts:
			r.append(" e ".join([lines[selected_cols[0]],lines[selected_cols[1]],lines[selected_cols[2]],lines[selected_cols[3]],lines[selected_cols[4]],lines[selected_cols[5]],lines[selected_cols[6]],lines[selected_cols[7]],lines[selected_cols[8]]]))
	elif len(selected_cols) == 10:
		for lines in list_of_dicts:
			r.append(" e ".join([lines[selected_cols[0]],lines[selected_cols[1]],lines[selected_cols[2]],lines[selected_cols[3]],lines[selected_cols[4]],lines[selected_cols[5]],lines[selected_cols[6]],lines[selected_cols[7]],lines[selected_cols[8]],lines[selected_cols[9]]]))
	else:
		print("Quantidade máxima de cruzamentos atingida...")

	r_set = set(r)
	o = OrderedDict()
	n = len(r)

	for i in r_set:
		o[i] = (r.count(i), float((r.count(i)/n)*100))

	o_file_data = ''
	for i in o.keys():
		o_file_data += str(i) + "," + str(o[i][0]) + "," + str(o[i][1]) + os.linesep
	f = open(arquivo_de_saida, 'w')
	f.write(o_file_data)
	f.close()

	return o




def get_indexes(item, lista):
	'''
	Retorna os índices de um elemento em uma lista. Usado em listas que possuam elementos repitidos.
	'''

	loops = lista.count(item)
	r = []
	idx = 0
	while loops != 0:
		try:
			nidx = lista[idx:].index(item)
			r.append(nidx+idx)
			idx = nidx+1
			loops -= 1
		except ValueError:
			break
	return r



def diff_lists(a, b):
	'''Retorna os itens da lista "a" que não estão em "b".'''
	o = []
	for i in a:
		if i not in b:
			o.append(i)
	return o




def compare_lists(a, b, historical_analisis=False, listA_NAME='First', listB_NAME='Second'):
	'''
	Compara duas listas e retorna um dicionário que agrupa itens exclusivos e compartilhados.
	Se historical_analisis=True, apresenta uma única lista mostrando o que mudou na lista [b] em relação a [a].
	Os argumentos listA_NAME e listB_NAME permitem usar nomes específicos para as listas.
	'''
	o = {}
	if historical_analisis == True:
		#A segunda lista deve ser a mais nova para que os valores retornados sejam os mais atuais...
		o[u'mudou'] = diff_lists(b,a)
	else:
		o[u'onlyOn%s' % listA_NAME] = diff_lists(a,b)
		o[u'onlyOn%s' % listB_NAME] = diff_lists(b,a)
		o[u'shared'] = intersect_lists(a,b)
	return o




def diff_dicts(a, b, historical_analisis=True):
	'''
	Realiza a comparação entre dois dicionários retornando o que mudou no segundo [b] em relação ao primeiro [a].
	Se historical_analisis=False, retorna um dicionário agrupando itens exclusivos e compartilhados dessas listas.
	'''
	k = []
	for i in a.keys():
		k.append(i)
	k.sort()
	l1 = []
	l2 = []
	for i in k:
		l1.append((i, a[i]))
		l2.append((i, b[i]))
	o = compare_lists(l1, l2, historical_analisis)
	return o




def merge_lists(a, b):
	'''Retorna a lista de união, sem repetição de itens existentes em ambas as listas.'''
	o = []
	for i in b:
		o.append(i)
	for i in a:
		if i not in b:
			o.append(i)
	return o




def intersect_lists(a, b):
	'''Retorna a lista com itens comuns a partir de duas listas de entrada.'''
	o = []
	tl = merge_lists(a,b)
	for i in tl:
		if (i in a) and (i in b):
			o.append(i)
	return o



def strip_digits(s):
	r = s
	for i in digits:
		r = r.replace(i,'')
	return r


def strip_simbols(s):
	r = s
	for i in punctuation+"/":
		r = r.replace(i,"")
	return r

def strip_spaces(s):
	r = s
	for i in whitespace:
		r = r.replace(i,"")
	return r

def strip_chars(s):
	r = s
	for i in "abcdefghijklmnopqrstuvxz":
		r = r.replace(i,"")
	return r


def create_new_value_col_if_old_has_value(list_of_dicts, list_of_old_cols, interactive=True, script_descriptor=None):
	num_of_cols = len(list_of_old_cols)

	if (interactive == False) and (script_descriptor == None):
		if type(script_descriptor) != dict:
			print("Descritor não apresentado ou em formato inadequado...")
			exit()

	if num_of_cols == 1:

		old_col1 = list_of_old_cols[0]
		old_col1_values = []
		for line in list_of_dicts:
			if not line[old_col1] in old_col1_values:
				old_col1_values.append(line[old_col1])
		old_col1_values.sort()

		if interactive == True:
			print("Selecione os valores que deverão ser checados para disparar o gatilho de registro:")
			selected = select_ops(old_col1_values, 2)
			print("Defina o nome da nova coluna:")
			print("Cuidado! Se o nome definido for igual a un nome anteriormente existente, as informações anteriores dessa coluna serão sobrescritas:\n")
			new_col_name = input("$: ")
			print("Defina o valor que deverá ser registrado na nova coluna quando os valores selecionados forem encontrados: \n")
			new_value = input("$: ")
		else:
			selected = script_descriptor['valores_de_checagem'][list_of_old_cols[0]]
			new_col_name = script_descriptor['nome_da_nova_coluna']
			new_value = script_descriptor['valor_se_checagem_verdadeira']

		for line in list_of_dicts:
			if line.get(new_col_name) == None:
				line[new_col_name] = ""
			if line[old_col1] in selected:
				line[new_col_name] = new_value
	
	elif num_of_cols == 2:
	
		old_col1 = list_of_old_cols[0]
		old_col2 = list_of_old_cols[1]
		old_col1_values = []
		old_col2_values = []
	
		for line in list_of_dicts:
			if not line[old_col1] in old_col1_values:
				old_col1_values.append(line[old_col1])
			if not line[old_col2] in old_col2_values:
				old_col2_values.append(line[old_col2])
	
		old_col1_values.sort()
		old_col2_values.sort()

		if interactive == True:
			print("Selecione os valores que deverão ser checados para disparar o gatilho de registro na coluna {}:".format(list_of_old_cols[0]))
			selected_itens_col1 = select_ops(old_col1_values, 2)
			print("Selecione os valores que deverão ser checados para disparar o gatilho de registro na coluna {}:".format(list_of_old_cols[1]))
			selected_itens_col2 = select_ops(old_col2_values, 2)

			print("Defina o nome da nova coluna:")
			print("Cuidado! Se o nome definido for igual a un nome anteriormente existente, as informações anteriores dessa coluna serão sobrescritas:\n")
			new_col_name = input("$: ")

			print("Defina o valor que deverá ser registrado na nova coluna quando os valores selecionados forem encontrados: \n")
			new_value = input("$: ")
		else:
			selected_itens_col1 = script_descriptor['valores_de_checagem'][list_of_old_cols[0]]
			selected_itens_col2 = script_descriptor['valores_de_checagem'][list_of_old_cols[1]]
			new_col_name = script_descriptor['nome_da_nova_coluna']
			new_value = script_descriptor['valor_se_checagem_verdadeira']

		for line in list_of_dicts:
			if line.get(new_col_name) == None:
				line[new_col_name] = ""
			if (line[old_col1] in selected_itens_col1) and (line[old_col2] in selected_itens_col2):
				line[new_col_name] = new_value
	
	elif num_of_cols == 3:
		old_col1 = list_of_old_cols[0]
		old_col2 = list_of_old_cols[1]
		old_col3 = list_of_old_cols[2]
		old_col1_values = []
		old_col2_values = []
		old_col3_values = []

		if interactive == True:

			for line in list_of_dicts:
				if not line[old_col1] in old_col1_values:
					old_col1_values.append(line[old_col1])
				if not line[old_col2] in old_col2_values:
					old_col2_values.append(line[old_col2])
				if not line[old_col3] in old_col3_values:
					old_col3_values.append(line[old_col3])				

			old_col1_values.sort()
			old_col2_values.sort()
			old_col3_values.sort()

			print("Selecione os valores que deverão ser checados para disparar o gatilho de registro na coluna {}:".format(old_col1))
			selected_itens_col1 = select_ops(old_col1_values, 2)
			print("Selecione os valores que deverão ser checados para disparar o gatilho de registro na coluna {}:".format(old_col2))
			selected_itens_col2 = select_ops(old_col2_values, 2)
			print("Selecione os valores que deverão ser checados para disparar o gatilho de registro na coluna {}:".format(old_col3))
			selected_itens_col3 = select_ops(old_col3_values, 2)

			print("Defina o nome da nova coluna:")
			print("Cuidado! Se o nome definido for igual a un nome anteriormente existente, as informações anteriores dessa coluna serão sobrescritas:\n")
			new_col_name = input("$: ")

			print("Defina o valor que deverá ser registrado na nova coluna quando os valores selecionados forem encontrados: \n")
			new_value = input("$: ")
		else:
			selected_itens_col1 = script_descriptor['valores_de_checagem'][list_of_old_cols[0]]
			selected_itens_col2 = script_descriptor['valores_de_checagem'][list_of_old_cols[1]]
			selected_itens_col3 = script_descriptor['valores_de_checagem'][list_of_old_cols[2]]

			new_col_name = script_descriptor['nome_da_nova_coluna']
			new_value = script_descriptor['valor_se_checagem_verdadeira']

		count = 0
		for line in list_of_dicts:
			count += 1

			if line.get(new_col_name) == None:
				line[new_col_name] = ""

			if selected_itens_col1.find(line[old_col1]) != -1:
				if selected_itens_col2.find(line[old_col2]) != -1:
					if selected_itens_col3.find(line[old_col3]) != -1:

						print("Encontrada correspondência na linha: {} » {} ".format(count, line["NOME_ESTUDANTE"]))
						print("  ·", old_col1, "»» {} in {}".format(line[old_col1], selected_itens_col1))
						print("  ·", old_col2, "»» {} in {}".format(line[old_col2], selected_itens_col2))
						print("  ·", old_col3, "»» {} in {}".format(line[old_col3], selected_itens_col3))	
						print("")
						if line["NOME_ESTUDANTE"] == "Rodrigo Ramos de Lima":
							input()

						line[new_col_name] = new_value

		return list_of_dicts

	elif num_of_cols == 4:

		old_col1 = list_of_old_cols[0]
		old_col2 = list_of_old_cols[1]
		old_col3 = list_of_old_cols[2]
		old_col4 = list_of_old_cols[4]
		old_col1_values = []
		old_col2_values = []
		old_col3_values = []
		old_col4_values = []

		for line in list_of_dicts:
			if not line[old_col1] in old_col1_values:
				old_col1_values.append(line[old_col1])
			if not line[old_col2] in old_col2_values:
				old_col2_values.append(line[old_col2])
			if not line[old_col3] in old_col3_values:
				old_col3_values.append(line[old_col3])
			if not line[old_col4] in old_col4_values:
				old_col4_values.append(line[old_col4])								

		old_col1_values.sort()
		old_col2_values.sort()
		old_col3_values.sort()
		old_col4_values.sort()

		if interactive == True:
			print("Selecione os valores que deverão ser checados para disparar o gatilho de registro na coluna {}:".format(old_col1))
			selected_itens_col1 = select_ops(old_col1_values, 2)
			print("Selecione os valores que deverão ser checados para disparar o gatilho de registro na coluna {}:".format(old_col2))
			selected_itens_col2 = select_ops(old_col2_values, 2)
			print("Selecione os valores que deverão ser checados para disparar o gatilho de registro na coluna {}:".format(old_col3))
			selected_itens_col3 = select_ops(old_col3_values, 2)
			print("Selecione os valores que deverão ser checados para disparar o gatilho de registro na coluna {}:".format(old_col4))
			selected_itens_col4 = select_ops(old_col4_values, 2)		

			print("Defina o nome da nova coluna:")
			print("Cuidado! Se o nome definido for igual a un nome anteriormente existente, as informações anteriores dessa coluna serão sobrescritas:\n")
			new_col_name = input("$: ")

			print("Defina o valor que deverá ser registrado na nova coluna quando os valores selecionados forem encontrados: \n")
			new_value = input("$: ")
		else:
			selected_itens_col1 = script_descriptor['valores_de_checagem'][list_of_old_cols[0]]
			selected_itens_col2 = script_descriptor['valores_de_checagem'][list_of_old_cols[1]]
			selected_itens_col3 = script_descriptor['valores_de_checagem'][list_of_old_cols[2]]
			selected_itens_col4 = script_descriptor['valores_de_checagem'][list_of_old_cols[3]]			
			new_col_name = script_descriptor['nome_da_nova_coluna']
			new_value = script_descriptor['valor_se_checagem_verdadeira']

		for line in list_of_dicts:
			if line.get(new_col_name) == None:
				line[new_col_name] = ""
			if (line[old_col1] in selected_itens_col1) and (line[old_col2] in selected_itens_col2) and (line[old_col3] in selected_itens_col3) and (line[old_col4] in selected_itens_col4):
				line[new_col_name] = new_value
	return list_of_dicts


def create_new_value_col_from_script(script_instructions, input_file_info):

	'''
	output = input_file_info

	for line in output:
		line['CALOURO_SELECIONADO'] = ''
		if (line['P_EST'] == line['P_ING']) and (line['AES_GRUPO'] == 'Perfil'):
			line['CALOURO_SELECIONADO'] = 1
	
	return output

	'''
	tasks = script_instructions['analises']

	output = input_file_info

	for task in tasks:
		colunas_selecionadas = []
		for c in task['valores_de_checagem'].keys():
			colunas_selecionadas.append(c)
			output = create_new_value_col_if_old_has_value(output, colunas_selecionadas, interactive=False, script_descriptor=task)
	
	return output


def convert_list_to_cli_args(lista):
    o = '" "'.join(lista)
    o = '"' + o + '"'
    return o


def mk_randnum_seq(num):
	output = ''
	while num != 0:
		idx = randrange(len(digits))
		output += digits[idx]
		num -= 1
	return output


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
		


def limpar_tela(msg=None):
	os.system("clear")
	if msg != None:
		print(msg)



def render_cols(lista, n, idx=True, item_color=amarelo, warning_color=vermelho):
	larguras = []
	largura_max = None
	for item in lista:
		if largura_max == None:
			largura_max = len(item)
		elif len(item) > largura_max:
			largura_max = len(item)
	largura_max += 5

	line = ''
	num_of_cols = n
	for item in lista:
		if idx == True:
			if num_of_cols != 0:
				line += '{}: {}'.format(str(lista.index(item)), item_color(item)).ljust(largura_max)
		elif idx == False:
			if num_of_cols != 0:
				line += '{}'.format(item_color(item)).ljust(largura_max)
		else:
			print(warning_color("Argumento idx deve ser Boleano..."))
			raise TypeError
		
		num_of_cols -= 1
		if num_of_cols == 0:
			line += os.linesep
			num_of_cols = n

	print(line)

		

def gerar_console_menu(lista, cols=1, item_color=amarelo, warning_color=vermelho):
	o = ''
	n = 0
	if type(lista) == list:
		o = ''
		for item in lista:
			o += str(n) + ': ' + str(item_color(item)) + os.linesep
			n += 1
		if cols == 1:
			print(o)
		else:
			render_cols(lista, cols)
		return lista
	else:
		print(warning_color("O argumento precisa ser do tipo lista..."))
		raise TypeError



def input_num(label, default=0, label_color=branco, warning_color=vermelho):
	entry = False
	while entry != True:
		try:
			num = input('{} [{}]: '.format(label_color(label), label_color(default)))
			if num == '':
				num = float(default)
				break
			num = float(num)
			break
		except:
			print(warning_color('Resultado precisa ser numérico...'))
			entry = False
	return num

def write_to_file(s, target_file):
	with open(target_file, 'w') as f:
		f.write(s)

def read_from_file(target_file):
	with open(target_file) as f:
		return f.read()


def input_op(lista_de_opcoes_validas, input_label=False, label_color=branco, warning_color=vermelho):
	if input_num:
		print(label_color(input_label), label_color('[{}]').format("|".join(lista_de_opcoes_validas)))
		
	while True:
		op = input(label_color(('$: ')))
		if not op in lista_de_opcoes_validas:
			print(warning_color("Opção inválida! Selecione entre [{}].".format("|".join(lista_de_opcoes_validas))))
		else:
			return op



def convert_items_to_int(original_list):
	return [int(n) for n in original_list]


def read_input(input_label=False, default=False, dada_type='string', data_pattern=False, prompt="$: ", list_item_delimiter=',', waring_msg="Resposta inválida ou em formato inadequado...", clear_screen=False, label_color=branco, prompt_color=branco, warning_color=vermelho, callback=False, break_line=True):
	if clear_screen:
		limpar_tela()
		
	if input_label:
		if default: print(input_label + ' [{}]'.format(str(default)))
		else: print(input_label)
		

	while True:

		response = input(prompt_color(prompt))
		all_ok = False

		if not data_pattern:
			if dada_type == 'string':
				break
			
			elif dada_type == 'int':
				try:
					response = int(response)
					all_ok = True
				
				except ValueError: print(warning_color(waring_msg))
			
			elif dada_type == 'float':
				try: 
					response = float(response)
					all_ok = True
				
				except ValueError: print(warning_color(waring_msg))

			elif dada_type == 'list':
				try: 
					response = split_and_strip(response, list_item_delimiter)
					all_ok = True
				
				except ValueError: print(warning_color(waring_msg))


			if all_ok:
				break
			
		else:
			try:
				re.search(data_pattern, response).string
				break

			except AttributeError:
				print(warning_color(waring_msg))

	if break_line: print('')

	return response


def sim_ou_nao(input_label=False, clear_screen=False, label_color=branco, prompt_color=branco, warning_color=vermelho):
	return read_input(input_label=input_label, dada_type='string', data_pattern='[sn]', waring_msg="Responda 's' ou 'n'...", clear_screen=False, label_color=branco, prompt_color=branco, warning_color=vermelho, callback=False, break_line=True)



def pick_options(selection_list, input_label=False, number_of_cols=1, max_selection=1, sort_selection_list=False, clear_screen=False, label_color=branco, item_color=amarelo, warning_msg='Digite número(s) correspondente(s) às opções...', prompt='$: ', prompt_color=branco, warning_color=vermelho, return_index=False):
	if clear_screen:
		limpar_tela()

	if input_label:
		print(label_color(input_label))

	if sort_selection_list:
		selection_list.sort()

	op_list = gerar_console_menu(selection_list, number_of_cols, item_color=item_color)
	op = None

	while True:
		op = read_input(prompt_color=prompt_color, prompt=prompt, dada_type='list', waring_msg=warning_msg, warning_color=warning_color, break_line=False)
		op = convert_items_to_int(op)

		if len(op) <= max_selection:
			end_loop = []

			for option in op:
				end_loop.append(option in tuple(range(0,len(op_list))))
			
			if all(end_loop):
				break
		
		else:
			print(warning_color('Você selecionou muitos itens, selecione, no máximo {}...'.format(max_selection)))

	print('')
	if max_selection == 1:
		if return_index: return op[0]
		else: return op_list[op[0]]
	
	else:
		if return_index: return op
		else: return [op_list[idx] for idx in op]



def select_op(lista_de_selecao, col_num, sort_list=False, input_label=False, clear_screen=False, label_color=branco, item_color=amarelo, warning_color=vermelho, return_index=False):
	if clear_screen:
		limpar_tela()

	if input_label:
		print(label_color(input_label))

	if sort_list == True:
		lista_de_selecao.sort()

	op_list = gerar_console_menu(lista_de_selecao, col_num, item_color=item_color)
	op = None
	#while check_item_list(op,range(0,len(op_list))) != True:
	while not op in range(0,len(op_list)):
		try:
			op = input(label_color('$: '))
			if op[0] == ":":
				return op
			op = int(op)
		except:
			print(warning_color('Resultado precisa ser numérico...'))
	if return_index:
		return op
	return [op_list[op]]



def select_ops(lista_de_selecao, col_num, sort_list=False, input_label=False, clear_screen=False, label_color=branco, item_color=amarelo, warning_color=vermelho, return_index=False):
	'''
	select_ops(lista_de_selecao, col_num, sort_list=False) -> similar à "select_op", mas aceita mais de uma resposta.
	
	O campo "col_num" indica a quantidade de colunas a ser apresentada. Em definindo "sort_list" como True a lista original será reorganizada.
	'''
	if clear_screen:
		limpar_tela()

	if input_label:
		print(input_label)

	if sort_list == True:
		lista_de_selecao.sort()
	op_list = gerar_console_menu(list(lista_de_selecao), col_num)
	while True:
		op = interval_select(input(amarelo('$: ')))
		if op[0] == ":":
			return op
		try:
			selecao = []
			for i in op:
				if return_index:
					selecao.append(int(i))
				else:
					selecao.append(op_list[int(i)])
			break
		except IndexError:
			print('Opção inválida...')
	
	return selecao


def interval_select(selection_string):
	if selection_string[0] == ':':
		return selection_string
	else:
		selection_list = selection_string.replace(" ","").split(",")
		output = []
		for item in selection_list:
			try:
				if item.find('-') != -1:
					first_interval_item = int(item.split('-')[0])
					last_interval_item = int(item.split('-')[1])
					for n in range(first_interval_item, last_interval_item+1):
						output.append(n)
				else:
					output.append(int(item))
			except AttributeError:
				pass
		output.sort()
		return output


def append_index_do_dict(key, index_value, index_dict):
	'''It adds a key index on index_dict'''
	if index_dict.get(key) == None:
		index_dict[key] = [index_value]
	else:
		index_dict[key].append(index_value)
	return index_dict


def exhaust_generator_and_print(generator, count_lines=False):
	counter = itertools.count(start=1)
	for line in generator:
		if count_lines:
			print(next(counter), line)
		else:
			print(line)




def render_form_get_values(form_file, skip_q=[]):
	'''
	Renderiza as questões de um formulário JSON conforme a estrutura abaixo.
	Retorna um dicionário com as respostas.
	As chaves são definidas conforme o atributo 'id'.
	Os valores são resultado do input dos usuários.

	{
		"form_head": "Registro de atendimento",
		"info": "Intrumental para registro de atendimentos no âmbito do SPS/FUP",
		"form_questions":
		[
			{
				"enunciado": "Matrícula",
				"id": "identificador",
				"tipo": "text",
			},
			{
				"enunciado": "Tipo de atendimento",
				"id": "atd_t",
				"tipo": "radio",
				"alternativas" :
				[
					"Informação presencial",
					"Informação via telefone",
					...
				]            
			}
		]
	}	
	'''
	
	def priorizar_defaults(alternativas, defaults):
		contador = len(defaults)
		defaults_itens = []
		for i in defaults:
			defaults_itens.append(alternativas[i])
		idx = -1
		while contador != 0:
			item = defaults_itens[idx]
			alternativas.insert(0, alternativas.pop(alternativas.index(item)))
			contador -= 1
			idx -= 1
		return alternativas


	def ler_categorias(q_categorias):
		categorias_de_alternativas = []
		for a in q['alternativas'].keys():
			categorias_de_alternativas.append(a)
		categorias_de_alternativas.sort()
		categorias_de_alternativas.append("Criar outra(s) categoria(s)...")	
		return categorias_de_alternativas


	def ler_alternativas(q_alternativas, q_defaults):
		q_alternativas = priorizar_defaults(q_alternativas, q_defaults)
		return q_alternativas



	def adicionar_categorias_de_op_ao_form(q_categorias):
		while True:
			categoria = input(verde("\nIndique o nome da nova categoria: "))
			print("\nIndique as opções a serem inseridas...")
			ops = adicionar_op_ao_form([], None)
			q_categorias[categoria] = ops
			print("")
			print(verde("Adicionar outra categoria? [s|n]"))
			op = input_op(['s','n'])
			if op == 'n':
				break
		return q_categorias


	def adicionar_op_ao_form(q_spot, grupo_de_alternativas):
		outros_recem_listados = []
		if type(q_spot) != list:
			print(verde('À qual grupo a opção divergente pertence: '))
			selected_op = select_op(grupo_de_alternativas, 1)[0]
			if type(q_spot[selected_op]) == dict:
				grupo_de_alternativas = list(q_spot[selected_op].keys())
			else:
				grupo_de_alternativas = q_spot[selected_op]
			o = adicionar_op_ao_form(q_spot[selected_op], grupo_de_alternativas)
			for i in o:
				outros_recem_listados.append(i)
		else:
			while True:
				print("")
				outro_detalhes = input(verde('Especifique: '))
				outros_recem_listados.append(outro_detalhes)
				q_spot.append(outro_detalhes)
				q_spot.sort()
				print("")
				print(verde("Adicionar outra opção? [s|n]"))
				op = input_op(['s','n'])
				if op == 'n':
					break
		return outros_recem_listados


	def objective_question_handler(q):
		rewrite_form = False
		rebuild_form = False
		reescolher = False
		grupos_de_opcao = []
		grupos_de_alternativas = []

		print(verde(q['enunciado']))

		if q['tipo'] == 'radio':
			if type(q['alternativas']) == list:
#				if q.get('defaults'):
#					print(priorizar_defaults(q['alternativas'], q['defaults']))
					
				nfo[q['id']] = select_op(q['alternativas'], 1)
				if "Outro" in nfo[q['id']]:
					rebuild_form = True

		elif q['tipo'] == 'checkbox':
			if type(q['alternativas']) == list:
#				if q.get('defaults'):
#					print(priorizar_defaults(q['alternativas'], q['defaults']))

				nfo[q['id']] = select_ops(q['alternativas'], 1)
				if "Outro" in nfo[q['id']]:
					rebuild_form = True
			
			elif type(q['alternativas']) == dict:
				grupos_de_alternativas = ler_categorias(q['alternativas'])
				gopt = select_ops(grupos_de_alternativas, 1)

				if type(gopt) == str:
					return gopt

				if "Criar outra(s) categoria(s)..." in gopt:
					q['alternativas'] = adicionar_categorias_de_op_ao_form(q['alternativas'])
					print(q['alternativas'])
					reescolher = True

				if reescolher:
					print("")
					print("Agora selecione a opção desejada para que o registro seja efetuado...")
					grupos_de_alternativas = ler_categorias(q['alternativas'])
					gopt = select_ops(grupos_de_alternativas, 1)

				alternativas_efetivas = []

				for grp_op_key in gopt:
					grupos_de_opcao.append(grp_op_key)
					for op in q['alternativas'][grp_op_key]:
						if not op in alternativas_efetivas:
							alternativas_efetivas.append(op)
				alternativas_efetivas.sort()
				alternativas_efetivas.append("Outro")
				nfo[q['id']] = select_ops(alternativas_efetivas, 1) #Mod2
				if "Outro" in nfo[q['id']]:
					rebuild_form = True
				
		if rebuild_form:
			op_adicional = adicionar_op_ao_form(q['alternativas'], grupos_de_alternativas)
			nfo[q['id']].remove("Outro")
			nfo[q['id']] = merge_lists(nfo[q['id']], op_adicional)
			rewrite_form = True
		
		if rewrite_form == True:
			save_json(sort_dict(form), form_file)

		#print(nfo[q['id']])

		if type(nfo[q['id']]) == list:
			if len(nfo[q['id']]) > 1:
				nfo[q['id']] = ';'.join(nfo[q['id']])
			else:
				nfo[q['id']] = nfo[q['id']][0]

		print("")
		return (nfo[q['id']], rewrite_form)

	def create_trigger_file(form_trigger_file):
		form_triggers_info = {}
		form_triggers_info['external_registry_file'] = form['external_registry_file']
		form_triggers_info['q_groups'] = {}
		form_triggers_info['index_list'] = []
		for q in form['form_questions']:
			form_triggers_info['index_list'].append(q['id'])
			if q.get('trigger_skip'):
				form_triggers_info[q['id']] = {}
				form_triggers_info[q['id']]['trigger_skip'] = {}
				condicoes_in_form = q['trigger_skip'].split(';')
				condicoes_in_trigger_file = {}
				for c in condicoes_in_form:
					csplit = c.split('::')
					if condicoes_in_trigger_file.get(csplit[0]):
						condicoes_in_trigger_file[csplit[0]].append(csplit[1])
					else:
						condicoes_in_trigger_file[csplit[0]] = [csplit[1]]
				form_triggers_info[q['id']]['trigger_skip'] = condicoes_in_trigger_file
			
			if q.get('q_group'):
				if form_triggers_info['q_groups'].get(q['q_group']):
					form_triggers_info['q_groups'][q['q_group']].append(q['id'])
				else:
					form_triggers_info['q_groups'][q['q_group']] = [q['id']]
			else:
				if form_triggers_info['q_groups'].get('undefined_q_group'):
					form_triggers_info['q_groups']['undefined_q_group'].append(q['id'])
				else:
					form_triggers_info['q_groups']['undefined_q_group'] = [q['id']]


		save_json(form_triggers_info, form_triggers_file)
		return form_triggers_info

	
	def prompt_questions(nfo, q):
		skip_this = False
		print(q['id'])
		if form_triggers_info.get(q['id']):
			if form_triggers_info[q['id']].get('trigger_skip'):
				for t in form_triggers_info[q['id']]['trigger_skip'].keys():
					print("» "+t)
					try:
						if nfo[t] in form_triggers_info[q['id']]['trigger_skip'].get(t):
							skip_this = True
							if q.get('autofill'):
								nfo[q['id']] = q['autofill']
							break
					except KeyError:
						skip_this = True
						if q.get('autofill'):
							nfo[q['id']] = q['autofill']
						break



		if not skip_this:
			if q['id'] in skip_q:
				pass

			elif q['tipo'] == 'text':
				nfo[q['id']] = input("{}: ".format(verde(q['enunciado'])))
				print("")

			elif q['tipo'] == 'radio' or q['tipo'] == 'checkbox':
				try:
					q_response = objective_question_handler(q)
					nfo[q['id']] = q_response[0]
				except TypeError:
					pass
		else:
			if q.get('skip_to'):
				return q['skip_to']

		return nfo


	#
	# Before render each question, 'create_trigger_file' iterates over 'form_questions' once and collect
	# the info stored on 'trigger_skip' field to construct '.form_triggers-*' file on current user folder.
	#
	# The '.form_triggers-*' holds the rules for questions' condicional render. When a question is 
	# render if one of de previous responses maches the critirium writen on 'trigger_skip', que question
	# will be skipped.
	# 
	# The '.form_triggers-*' are created on users' folder to avoid colisions on multi user envirioment.
	#
	#

	form = load_json(form_file)
	form_triggers_file = getoutput('echo $HOME')+'/.form_triggers-'+form_file.split(os.sep)[-1].split('.')[0]
	form_triggers_info = create_trigger_file(form_triggers_file)
	
	#
	# The next loop will iterate over all questions defined on JSON form.
	# 
	# Actual responses will be stored on 'nfo' dict. Responses initialized by ':' will be
	# interpreted as commands.
	#

	nfo = OrderedDict()
	grp_nfo = {}
	grp_nfo_tag = ""
	grp_tag = ""
	max_idx = len(form['form_questions'])-1
	idx = 0
	grp_prompt_pass = False
	clean_up_keys = []

	while idx <= max_idx:
		print(amarelo("idx: {}".format(idx))) #used for debug
		q = form['form_questions'][idx]
		first_idx = False
		last_idx = False
		if q.get('q_group'):
			inside_q_group = True
			grp_tag=q['q_group']
			clean_up_keys.append(q['id'])
			first = form_triggers_info['q_groups'][q['q_group']][0]
			last = form_triggers_info['q_groups'][q['q_group']][-1]
			first_idx = form_triggers_info['index_list'].index(first)
			last_idx = form_triggers_info['index_list'].index(last)
			print(amarelo("first_qg_idx: {}".format(first_idx))) #used for debug
			print(amarelo("last_qg_idx: {}".format(last_idx))) #used for debug
		else:
			inside_q_group = False
		
		if (idx == first_idx) and inside_q_group == True:
			if grp_prompt_pass == False:
				print(verde("Inserir registro para ")+amarelo(q['q_group'])+verde("?"))
				resposta = select_op(["Sim", "Não"], 1)
				print("")
				if resposta == ['Não']:
					idx = last_idx+1
					inside_q_group = False

		grp_prompt_pass = False

		response = prompt_questions(nfo, q)
		
		#
		# This block of code checks the response and leads to diferent acctions deppending on the value
		# the 'try...except' block deals with skipped fields since q['id'] from sikiped fields are not 
		# writen or created on response dict.
		#
		# Responses that starts with ':', falowed by a negative or positive integer, skips the current
		# question and jumps to other based on the result of the calculation of the current question's
		# index plus the given integer. A positive integer implies jump to previous questions while a 
		# negative integer skips to the next. Skipping responses may interfirer on other tools, as 'mkrel'...
		#
		
		try:
			try:
				if response[q['id']][0] == ':':
					command = True
					idx = idx - (int(response[q['id']][1:]) + 1)
				command = False
			except IndexError:
				command = False
			
			if not command:
				if inside_q_group == True:
					print(vermelho("idx: {}".format(idx))) #used for debug
					print(vermelho("first_idx: {}".format(first_idx))) #used for debug
					if idx == first_idx:
						print('Criando registro...') #used for debug
						grp_nfo_tag = response[q['id']]
						grp_nfo[grp_nfo_tag] = OrderedDict()
					else:
						try:
							grp_nfo[grp_nfo_tag][q['id']] = response[q['id']]
						except KeyError:
							pass
				else:
					nfo = response
					
				if (idx == last_idx) and (inside_q_group == True):
					print(verde("Inserir registro adicional para ")+amarelo(q['q_group'])+verde("?"))
					resposta = select_op(["Sim", "Não"], 1)
					print("")
					if resposta == ['Sim']:
						idx = first_idx-1
						grp_prompt_pass = True
					else:
						nfo[grp_tag] = grp_nfo
						grp_nfo = OrderedDict()
						grp_tag = ""
		
		except KeyError: pass

		#
		# Increments the index to render next question. If index became greater 'max_idx', the form is over.
		#

		idx += 1

		if idx > max_idx:
			output = OrderedDict()
			for k in sorted(nfo.keys()):
				output[k] = nfo[k]
			for k in set(clean_up_keys):
				if output.get(k):
					del(output[k])
			break
		
	os.remove(form_triggers_file)

	try:
		return output
	except UnboundLocalError:
		return nfo

	
def lexical_list_join(lista):
    output = ""
    for item in lista:
        output += item
        if item == lista[-1]:
            pass
        elif item == lista[-2]:
            output += ' e '
        else:
            output += ', '
    return output


def sort_dict(dictionary):
	output = OrderedDict()
	for key in sorted(dictionary):
		if type(dictionary[key]) == dict:
			output[key] = sort_dict(dictionary[key])
		elif type(dictionary[key]) == list:
			output[key] = sort_questions_inner_dict(dictionary[key])
		else:
			output[key] = dictionary[key]
	return output


def sort_questions_inner_dict(list_of_dicts):
	output = []
	for dict_item in list_of_dicts:
		sorted_dict_item = OrderedDict()
		for k in sorted(dict_item, reverse=True):
			sorted_dict_item[k] = dict_item[k]
		output.append(sorted_dict_item)
	return output


def return_obj_from_dict(dictionary):
    class Obj:
        pass
    obj = Obj()

    for k, v in dictionary.items():
        setattr(obj, k, v)
    
    return obj

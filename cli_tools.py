#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# license: AGPL-3.0 
#


import sys
import itertools
import os
import uuid
import json
import csv
import tempfile
import heapq
import re
import time

from colored import fg, attr#, bg
from subprocess import getoutput
from random import randrange, randint
from string import whitespace, punctuation, digits, ascii_letters
from collections import OrderedDict#, Counter
from copy import copy


from decorators import clear_screen

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
		self._stack_size = self.size() - 1
		self._index = 0

	def __iter__(self):
		for element in self.stack:
			yield self.__next__()

	def __next__(self):
		if self._stack_size > -1:
			result = self.stack[self._stack_size]
			self._stack_size -=1
			return result
		self._stack_size = self.size() - 1

	def __len__(self):
		return len(self.stack)

	def __repr__(self):
		self._stack_size = self.size() - 1
		output = "top »» ["
		while self._stack_size > -1:
			if self._stack_size == 0:
				output += '"' + str(self.stack[self._stack_size]) + '"]'
			else:
				output += '"' + str(self.stack[self._stack_size]) + '", '
			self._stack_size -=1
		self._stack_size = self.size() - 1
		return output

	def push(self, item):
		self.stack.append(item)
		self._stack_size = self.size() - 1

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
		self._queue_size = self.size() - 1
		self._index = 0

	def __iter__(self):
		for element in self.queue:
			yield self.__next__()

	def __next__(self):
		if self._index < self._queue_size:
			result = self.queue[self._index]
			self._index += 1
			return result
		self._index = 0

	def __len__(self):
		return len(self.queue)


	def __repr__(self):
		output = str(self.queue).replace('[', 'init «« ').replace(']', ' «« end')
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

		


def create_col_labels(table, delimiter=False):
	"""Retorna um dicionário com os nomes das colunas e indexes de referência
	
	Arguments:
		num_of_cols {int} -- quantidade de colunas da tabela
		table {table} -- matrix 1xN ou string com valores separados pelo delimitador
	
	Keyword Arguments:
		use_delimiter {bool} -- utiliza o delimitador no caso da amostra de dados ser uma string com delimitador (default: {True})
		delimiter {str} -- o caractere/substring que demarca a separação das colunas (default: {'\t'})

	Returns:
		{list} -- retorna uma lista
	"""

	assert isinstance(table, (list, tuple, str)), "A tabela deve ser do tipo 'list', 'tuple' ou 'str'"

	if isinstance(table[0], str):
		assert delimiter != False, "O delimitador deve ser informado para tabelas com linhas em formato 'string'"
		values = split_and_strip(table[0], delimiter=delimiter)
		input(values)

	elif isinstance(table[0], (list, tuple)):
		values = table[0]

	output_label_list = []
		
	for value in values:
		label = read_input(input_label='Indique o nome da coluna que armazena o dado: {}'.format(value))
		output_label_list.append(label)
	
	return output_label_list


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

	if not isinstance(text, str):
		text = text[0]

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



def print_text_table_file(text_table_filename, count_lines=True, delimiter='\t', col_padding=2):
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
				op = input_yes_or_no(input_label="Gravar alterações e sair?")
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



def print_list(iterator, key=lambda x: x):
	"""Imprime os elementos de uma lista

	Arguments:
		iterator {list|tuple|iterator} -- objeto de entrada
	"""
	assert isinstance(iterator, (list, tuple)), "Argumento deve ser do tipo 'list' ou 'tuple'"
	assert callable(key), "Argumento 'key' deve ser uma função"

	for item in iterator:
		print(key(item))



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
	"""Função genérica para salvar dados, chama as funções específicas de escrita conforme o tipo de arquivo definido.
	
	Arguments:
		data {table|list_of_dicts} -- variável com os dados a serem inseridos.
		filename {string} -- nome do arquivo de destino.
	
	Keyword Arguments:
		file_folder {string} -- pasta onde o arquivo será gravado (default: {os.curdir})
		delimiter {str} -- delimitador de campo/colunas, necessário para arquivos 'txt' e 'csv' (default: {'\t'})
		lineterminator {str} -- caractere de final de linha (default: {'\n'})
		filemimetype {str} -- extensão do arquivo de entrata (default: {'csv'})
	"""
	assert filemimetype in ('csv', 'json', 'txt'), "Os únicos valores válidos para 'filemimetype' são: 'csv', 'json' ou 'txt'"

	if filemimetype == 'csv':
		save_csv(data, filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator)

	elif filemimetype == 'json':
		save_json(data, filename, file_folder=file_folder)

	elif filemimetype == 'txt':
		append_to_text_table_file(data, filename, file_folder=file_folder, delimiter=delimiter)



def load_data_file_fields(filemimetype):

	assert filemimetype in ('csv', 'json', 'txt'), "Os únicos valores válidos para 'filemimetype' são: 'csv', 'json' ou 'txt'"

	if filemimetype == 'csv':
		pass

	elif filemimetype == 'json':
		pass

	elif filemimetype == 'txt':
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



def new_line_on_csv_file(filename, file_folder=os.curdir, translator={}, delimiter='\t', lineterminator='\n'):
	"""Adiciona valores em um arquivo CSV coluna à coluna. Se houver um dicionário como argumento 'translator', o nome das colunas poderão ser ampliados como questões de um formulário.
	
	Arguments:
		filename {string} -- nome do arquivo de dados em que a linha deve ser inserida
	
	Keyword Arguments:
		file_folder {string} -- nome da pasta onde o arquivo está localizado (default: {os.curdir})
		translator {dict} -- arquivo para exibição/explicação detalhada das colunas (default: {{}})
		delimiter {string} -- delimitador de campo do arquivo CSV (default: {'\t'})
		lineterminator {string} -- delimitador de linha (default: {'\n'})
	"""
	
	while True:
		conteudo = load_full_csv(filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator)
		columms = load_csv_head(filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator)
		nova_linha = OrderedDict()

		for col in columms:
			if translator.get(col):
				new_value = read_input(input_label=translator[col])
			else:
				new_value = read_input(input_label=col)
			nova_linha[col] = new_value
			
		conteudo.append(nova_linha)

		save_csv(conteudo, filename, file_folder=file_folder)

		op = input_yes_or_no(input_label="Adicionar outro? (s/n)")
		if op == "n": break



def convert_csv_type(filename, old_delimiter, new_delimiter, file_folder=os.curdir, old_lineterminator=os.linesep, new_lineterminator=os.linesep):
	"""Converte os tipos de delimitadores de campo e linhas de um arquivo CSV.
	
	Arguments:
		filename {string} -- nome do arquivo CSV que será modificado
		old_delimiter {string} -- antigo delimitador de campo
		new_delimiter {string} -- novo delimitador de campo
	
	Keyword Arguments:
		old_lineterminator {string} -- antigo delimitador de linha (default: {os.linesep})
		new_lineterminator {string} -- novo delimitador de linha (default: {os.linesep})
	"""
		
	conteudo = load_csv(filename, delimiter=old_delimiter, lineterminator=old_lineterminator)
	save_csv(conteudo, filename, delimiter=new_delimiter, lineterminator=new_lineterminator)



def print_dict(dictionary, indent=0, indent_incrementation=3):
	"""Imprimie o conteúdo de um dicionário na tela
	
	Arguments:
		dictionary {dict|OrderedDict} -- dicionário a ser impresso
	
	Keyword Arguments:
		indent {int} -- valor inicial de edentação da raiz da árvore (default: {0})
		indent_incrementation {int} -- valor a ser incrementada a cada novo nó (default: {3})
	"""
	
	
	for key, value in dictionary.items():
		if isinstance(value, (dict, OrderedDict)):
			incremented_indent = indent + indent_incrementation
			print(''.ljust(indent), key, ':')
			print_dict(value, indent=incremented_indent, indent_incrementation=indent_incrementation)
		else:
			print(''.ljust(indent), key, ':', value)
		


def check_table_atributes(table, select=False, delimiter=False):
	if isinstance(table[0], dict):
		fields = list(table[0].keys())
		table_data = table
		line_type = 'dict'

	elif isinstance(table[0], str):
		assert delimiter != False
		fields = split_and_strip(table, delimiter)
		print_list(fields)
		op = input_yes_or_no(input_label="Estes valores são os nomes corretos das colunas?")
		if op == 'n': 
			fields = create_col_labels([fields], delimiter=delimiter)
			table_data = table
		else:
			table_data = table[1:]
		line_type = 'str'

	else:
		print_list(table[0])
		op = input_yes_or_no(input_label="Estes valores são os nomes corretos das colunas?")
		if op == 'n':
			fields = create_col_labels(table, delimiter=delimiter)
			table_data = table
		else:
			fields = table[0]
			table_data = table[1:]
		line_type = 'list/tuple'

	fields_index_map = create_line_index(fields)

	selected_cols = fields
	if select:
		selected_cols = pick_options(fields, input_label="Selecione as colunas que devem ser tabuladas", max_selection=len(fields))


	return table_data, line_type, selected_cols, fields_index_map



@clear_screen
def print_table_line_by_line(iterator, initial_index=0, delimiter=False, select=False):
	"""Apresenta as informações de uma tabela bloco por bloco.
	
	Arguments:
		iterator {table} -- massa e dados
	
	Keyword Arguments:
		initial_index {int} -- posição/linha inicial a ser apresentada (default: {0})
		delimiter {bool} -- delimitador de campo (default: {False})
		select {bool} -- ativa/desativa seleção de colunas (default: {False})
	"""
	assert isinstance(iterator, (list, tuple))
	assert isinstance(iterator[0], (list, tuple, dict, str))
	
	@clear_screen
	def show_info_block(line_type):
		if line_type == 'str':
			for col in selected_cols:
				print(col, ":", iterator_data[idx].split(delimiter)[fields_index_map[col]])
			input("Pressione enter ver a linha seguinte...")
		
		elif line_type == 'dict':
			for col in selected_cols:
				print(col, ":", iterator_data[idx][col])
			input("Pressione enter ver a linha seguinte...")

		elif line_type == 'list/tuple':
			for col in selected_cols:
				print(col, ":", iterator_data[idx][fields_index_map[col]])
			input("Pressione enter ver a linha seguinte...")

	iterator_data, line_type, selected_cols, fields_index_map = check_table_atributes(iterator, select=select, delimiter=delimiter)

	for idx in range(initial_index, len(iterator_data)):
		show_info_block(line_type)




def table_junction(table1, table2, junction_col, select=False, delimiter=False):
	"""Cria uma tabela a partir da união duas tabelas em que respostas da coluna selecionada coincidam
	
	Arguments:
		table1 {table} -- variável com os dados da tabela 1
		table2 {table} -- variável com os dados da tabela 2
		junction_col {string} -- coluna de referência para junção
	
	Keyword Arguments:
		select {bool} -- esta opção permite selecionar as colunas a serem cruzadas (default: {False})
		delimiter {bool} -- opção necessária quando as lihas da tabela forem strings de texto com delimitadores (default: {False})
	
	Returns:
		{list_of_dicts} -- lista de dicionários para fácil conversão em CSV ou JSON
	"""
	
	table1_data, table1_line_type, table1_selected_cols, table1_fields_index_map = check_table_atributes(table1, select=select, delimiter=delimiter)
	table2_data, table2_line_type, table2_selected_cols, table2_fields_index_map = check_table_atributes(table2, select=select, delimiter=delimiter)

	output = []
	tmpdict = {}

	for idx in range(0, len(table1_data)):
		if table1_line_type == 'dict':
			tmpdict[table1_data[idx][junction_col]] = table1_data[idx]

		elif table1_line_type == 'str':
			converted_line = {}
			for col in table1_selected_cols:
				converted_line[col] = table1_data[idx].split(delimiter)[table1_fields_index_map[col]]
			tmpdict[converted_line[junction_col]] = converted_line
			
		elif table1_line_type == 'list/tuple':
			converted_line = {}
			for col in table1_selected_cols:
				converted_line[col] = table1_data[idx][table1_fields_index_map[col]]
			tmpdict[converted_line[junction_col]] = converted_line


	for idx in range(0, len(table2_data)):
		if table2_line_type == 'dict':
			if table2_data[idx][junction_col] in tmpdict:
				joined_line = tmpdict[table2_data[idx][junction_col]]
				for col in table2_selected_cols:
					if col != junction_col:
						joined_line[col] = table2_data[idx][col]
				output.append(joined_line)

		elif table2_line_type == 'str':
			converted_line = {}
			for col in table2_selected_cols:
				converted_line[col] = table2_data[idx].split(delimiter)[table2_fields_index_map[col]]
			
			if converted_line[junction_col] in tmpdict:
				joined_line = tmpdict[converted_line[junction_col]]
				for col in table2_selected_cols:
					if col != junction_col:
						joined_line[col] = converted_line[col]
				output.append(joined_line)

		elif table2_line_type == 'list/tuple':
			converted_line = {}
			for col in table2_selected_cols:
				converted_line[col] = table2_data[idx][table2_fields_index_map[col]]
			
			if converted_line[junction_col] in tmpdict:
				joined_line = tmpdict[converted_line[junction_col]]
				for col in table2_selected_cols:
					if col != junction_col:
						joined_line[col] = converted_line[col]
				output.append(joined_line)
			
	return output



def table_merge(list_of_dicts1, list_of_dicts2, joint_key):
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




def cross_table_values(filename, overwrite_file=False, file_folder=os.curdir, delimiter='\t', lineterminator='\n'):
	"""Esta função combina os valores de duas ou mais colunas para criar uma nova coluna com os valores combinados
	
	Arguments:
		filename {string} -- arquivo CSV alvo.
	
	Keyword Arguments:
		overwrite_file {bool} -- indica se o arquivo original deve ser sobregravado (default: {False})
		file_folder {string} -- pasta onde o arquivo alvo está (default: {os.curdir})
		delimiter {str} -- delimitador de campo (default: {'\t'})
		lineterminator {str} -- delimitador de linha (default: {'\n'})
	"""

	assert isinstance(filename, str)
	assert isinstance(overwrite_file, bool)

	if not overwrite_file:
		output_filename = read_input(input_label="Salvar resultado como")
	else:
		output_filename = filename

	table = load_full_csv(filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator)

	if isinstance(table[0], dict):
		fields = list(table[0].keys())
		selected_cols = pick_options(fields, input_label="Selecione colunas que devem ser cruzadas", number_of_cols=1, max_selection=len(fields))
		new_col_name = read_input(input_label="Nome da nova coluna a ser criada")
		for line in table:
			combined_data = []
			for col in selected_cols:
				combined_data.append(line[col])
			combined_data = lexical_list_join(combined_data)
			line[new_col_name] = combined_data

	save_csv(table, filename=output_filename, file_folder=file_folder)



def simplify_table_values(filename, overwrite_file=False, file_folder=os.curdir, delimiter='\t', lineterminator='\n'):
	"""Simplifica os valores de uma determinada coluna pela substituição de um ou mais respostas anteriores por respostas arbitrárias definidas pelo analista
	
	Arguments:
		filename {string} -- arquivo alvo que terá as informações manipuladas
	
	Keyword Arguments:
		overwrite_file {bool} -- indica se o arquivo original deve ser substituído (default: {False})
		file_folder {string} -- local onde o arquivo original está (default: {os.curdir})
		delimiter {str} -- delimitador de campo (default: {'\t'})
		lineterminator {str} -- delimitador de linha (default: {'\n'})
	"""

	def map_values(selected_col):
		mapped_values = {}
		for line in table:
			if not mapped_values.get(line[selected_col]):
				mapped_values[line[selected_col]] = True
		return list(mapped_values.keys())


	def conversion_rule(mapped_values):
		conversion_dict = {}
		while True:
			new_value = read_input(input_label="Indique o valor que deverá substituir respostas anteriormente existentes")
			selected_values = pick_options(mapped_values, input_label="Selecione os valores a serem substituídos", number_of_cols=1, max_selection=len(mapped_values))
			for v in selected_values:
				mapped_values.remove(v)
				conversion_dict[v] = new_value
			if len(selected_values) > 0:
				op = input_yes_or_no(input_label="Simplificar outros valores? (s/n)")
				if op == 'n': 
					for v in mapped_values:
						conversion_dict[v] = v
					break
		return conversion_dict

	assert isinstance(filename, str)
	assert isinstance(overwrite_file, bool)

	if not overwrite_file:
		output_filename = read_input(input_label="Salvar resultado como")
	else:
		output_filename = filename

	table = load_full_csv(filename, file_folder=file_folder, delimiter=delimiter, lineterminator=lineterminator)

	if isinstance(table[0], dict):
		fields = list(table[0].keys())
		selected_col = pick_options(fields, input_label="Selecione a colunas que devem ter os valores simplificados", number_of_cols=1, max_selection=1)
		mapped_values = map_values(selected_col)
		conversion_dict = conversion_rule(mapped_values)
		new_col_name = read_input(input_label="Nome da nova coluna a ser criada")

		for line in table:
			line[new_col_name] = conversion_dict[line[selected_col]]

	save_csv(table, filename=output_filename, file_folder=file_folder)




def get_indexes(item, iterator):
	"""Retorna os indices de um dado elemento em uma lista/tupla

	Arguments:
		item {string} -- elemento a ser pesquisado
		iterator {list|tuple} -- iterador onde o elemento será pesquisado

	Returns:
		{tuple} - tupla com os indices onde o elemento solicitado está
	"""


	counter = itertools.count()
	output = []
	for element in iterator:
		idx = next(counter)
		if element == item: output.append(idx) 
	return tuple(output)



def return_longest_then_shortest_list(first_list, second_list):
	if len(first_list) >= len(second_list):
		longuest = first_list.copy()
		shortest = second_list

	elif len(first_list) < len(second_list):
		longuest = second_list.copy()
		shortest = first_list

	return longuest, shortest


def diff_lists(first_list, second_list):
	"""Retorna os itens da lista "a" que não estão em "b".
	
	Arguments:
		first_list {list|tuple} -- primeiro iterador 
		second_list {list|tuple} -- segundo iterador 
	
	Returns:
		{list} -- retorna uma lista com os elementos existentes apenas na primeira lista
	"""

	second_list_sorted = second_list.copy()
	second_list_sorted.sort()

	output = []
	for item in first_list:
		if not bisect_search(item, second_list_sorted):
			output.append(item)
	return output




def compare_lists(first_list, second_list, historical_analisis=False, first_list_dict_label='First', second_list_dict_label='Second'):
	"""Compara duas listas e retorna um dicionário que agrupa itens exclusivos e compartilhados.
	
	Arguments:
		first_list {list|tuple} -- primeiro iterador 
		second_list {list|tuple} -- segundo iterador 
	
	Keyword Arguments:
		historical_analisis {bool} -- apresenta uma única lista mostrando o que mudou na lista [b] em relação a [a] (default: {False})
		first_list_dict_label {str} -- [description] (default: {'First'})
		second_list_dict_label {str} -- [description] (default: {'Second'})
	
	Returns:
		[type] -- [description]
	"""
	'''
	
	Se historical_analisis=True, apresenta uma única lista mostrando o que mudou na lista [b] em relação a [a].
	Os argumentos first_list_dict_label e second_list_dict_label permitem usar nomes específicos para as listas.
	'''
	output = {}

	if historical_analisis == True:
		#A segunda lista deve ser a mais nova para que os valores retornados sejam os mais atuais...
		output[u'mudou'] = diff_lists(second_list, first_list)

	else:
		output[u'onlyOn%s' % first_list_dict_label] = diff_lists(first_list, second_list)
		output[u'onlyOn%s' % second_list_dict_label] = diff_lists(second_list, first_list)
		output[u'shared'] = intersect_lists(first_list, second_list)

	return output



def diff_dicts(first_dict, second_dict):
	"""Compara dois dicionários e retorna os que mudou do segundo em relação ao primeiro
	
	Arguments:
		first_dict {dict} -- primeiro dicionário
		second_dict {dict} -- segundo dicionário
	
	Returns:
		{list} -- retorna uma lista com o que mudou
	"""

	l1 = [": ".join(pair) for pair in first_dict.items()]
	l2 = [": ".join(pair) for pair in second_dict.items()]

	output = compare_lists(l1, l2, historical_analisis=True)

	return output




def merge_lists(first_list, second_list):
	"""Une duas listas assumindo que não devem haver quaisquer itens repetidos nelas
	
	Arguments:
		first_list {list} -- [description]
		second_list {list} -- [description]
	
	Returns:
		{list} -- lista combinada sem repetição de elementos entre a primeira e a segunda lista
	"""

	longuest, shortest = return_longest_then_shortest_list(first_list, second_list)

	longuest.sort()

	for item in shortest:
		if not bisect_search(item, longuest):
			longuest.append(item)
	
	return longuest




def intersect_lists(first_list, second_list):
	"""Retorna a lista com itens comuns a partir de duas listas de entrada.
	
	Arguments:
		first_list {list} -- primeira lista de entrada
		second_list {list} -- segunda lista
	
	Returns:
		{list} -- retorna uma sublista com elementos comuns
	"""

	longuest, shortest = return_longest_then_shortest_list(first_list, second_list)

	longuest.sort()

	output = []

	for item in shortest:
		if bisect_search(item, longuest):
			output.append(item)

	return output



def convert_list_to_cli_args(iterator):
	"""Converte uma iterator de elementos em uma string de argumentos do shell
	
	Arguments:
		iterator {list|tuple} -- lista de entrada
	
	Returns:
		{string} -- retorna uma string de argumentos encapsulados em '"'.
	"""
	
	iterator_checked = [str(element) for element in iterator]
	o = '" "'.join(iterator_checked)
	o = '"' + o + '"'
	return o




def mk_random_pass(lenght, pass_type='alpha-numeric'):
	"""Cria uma sequência 'aleatória' para ser utilizada como senha
	
	Arguments:
		lenght {int} -- comprimento da saída
	
	Keyword Arguments:
		pass_type {str} -- tipo de caracteres que podem ser utilizados (default: {'alpha-numeric'})
	
	Returns:
		{string} -- sequencia de caracteres aleatória conforme regra definida
	"""

	def pick_one_from(string):
		idx = randrange(len(string))
		return string[idx]

	output = ''

	while lenght != 0:
		if pass_type == 'numeric':
			output += pick_one_from(digits)

		elif pass_type == 'alphabetic':
			output += pick_one_from(ascii_letters)

		elif pass_type == 'alpha-numeric':
			output += pick_one_from(digits+ascii_letters)
			
		elif pass_type == 'alpha-numeric+':
			output += pick_one_from(digits+ascii_letters+punctuation)

		lenght -= 1

	return output



def render_selection_items(lista, n, item_color=amarelo, warning_color=vermelho):
	"""Imprime um campo de opçõe numeradas para ser usado em perguntas fechadas
	
	Arguments:
		lista {list} -- lista de opções/respostas possíveis
		n {int} -- número de colunas
	
	Keyword Arguments:
		item_color {lambda} -- função definidora da cor de saída (default: {amarelo})
		warning_color {lambda} -- função definidora da cor de saída (default: {vermelho})
	"""
	
	assert isinstance(lista, (list, tuple))
	assert isinstance(n, int)

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
		if num_of_cols != 0:
			line += '{}: {}'.format(str(lista.index(item)), item_color(item)).ljust(largura_max)
		
		num_of_cols -= 1
		if num_of_cols == 0:
			line += os.linesep
			num_of_cols = n

	print(line)
	return lista



def write_to_file(s, filename, file_folder=os.curdir):
	"""Cria o arquivo alvo e escreve a string 's' nele. Se o arquivo existir, o conteúdo será apagado.
	
	Arguments:
		s {str} -- informação a ser escrita
		target_file {str} -- [description]

	Keyword Arguments:
		file_folder {string} -- pasta onde o arquivo está localizado (default: {os.curdir})
	"""
	with open(file_folder + os.sep + filename, 'w') as f:
		f.write(s)



def read_from_file(filename, file_folder=os.curdir):
	"""Lê o conteúdo de um arquivo de texto alvo
	
	Arguments:
		filename {string} -- nome do arquivo alvo
	
	Keyword Arguments:
		file_folder {string} -- pasta onde o arquivo está localizado (default: {os.curdir})
	
	Returns:
		{string} -- conteúdo do arquivo
	"""

	with open(filename) as f:
		return f.read()




def convert_items_to_int(original_list):
	"""Converte os elementos da lista fornecida em inteiros, elementos precisam ser conversíveis...
	
	Arguments:
		original_list {list} -- lista de números em formato string
	
	Returns:
		[type] -- [description]
	"""

	assert isinstance(original_list[0], (str, float, int))

	return [int(n) for n in original_list]



def read_input(input_label=False, default=False, dada_type='string', data_pattern=False, prompt="$: ", list_item_delimiter=',', waring_msg="Resposta inválida ou em formato inadequado...", clear_screen=False, label_color=branco, prompt_color=branco, warning_color=vermelho, callback=False, break_line=True):
	"""Recebe as informações fornecidas pelo teclado e converte conforme o dado conforme o tipo definido
	
	Keyword Arguments:
		input_label {string} -- enunciado do campo input (default: {False})
		default {value} -- valor a ser apresentado como padrão (default: {False})
		dada_type {str} -- string indicativa do tipo de dado a ser recebido:
		    » string: campo textual (default: {'string'})
			» int: número inteiro
			» float: número real
			» list: lista de elementos
			» date-br: data no formato brasileiro DD/MM/AAAA
			» date-us: data no formato norte-americano MM/DD/AAAA
			» date: data no formato internacional AAAA-MM-DD
		data_pattern {regex} -- expressão regular de validação (default: {False})
		prompt {str} -- estilo do prompt do input (default: {"$: "})
		list_item_delimiter {str} -- delimitador de lista utilizado para conversão da resposta em elementos (default: {','})
		waring_msg {str} -- mensagem de atenção (default: {"Resposta inválida ou em formato inadequado..."})
		clear_screen {bool} -- indica se a tela deve ser limpa antes de renderizar o input (default: {False})
		label_color {[type]} -- cor do enunciado do campo input  (default: {branco})
		prompt_color {[type]} -- cor do prompt (default: {branco})
		warning_color {[type]} -- cor do texto de aviso (default: {vermelho})
		callback {lambda} -- função de retorno que deverá ser executada ao final das intruções  (default: {False})
		break_line {bool} -- indica a necessidade de incluir quebra de linha após a seleção (default: {True})
	
	Returns:
		{string|int|float...} -- retorna o dado inserido no formato desejado...
	"""
	
	if clear_screen:
		clear()
		
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

			elif dada_type == 'date':
				pass

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


def input_yes_or_no(input_label=False, clear_screen=False, label_color=branco, prompt_color=branco, warning_color=vermelho):
	"""Utiliza 'read_input' para fazer uma pergunta de resposta binária sim/não
	
	Keyword Arguments:
		input_label {string} -- enunciado a ser presentado (default: {False})
		clear_screen {bool} -- indica se a tela deve ser apagada antes de apresentar a questão (default: {False})
		label_color {[type]} -- cor do enunciado da questão (default: {branco})
		prompt_color {[type]} -- cor do prompt de resposta (default: {branco})
		warning_color {[type]} -- cor da mensagem de aviso (default: {vermelho})
	
	Returns:
		{string} -- retorna 's' ou 'n'
	"""
	return read_input(input_label=input_label, dada_type='string', data_pattern='[sn]', waring_msg="Responda 's' ou 'n'...", clear_screen=False, label_color=branco, prompt_color=branco, warning_color=vermelho, callback=False, break_line=True)



def clear():
	if sys.platform == 'win32': os.system('cls')
	else: os.system('clear')



def pick_options(selection_list, input_label=False, number_of_cols=1, max_selection=1, sort_selection_list=False, clear_screen=False, label_color=branco, item_color=amarelo, warning_msg='Digite número(s) correspondente(s) às opções...', prompt='$: ', prompt_color=branco, warning_color=vermelho, return_index=False, ensure_list_output=False):
	"""[summary]
	
	Arguments:
		selection_list {list} -- lista com opções fechadas para serem selecionadas
	
	Keyword Arguments:
		input_label {bool} -- enunciado que deverá ser apresentado para a questão (default: {False})
		number_of_cols {int} -- nomero de colunas a ser impressa (default: {1})
		max_selection {int} -- numero máximo de elementos que podem ser selecionados (default: {1})
		sort_selection_list {bool} -- indica se a lista deve ser ordenada antes de ser impressa (default: {False})
		clear_screen {bool} -- indica se a tela deve ser limpa antes da questão ser impressa (default: {False})
		label_color {[type]} -- cor do enunciado (default: {branco})
		item_color {[type]} -- cor dos itens (default: {amarelo})
		warning_msg {str} -- conteúdo da mensagem de atenção (default: {'Digite número(s) correspondente(s) às opções...'})
		prompt {str} -- formato do prompt (default: {'$: '})
		prompt_color {[type]} -- cor do prompt (default: {branco})
		warning_color {[type]} -- cor da mensagem de alerta (default: {vermelho})
		return_index {bool} -- indica se a função deve retornar o elemento selecionado ou o seu index (default: {False})
	
	Returns:
		{string|list} -- retorna a string do elemento selecionado ou uma lista quando mais elementos são escolhidos
	"""

	if clear_screen:
		clear()

	if input_label:
		print(label_color(input_label))

	if sort_selection_list:
		selection_list.sort()

	op_list = render_selection_items(selection_list, number_of_cols, item_color=item_color)

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
		if return_index: 
			if ensure_list_output:
				return [op[0]]
			return op[0]
		else:
			if ensure_list_output:
				return [op_list[op[0]]]
			return op_list[op[0]]
	
	else:
		if return_index: 
			if ensure_list_output:
				return [op]
			return op
		else: return [op_list[idx] for idx in op]




def interval_select(selection_string):
	"""Converte intervalos de seleção (ex.: 1-5) em uma sequência (1,2,3,4,5)
	
	Arguments:
		selection_string {string} -- string com representação dos elementos selecionados
	
	Returns:
		{list} -- retorna lista ordenada
	"""

	selection_string = selection_string.replace(" ","") 
	selection_list = split_and_strip(selection_string,",")

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



def lexical_list_join(iterator):
	"""Concatena elementos de uma iterator conforme enumeração formal na língua portuguesa
	
	Arguments:
		iterator {list|tuple} -- lista com elementos a serem concatenados
	
	Returns:
		{string} -- retorna uma string no formato: 'e1, e2, [...] e en'
	"""

	assert isinstance(iterator, (list, tuple))

	output = ""

	for item in iterator:
		output += item
		if item == iterator[-1]:
			pass
		elif item == iterator[-2]:
			output += ' e '
		else:
			output += ', '

	return output


def sort_dict(dictionary, sorting_criteria=lambda x: x, reverse=False):
	"""Retorna um OrderedDict com as chaves apresntadas conforme a ordem definida
	
	Arguments:
		dictionary {dict} -- dicionário de entrada as chaves precisam ser comparáveis
	
	Returns:
		{OrderedDict} -- dicionário com chaves ordenadas conforme o critério fornecido
	"""

	output = OrderedDict()
	for key in sorted(dictionary, key=sorting_criteria, reverse=reverse):
		if type(dictionary[key]) == dict:
			output[key] = sort_dict(dictionary[key], reverse=reverse)
		elif type(dictionary[key]) == list:
			output[key] = sort_inner_dicts(dictionary[key])
		else:
			output[key] = dictionary[key]
	return output


def sort_inner_dicts(list_of_dicts, sorting_criteria=lambda x: x, reverse=False):
	"""Retorna uma lista em que os dicionários fornecidos na lista original são ordenados

	Arguments:
		list_of_dicts {list|tuple} -- lista de entrada com dicionários dispostos

	Returns:
		{list} -- lista com os dicionários/linhas ordenados conforme o critério fornecido
	"""

	output = []
	for dict_item in list_of_dicts:
		sorted_dict_item = sort_dict(dict_item, sorting_criteria=sorting_criteria, reverse=reverse)
		output.append(sorted_dict_item)
	return output



def render_form_get_values(form_file, file_folder=os.curdir, skip_q=[]):
	"""Lê um formulário JSON e retorna ao final do processo, as respostas solecionadas

	Arguments:
		form_file {string} -- nome do arquivo JSON referente ao formulário, a estrutura do arquivo precisar ser compatível com essa função (ver adiante)

	Keyword Arguments:
		file_folder {string} -- local onde o arquivo de formulário está localizado (default: {os.curdir})
		skip_q {list} -- lista de chaves/ids de questões que devem ser ignoradas (default: {[]})

	Returns:
		{OrderedDict} -- respostas são retornadas como dicionário

	Form file struct:
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
					"Informação via telefone"
				]            
			},
			{
				"enunciado": "Procedimento",
				"id": "procedimento",
				"tipo": "checkbox",
				"alternativas": 
				{
					"Registros de presença do estudante": [
						"Dúvida",
						"Estudante compareceu ao setor com dúvidas quanto a possibilidade de outra pessoa, além da coordenadora, assinar o processo"
					],
					"Problemas no recebimento de recursos": [
						"Contacto telefônico com a tesouraria para verificação de pagamento de auxílio",
						"Não recebimento de parcelas referente ao PASeUnB"
					],
					"Dados bancários": [
						"Recebimento de ficha para alteração de informações bancárias",
						"Encaminhamento de ficha de alteração das informações bancárias"
					]
				}
			}
		]
	}	

	"""
	
	def priorize_defaults(alternativas, defaults):
		#Não incorporado, ainda
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


	def read_categories(q_categorias):
		categorias_de_alternativas = []
		for a in q['alternativas'].keys():
			categorias_de_alternativas.append(a)
		categorias_de_alternativas.sort()
		categorias_de_alternativas.append("Outro")	
		return categorias_de_alternativas


	def objective_question_handler(q):
		grupos_de_opcao = []
		grupos_de_alternativas = []

		if q['tipo'] == 'radio':
			if isinstance(q['alternativas'], list):
				nfo[q['id']] = pick_options(q['alternativas'], input_label=q['enunciado'], ensure_list_output=True)
				if "Outro" in nfo[q['id']]:
					expliciting_others = read_input(input_label="Especifique as opções divergentes separando-as com ';'", dada_type='list', list_item_delimiter=';')
					for element in expliciting_others:
						nfo[q['id']].append(element)
					nfo[q['id']].remove("Outro")

		elif q['tipo'] == 'checkbox':
			if isinstance(q['alternativas'], list):
				nfo[q['id']] = pick_options(q['alternativas'], input_label=q['enunciado'], ensure_list_output=True, max_selection=len(q['alternativas']))
				if "Outro" in nfo[q['id']]:
					expliciting_others = read_input(input_label="Especifique as opções divergentes separando-as com ';'", dada_type='list', list_item_delimiter=';')
					for element in expliciting_others:
						nfo[q['id']].append(element)
					nfo[q['id']].remove("Outro")
			
			elif isinstance(q['alternativas'], dict):
				nfo[q['id']] = []
				get_explicit = False
				grupos_de_alternativas = read_categories(q['alternativas'])
				gopt = pick_options(grupos_de_alternativas, input_label=q['enunciado'], ensure_list_output=True, max_selection=len(grupos_de_alternativas))

				if type(gopt) == str:
					return gopt

				if "Outro" in gopt:
					get_explicit = True

				alternativas_efetivas = []

				for grp_op_key in gopt:
					if not grp_op_key == "Outro":
						grupos_de_opcao.append(grp_op_key)
						for op in q['alternativas'][grp_op_key]:
							if not op in alternativas_efetivas:
								alternativas_efetivas.append(op)

				alternativas_efetivas.sort()
				nfo[q['id']] = pick_options(alternativas_efetivas, input_label=q['enunciado'], ensure_list_output=True, max_selection=len(alternativas_efetivas))

				if get_explicit:
					expliciting_others = read_input(input_label="Especifique as opções divergentes separando-as com ';'", dada_type='list', list_item_delimiter=';')
					for element in expliciting_others:
						nfo[q['id']].append(element)


		if isinstance(nfo[q['id']], list):
			if len(nfo[q['id']]) > 1:
				nfo[q['id']] = '; '.join(nfo[q['id']])
			else:
				nfo[q['id']] = nfo[q['id']][0]

		return (nfo[q['id']], )

	def create_trigger_file(form_trigger_file, triggers_folder=getoutput('echo $HOME')):
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

		save_json(form_triggers_info, form_triggers_file, file_folder=triggers_folder)
		return form_triggers_info

	
	def prompt_questions(nfo, q):
		skip_this = False
		#print(q['id'])
		if form_triggers_info.get(q['id']):
			if form_triggers_info[q['id']].get('trigger_skip'):
				for t in form_triggers_info[q['id']]['trigger_skip'].keys():
					#print("» "+t)
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
				nfo[q['id']] = read_input(input_label=q['enunciado'])
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
	# Antes de apresentar e coletar informações sobre as questões, 'create_trigger_file' lê o formulário e
	# registra os gatilhos definidos nos campos 'trigger_skip', caso existam. Este gatilhos são registrados
	# no arquivo '.form_triggers-*' dentro da pasta do usuário. '*' será substituído pelo nome do arquivo
	# original do formulário.
	#
	# O arquivo de gatilhos, '.form_triggers-*', guardará as regras/condições para apresentação condicional
	# das questões do formulário. Dessa forma, quando for o momento de iterar sobre uma questão específica,
	# primeiramentese o arquivo degatilho será colsultado. Se algumas das regras definidas em 'trigger_skip'
	# para a questão do momento for identificada, a questão será ignorada.
	#
	# O arquivo '.form_triggers-*' foi criado na pasta do usuário para evitar conflitos em ambientes com múltiplos
	# usuários acessando simultaneamente o aplicaivo
	#

	form = load_json(form_file, file_folder=file_folder)
	form_triggers_file = '.form_triggers-'+form_file.split(os.sep)[-1].split('.')[0]
	form_triggers_info = create_trigger_file(form_triggers_file)
	
	#
	# O while loop seguinte fara a iteração em cada uma das questões definidas no formulário JSON
	# 
	# As respostas serão alojadas no dicionário 'nfo'
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
		else:
			inside_q_group = False
		
		if (idx == first_idx) and inside_q_group == True:
			if grp_prompt_pass == False:
				resposta = input_yes_or_no(input_label="Inserir registro para {} ?".format(amarelo(q['q_group'])))
				if resposta == 'n':
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
					if idx == first_idx:
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
					resposta = input_yes_or_no(input_label="Inserir registro adicional para {} ?".format(amarelo(q['q_group'])))
					if resposta == 's':
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
		
	try: os.remove(form_triggers_file)
	except FileNotFoundError: pass

	try: return output
	except UnboundLocalError: return nfo


def create_response_json_file(form_filename, response_filename=False, response_file_folder=os.curdir, form_file_folder=os.curdir):
	if not response_filename:
		response_filename = str(uuid.uuid4())+'.json'
	save_json(render_form_get_values(form_filename, file_folder=form_file_folder), response_filename, file_folder=response_file_folder)


def edit_form_file():
	def add_alternative_categories(q_categorias):
		while True:
			categoria = read_input(input_label="Indique o nome da nova categoria")
			ops = add_alternative([], None)
			q_categorias[categoria] = ops
			op = input_yes_or_no(input_label="Adicionar outra categoria? [s|n]")
			if op == 'n':
				break
		return q_categorias


	def add_alternative(q_spot, grupo_de_alternativas):
		outros_recem_listados = []
		if type(q_spot) != list:
			selected_op = pick_options(grupo_de_alternativas, input_label='À qual grupo a opção divergente pertence')
			if isinstance(q_spot[selected_op], dict):
				grupo_de_alternativas_internas = list(q_spot[selected_op].keys())
			#else:
			elif isinstance(q_spot[selected_op], list):
				grupo_de_alternativas_internas = q_spot[selected_op]
			o = add_alternative(q_spot[selected_op], grupo_de_alternativas_internas)
			for i in o:
				outros_recem_listados.append(i)
		else:
			while True:
				outro_detalhes = read_input(input_label="Especifique")
				outros_recem_listados.append(outro_detalhes)
				q_spot.append(outro_detalhes)
				q_spot.sort()
				op = input_yes_or_no(input_label="Adicionar outra opção? [s|n]")
				if op == 'n':
					break
		return outros_recem_listados


	def rebuild_form_file(q_alternatives, grupos_de_alternativas):
		op_adicional = add_alternative(q['alternativas'], grupos_de_alternativas)
		nfo[q['id']].remove("Outro")
		nfo[q['id']] = merge_lists(nfo[q['id']], op_adicional)
		input("Gravando alterações...")
		save_json(sort_dict(form), "iabadu.json", file_folder=os.curdir)
		input("Alterações gravadas...")	
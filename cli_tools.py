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

from colored import fg, bg, attr
from subprocess import getoutput
from random import randrange
from string import whitespace, punctuation, digits
from collections import OrderedDict
from copy import copy
from decorators import only_tuple_and_list

time.strptime('02/01/1986','%d/%m/%Y')

tmp_folder = tempfile.gettempdir()

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
	if lkf_name.find(".") != -1 or lkf_name.find(".") != 0:
		lkf_name = lkf_name.split(".")[0]
	file_name = '~lock_'+str(lkf_name)
	return file_name

def list_folder(folder):
    return os.listdir(os.getcwd()+os.sep+folder)


def list_col_responses(iterator, col_num=0, delimitor='\t'):
	"""Retorna os valores de uma tabela, linha à linha, para a coluna selecionada
	
	Arguments:
		iterator {table} -- é uma tabela NxN ou uma lista ou tupla com strings e um caractere delimitor
	
	Keyword Arguments:
		col_num {int} -- o numero correspondente à coluna desejada (default: {0})
		delimitor {str} -- o caractere/substring que demarca a separação das colunas (default: {'\t'})
	
	Yields:
		{string} -- each cell will be returned separatedly
	"""

	for item in iterator:
		yield item.split(delimitor)[col_num]


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


def dict_from_table(iterator, col_num=0, delimitor='\t'):
	"""Converte uma tabela em um dicionário utilizando os valores da coluna selecionada como chaves
	
	Arguments:
		iterator {table} -- é uma tabela NxN ou uma lista ou tupla com strings e um caractere delimitor
	
	Keyword Arguments:
		col_num {int} -- número da coluna de referência (default: {0})
		delimitor {str} -- o caractere/substring que demarca a separação das colunas (default: {'\t'})
	
	Returns:
		{dict} -- retorna um OrderedDict

	Observation:
		Colisões serão aninhadas conforme a função 'concat_dict_values'
	"""

	assert isinstance(iterator, (tuple, list)), "Iterador não suportado, utilizar 'tuple' ou 'list' como argumento."
	assert isinstance(iterator[0], (list, str)), "As linhas da tabela devem ser to tipo 'list'."

	use_delimitor = check_table_type(iterator)

	output = OrderedDict()
	for item in iterator:
		if use_delimitor:
			num_of_cols = item.count(delimitor)+1
		else:
			num_of_cols = len(item)
		
		indexes = list(range(0,num_of_cols))
		indexes.remove(col_num)

		if use_delimitor:
			tmp_list = item.split(delimitor)
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


def create_col_index(list_of_labels):
	"""Cria um índice para as colunas de uma tabela
	
	Arguments:
		list_of_labels {list|tuple} -- lista com os nomes das colunas na mesma ordem da tabela original
	
	Returns:
		{dict} -- retorna um dicionário com rótulos apontando para os indexes
	"""

	assert isinstance(iterator, (tuple, list)), "Iterador não suportado, utilizar 'tuple' ou 'list' como argumento."

	output = dict()

	n = itertools.count()

	for col in list_of_labels:
		idx = next(n)
		output[col] = idx
	
	return output


def create_line_index(iterator, col_num_list=[0], delimitor='\t'):
	"""Cria um dicionário a partir de uma tabela em que os valores das colunas selecionadas apontam para o número da linha da tabela original
	
	Arguments:
		iterator {table} -- é uma tabela NxN ou uma lista ou tupla com strings e um caractere delimitor
	
	Keyword Arguments:
		col_num_list {list} -- lista com o numero das colunas que serão indexadas (default: {[0]})
		delimitor {str} -- o caractere/substring que demarca a separação das colunas (default: {'\t'})
	
	Returns:
		{dict} -- retorna um dicionário com referências para as linhas da tabela original
	"""
	
	assert isinstance(iterator, (tuple, list)), "Iterador não suportado, utilizar 'tuple' ou 'list' como argumento."

	output = dict()
	
	use_delimitor = check_table_type(iterator)
	
	for col in col_num_list:
		idx = itertools.count()
		for line in iterator:
			n = next(idx)
			if use_delimitor:
				line = line.split(delimitor)
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

		


def ask_for_col_labels(num_of_cols, table_first_line, use_delimitor=True, delimitor='\t'):
	"""Retorna um dicionário com os nomes das colunas e indexes de referência
	
	Arguments:
		num_of_cols {int} -- quantidade de colunas da tabela
		table_first_line {table} -- matrix 1xN ou string com valores separados pelo delimitador
	
	Keyword Arguments:
		use_delimitor {bool} -- utiliza o delimitador no caso da amostra de dados ser uma string com delimitador (default: {True})
		delimitor {str} -- o caractere/substring que demarca a separação das colunas (default: {'\t'})

	Returns:
		{list} -- retorna uma lista
	"""

	assert isinstance(num_of_cols, int), "Número de colunas deve ser do tipo 'int'."
	assert isinstance(table_first_line, (list, str, tuple)), "Linha da tabela deve ser 'list', 'tuple' ou 'str'."

	output = []
	n = itertools.count() 
	
	if use_delimitor: table_first_line = table_first_line.split(delimitor)

	while True:
		idx = next(n)
		print('Indique o nome da coluna que armazena o dado: {}'.format(table_first_line[idx]))
		label = input(' :$')
		output.append(label)
		if len(output) == num_of_cols: break
	
	return output


def string_table_to_int_matrix(iterator, reference_data=False, delimitor='\t'):
	"""Converte uma tabela com strings em uma matriz numérica a partir de uma referência prévia ou a partir da atribuição arbitrária de números aos valores dos campos textuais na ordem em que estes são apresentados
	
	Returns:
		{tupla} -- uma tupla com dois elementos, o primeiro a matriz com as respostas convertidas em números, o segundo uma lista de dicionários com as referências
	"""

	assert isinstance(iterator, (tuple, list)), "Iterador não suportado, utilizar 'tuple' ou 'list' como argumento."

	numeric_matrix = []

	use_delimitor = check_table_type(iterator)
	
	if use_delimitor:
		num_of_cols = len(iterator[0].split(delimitor))
	else:
		num_of_cols = len(iterator[0])

	if not reference_data:
		reference_list = []
	else:
		reference_list = reference_data
		assert len(reference_data) == num_of_cols, "A quantidade de dicionários na lista de referência de valores deve corresponder ao número de colunas da tabela"
	
	for n in range(num_of_cols):
		reference_list.append({})

	for line in iterator:
		if use_delimitor:
			line = line.split(delimitor)
		
		n = itertools.count()
		numeric_matrix_line = []

		for col_idx in range(len(line)):
			ref_idx = next(n)
			print(line[col_idx])
			if not reference_list[ref_idx].get(line[col_idx]): 
				novo_escore = len(reference_list[ref_idx]) + 1
				reference_list[ref_idx][line[col_idx]] = novo_escore
				numeric_matrix_line.append(novo_escore)
			else:
				numeric_matrix_line.append(reference_list[ref_idx][line[col_idx]])

		numeric_matrix.append(numeric_matrix_line)

	return numeric_matrix, reference_list
		


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





def read_all_text_table_file(filename, delimitor='\t'):
	"""Ler todas as linhas de uma tabela em formato texto
	
	Arguments:
		filename {string} -- nome do arquivo da tabela
	
	Keyword Arguments:
		delimitor {string} -- caractere ou substring que delimita as colunas (default: {'\t'})
	
	Yields:
		{string} -- retorna as linhas uma a uma...
	"""

	with open(filename) as f:
		for line in f:
			yield split_and_strip(line, delimitor=delimitor)


def split_and_strip(text, delimitor='\t'):
	"""Separa uma string com base no delimitador e retira espaços em branco no início e final dos elementos
	
	Arguments:
		texto {string} -- texto ou string de entrada
	
	Keyword Arguments:
		delimitor {string} -- caractere ou substring que delimita os campos (default: {'\t'})
	
	Returns:
		{list} -- retorna uma lista com os elementos
	"""
	
	output = text.split(delimitor)
	idx = itertools.count()
	for i in output: output[next(idx)] = i.strip()
	return output



def read_target_line_on_text_table_file(filename, line_number, delimitor='\t'):
	"""Lê uma linha alvo de uma tabela em formato texto e retorna seu conteúdo, bem como o rótulo dos campos (primeira linha)
	
	Arguments:
		filename {string} -- nome do arquivo de tabela em formato texto
		line_number {int} -- linha alvo
	
	Keyword Arguments:
		delimitor {str} -- caractere ou substring que delimita os campos (default: {'\t'})
	
	Returns:
		{dict} -- retorna dicionário com nome/ordem dos campos e dados da linha selecionada
	"""
	assert isinstance(line_number, int)

	with open(filename) as f:
		fields = itertools.islice(f, 0, 1)
		fields = split_and_strip(next(fields), delimitor=delimitor) 
	
	with open(filename) as f:
		output = itertools.islice(f, line_number, line_number+1)
		output = split_and_strip(next(output), delimitor=delimitor)
		output = dict(zip(fields, output))

	return {'fields': fields, 'data': output}


def save_text_table_file(filename, new_line, delimitor='\t', constrain_cols=True):
	"""Adiciona linha no final de uma tabela em texto
	
	Arguments:
		filename {string} -- arquivo de tabela em formato texto
		new_line {dict, tuple, list} -- novo conteúdo a ser inserido do arquivo
	
	Keyword Arguments:
		delimitor {str} -- caractere ou substring que delimita os campos (default: {'\t'})
		constrain_cols {bool} -- ativa/desativa validação de colunas e posição (default: {True})
	"""

	if constrain_cols:
		assert isinstance(new_line, dict), "Para verificação das colunas é necessário passar os valores em um 'dict'"
		with open(filename) as f:
			fields = split_and_strip(next(f), delimitor=delimitor)
		assert len(fields) == len(new_line), "A quantidade de colunas no dicionário não corresponde à do arquivo"
		for key in new_line:
			assert key in fields, "O campo '{}' não existe no arquivo '{}'".format(key, filename)

	else:
		assert isinstance(new_line, (tuple, list)), "O argumento 'new_line' deve ser uma 'list' ou 'tuple'"
		new_line = delimitor.join(new_line) + os.linesep
	
	with open(filename, 'a') as f:
		if constrain_cols:
			new_line_ordered_info = []
			for field in fields:
				new_line_ordered_info.append(new_line[field])
			new_line = delimitor.join(new_line_ordered_info) + os.linesep
			f.write(new_line)
		else:
			f.write(new_line)
	



#Em processo de implementação
def save_text_db_file(novos_dados, path_to_file, tmp_folder=tmp_folder):
	lockf = lockfile_name(path_to_file)
	initfolder = os.getcwd()
	nfo = path_to_file.split('/')
	fname = nfo[-1]
	path = path_to_file.replace(fname, '')

	while True:
		if os.path.isfile(tmp_folder+os.sep+lockf):
			time.sleep(0.1)
		else:
			create_lockfile(lockf)
			break

	os.chdir(path.replace('/', os.sep))
	with open(path_to_file, 'w') as f:
		f.write(novos_dados)

	os.chdir(initfolder)
	remove_lockfile(lockf)



def load_json(path_to_file):
	with open(path_to_file) as f:
		data = f.read()
		return json.loads(data)


#Em processo de implementação
def print_json_file_v2(path_to_file_responses_file, path_to_form_file, columns_metadata, lines=None):
	assert (lines == None) or (type(lines) == tuple)

	with open(path_to_file_responses_file) as f:
		print("Size of 'f':", sys.getsizeof(f))
		if type(lines) == tuple:
			linha = itertools.islice(f, lines[0], lines[1])
			print("Size of 'linha':", sys.getsizeof(linha))
			print(json.loads(next(linha)))
		else:
			#exhaust_generator_and_print(convert_generator_itens_to_json(f), count_lines=True)
			exhaust_generator_and_print_cli_list(convert_generator_itens_to_json(f), path_to_form_file, columns_metadata)

#Em processo de implementação
def convert_generator_itens_to_json(generator):
	for line in generator:
		yield json.loads(line)

#Em processo de implementação
def exhaust_generator_and_print_cli_list(generator, form_file, columns_metadata):
	form_file_data = load_json(form_file)
	fields_to_list = form_file_data['form_lst_fields'].split(', ')
	current_list_column_wid = []
	for field in fields_to_list:
		current_list_column_wid.append(columns_metadata[field])
	listagem_cli2(generator, current_list_column_wid)


def make_float_list():
    r = []
    while True:
        v = input("Value: ")
        n = input("Frequenci: ")
        ni = int(n)
        vf = float(v)
        while ni != 0:
            r.append(vf)
            ni -= 1
        op = input('Insert other? [default:y] ')
        if op == 'n':
            break
            
    return r

#Em processo de implementação
def listagem_cli2(generator, cols):
	visual_count = itertools.count(start=1)
	for linha in generator:
		next(visual_count)
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
								print(visual_nfo)
			else:
				li += "".ljust(col[1])

		
		if linha_sem_quebra == True:
			visual_nfo += li 
			print(visual_nfo)
	
	print("Total: {}".format(visual_count))



def save_json(novos_dados, path_to_file, tmp_folder=tmp_folder):
	lockf = lockfile_name(path_to_file)
	initfolder = os.getcwd()
	nfo = path_to_file.split('/')
	fname = nfo[-1]
	path = path_to_file.replace(fname, '')

	while True:
		if os.path.isfile(tmp_folder+os.sep+lockf):
			time.sleep(0.1)
		else:
			create_lockfile(lockf)
			break

	os.chdir(path.replace('/', os.sep))
	with open(path_to_file, 'w') as f:
		f.write(json.dumps(novos_dados, ensure_ascii=False, indent=4))


	os.chdir(initfolder)
	remove_lockfile(lockf)

#
# Em processo de implementação, conversão de list_of_dicts para arquivo de texto com dicts listados linha à linha...
#
# O objetivo dessa implementação é ganhar perfomance e diminuir consumo de memória com o
# itertools.isslice... Para que isso funcione a insersão deve ser feita de forma centralizada pelo
# worker...
#

def save_json2(novos_dados, path_to_file, tmp_folder=tmp_folder):
	lockf = lockfile_name(path_to_file)
	initfolder = os.getcwd()
	nfo = path_to_file.split('/')
	fname = nfo[-1]
	path = path_to_file.replace(fname, '')

	while True:
		if os.path.isfile(tmp_folder+os.sep+lockf):
			time.sleep(0.1)
		else:
			create_lockfile(lockf)
			break

	os.chdir(path.replace('/', os.sep))
	with open(path_to_file, 'w') as f:
		for l in novos_dados:
			f.write(json.dumps(l, ensure_ascii=False))
			f.write(os.linesep)

	os.chdir(initfolder)
	remove_lockfile(lockf)


#
# Em processo de implementação
#
# Tem de ser implementado o método isslice de itertools
#

def load_big_csv(csv_file, delimiter='\t', lineterminator='\n'):
	'''
	Acessa o conteúdo do arquivo CSV e o armazena na memória como um list_of_dicts.
	'''
	#o = []
	#fields = load_csv_head(csv_file, delimiter=delimiter, lineterminator=lineterminator)
	try:
		with open(os.path.join(os.getcwd(), csv_file), encoding="utf8") as csv_fileobj:
			rd = csv.DictReader(csv_fileobj, delimiter=delimiter, lineterminator=lineterminator)
			for row in rd:
				yield row
	except:
		with open(os.path.join(os.getcwd(), csv_file), encoding="cp1252") as csv_fileobj:
			rd = csv.DictReader(csv_fileobj, delimiter=delimiter, lineterminator=lineterminator)
			for row in rd:
				yield row



def load_csv(csv_file, delimiter='\t', lineterminator='\n'):
	'''
	Acessa o conteúdo do arquivo CSV e o armazena na memória como um list_of_dicts.
	'''
	o = []
	fields = load_csv_head(csv_file, delimiter=delimiter, lineterminator=lineterminator)
	try:
		with open(os.path.join(os.getcwd(), csv_file), encoding="utf8") as csv_fileobj:
			rd = csv.DictReader(csv_fileobj, delimiter=delimiter, lineterminator=lineterminator)
			for row in rd:
				ordered_row = OrderedDict()
				for col in fields:
					ordered_row[col] = row[col]
				o.append(ordered_row)
	except:
		with open(os.path.join(os.getcwd(), csv_file), encoding="cp1252") as csv_fileobj:
			rd = csv.DictReader(csv_fileobj, delimiter=delimiter, lineterminator=lineterminator)
			for row in rd:
				ordered_row = OrderedDict()
				for col in fields:
					ordered_row[col] = row[col]
				o.append(ordered_row)
	return o


def load_csv_head(csv_file, delimiter='\t', lineterminator='\n'):
	f = open(csv_file)
	f_csv_obj = csv.DictReader(f, delimiter=delimiter, lineterminator=lineterminator)
	header = f_csv_obj.fieldnames
	f.close()
	return header



def load_csv_col(col, csv_file, delimiter='\t', lineterminator='\n', sort_r=False):
	fd = load_csv(csv_file, delimiter=delimiter, lineterminator=lineterminator)
	o = []
	for i in fd:
		o.append(i[col])
	if sort_r == True:
		o.sort()
	return o



#### Refatorar
def fill_gaps(csv_file,refcol=[],targetcol=[],targetcolops=[]):
	conteudo = load_csv(csv_file)
	cols = load_csv_head(csv_file)
	
	print_refcol = True
	keep_working = True
	
	for l in conteudo:
		if keep_working == False:
			break
		white_cels = 0
		if targetcol == []:
			for c in l:
				if l[c] == '':
					if print_refcol == True:
						print_refcol = False
						for r in refcol:
							print(l[r])
					l[c] = input(c+': ')
				else:
					white_cels += 1
		else:
			for c in l:
				for selected in targetcol:
					print(c)
					print(selected)
					if l[selected] == '':
						if print_refcol == True:
							print_refcol = False
							for r in refcol:
								print(l[r])
					else:
						white_cels += 1			
		
		if white_cels < len(cols)-1:
			while True:
				op = input("Gravar alterações e continuar? s/n : ")
				if (op == 's') or (op == 'S'):
					save_csv(conteudo,csv_file)
					break
				elif (op == 'n') or (op == 'N'):
					keep_working = False
					break
				else:
					print('Responda [s] para sim ou [n] para não...')
			
		print_refcol = True
	
	return conteudo



#### Refatorar
def extract_lines(csv_file, csv_col, test_value, delimiter='\t', backup_2_trash=True):
	conteudo = load_csv(csv_file, delimiter=delimiter)
	keep_this = []
	remove_that = []
	for line in conteudo:
		if line[csv_col] == test_value:
			remove_that.append(line)
		else:
			keep_this.append(line)
	op = input("Deseja remover as {} linhas encontradas na tabela? (s/n)".format(len(remove_that)))
	if op == "s" or op == "S":
		save_csv(keep_this, csv_file)
		if backup_2_trash == True:
			new_csv_file = time.ctime().replace(' ','_') + "_rmLines_from_" + csv_file
			save_csv(remove_that, new_csv_file)



#### Refatorar
def copy_col(csv_file, source_col, destination_col):
	"Copia o conteúdo de uma coluna alvo para uma coluna de destino se a célula do destino ainda não estiver preechida"
	conteudo = load_csv(csv_file)
	cols = load_csv_head(csv_file)
	change_info = False
	if destination_col in cols:
		for line in conteudo:
			if line[source_col] != '' and line[destination_col] == '':
				change_info = True
				line[destination_col] = line[source_col]
	else:
		for line in conteudo:
			line[destination_col] = ''
			if line[source_col] != '' and line[destination_col] == '':
				change_info = True
				line[destination_col] = line[source_col]		
	
	if change_info == True:
		print("Cópia efetuada...")
		save_csv(conteudo, csv_file)
	else:
		print("Não há o que alterar...")



#### Refatorar
def add_line(csv_file, refcols=[]):
	conteudo = load_csv(csv_file)
	cols = load_csv_head(csv_file)
	nova_linha = OrderedDict()
	for c in cols:
		v = input(c+": ")
		nova_linha[c] = v
		
	conteudo.append(nova_linha)
	save_csv(conteudo, csv_file)
	v = input("Adicionar outro? (s/n) ")
	if v == "s" or v == "S":
		add_line(csv_file)


#### Refatorar
def convert_csv_type(csv_file, old_delimiter, new_delimiter, old_lineterminator=os.linesep, new_lineterminator=os.linesep):
	conteudo = load_csv(csv_file, delimiter=old_delimiter, lineterminator=old_lineterminator)
	save_csv(conteudo, csv_file, delimiter=new_delimiter, lineterminator=new_lineterminator)


#### Refatorar
def save_csv(list_of_dicts, path_to_file, header=None, delimiter='\t', lineterminator='\n', tmp_folder=tmp_folder):
	'''
	Escreve o conteudo de uma lista de dicionários em um arquivo CSV.
	Esta função gera um arquivo de trava até que o processo seja concluído impossibilitanto a realização de cópias simultâneas.
	A ordem do cabeçalho pode ser definido arbitrariamente mediante a inclusão de uma lista com o come das colunas na argumento "header".
	'''

	fields = list_of_dicts[0].keys()
	lockf = lockfile_name(path_to_file)
	initfolder = os.getcwd()

	while True:
		if os.path.isfile(tmp_folder+os.sep+lockf):
			time.sleep(0.1)
		else:
			create_lockfile(lockf)
			break

	with open(path_to_file, 'w') as f:
		w = csv.DictWriter(f, fields, delimiter=delimiter, lineterminator=lineterminator)
		w.writeheader()
		w.writerows(list_of_dicts)

	os.chdir(initfolder)
	remove_lockfile(lockf)


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


def read_input(input_label=False, default=False, dada_type='string', data_pattern=False, prompt="$: ", list_item_delimitor=',', waring_msg="Resposta inválida ou em formato inadequado...", clear_screen=False, label_color=branco, prompt_color=branco, warning_color=vermelho, callback=False, break_line=True):
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
					response = split_and_strip(response, list_item_delimitor)
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

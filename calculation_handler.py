#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# license: AGPL-3.0 
#



from collections import Counter, OrderedDict
from cli_tools import create_col_labels, split_and_strip, print_list, sim_ou_nao, create_line_index, pick_options, try_implict_convert




def sum(lista, key=lambda x: x):
	"""Adiniona os elementos de uma lista numérica
	
	Arguments:
		lista {list|tuple} -- lista com números a serem adicionados

	Keyword Arguments:
		key {function} -- função para indicar atributo a ser somado em elementos complexos

	Returns:
		{int|float} -- resultado da soma entre os elementos
	"""

	assert isinstance(lista, (list, tuple)), "Argumento deve ser do tipo 'list' ou 'tuple'"
	assert callable(key), "Argumento 'key' deve ser uma função"

	output = 0

	for item in lista:
		output += key(item)

	return output



def map_values(iterator, delimiter=False, select=False, count=False):
    """Conta a quantidade de respostas das colunas de uma tabela
    
    Arguments:
        iterator {table} -- lista de dicionários, tuplas, listas ou strings com delmitadores de campo
    
    Keyword Arguments:
        delimiter {bool} -- necessário se as linhas da tabela forem do tipo string (default: {False})
        select {bool} -- permite seleleção de colunas específicas (default: {False})

    Returns:
        {dict} -- dicionário com valores tabulados conforme as colunas da tabela
    """

    assert isinstance(iterator, (list, tuple))
    assert isinstance(iterator[0], (list, tuple, dict, str))


    if isinstance(iterator[0], dict):
        fields = list(iterator[0].keys())
        iterator_data = iterator

    elif isinstance(iterator[0], str):
        assert delimiter != False
        fields = split_and_strip(iterator[0], delimiter)

        print_list(fields)
        op = sim_ou_nao(input_label="Estes valores são os nomes corretos das colunas?")
        if op == 'n': 
            fields = create_col_labels(iterator, delimiter=delimiter)
            iterator_data = iterator
        else:
            iterator_data = iterator[1:]


    else:
        print_list(iterator[0])
        op = sim_ou_nao(input_label="Estes valores são os nomes corretos das colunas?")
        if op == 'n':
            fields = create_col_labels(iterator, delimiter=delimiter)
            iterator_data = iterator
        else:
            fields = iterator[0]
            iterator_data = iterator[1:]

    fileds_index_map = create_line_index(fields)

    selected_cols = fields
    if select:
        selected_cols = pick_options(fields, input_label="Selecione as colunas que devem ser tabuladas", max_selection=len(fields))

    output = OrderedDict()

    if count:
        for col in selected_cols:
            output[col] = Counter()

            if isinstance(iterator[0], dict):
                for line in iterator_data:
                    value = try_implict_convert(line[col])
                    output[col].update([value])

            else:
                for line in iterator_data:
                    value = try_implict_convert(line[fileds_index_map[col]])
                    output[col].update([value])
    
    else:
        for col in selected_cols:
            output[col] = {}

            if isinstance(iterator[0], dict):
                for line in iterator_data:
                    if not output[col].get(line[col]):
                        value = try_implict_convert(line[col])
                        output[col][value] = True
                output[col] = tuple(output[col].keys())

            else:
                for line in iterator_data:
                    if not output[col].get(line[fileds_index_map[col]]):
                        value = try_implict_convert(line[fileds_index_map[col]])
                        output[col][value] = True
                output[col] = tuple(output[col].keys())

    return output


def calculate_relative_freq(iterator, delimiter=False, select=False):
    """Calcula a quantidade absoluta e relativa das respostas fornecidas em uma tabela (tabulação)
    
    Arguments:
        iterator {table} -- lista de dicionários, tuplas, listas ou strings com delmitadores de campo
    
    Keyword Arguments:
        delimiter {bool} -- necessário se as linhas da tabela forem do tipo string (default: {False})
        select {bool} -- permite seleleção de colunas específicas (default: {False})
    
    Returns:
        {dict} -- dicionário com valores tabulados conforme as colunas da tabela
    """
	
    absolute_freq = map_values(iterator, delimiter=False, select=False, count=True)

    for col in absolute_freq:
        sigma_col = 0
        for number in absolute_freq[col].values():
            sigma_col += number
        
        for key, number in absolute_freq[col].items():
            absolute_freq[col][key] = (number, (number / sigma_col)*100)

    return absolute_freq



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# license: AGPL-3.0 
#


import itertools
import re
import os

from collections import OrderedDict

from cli_tools import strip_simbols, strip_spaces, verde, amarelo, select_op, limpar_tela, branco, amarelo, vermelho, read_input
from cli_tools import bisect_search_idx, create_col_index, string_table_to_int_matrix, create_reference_table, print_numeric_matrix
from cli_tools import ExtendedDict, UnicOrderedList

import py_pickle_handlers as pk



class PickleDataType():
    def __init__(self, target_folder=False, filename=False):
        self.target_folder = target_folder
        self.filename = filename

    def persist(self, file_ext=False, filename=False):
        if filename:
            self.filename = filename

        if not self.filename:
            self.filename = read_input(input_label="Defina o nome para o arquivo de saída")

        if file_ext:
            self.filename = self.filename.strip() + file_ext
            
        if not self.target_folder:
            input_value = read_input(input_label='Defina a pasta de destino [{}]: '.format(amarelo("aperte ENTER para pasta corrente")))
            if not input_value:
                self.target_folder = os.curdir

        pk.write_pickle(self, self.target_folder, self.filename)

    def fullpath(self):
        return '{folder}{os_sep}{filename}'.format(folder=self.target_folder, os_sep=os.sep, filename=self.filename)



class Form(PickleDataType):
    def __init__(self, titulo, folder):
        def definir_questoes():
            output = OrderedDict()
            q_num = itertools.count()
            
            while True:
                limpar_tela()
                n = next(q_num)
                output[n] = OrderedDict()
                output[n]['regex'] = False
                output[n]['enunciado'] = self.read_input(input_label="Qual o enunciado da questão?")
                output[n]['tipo_dado'] = select_op(['string', 'int', 'float', 'list'], 1, input_label="Selecione o tipo de dado")[0]
                output[n]['tipo_questão'] = select_op(['text', 'radio', 'checkbox'], 1, input_label="Selecione o tipo de questão")[0]
                
                if output[n]['tipo_dado'] == 'string':
                    op = self.read_input(input_label='Necessário validar a informação?', data_pattern='[sn]', waring_msg='Responda ["s" ou "n"]...')
                    if op == 's':
                        output[n]['regex'] = self.read_input(input_label="Qual a expressão regular de validação da informação?")
                
                output[n]['warning_msg'] = self.read_input(input_label="Qual a mensagem de alerta em caso de erro?")
                output[n]['warning_color'] = amarelo

                op = self.read_input(input_label='Inserir outra questão?', data_pattern='[sn]', waring_msg='Responda ["s" ou "n"]...')
                if op == 'n': break
            
            return output


        super(Form, self).__init__()
        self.target_folder = folder
        self.titulo = titulo
        self.q = definir_questoes()
        self.persist()

    def __repr__(self):
        return self.filename

    def executar_formulario(self):
        respostas = OrderedDict()
        for n in self.q.keys():
            respostas[self.q[n]['enunciado']] = self.read_input(\
                input_label=self.q[n]['enunciado'],\
                dada_type=self.q[n]['tipo_dado'],\
                data_pattern=self.q[n]['regex'],\
                waring_msg=self.q[n]['warning_msg'],\
                warning_color=self.q[n]['warning_color'])
        return respostas


    def split_and_strip(self, string, list_item_delimitor=','):
        output = string.split(list_item_delimitor)
        idx = itertools.count()
        for i in output: output[next(idx)] = i.strip()
        return output


    def read_input(self, input_label=False, dada_type='string', data_pattern=False, prompt="$: ", list_item_delimitor=',', waring_msg="Resposta inválida ou em formato inadequado...", clear_screen=False, label_color=branco, prompt_color=branco, warning_color=vermelho, callback=False):
        if clear_screen:
            limpar_tela()
         
        if input_label:
            print(input_label)

        while True:

            response = input(prompt_color(prompt))
            all_ok = False

            if not data_pattern:
                if dada_type == 'string':
                    print(response)
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
                        response = self.split_and_strip(response, list_item_delimitor)
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
        
        return response







class FileIndexDict(ExtendedDict, PickleDataType):
    def __init__(self):
        super(FileIndexDict, self).__init__()
        self.target_folder = False
        self.filename = False


class UnicListFile(UnicOrderedList, PickleDataType):
    def __init__(self, target_folder=False, filename=False):
        super(UnicListFile, self).__init__()
        self.target_folder = target_folder
        self.filename = filename

    def append(self, element):
        super(UnicListFile, self).append(element)
        self.persist()


class HistoryTable(PickleDataType):
    def __init__(self, target_folder=False, filename=False):
        super(HistoryTable, self).__init__()
        self.target_folder = target_folder
        self.filename = filename
        self.fieldnames = read_input(input_label="Indique o nome dos campos separando-os por ';'", dada_type='list', list_item_delimiter=';')
        self.fieldnames_idx = create_col_index(self.fieldnames)
        self.matrix = []
        self.col_wid = create_reference_table(num_of_cols=len(self.fieldnames), zeros=True)
        self.reference_table = create_reference_table(num_of_cols=len(self.fieldnames))
        self.reversed_reference_table = create_reference_table(num_of_cols=len(self.fieldnames))

    def append(self, dictionary):

        assert isinstance(dictionary, dict)

        new_line = list(range(0, len(self.fieldnames)))
        for key in dictionary.keys():
            try:
                new_line[self.fieldnames_idx[key][0]] = dictionary[key]
                if len(dictionary[key]) > self.col_wid[self.fieldnames_idx[key][0]]:
                    self.col_wid[self.fieldnames_idx[key][0]] = len(dictionary[key]) + 2

            except KeyError:
                print("Coluna não encontrada...")
                return

        lines = string_table_to_int_matrix([new_line], reference_data=self.reference_table, reversed_reference_data=self.reversed_reference_table)
        self.matrix = self.matrix + lines[0]
        self.persist()
    

    def __str__(self):
        return print_numeric_matrix(self.matrix, translator=self.reversed_reference_table, col_wid=self.col_wid, return_value=True)


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# license: AGPL-3.0 
#


import itertools
import re
import os
import time

from collections import OrderedDict


import py_pickle_handlers as pk

from cli_tools import clear, verde, amarelo, branco, vermelho, read_input, pick_options, input_yes_or_no
from cli_tools import bisect_search_idx, create_col_index, string_table_to_int_matrix, create_reference_table, print_numeric_matrix, pick_options
from cli_tools import ColisionDict, PK_LinkedList
from time_handler import today_date





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
            in_block = False
            current_block_name = ""
            while True:
                clear()
                n = next(q_num)
                output[n] = OrderedDict()
                output[n]['regex'] = False
                if not in_block:
                    op = input_yes_or_no(input_label="Iniciar bloco de questões?")
                    if op == 's':
                        current_block_name = read_input(input_label="Qual o nome do bloco?")
                        in_block = True
                if in_block: output[n]['grp_block'] = current_block_name
                output[n]['enunciado'] = read_input(input_label="Qual o enunciado da questão?")
                output[n]['tipo_dado'] = pick_options(['string', 'int', 'float', 'list'], input_label="Selecione o tipo de dado")
                output[n]['tipo_questão'] = pick_options(['text', 'radio', 'checkbox'], input_label="Selecione o tipo de questão")
                if output[n]['tipo_dado'] == 'string':
                    op = input_yes_or_no(input_label='Necessário validar a informação?')
                    if op == 's': output[n]['regex'] = read_input(input_label="Informe a expressão regular de validação:")
                output[n]['warning_msg'] = read_input(input_label="Qual a mensagem de alerta em caso de erro?")
                output[n]['warning_color'] = amarelo
                if in_block:
                    op = input_yes_or_no(input_label="Inserir outra questão no bloco?")
                    if op == 'n': 
                        in_block = False
                        op = input_yes_or_no(input_label="Inserir outra questão no formulário?")
                        if op == 'n': break
                else:
                    op = input_yes_or_no(input_label="Inserir outra questão no formulário?")
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
            respostas[self.q[n]['enunciado']] = read_input(\
                input_label=self.q[n]['enunciado'],\
                dada_type=self.q[n]['tipo_dado'],\
                data_pattern=self.q[n]['regex'],\
                waring_msg=self.q[n]['warning_msg'],\
                warning_color=self.q[n]['warning_color'])
        return respostas






class FileIndexDict(ColisionDict, PickleDataType):
    def __init__(self):
        super(FileIndexDict, self).__init__()
        self.target_folder = False
        self.filename = False


class UnicListFile(PK_LinkedList, PickleDataType):
    def __init__(self, target_folder=False, filename=False):
        super(UnicListFile, self).__init__()
        self.target_folder = target_folder
        self.filename = filename

    def append(self, element):
        super(UnicListFile, self).append(element)
        self.persist()


class HistoryTable(PickleDataType):
    """Tabela histórico. Tabela para armazenamento de informações com objetivo de minimizar redundância e permitir filtragem rápida de valores.
    
    Atributos:
        target_folder {string} -- pasta onde o arquivo será salvo
        filename {string} -- nome do arquivo a ser salvo
        fieldnames {list} -- lista com o nome das colunas da tabela
        fieldnames_idx {dict} -- dicionário com index de referencia para cada coluna nominal de 'self.fieldnames'
        fieldnames_mapping {ColisionDict} -- dicionário com indicação das linhas onde estão situados um dado valor
        fieldnames_to_map {list} -- lista com o nome das colunas que terão seus valores mapeados
        matrix {list_of_lists} -- matriz numérica onde os dados da tabela serão efetivamente armazenados como números
        col_wid {list} -- lista de inteiros com a largura das colunas a ser usada quando tabela for impressa
        referense_table {list_of_dicts} -- lista dicionários contendo a referencia entre o valor de um campo específico (geralmente string) e o inteiro a ser registrado na respectiva coluna da matrix
        reversed_reference_table {list_of_dicts} -- lista de dicionários para tradução da matrix, usada para restabelecer os valores originais quando a tabela for impressa
        

    Methods:
        append -- adiciona informações na tabela, o argumento deve ser do tipo 'dict'
        filter -- imprime as linhas corespondentes ao valor filtrado
    
    """
    def __init__(self, target_folder=False, filename=False, fieldnames=False, map_fields=False):
        super(HistoryTable, self).__init__()
        self.target_folder = target_folder
        self.filename = filename
        self.__set_fieldnames__(fieldnames)
        self.fieldnames_mapping = ColisionDict()
        self.fieldnames_to_map = []
        self.__set_mapping__(map_fields)
        self.fieldnames_idx = create_col_index(self.fieldnames)
        self.matrix = []
        self.col_wid = create_reference_table(num_of_cols=len(self.fieldnames), zeros=True)
        self.reference_table = create_reference_table(num_of_cols=len(self.fieldnames))
        self.reversed_reference_table = create_reference_table(num_of_cols=len(self.fieldnames))


    def __str__(self):
        return print_numeric_matrix(self.matrix, translator=self.reversed_reference_table, col_wid=self.col_wid, return_value=True)


    def __set_fieldnames__(self, fieldnames):
        base_fieldnames = ['data_registro']

        if fieldnames:
            assert isinstance(fieldnames, (list, tuple)), "Argumento 'fieldnames', deve ser do tipo 'list' ou 'tuple'"
            custom_fieldnames = fieldnames
        else:
            custom_fieldnames = read_input(input_label="Indique o nome dos campos separando-os por ';'", dada_type='list', list_item_delimiter=';')
        
        self.fieldnames = base_fieldnames + custom_fieldnames


    def __set_mapping__(self, map_fields):
        if map_fields:
            if isinstance(map_fields, bool):
                self.fieldnames_to_map = pick_options(self.fieldnames, input_label="Selecione as colunas a serem mapeadas", max_selection=len(self.fieldnames))
            else:
                assert isinstance(map_fields, (list, tuple)), "Argumento 'map_fields', deve ser do tipo 'list' ou 'tuple'"
                self.fieldnames_to_map = map_fields 


    def filter(self, value, return_value=False):
        output = []
        
        for line in self.fieldnames_mapping[value]:
            output.append(self.matrix[line])
        
        if return_value:
            return print_numeric_matrix(output, translator=self.reversed_reference_table, col_wid=self.col_wid, return_value=return_value, output_format='list')
        else:
            return print_numeric_matrix(output, translator=self.reversed_reference_table, col_wid=self.col_wid, return_value=return_value, output_format='string')

    def append(self, dictionary):
        """Adiciona linha à tabela
        
        Arguments:
            dictionary {dict} -- dicionário contendo as mesmas chaves definidas em 'fieldnames'
        """

        assert isinstance(dictionary, dict)

        dictionary['data_registro'] = today_date()

        matrix_lines = len(self.matrix)
        new_line = list(range(0, len(self.fieldnames)))
        for key in dictionary.keys():

            try:
                new_line[self.fieldnames_idx[key][0]] = dictionary[key]
                if len(dictionary[key]) > self.col_wid[self.fieldnames_idx[key][0]]:
                    self.col_wid[self.fieldnames_idx[key][0]] = len(dictionary[key]) + 2
                
                if key in self.fieldnames_to_map:
                    self.fieldnames_mapping.append(dictionary[key], matrix_lines)

            except KeyError:
                print("Coluna não encontrada...")
                return

        lines = string_table_to_int_matrix([new_line], reference_data=self.reference_table, reversed_reference_data=self.reversed_reference_table)
        self.matrix = self.matrix + lines[0]
        self.persist()
    

class HistoryTasks(HistoryTable):
    pass



#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from cli_tools import *
from pytest import fixture, raises


dictionary = {'Daniel': 22, 'Lara': [33, 88, 56], 'Joana': [[40, 67, 86], [13, 15]]}

table1 = ['Daniel:36:dan@gmail.com','Mara:22:mara@outlook.com','Silvia:22:slv@gmail.com']
table2 = [('Daniel', 36, 'dan@gmail.com'), ('Mara', 22, 'mara@outlook.com'), ('Silvia', 22, 'slv@gmail.com')]
table3 = ['Masculino:DF:Branco','Feminino:DF:Pardo','Feminino:DF:Branco', 'Feminino:GO:Indígena', 'Masculino:GO:Branco']
table4 = '{"nome": "Daniel", "idade": 22}\n{"nome": "Helena", "idade": 42}\n{"nome": "Simone", "idade": 30}\n'
table5 = 'nome:idade\nDaniel:22\nHelena:42\nSimone:30\n'


def test_create_lockfile():
    create_lockfile('test_lock')
    assert os.path.isfile(tmp_folder+os.sep+'test_lock') == True

def test_create_target_file():
    #Necessário executar teste 'test_create_lockfile' primeiro
    create_target_file("test_lock", ".test_create_target_file", file_folder=tmp_folder+os.sep)
    assert os.path.isfile(os.getcwd()+os.sep+".test_create_target_file") == True
    os.remove(os.getcwd()+os.sep+".test_create_target_file")


def test_remove_lockfile():
    #Necessário executar teste 'test_create_lockfile' primeiro
    remove_lockfile('test_lock')
    assert os.path.isfile(tmp_folder+os.sep+'test_lock') == False


def test_lockfile_name():
    assert lockfile_name('/tmp/www/work/test_lock') == '~lock_'+'test_lock'


def test_list_col_responses():
    assert next(list_col_responses(table1, 1, delimitor=':')) == '36'
    assert list(list_col_responses(table1, 1, delimitor=':'))[-1] == '22'
    assert list(list_col_responses(table1, 2, delimitor=':'))[-1] == 'slv@gmail.com'


def test_concat_dict_values():
    assert concat_dict_values(dictionary, 'Daniel', 38)['Daniel'] == [22, 38]
    assert concat_dict_values(dictionary, 'Lara', 13)['Lara'] == [[33, 88, 56], 13]
    assert concat_dict_values(dictionary, 'Joana', ['A', 'B'])['Joana'] == [[40, 67, 86], [13, 15], ['A', 'B']]


def test_dict_from_table():
    assert dict_from_table(table1, col_num=0, delimitor=':')['Daniel'] == ['36', 'dan@gmail.com']
    assert dict_from_table(table1, col_num=2, delimitor=':')['slv@gmail.com'] == ['Silvia', '22']
    assert dict_from_table(table1, col_num=1, delimitor=':')['22'] == [['Mara', 'mara@outlook.com'], ['Silvia', 'slv@gmail.com']]
    with raises(AssertionError):
        dict_from_table(1)
        dict_from_table(dictionary)
        dict_from_table(table2)
    


def test_create_line_index():
    index1 = create_line_index(table1, col_num_list=[0,2], delimitor=':')
    index2 = create_line_index(table2, col_num_list=[0,1,2])
    assert index1['Silvia'] == 2
    assert index1['dan@gmail.com'] == 0
    assert isinstance(index1, dict) == True
    assert index2['Daniel'] == 0
    assert index2['mara@outlook.com'] == 1
    assert isinstance(index2, dict) == True
    assert index2[22] == [1,2]
    with raises(AssertionError):
        create_line_index(1)
        create_line_index(dictionary)



def test_string_table_to_int_matrix():
    matrix, references = string_table_to_int_matrix(table3, delimitor=':')
    assert len(matrix[0]) == len(references)
    assert len(references[0]) == 2
    assert len(references[2]) == 3
    with raises(AssertionError):
        string_table_to_int_matrix(1)
        string_table_to_int_matrix(dictionary)
        string_table_to_int_matrix(table3, delimitor=':', reference_data=[{'Masculino': 0}, {'DF': 0}])




def test_check_table_type():
    assert check_table_type(table1) == True
    assert check_table_type(table2) == False
    assert check_table_type(table3) == True
    with raises(AssertionError):
        check_table_type(1)
        check_table_type(dictionary)
    

def test_read_all_text_json_file():
    with open('text_json_file.test', 'w') as f:
        f.write(table4)
    info = read_all_text_json_file('text_json_file.test')
    assert isinstance(next(info), (dict, list, tuple))
    assert next(info)['nome'] == "Helena" 
    os.remove('text_json_file.test')


def test_read_target_line_on_text_json_file():
    with open('text_json_file.test', 'w') as f:
        f.write(table4)
    info = read_target_line_on_text_json_file('text_json_file.test', 2)
    assert isinstance(info, (dict, list, tuple))
    assert info['nome'] == "Simone" 
    os.remove('text_json_file.test')


def test_read_all_text_table_file():
    with open('text_table_file.test', 'w') as f:
        f.write(table5)
    info = read_all_text_table_file('text_table_file.test', delimitor=':')
    fields = next(info)
    assert fields == ['nome', 'idade']
    assert next(info)[0] == "Daniel" 
    assert next(info)[1] == "42"
    os.remove('text_table_file.test')


def test_save_text_table_file():
    with open('text_table_file.test', 'w') as f:
        f.write(table5)
    
    save_text_table_file('text_table_file.test', ['Bruno', '27'], delimitor=':', constrain_cols=False)
    save_text_table_file('text_table_file.test', {'nome': 'Manoel', 'idade': '57'}, delimitor=':', constrain_cols=True)
    assert read_target_line_on_text_table_file('text_table_file.test', 4, delimitor=":")['data']['idade'] == '27'
    assert read_target_line_on_text_table_file('text_table_file.test', 5, delimitor=":")['data']['nome'] == 'Manoel'
    with raises(AssertionError):
        save_text_table_file('text_table_file.test', 'Bruno:27', delimitor=':', constrain_cols=True)
        save_text_table_file('text_table_file.test', ['Bruno', '27'], delimitor=':', constrain_cols=True)
        save_text_table_file('text_table_file.test', {'name': 'Bruno', 'age': '27'}, constrain_cols=True)
    os.remove('text_table_file.test')


def test_read_target_line_on_text_table_file():
    read_target_line_on_text_table_file
    with open('text_table_file.test', 'w') as f:
        f.write(table5)
    info = read_target_line_on_text_table_file('text_table_file.test', 2, delimitor=':')
    assert info['fields'] == ['nome', 'idade']
    assert info['data']['nome'] == "Helena" 
    assert info['data']['idade'] == "42" 
    os.remove('text_table_file.test')


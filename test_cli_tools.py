#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from cli_tools import *
from pytest import fixture, raises

dictionary = {'Daniel': 22, 'Lara': [33, 88, 56], 'Joana': [[40, 67, 86], [13, 15]]}


test_data_folder = ".test_data/"

table1 = ['Daniel:36:dan@gmail.com','Mara:22:mara@outlook.com','Silvia:22:slv@gmail.com']
table2 = [('Daniel', 36, 'dan@gmail.com'), ('Mara', 22, 'mara@outlook.com'), ('Silvia', 22, 'slv@gmail.com')]
table3 = ['Masculino:DF:Branco','Feminino:DF:Pardo','Feminino:DF:Branco', 'Feminino:GO:Indígena', 'Masculino:GO:Branco']
table4 = '{"nome": "Daniel", "idade": 22}\n{"nome": "Helena", "idade": 42}\n{"nome": "Simone", "idade": 30}\n'
table5 = 'nome:idade\nDaniel:22\nHelena:42\nSimone:30\n'

json_string1='''
{
    "info": "Relatório de estudantes",
    "dados":
    [
        {
            "nome": "Daniel",
            "idade": 22,
            "altura": 1.84
        },
        {
            "nome": "Vanessa",
            "idade": 32,
            "altura": 1.72
        },
        {
            "nome": "Antônio",
            "idade": 37,
            "altura": 1.78
        }
    ]
}
'''

json_string2='''
[
    "Banana",
    "Maçã",
    "Pêra"
]
'''

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
    assert next(list_col_responses(table1, 1, delimiter=':')) == '36'
    assert list(list_col_responses(table1, 1, delimiter=':'))[-1] == '22'
    assert list(list_col_responses(table1, 2, delimiter=':'))[-1] == 'slv@gmail.com'


def test_concat_dict_values():
    assert concat_dict_values(dictionary, 'Daniel', 38)['Daniel'] == [22, 38]
    assert concat_dict_values(dictionary, 'Lara', 13)['Lara'] == [[33, 88, 56], 13]
    assert concat_dict_values(dictionary, 'Joana', ['A', 'B'])['Joana'] == [[40, 67, 86], [13, 15], ['A', 'B']]


def test_dict_from_table():
    assert dict_from_table(table1, col_num=0, delimiter=':')['Daniel'] == ['36', 'dan@gmail.com']
    assert dict_from_table(table1, col_num=2, delimiter=':')['slv@gmail.com'] == ['Silvia', '22']
    assert dict_from_table(table1, col_num=1, delimiter=':')['22'] == [['Mara', 'mara@outlook.com'], ['Silvia', 'slv@gmail.com']]
    with raises(AssertionError):
        dict_from_table(1)
        dict_from_table(dictionary)
        dict_from_table(table2)
    


def test_create_line_index():
    index1 = create_line_index(table1, col_num_list=[0,2], delimiter=':')
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
    matrix, references = string_table_to_int_matrix(table3, delimiter=':')
    assert len(matrix[0]) == len(references)
    assert len(references[0]) == 2
    assert len(references[2]) == 3
    with raises(AssertionError):
        string_table_to_int_matrix(1)
        string_table_to_int_matrix(dictionary)
        string_table_to_int_matrix(table3, delimiter=':', reference_data=[{'Masculino': 0}, {'DF': 0}])




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
    info = read_all_text_table_file('text_table_file.test', delimiter=':')
    fields = next(info)
    assert fields == ['nome', 'idade']
    assert next(info)[0] == "Daniel" 
    assert next(info)[1] == "42"
    os.remove('text_table_file.test')


def test_save_text_table_file():
    with open('text_table_file.test', 'w') as f:
        f.write(table5)
    
    save_text_table_file('text_table_file.test', ['Bruno', '27'], delimiter=':', constrain_cols=False)
    save_text_table_file('text_table_file.test', {'nome': 'Manoel', 'idade': '57'}, delimiter=':', constrain_cols=True)
    assert read_target_line_on_text_table_file('text_table_file.test', 4, delimiter=":")['data']['idade'] == '27'
    assert read_target_line_on_text_table_file('text_table_file.test', 5, delimiter=":")['data']['nome'] == 'Manoel'
    with raises(AssertionError):
        save_text_table_file('text_table_file.test', 'Bruno:27', delimiter=':', constrain_cols=True)
        save_text_table_file('text_table_file.test', ['Bruno', '27'], delimiter=':', constrain_cols=True)
        save_text_table_file('text_table_file.test', {'name': 'Bruno', 'age': '27'}, constrain_cols=True)
    os.remove('text_table_file.test')


def test_read_target_line_on_text_table_file():
    with open('text_table_file.test', 'w') as f:
        f.write(table5)
    info = read_target_line_on_text_table_file('text_table_file.test', 2, delimiter=':')
    assert info['fields'] == ['nome', 'idade']
    assert info['data']['nome'] == "Helena" 
    assert info['data']['idade'] == "42" 
    os.remove('text_table_file.test')


def test_create_column_metainfo_file():
    with open('text_table_file.test', 'w') as f:
        f.write(table5)
    create_column_metainfo_file('text_table_file.test', delimiter=':', col_space=3)
    assert os.path.isfile('text_table_file.test')
    metadata = load_json('metainfo_text_table_file.test', file_folder=tmp_folder)
    assert isinstance(metadata, dict)
    assert metadata['nome'] == 9
    assert metadata['idade'] == 5
    os.remove('text_table_file.test')



def test_return_bisect_lists():
    assert return_bisect_lists([1,2,3,4,5,6,7,8,9]) == ([1,2,3,4], 5, [6,7,8,9])
    assert return_bisect_lists([1,2,3,4,5,6,7,8]) == ([1,2,3,4], 5, [6,7,8])
    assert return_bisect_lists([1,2]) == ([1], 2, [])
    assert return_bisect_lists([1]) == 1
    assert return_bisect_lists([]) == None


def test_return_bisect_lists_idx():
    l1 = [1,2,3,4,5,6,7,8,9]
    l2 = [1,2,3,4,5,6,7,8]
    
    idx_left, idx_mid, idx_right = return_bisect_lists_idx(l1, (0, len(l1)))
    assert return_bisect_lists(l1) == (l1[idx_left[0]:idx_left[1]], l1[idx_mid], l1[idx_right[0]:idx_right[1]])

    idx_left, idx_mid, idx_right = return_bisect_lists_idx(l2, (0, len(l2)))
    assert return_bisect_lists(l2) == (l2[idx_left[0]:idx_left[1]], l2[idx_mid], l2[idx_right[0]:idx_right[1]])

def test_bisect_search():
    l1 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    n = itertools.count()
    for element in l1:
        assert bisect_search(element, l1) == True
    assert bisect_search(8, l1) == False
    assert bisect_search(534, list(range(10000))) == True

def test_bisect_search_idx():
    l1 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    n = itertools.count()
    for element in l1:
        assert bisect_search_idx(element, l1, (0,len(l1))) == next(n)
    assert bisect_search_idx('a', l1, (0,len(l1))) == False
    assert bisect_search_idx(7, l1, (0,len(l1))) == False
    assert bisect_search_idx('z', l1, (0,len(l1))) == False


def test_load_json():
    with open('text_json_file.test', 'w') as f:
        f.write(json_string1)
    json_data = load_json('text_json_file.test')
    assert isinstance(json_data, dict)
    assert json_data['dados'][0]['nome'] == 'Daniel'
    assert isinstance(json_data['dados'][0]['idade'], int)
    assert isinstance(json_data['dados'][0]['altura'], float)
    
    with open('text_json_file.test', 'w') as f:
        f.write(json_string2)
    json_data = load_json('text_json_file.test')
    assert json_data == ['Banana', 'Maçã', 'Pêra']
    os.remove('text_json_file.test')


def test_load_csv():
    info = load_csv("csv_table.csv", file_folder=test_data_folder)
    first_line = next(info)
    assert list(first_line.keys()) == ['nome', 'idade', 'altura'] 
    assert first_line['nome'] == 'Daniel'


def test_load_full_csv():
    info = load_full_csv("csv_table.csv", file_folder=test_data_folder)
    assert len(info) == 4
    assert info[3]['nome'] == 'Vicente'


def test_load_csv_cols():
    info1 = load_csv_cols("csv_table.csv", file_folder=test_data_folder, selected_cols=['nome'])
    info2 = load_csv_cols("csv_table.csv", file_folder=test_data_folder, selected_cols=['nome', 'idade'], sort_by='nome')
    info3 = load_csv_cols("csv_table.csv", file_folder=test_data_folder, selected_cols=['nome', 'altura'], sort_by='altura')
    info4 = load_csv_cols("csv_table.csv", file_folder=test_data_folder, selected_cols=['nome', 'idade'], sort_by='idade', reverse_sort=True)
    info5 = load_csv_cols("csv_table.csv", file_folder=test_data_folder, selected_cols=['nome', 'idade'], implict_convert=False)
    assert info1 == [['Daniel'], ['Mariana'], ['Alice'], ['Vicente']]
    assert info2 == [['Alice', 6], ['Daniel', 38], ['Mariana', 36], ['Vicente', 3]]
    assert info3 == [['Vicente', 0.9], ['Alice', 1.2], ['Mariana', 1.7], ['Daniel', 1.84]]
    assert info4 == [['Daniel', 38], ['Mariana', 36], ['Alice', 6], ['Vicente', 3]]
    assert info5 == [['Daniel', '38'], ['Mariana', '36'], ['Alice', '6'], ['Vicente', '3']]

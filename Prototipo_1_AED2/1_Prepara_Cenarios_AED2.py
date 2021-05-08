import f90nml
import pandas as pd
import numpy as np
import os
import shutil


def n_variables(dt_pars):
    if dt_pars.shape[1] % 3 == 0:
        return dt_parametros.shape[1] // 3
    else:
        print("Erro na tabela de parâmetros")
        exit()


def merge_dicts(dict1, dict2):
    """ Recursively merges dict2 into dict1 """
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict2
    for k in dict2:
        if k in dict1:
            dict1[k] = merge_dicts(dict1[k], dict2[k])
        else:
            dict1[k] = dict2[k]
    return dict1


def dicts_for_variables_and_cenarios(dt_pars):
    N_vars = n_variables(dt_pars)
    List_Cena = []
    for _, row in dt_pars.iterrows():
        list_Dics = []
        for k in range(N_vars):
            if not np.isnan(row[2 + 3 * k]):
                Dic = {row[0 + 3 * k]: {row[1 + 3 * k]: row[2 + 3 * k]}}
                list_Dics.append(Dic)

        Dic_Base = list_Dics[0]
        for dic in list_Dics[1:]:
            Dic_Base = merge_dicts(Dic_Base, dic)
        List_Cena.append(Dic_Base)
    return List_Cena

# Diretoro onde será feita a calibração
Dir = '/media/joao/HD-jao/Calibrador_GLM/Prototipo_1_AED2/'

# Arquivo base do modelo GLM, capaz de ser executado
f_base_model = 'Kinneret97'
# Arquivo com as combinações dos parâmetros de teste para calibracao
f_parametros = 'Parametros_de_calibracao_AED2.txt'

# Abre os parametros de calibracao como dataframe
dt_parametros = pd.read_csv(f'{Dir}{f_parametros}', sep='\t')

# Transforma o dataframe com os parametro
# em uma lista de dicionarios
# Os dicionarios são usadas para alterar os parametros dentro do glm3.nml
# Cada dicionário representa um cenário de calibração
Dics_Cenarios = dicts_for_variables_and_cenarios(dt_parametros)

# Checa se existe a pasta para gerar os cenários de calibração
# Se não existe o python cria
Folder_Cenarios = f'{Dir}/Modelos_Calibracao/'
if not os.path.exists(Folder_Cenarios):
    os.mkdir(Folder_Cenarios)

Folder_base = f'{Dir}{f_base_model}/'
# Itera os dicionários
for i in range(0, len(Dics_Cenarios)):
    print(f'{i+1} de {len(Dics_Cenarios)}')
    # Nome da pasta onde será montado o cenário
    Folder_new = f'{Dir}Modelos_Calibracao/{f_base_model}_{i}_AED2/'

    # Se a pasta já existe não precisa recriar
    # A nova pasta é uma copia do arquivo base (Folder_base)
    if not os.path.exists(Folder_new):
        print(f'Criando arquivo {Folder_new}')
        shutil.copytree(Folder_base, Folder_new)
    else:
        print('Arquivo JÁ EXISTE: Apenas NML será alterado')

    # Altera as configuraµções do .nml para ficar igual ao do cenário
    f90nml.patch(Folder_base + '/aed2.nml', Dics_Cenarios[i], Folder_new + '/aed2.nml')

import f90nml
import pandas as pd
import os
import shutil


def n_variables(dt_pars):
    if dt_pars.shape[1] % 4 == 0:
        return dt_parametros.shape[1] // 4
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
            if not pd.isnull(row[2 + 4 * k]):
                Dic = {row[0 + 4 * k]: {row[1 + 4 * k]: {row[2 + 4 * k]: row[3 + 4 * k]}}}
                list_Dics.append(Dic)

        Dic_Base = list_Dics[0]
        for dic in list_Dics[1:]:
            Dic_Base = merge_dicts(Dic_Base, dic)
        List_Cena.append(Dic_Base)
    return List_Cena


# Diretoro onde será feita a calibração
Dir = '/media/joao/HD-jao/Calibrador_GLM/Prototipo_1_AED2_Phyto/'

# Arquivo base do modelo GLM, capaz de ser executado
f_base_model = 'Kinneret97'
# Arquivo com as combinações dos parâmetros de teste para calibracao
f_parametros = 'Parametros_de_calibracao_AED2_Phyto.txt'

# Abre os parametros de calibracao como dataframe
dt_parametros = pd.read_csv(f'{Dir}{f_parametros}', sep='\t')
dt_parametros[['SubBloco', 'Nome']] = dt_parametros['Nome'].str.split('%', 1, expand=True)
dt_parametros = dt_parametros[['Bloco', 'SubBloco', 'Nome', 'Valor']]
dt_parametros['SubBloco'] = dt_parametros['SubBloco'].str.strip()
dt_parametros['Nome'] = dt_parametros['Nome'].str.strip()

# Checa se existe a pasta para gerar os cenários de calibração
# Se não existe o python cria
Folder_Cenarios = f'{Dir}/Modelos_Calibracao/'
if not os.path.exists(Folder_Cenarios):
    os.mkdir(Folder_Cenarios)

Folder_base = f'{Dir}{f_base_model}/'
# Itera as linhas do arquivo de parametros
for i, row in dt_parametros.iterrows():
    print(f'{i + 1} de {len(dt_parametros)}')
    # Nome da pasta onde será montado o cenário
    Folder_new = f'{Dir}Modelos_Calibracao/{f_base_model}_{i}_Phyto/'

    # Se a pasta já existe não precisa recriar
    # A nova pasta é uma copia do arquivo base (Folder_base)
    if not os.path.exists(Folder_new):
        print(f'Criando arquivo {Folder_new}')
        shutil.copytree(Folder_base, Folder_new)
    else:
        print('Arquivo JÁ EXISTE: Apenas NML será alterado')

    nml = f90nml.read(Folder_base + '/aed2_phyto_pars.nml')

    for k in range(0, len(row)//4):
        if not pd.isnull(row[0 + 4 * k]):
            parameters = [float(s) for s in row[3+4*k].split(', ')]
            nml[row[0 + 4 * k]][row[1 + 4 * k]][row[2 + 4 * k]] = parameters



    # Altera as configuraµções do .nml para ficar igual ao do cenário
    os.remove(Folder_new + '/aed2_phyto_pars.nml')
    nml.write(Folder_new + '/aed2_phyto_pars.nml')
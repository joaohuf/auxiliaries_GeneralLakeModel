import os
from netCDF4 import Dataset
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import netCDF4
from scipy.interpolate import interp1d

def formata_netcdf(dataset, list_keys=None):

    list_par = []
    if not list_keys:
        list_keys = dataset.dimensions.keys()

    for key in list_keys:

        # Abre cada uma das  chaves e mascara elas com NaN
        par_masked = dataset[key][:]
        if np.ma.isMaskedArray(par_masked): par = par_masked.filled(np.nan)
        else: par = par_masked

        # Formata o tempo em datetime
        if key == 'time':
            par = netCDF4.num2date(par, units=dataset.variables[key].units, only_use_cftime_datetimes=False)

        list_par.append(par)
    return list_par

def Matriz_Dados(Array_Zs, Array_Par, Hs_base, metodo='next'):
    # A PRECISÃO DEPENDE DO DELTA H ESCOLHIDO
    # Cria a matriz repetidindo as camadas com o dados acima

    # z = np.array([[1, 2, 3, 4], [1, 2, 3, 4]])
    # par = np.array([[0, 0, 1, 2], [1, 2, 0, 4]])
    # Hs = [0, 1, 2, 3, 4, 5]
    # matrix = Matriz_Dados(z, par, Hs)
    # print(matrix)

    Zs = np.round(Array_Zs, 2)

    Linhas = []
    for z, Par in zip(Zs, Array_Par):
        z = z.flatten()
        Par = Par.flatten()

        funcao = interp1d(z, Par, kind=metodo, fill_value="extrapolate")
        Par_New = funcao(Hs_base)

        Linhas.append(Par_New)

    Matrix = np.stack(Linhas, axis=0)
    Matrix = np.transpose(Matrix)

    return Matrix


# Diretorio base da calibracao
Dir = 'E:/Calibrador_GLM/Prototipo_1_AED2/'
Folder_Cenarios = f'{Dir}Modelos_Calibracao/'
# Nome do arquivo com os dados medidos
f_medicoes = 'Dados_Medidos_netcdf_AED2.txt'
# Frequencia para fazer a análise
Freq = 'D'

# Delta a ser usado na escala de profundidades
# Como o grid do GLM é irregular, prefiri reescalar ele para facilitar a manipulação
delta = 0.10
# Determina o número de casas decimais da profundidade
decimal_cases = str(delta)[::-1].find('.')

# Separa os sub_diretorios dentro da pasta Modelos_Calibracao
sub_dirs = [f'{Folder_Cenarios}{sub}/' for sub in os.listdir(Folder_Cenarios)]

# Abre os dados medidos como dataframe
dt_medicoes = pd.read_csv(f'{Dir}{f_medicoes}', sep='\t', index_col=[0, 1], parse_dates=True)

# Itera entre as variaveis a serem comparadas
for var_name in dt_medicoes.index.levels[0]:

    # Separa só os dados da variável analisada
    dt_var = dt_medicoes.loc[var_name]
    dt_var.index = pd.to_datetime(dt_var.index)

    # Arruma a frequência pela média
    dt_var = dt_var.groupby(pd.Grouper(freq=Freq)).mean().reset_index().dropna()
    # Arredonda a profundidade
    dt_var['Lake Level'] = dt_var['Lake Level'].round(decimal_cases)
    # Padroniza os nomes das colunas
    dt_var.columns = ['Time', 'Level', 'Medido']
    # Força as medições para o grid de profundidades anterior
    dt_var['Level'] = delta * round(dt_var['Level'] / delta)
    # Se duas medições forem jogadas para o mesmo interlavo de profundidade e tempo, usa a média delas
    dt_var = dt_var.groupby(['Time', 'Level']).mean()

    # Lista para guardar os resultados
    metricas = []
    for k, sub_dir in enumerate(sub_dirs):
        print(f'{k + 1} diretório de {len(sub_dirs)}')

        # Pega número do cenário
        i_modelo = sub_dir.split('_')[-2]

        # Abre os resultados do netcdf do GLM
        f_netcdf = f'{sub_dir}output/output.nc'
        Data = Dataset(f_netcdf, "r", format="NETCDF4")

        # Matriz BRUTA de dados do netcdf
        time, zs, var = formata_netcdf(Data, ['time', 'z', var_name])

        # Gera a série temporal de níveis máximos
        Nivel = np.array([max(zs[i].flatten()) for i in range(0, zs.shape[0])])
        # Gera os valores da nova escala de temperatura
        Hs = np.arange(0, round(np.max(Nivel)+delta, decimal_cases)+delta, delta)

        # Gera uma matriz simplificada
        # E também reescala as profundidades
        var = Matriz_Dados(zs, var, Hs)

        # Transforma os dados em dataframe
        dt_netcdf = pd.DataFrame(var, columns=time, index=Hs)
        # Arruma a frequência
        dt_netcdf = dt_netcdf.groupby(pd.Grouper(freq=Freq, axis=1), axis=1).mean()
        # Deixa no mesmo formato que o dataframe de dados medidos
        dt_netcdf = pd.melt(dt_netcdf.reset_index(), id_vars='index').dropna()
        # Renomeia as colunas
        dt_netcdf.columns = ['Level', 'Time', 'Calculado']

        # COmbina os dois dataframes com base nas colunas de tempo e nível
        dt_comb = pd.merge(dt_netcdf, dt_var, on=['Time', 'Level'])
        # Separa os dados medidos e calculados já emparelhados
        medicao = dt_comb['Medido'].values
        calculo = dt_comb['Calculado'].values

        # Calcula as métricas
        mae = mean_absolute_error(y_true=medicao, y_pred=calculo)
        mse = mean_squared_error(y_true=medicao, y_pred=calculo)
        rmse = np.sqrt(mean_squared_error(y_true=medicao, y_pred=calculo))
        r2 = r2_score(y_true=medicao, y_pred=calculo)

        # Salva os resultados
        metricas.append([i_modelo, mae, mse, rmse, r2])

    # Cria um dataframe com os resultados e formata
    dt_results = pd.DataFrame(metricas, columns=['index', 'MAE', 'MSE', 'RMSE', 'R2'])
    dt_results = dt_results.set_index('index').sort_index()
    dt_results = dt_results.round(3)

    # Salva os resultados das métricas de cada variável
    save_name = var_name.replace(' ', '_')
    dt_results.to_csv(f'{Dir}Resultados/Metricas_{save_name}_netcdf_AED2.txt', sep='\t')
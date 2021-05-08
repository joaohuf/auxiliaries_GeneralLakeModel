import os
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
from datetime import timedelta

# Diretorio base da calibracao
Dir = 'E:\\Calibrador_GLM\\Prototipo_1_GLM\\'
Folder_Cenarios = f'{Dir}Modelos_Calibracao/'
# Nome do arquivo com os dados medidos
f_medicoes = 'Dados_Medidos.txt'
# Nome do .csv geral de saida do GLM
f_lake = 'lake.csv'
# Frequencia para fazer a análise
Freq = 'D'

# Separa os sub_diretorios dentro da pasta Modelos_Calibracao
sub_dirs = [f'{Folder_Cenarios}{sub}/' for sub in os.listdir(Folder_Cenarios)]

# Abre os dados medidos como dataframe
dt_medicoes = pd.read_csv(f'{Dir}{f_medicoes}', sep='\t', index_col=0, parse_dates=True)

# Itera entre as variaveis a serem comparadas
for var in dt_medicoes.columns:

    # Lista para guardar os resultados
    metricas = []
    # Itera entre os modelos
    for sub_dir in sub_dirs:
        # Pega número do cenário
        i_modelo = sub_dir.split('_')[-1][:-1]

        # Abre os resultados do GLM como dataframe
        f_csv = f'{sub_dir}output/lake.csv'
        dt_csv_general = pd.read_csv(f_csv, sep=',')

        # Acerta a formatação do tempo, pois 24:00 não pode ser reconhecido
        dt_csv_general['time Original'] = dt_csv_general['time']
        dt_csv_general['time'] = dt_csv_general['time'].str.replace('24:00', '00:00')
        dt_csv_general['time'] = pd.to_datetime(dt_csv_general['time'], format='%Y-%m-%d %H:%M:%S')

        # Cria um máscara somar 1 dia apenas nos valores que tiveram a data alterada
        mask = dt_csv_general['time Original'].str.contains('24:00')
        dt_csv_general['time'][mask] += timedelta(days=1)
        dt_csv_general = dt_csv_general.set_index('time')

        # Agrupa pela frequencia dos dados medidos
        dt_csv_general = dt_csv_general.groupby(pd.Grouper(freq='D')).mean()
        dt_csv_general = dt_csv_general.resample(Freq).ffill()

        # Coloca os dois dataframes lado a lado, para pegar os períodos em comum
        dt_pivot = pd.concat([dt_medicoes[var], dt_csv_general[var]], axis=1).dropna()
        dt_pivot.columns = ['Medido', 'Calculado']

        # Lista com os dados medidos e os calculados
        medicao = dt_pivot['Medido'].values
        calculo = dt_pivot['Calculado'].values

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
    save_name = var.replace(' ', '_')
    dt_results.to_csv(f'{Dir}Resultados/Metricas_{save_name}.txt', sep='\t')
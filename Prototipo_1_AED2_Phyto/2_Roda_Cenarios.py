import multiprocessing
import os
import time
import subprocess

def Executa_GLM_Linux(Dir, GLM_path='/usr/local/bin/glm', graph=False):
    comando = 'cd ' + Dir + ';' + GLM_path
    if graph: comando = comando + ' --xdisp'
    subprocess.call(comando, shell=True)

def Executa_GLM_Win(Dir, GLM_path='C:\Program Files\GLM\glm', graph=False):
    comando = [GLM_path]
    if graph: comando.append('--xdisp')

    try:
        subprocess.check_call(comando, cwd=Dir, shell=False)
    except subprocess.CalledProcessError:
        Executa_GLM_Win(Dir)

# PRIMEIRO
# MUDAR O CAMINHO DO GLM DENTRO DA FUNCAO Executa_GLM
# MUDAR O CAMINHO DO GLM DENTRO DA FUNCAO Executa_GLM
# MUDAR O CAMINHO DO GLM DENTRO DA FUNCAO Executa_GLM
# MUDAR O CAMINHO DO GLM DENTRO DA FUNCAO Executa_GLM

# Diretorio de calibracao e Pasta com os modelos criados
Dir = '/media/joao/HD-jao/Calibrador_GLM/Prototipo_1_AED2_Phyto/'
Folder_Cenarios = f'{Dir}Modelos_Calibracao/'

# Separa os sub_diretorios dentro da pasta Modelos_Calibracao
sub_dirs = [f'{Folder_Cenarios}{sub}/' for sub in os.listdir(Folder_Cenarios)]

if __name__ == '__main__':
    # Determina o número de processadore que a cpu possui
    N = multiprocessing.cpu_count()
    # Determina quando processadores usar
    pool = multiprocessing.Pool(processes=N)

    start_time = time.time()

    # Executa o GLM em paralelo
    pool.map(Executa_GLM_Win, sub_dirs)

    print("--- %s seconds ---" % (time.time() - start_time))

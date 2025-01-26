# -*- coding: utf-8 -*-
"""SAE_Optuna_segmentado.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1w7wnRVoVCcGAqPV22d0RdKkkydqvtNM0
"""

import time

# Começa a contagem do tempo
start_time = time.time()

!pip install keras==3.1.1
!pip install tensorflow==2.11.0
!pip install optuna
import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import scipy.io as sio
import keras
import numpy as np
from keras import backend as K
import seaborn as sns
from scipy.stats import gaussian_kde
import optuna
from sklearn.preprocessing import MinMaxScaler
import os
import re
from sklearn.model_selection import train_test_split
from keras.layers import Input, Dense, Lambda, Dropout
from keras.initializers import GlorotNormal, HeNormal
from keras.models import Model
import pandas as pd
import scipy.io as sio
import keras
from keras import backend as K
import seaborn as sns
from scipy.stats import gaussian_kde

# Função para extrair números do nome do arquivo
def ordenar_numericamente(nome_arquivo):
    # Acha todos os números no nome do arquivo
    numeros = re.findall(r'\d+', nome_arquivo)
    # Converte os números encontrados para inteiros e retorna como uma tupla
    return tuple(map(int, numeros))

diretorio1 = r'c:\Users\User\Desktop\1st-novo'
diretorio2 = r'c:\Users\User\Desktop\3rd'
diretorio3 = r'c:\Users\User\Desktop\5th-novo'

arquivos_1 = sorted(os.listdir(diretorio1), key=ordenar_numericamente)
arquivos_2 = sorted(os.listdir(diretorio2), key=ordenar_numericamente)
arquivos_3 = sorted(os.listdir(diretorio3), key=ordenar_numericamente)

print(arquivos_1)
print(arquivos_2)
print(arquivos_3)

# Carregar os dados de Irregularidade 1
corr1 = []
arquivos_corr1 = os.listdir(diretorio1)
for arquivo in arquivos_corr1[:100]:
    if arquivo.endswith(".mat"):
        caminho_arquivo = os.path.join(diretorio1, arquivo)
        arquivo_mat = sio.loadmat(caminho_arquivo)
        dados = arquivo_mat['segment'][:,0]
        corr1.append(dados)

corr1 = np.array(corr1)
print(corr1.shape)

plt.figure(figsize=(10, 6))
plt.plot(corr1[10], label='Original')  # Corrigido para massa0[50]
plt.title('Sinal Original - Arquivo 0 - Corrugação 1')
plt.xlabel('Amostras')
plt.ylabel('Valores')
plt.legend()
plt.show()

# Carregar os dados de Irregularidade 2
corr2 = []
arquivos_corr2 = os.listdir(diretorio2)
for arquivo in arquivos_corr2[:100]:
    if arquivo.endswith(".mat"):
        caminho_arquivo = os.path.join(diretorio2, arquivo)
        arquivo_mat = sio.loadmat(caminho_arquivo)
        dados = arquivo_mat['segment'][:, 0]
        corr2.append(dados)

corr2 = np.array(corr2)
print(corr2.shape)

plt.figure(figsize=(10, 6))
plt.plot(corr2[0], label='Original')  # Corrigido para massa0[50]
plt.title('Sinal Original - Arquivo 0 - Corrugação 2')
plt.xlabel('Amostras')
plt.ylabel('Valores')
plt.legend()
plt.show()

corr3 = []
arquivos_corr3 = os.listdir(diretorio3)
for arquivo in arquivos_corr3[:100]:
    if arquivo.endswith(".mat"):
        caminho_arquivo = os.path.join(diretorio3, arquivo)
        arquivo_mat = sio.loadmat(caminho_arquivo)
        dados = arquivo_mat['segment'][:, 0]

        # Verificar se o comprimento dos dados é 3916 antes de adicionar
        if len(dados) == 3916:
            corr3.append(dados)

# Converter para um array numpy
corr3 = np.array(corr3)

# Exibir o formato do array e plotar o primeiro elemento
print(corr3.shape)

plt.figure(figsize=(10, 6))
plt.plot(corr3[0], label='Original')
plt.title('Sinal Original - Arquivo 0 - Corrugação 3')
plt.xlabel('Amostras')
plt.ylabel('Valores')
plt.legend()
plt.show()

# Calcular a média e o desvio padrão dos dados
media_corr1 = np.mean(corr1)
desvio_corr1 = np.std(corr1)

media_corr2 = np.mean(corr2)
desvio_corr2 = np.std(corr2)

media_corr3 = np.mean(corr3)
desvio_corr3 = np.std(corr3)

# Normalizar
corr1 = (corr1 - media_corr1) / desvio_corr1
corr2 = (corr2 - media_corr2) / desvio_corr2
corr3 = (corr3 - media_corr3) / desvio_corr3

print(corr1.shape)
print(corr2.shape)
print(corr3.shape)

# Definindo a função do modelo Sparse Autoencoder com Optuna
def create_and_train_sae(trial):
    input_dim = corr1.shape[1]
    latent_dim = trial.suggest_int('latent_dim', 150, 500)
    learning_rate = trial.suggest_float('learning_rate', 1e-6, 1e-3, log=True)
    batch_size = trial.suggest_int('batch_size', 2, 32)
    epochs = trial.suggest_int('epochs', 2, 350)
    lambda_sparse = trial.suggest_float('lambda_sparse', 1e-7, 1e-3, log=True)

    # Definição do SAE com regularização L1
    inputs = keras.Input(shape=(input_dim,))
    encoded = keras.layers.Dense(latent_dim, activation='relu', activity_regularizer=keras.regularizers.l1(lambda_sparse))(inputs)
    decoded = keras.layers.Dense(input_dim, activation='linear')(encoded)
    sae = keras.Model(inputs, decoded)

    # Compilação do modelo
    sae.compile(optimizer=keras.optimizers.Nadam(learning_rate=learning_rate), loss='mean_squared_error')

    # Dividir corr1 em treino e teste
    np.random.shuffle(corr1)
    corr1_train, corr1_test = corr1[:70], corr1[70:]

    # Treinamento
    sae.fit(corr1_train, corr1_train, epochs=epochs, batch_size=batch_size, shuffle=True, verbose=0)

    # Avaliação de reconstrução para calculo do erro residual médio
    corr1_recon_train = sae.predict(corr1_train)
    corr1_recon_test = sae.predict(corr1_test)
    corr2_recon = sae.predict(corr2)
    corr3_recon = sae.predict(corr3)

    error_train = np.mean(np.square(corr1_train - corr1_recon_train), axis=1)
    error_test = np.mean(np.square(corr1_test - corr1_recon_test), axis=1)
    error_corr2 = np.mean(np.square(corr2 - corr2_recon), axis=1)
    error_corr3 = np.mean(np.square(corr3 - corr3_recon), axis=1)

    # Erro médio de reconstrução
    reconstruction_error = np.mean(np.concatenate([error_train, error_test, error_corr2, error_corr3]))

    # Plotar sinais originais e reconstruídos para cada repetição
    def plot_signals(original, reconstructed, title, color_orig="blue", color_recon="orange"):
        plt.figure(figsize=(12, 6))
        for i in range(len(original)):
            plt.plot(np.abs(original[i]), color=color_orig, label=f'Sinal {i+1} (Original)')
            plt.plot(np.abs(reconstructed[i]), color=color_recon, label=f'Sinal {i+1} (Reconstruído)')
        plt.xlabel('Frequência')
        plt.ylabel('Amplitude')
        plt.title(title)
        plt.show()

    plot_signals(corr1_train, corr1_recon_train, 'Treino Corrugação 1 - Sinais Originais e Reconstruídos')
    plot_signals(corr1_test, corr1_recon_test, 'Teste Corrugação 1 - Sinais Originais e Reconstruídos')
    plot_signals(corr2, corr2_recon, 'Corrugação 2 - Sinais Originais e Reconstruídos')
    plot_signals(corr3, corr3_recon, 'Corrugação 3 - Sinais Originais e Reconstruídos')

    return reconstruction_error

from tensorflow.keras import layers
# Executando o estudo com Optuna
study = optuna.create_study(direction="minimize")
study.optimize(create_and_train_sae, n_trials=50)

# Imprime os melhores hiperparâmetros
print("Melhores parâmetros:")
print(study.best_params)

# Resultados finais
print("Melhor erro de reconstrução:", study.best_value)

learning_rate= 5.659338648510935e-06
epochs= 183
batch_size= 2

# Definição dos parâmetros do SAE
input_dim = corr1.shape[1]
latent_dim = 174
lambda_sparse = 1.5579602116725724e-07  # Fator de regularização sparsity


# Número de repetições desejadas
num_repeticoes = 25

# Lista para armazenar os erros residuais de cada repetição
erros_residuais_por_repeticao = []

# Lista para armazenar os erros residuais totais
erros_residuais_totais = []

resi_latente_train_acumulado = []
resi_latente_teste_acumulado = []
resi_latente_corr2_acumulado = []
resi_latente_corr3_acumulado = []

#keras.utils.plot_model(encoder, to_file='model.png', show_shapes=True)

for repeticao in range(num_repeticoes):
    print(f'Repetição {repeticao + 1}')

    # Dividir massa0 em massa0Treino e massa0Teste
    np.random.shuffle(corr1)
    corr1Treino = corr1[:35]
    corr1Teste = corr1[35:]
    # Definição do modelo SAE
    inputs = keras.Input(shape=(input_dim,))
    encoded = keras.layers.Dense(latent_dim, activation='relu')(inputs)
    # Adicionando regularização L1 para promover esparsidade
    regularizer = keras.regularizers.l1(lambda_sparse)
    sparse_activity = keras.layers.ActivityRegularization(l1=lambda_sparse)(encoded)
    decoded = keras.layers.Dense(input_dim, activation='linear')(encoded)

    sae = keras.Model(inputs, decoded, name='sae_mlp')


    # Definir um otimizador Adam personalizado com um learning rate específico
    custom_optimizer = keras.optimizers.Nadam(learning_rate=learning_rate)

    # Compilando o modelo AE com o otimizador personalizado
    sae.compile(optimizer=custom_optimizer, loss='mean_squared_error')

    # Treinamento do SAE com os dados de Massa 0
    sae.fit(corr1Treino, corr1Treino, epochs=epochs, batch_size=batch_size, shuffle=True, verbose=0)

    # Reconstruir os sinais
    corr1_reconstruidoTreino = sae.predict(corr1Treino)
    corr1_reconstruidoTeste = sae.predict(corr1Teste)
    corr2_reconstruido = sae.predict(corr2)
    corr3_reconstruido = sae.predict(corr3)

    # Calcular os erros residuais e armazená-los
    erroTreino = np.mean(np.square(corr1Treino - corr1_reconstruidoTreino), axis=1)
    erro_corr1Teste = np.mean(np.square(corr1Teste - corr1_reconstruidoTeste), axis=1)
    erro_corr2 = np.mean(np.square(corr2 - corr2_reconstruido), axis=1)
    erro_corr3 = np.mean(np.square(corr3 - corr3_reconstruido), axis=1)

    erros_residuais = np.concatenate([erroTreino, erro_corr1Teste, erro_corr2, erro_corr3])
    erros_residuais_por_repeticao.append(erros_residuais)
    # Coletar resíduos da camada latente para Corrugação 1 Treino
    resi_latente_train = sae.predict(corr1Treino)

    # Coletar resíduos da camada latente para Corrugação 1 Teste
    resi_latente_teste = sae.predict(corr1Teste)

    # Coletar resíduos da camada latente para Corrugação 2
    resi_latente_corr2 = sae.predict(corr2)

    # Coletar resíduos da camada latente para Corrugação 3
    resi_latente_corr3 = sae.predict(corr3)

    # Acumular os resíduos da camada latente para Corrugação 1 Treino
    resi_latente_train_acumulado.append(resi_latente_train)

    # Acumular os resíduos da camada latente para Corrugação 1 Teste
    resi_latente_teste_acumulado.append(resi_latente_teste)

    # Acumular os resíduos da camada latente para Corrugação 2
    resi_latente_corr2_acumulado.append(resi_latente_corr2)

    # Acumular os resíduos da camada latente para Corrugação 3
    resi_latente_corr3_acumulado.append(resi_latente_corr3)

    # Plotar os sinais originais e reconstruídos de corr1_train
    plt.figure(figsize=(12, 6))
    for i in range(len(corr1Treino)):
        plt.plot(np.abs(corr1Treino[i]), color='blue', label=f'Sinal {i+1} - Corrugação 1 (Original) - Treino')
    for i in range(len(corr1Treino)):
        plt.plot(np.abs(corr1_reconstruidoTreino[i]), color='orange', label=f'Sinal {i+1} - Corrugação 1 (Reconstruído) - Treino')

    plt.xlabel('Frequência')
    plt.ylabel('Amplitude')
    plt.title(f'Sinais Originais e Reconstruídos do Treino de Corrugação 1 - Repetição {repeticao + 1}')
    plt.show()

    # Plotar os sinais originais e reconstruídos de corr1_test
    plt.figure(figsize=(12, 6))
    for i in range(len(corr1Teste)):
        plt.plot(np.abs(corr1Teste[i]), color='blue', label=f'Sinal {i+1} - Corrugação 1 (Original) - Validação')
    for i in range(len(corr1Teste)):
        plt.plot(np.abs(corr1_reconstruidoTeste[i]), color='orange', label=f'Sinal {i+1} - Corrugação 1 (Reconstruído) - Validação')

    plt.xlabel('Frequência')
    plt.ylabel('Amplitude')
    plt.title(f'Sinais Originais e Reconstruídos da Validação de Corrugação 1 - Repetição {repeticao + 1}')
    plt.show()

    # Plotar os sinais originais e reconstruídos de corr2
    plt.figure(figsize=(12, 6))
    for i in range(len(corr2)):
        plt.plot(np.abs(corr2[i]), color='blue', label=f'Sinal {i+1} - Corrugação 2 (Original)')
    for i in range(len(corr2)):
        plt.plot(np.abs(corr2_reconstruido[i]), color='orange', label=f'Sinal {i+1} - Corrugação 2 (Reconstruído)')

    plt.xlabel('Frequência')
    plt.ylabel('Amplitude')
    plt.title(f'Sinais Originais e Reconstruídos do teste de Corrugação 2 - Repetição {repeticao + 1}')
    plt.show()

    # Plotar os sinais originais e reconstruídos de corr3
    plt.figure(figsize=(12, 6))
    for i in range(len(corr3)):
        plt.plot(np.abs(corr3[i]), color='blue', label=f'Sinal {i+1} - Corrugação 3 (Original)')
    for i in range(len(corr3)):
        plt.plot(np.abs(corr3_reconstruido[i]), color='orange', label=f'Sinal {i+1} - Corrugação 3 (Reconstruído)')

    plt.xlabel('Frequência')
    plt.ylabel('Amplitude')
    plt.title(f'Sinais Originais e Reconstruídos do teste de Corrugação 3 - Repetição {repeticao + 1}')
    plt.show()

# Calcular a média dos erros residuais para cada ponto
media_erros_residuais = np.mean(erros_residuais_por_repeticao, axis=0)

# Converter as listas acumuladas em matrizes NumPy
resi_latente_train_acumulado = np.array(resi_latente_train_acumulado)
resi_latente_teste_acumulado = np.array(resi_latente_teste_acumulado)
resi_latente_corr2_acumulado = np.array(resi_latente_corr2_acumulado)
resi_latente_corr3_acumulado = np.array(resi_latente_corr3_acumulado)

for j in range(latent_dim):
    kde_latente_train = gaussian_kde(resi_latente_train_acumulado[:, :, j].flatten())
    kde_latente_teste = gaussian_kde(resi_latente_teste_acumulado[:, :, j].flatten())
    kde_latente_corr2 = gaussian_kde(resi_latente_corr2_acumulado[:, :, j].flatten())
    kde_latente_corr3 = gaussian_kde(resi_latente_corr3_acumulado[:, :, j].flatten())


    x = np.linspace(min(resi_latente_train_acumulado[:, :, j].flatten()),
                    max(resi_latente_train_acumulado[:, :, j].flatten()), 1000)

# Calcular a média e o desvio padrão dos resíduos da camada latente para cada classe
media_resi_latente_corr1 = np.mean(resi_latente_train_acumulado, axis=(0, 1))
desvio_resi_latente_corr1 = np.std(resi_latente_train_acumulado, axis=(0, 1))
media_resi_latente_teste_corr1 = np.mean(resi_latente_teste_acumulado, axis=(0, 1))
desvio_resi_latente_teste_corr1 = np.std(resi_latente_teste_acumulado, axis=(0, 1))
media_resi_latente_corr2 = np.mean(resi_latente_corr2_acumulado, axis=(0, 1))
desvio_resi_latente_corr2 = np.std(resi_latente_corr2_acumulado, axis=(0, 1))
media_resi_latente_corr3 = np.mean(resi_latente_corr3_acumulado, axis=(0, 1))
desvio_resi_latente_corr3 = np.std(resi_latente_corr3_acumulado, axis=(0, 1))

# Parâmetros
r = 2  # Subgroups com r observações de x (quantidade de sinais)
m = latent_dim  # Número de características da camada latente

# Matriz de características da camada latente para treinamento e teste
features_train = np.concatenate(resi_latente_train_acumulado, axis=0)
features_test = np.concatenate(resi_latente_teste_acumulado, axis=0)
features_corr2 = np.concatenate(resi_latente_corr2_acumulado, axis=0)
features_corr3 = np.concatenate(resi_latente_corr3_acumulado, axis=0)

# Número de grupos coletados no estado de referência (treinamento) e teste
s_train = len(resi_latente_train_acumulado)
s_test = len(resi_latente_teste_acumulado)
s_corr2 = len(resi_latente_corr2_acumulado)
s_corr3 = len(resi_latente_corr3_acumulado)

# Estimador S1:
S = np.cov(features_train, rowvar=False)  # Matriz de covariância das características da camada latente

# T-squared para a fase de treinamento
x_ref_m = np.mean(features_train, axis=0)  # Média dos dados de treinamento
T_squared_train = []

for i in range(0, len(features_train), r):
    x = features_train[i:i+r, :]  # "Novos" dados
    x_m = np.mean(x, axis=0)  # Média dos "novos" dados
    T_squared_train.append(r * np.dot((x_m - x_ref_m), np.dot(np.linalg.pinv(S), (x_m - x_ref_m))))

# T-squared para a fase de teste
T_squared_test = []

for i in range(0, len(features_test), r):
    x = features_test[i:i+r, :]  # Novos dados
    x_m = np.mean(x, axis=0)  # Média dos novos dados
    T_squared_test.append(r * np.dot((x_m - x_ref_m), np.dot(np.linalg.pinv(S), (x_m - x_ref_m))))

# T-squared para a Massa 1
T_squared_corr2 = []

for i in range(0, len(features_corr2), r):
    x = features_corr2[i:i+r, :]  # Novos dados
    x_m = np.mean(x, axis=0)  # Média dos novos dados
    T_squared_corr2.append(r * np.dot((x_m - x_ref_m), np.dot(np.linalg.pinv(S), (x_m - x_ref_m))))

# T-squared para a Massa 2
T_squared_corr3 = []

for i in range(0, len(features_corr3), r):
    x = features_corr3[i:i+r, :]  # Novos dados
    x_m = np.mean(x, axis=0)  # Média dos novos dados
    T_squared_corr3.append(r * np.dot((x_m - x_ref_m), np.dot(np.linalg.pinv(S), (x_m - x_ref_m))))


# Calcular o percentil 95 dos valores de T_squared_train
percentile_95 = np.percentile(T_squared_train, 95)

# Definir a UCL como um múltiplo do percentil 95
UCL = percentile_95

# Criar uma lista única de UCL para todas as fases
UCL_axis = np.full(len(T_squared_train) + len(T_squared_test) + len(T_squared_corr2) + len(T_squared_corr3), UCL)


# Plotar carta de controle T^2 de Hotelling para treinamento, teste, Massa 1, Massa 2, Massa 3 e Massa 4
plt.figure(figsize=(16, 8))

# Plotar carta de controle T^2 de Hotelling para treinamento
plt.plot(np.arange(len(T_squared_train)), T_squared_train, 'x', color='#2924be', label='training')

# Plotar carta de controle T^2 de Hotelling para teste
plt.plot(np.arange(len(T_squared_train), len(T_squared_train) + len(T_squared_test)), T_squared_test, 'h', color='#71bdd7', fillstyle='none', label='validation')

# Plotar carta de controle T^2 de Hotelling para Corrugação 2
plt.plot(np.arange(len(T_squared_train) + len(T_squared_test), len(T_squared_train) + len(T_squared_test) + len(T_squared_corr2)), T_squared_corr2, linestyle='None', marker=(8, 2, 0), markersize=5, mew=0.75, color='#9c1732', label='monitoring')

# Plotar carta de controle T^2 de Hotelling para Corrugação 3
plt.plot(np.arange(len(T_squared_train) + len(T_squared_test) + len(T_squared_corr2), len(T_squared_train) + len(T_squared_test) + len(T_squared_corr2) + len(T_squared_corr3)), T_squared_corr3, 'D', color='#82b33d', fillstyle='none', markersize=4, mew=0.75, label='monitoring')

# Plotar carta de controle T^2 de Hotelling para o Limite de Controle Superior (UCL)
plt.plot(np.arange(len(UCL_axis)), UCL_axis, 'k-', linewidth=3, label='UCL')

#  adicionar linhas verticais tracejadas a cada 200 pontos
for i in range(0, len(T_squared_train) + len(T_squared_test) + len(T_squared_corr2) + len(T_squared_corr3), 60):
    plt.axvline(x=i, linestyle='--', color='gray', linewidth=1, dashes=(6, 6))
#  adicionar linhas verticais tracejadas a cada 200 pontos
for i in range(len(T_squared_train) + len(T_squared_test) + len(T_squared_corr2) + len(T_squared_corr3), 345, 44):
    plt.axvline(x=i, linestyle='--', color='gray', linewidth=1, dashes=(6, 6))
plt.yscale('log')

plt.xlabel('data subgroups')
plt.ylabel('T²')
plt.legend()

plt.show()

def plot_t_squared_boxplots():
    import matplotlib.pyplot as plt

    # Dados para os boxplots
    data = [T_squared_train, T_squared_test, T_squared_corr2, T_squared_corr3]
    labels = ['Training', 'Validation', 'Corrugation 2', 'Corrugation 3']

    plt.figure(figsize=(16, 8))
    plt.boxplot(data, labels=labels)

    # Configurar a escala logarítmica no eixo y
    plt.yscale('log')

    # Ajustar títulos e legendas
    plt.xlabel('Irregularity Classes', fontsize=fontsize)
    plt.ylabel('T² values', fontsize=fontsize)
    plt.title('Boxplots dos valores de T-squared para diferentes classes de irregularidades', fontsize=fontsize - 2)

    # Configuração do tamanho das fontes nos ticks
    plt.tick_params(axis='both', which='major', labelsize=tick_fontsize)
    plt.tick_params(axis='both', which='minor', labelsize=tick_fontsize - 2)

    plt.show()

# Chamar a função de plotagem dos boxplots
plot_t_squared_boxplots()

# Termina a contagem do tempo
end_time = time.time()

# Calcula o tempo decorrido
tempo_decorrido = end_time - start_time

print(f"Tempo de execução: {tempo_decorrido} segundos")

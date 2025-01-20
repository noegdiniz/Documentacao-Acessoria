import matplotlib.pyplot as plt
import numpy as np
import random

# Crie uma lista com os dados a serem plotados
dados = [(random.random() * random.randint(1,10)) / random.random() for n in range(10)]

# Gere um gráfico de histograma
plt.hist(dados, bins=5, edgecolor='black')

# Adicione um título ao gráfico
plt.title('Gráfico de Histograma')

# Adicione uma legenda ao gráfico
plt.xlabel('Valor')
plt.ylabel('Frequência')

# Mostre o eixo dos valores
plt.xticks(np.arange(1, 10, 2))

# Mostre o gráfico
plt.show()

import pandas as pd

#carregando o data set
df_largo = pd.read_csv('data/bairros_recife.csv')

#derretendo o data set
df_longo = pd.melt(df_largo, var_name='microrregiao', value_name='bairro')

# 1. Remove linhas que não têm bairro (células vazias)
df_limpo = df_longo.dropna(subset=['bairro'])

# 2. Remove bairros duplicados, se houver [cite: 56]
df_limpo = df_limpo.drop_duplicates(subset=['bairro'])

# 3. (Opcional, mas bom) Remove espaços em branco antes/depois
df_limpo['bairro'] = df_limpo['bairro'].str.strip()

# 4. (Opcional, mas bom) Ordena para ficar organizado
df_limpo = df_limpo.sort_values(by='bairro')

# Salva o arquivo limpo e "derretido"
df_limpo.to_csv('data/bairros_unique.csv', index=False)
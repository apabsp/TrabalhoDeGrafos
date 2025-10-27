# Em: src/io.py

import pandas as pd
import os

# Define os caminhos dos arquivos
ARQUIVO_BAIRROS_ORIGINAL = 'data/bairros_recife.csv'
ARQUIVO_BAIRROS_PROCESSADO = 'data/bairros_unique.csv'
ARQUIVO_ADJACENCIAS = 'data/adjacencias_bairros.csv'

def _processar_e_salvar_bairros():
    """
    Função interna para "derreter" (melt) o CSV de bairros.
    Lê 'bairros_recife.csv' e salva 'bairros_unique.csv'.
    """
    print(f"Processando '{ARQUIVO_BAIRROS_ORIGINAL}'...")
    try:
        df_largo = pd.read_csv(ARQUIVO_BAIRROS_ORIGINAL)
        
        # Derretendo o data set
        df_longo = pd.melt(df_largo, var_name='microrregiao', value_name='bairro')

        # 1. Remove linhas que não têm bairro (células vazias)
        df_limpo = df_longo.dropna(subset=['bairro'])

        # 2. Remove bairros duplicados
        df_limpo = df_limpo.drop_duplicates(subset=['bairro'])

        # 3. Remove espaços em branco
        df_limpo['bairro'] = df_limpo['bairro'].str.strip()

        # 4. Ordena
        df_limpo = df_limpo.sort_values(by='bairro')

        # Salva o arquivo limpo e "derretido"
        df_limpo.to_csv(ARQUIVO_BAIRROS_PROCESSADO, index=False)
        print(f"Arquivo '{ARQUIVO_BAIRROS_PROCESSADO}' criado com sucesso.")
        
        return df_limpo

    except FileNotFoundError:
        print(f"Erro: Arquivo original '{ARQUIVO_BAIRROS_ORIGINAL}' não encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao processar o arquivo de bairros: {e}")
        return None

def carregar_dados_principais():
    """
    Função principal de I/O. Carrega os dados processados para o projeto.
    Se 'bairros_unique.csv' não existir, ele o cria.
    
    Retorna:
        (pd.DataFrame, pd.DataFrame): Tupla com (df_bairros, df_adjacencias)
                                      ou (None, None) se falhar.
    """
    df_bairros = None
    df_adjacencias = None
    
    # --- 1. Carregar/Processar Bairros ---
    try:
        if not os.path.exists(ARQUIVO_BAIRROS_PROCESSADO):
            print(f"'{ARQUIVO_BAIRROS_PROCESSADO}' não encontrado. Gerando agora...")
            df_bairros = _processar_e_salvar_bairros()
            if df_bairros is None:
                return None, None # Falha no processamento
        else:
            df_bairros = pd.read_csv(ARQUIVO_BAIRROS_PROCESSADO)
            
    except Exception as e:
        print(f"Erro ao carregar '{ARQUIVO_BAIRROS_PROCESSADO}': {e}")
        return None, None
        
    # --- 2. Carregar Adjacências ---
    try:
        df_adjacencias = pd.read_csv(ARQUIVO_ADJACENCIAS)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{ARQUIVO_ADJACENCIAS}' não encontrado.")
        return None, None
    except Exception as e:
        print(f"Erro ao carregar '{ARQUIVO_ADJACENCIAS}': {e}")
        return None

    print("Dados de bairros e adjacências carregados.")
    return df_bairros, df_adjacencias
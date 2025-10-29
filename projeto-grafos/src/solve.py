# Em: src/solve.py

import pandas as pd
import json
import os 

from .graphs.graph import Grafo 
from .graphs.io import carregar_dados_principais

# Define os caminhos de saída obrigatórios
OUTPUT_DIR = 'out'
FILE_OUT_GLOBAL = os.path.join(OUTPUT_DIR, 'recife_global.json')
FILE_OUT_MICRO = os.path.join(OUTPUT_DIR, 'microrregioes.json')
FILE_OUT_EGO = os.path.join(OUTPUT_DIR, 'ego_bairro.csv')
FILE_OUT_GRAUS = os.path.join(OUTPUT_DIR, 'graus.csv')

# ===================================================================
# PARTE 1: CONSTRUÇÃO DO GRAFO
# ===================================================================

def construir_grafo_principal():
    # ... (Esta função está perfeita, não precisa mudar) ...
    # ... (Vou omiti-la aqui para ser breve) ...
    """
    Orquestra o carregamento dos dados e a construção do grafo principal.
    
    Retorna:
        Grafo: O objeto Grafo de Recife.
        (pd.DataFrame, pd.DataFrame): Os dataframes carregados.
    """
    # 1. Carregar os dados processados
    df_bairros, df_adjacencias = carregar_dados_principais()
    
    if df_bairros is None or df_adjacencias is None:
        print("Falha ao carregar dados. Abortando construção do grafo.")
        return None, None, None
    
    # 2. Criar a instância do Grafo
    G_recife = Grafo()

    # 3. Adicionar todos os bairros como nós (vértices)
    for bairro in df_bairros['bairro'].unique():
        G_recife.add_node(bairro) # add_node está em graph.py

    # 4. Adicionar todas as adjacências como arestas
    for index, linha in df_adjacencias.iterrows():
        G_recife.add_edge(
            linha['bairro_origem'],
            linha['bairro_destino'],
            linha['peso']
        ) # add_edge está em graph.py

    print(f"Grafo principal construído: {G_recife.get_numero_de_nos()} nós e {G_recife.get_numero_de_arestas()} arestas.")
    
    return G_recife, df_bairros, df_adjacencias


# ===================================================================
# PARTE 2: CÁLCULO DE MÉTRICAS (Lógica da Pergunta 3)
# ===================================================================

def _calcular_metricas_basicas(grafo: Grafo):
    # ... (Esta função está perfeita, não precisa mudar) ...
    # ... (Vou omiti-la aqui para ser breve) ...
    """
    Função auxiliar para calcular Ordem (N), Tamanho (M) e Densidade (D).
    """
    try:
        ordem = grafo.get_numero_de_nos()
        tamanho = grafo.get_numero_de_arestas()
        
        if ordem <= 1:
            densidade = 0.0
        else:
            # Fórmula para grafo não-direcionado
            densidade = (2 * tamanho) / (ordem * (ordem - 1))
            
        return {'ordem': ordem, 'tamanho': tamanho, 'densidade': densidade}
    except Exception as e:
        print(f"Erro ao calcular métricas: {e}. Verifique 'get_numero_de_nos' e 'get_numero_de_arestas' em graph.py")
        return None

def analisar_grafo_completo(grafo_principal: Grafo):
    """
    Ponto 1 da entrega: Calcula as métricas para a Cidade do Recife
    e salva em 'out/recife_global.json'.
    """
    print("\n--- 1. Análise: Cidade do Recife (Grafo Completo) ---")
    metricas = _calcular_metricas_basicas(grafo_principal)
    
    if metricas:
        # --- MUDANÇA: Comente as linhas de print ---
        # print(f"Ordem (N): {metricas['ordem']}")
        # print(f"Tamanho (M): {metricas['tamanho']}")
        # print(f"Densidade (D): {metricas['densidade']:.4f}")
        # --- FIM DA MUDANÇA ---
        
        try:
            with open(FILE_OUT_GLOBAL, 'w', encoding='utf-8') as f:
                json.dump(metricas, f, indent=4, ensure_ascii=False)
            print(f"Resultados salvos em '{FILE_OUT_GLOBAL}'")
        except Exception as e:
            print(f"Erro ao salvar '{FILE_OUT_GLOBAL}': {e}")

    return metricas

def analisar_microrregioes(df_bairros: pd.DataFrame, df_adjacencias: pd.DataFrame):
    """
    Ponto 2 da entrega: Calcula métricas para os subgrafos das Microrregiões
    e salva em 'out/microrregioes.json'.
    """
    print("\n--- 2. Análise: Microrregiões (Subgrafos Induzidos) ---")
    
    coluna_rpa = 'microrregiao' 
    if coluna_rpa not in df_bairros.columns:
        print(f"Erro: Coluna '{coluna_rpa}' não encontrada em bairros_unique.csv")
        return None

    lista_rpas = df_bairros[coluna_rpa].dropna().unique()
    resultados_rpa = {} 

    for rpa in sorted(lista_rpas):
        bairros_da_rpa = set(df_bairros[df_bairros[coluna_rpa] == rpa]['bairro'])
        subgrafo = Grafo()
        for bairro in bairros_da_rpa:
            subgrafo.add_node(bairro)

        for index, linha in df_adjacencias.iterrows():
            u, v = linha['bairro_origem'], linha['bairro_destino']
            if u in bairros_da_rpa and v in bairros_da_rpa:
                subgrafo.add_edge(u, v, linha['peso'])

        metricas_subgrafo = _calcular_metricas_basicas(subgrafo)
        resultados_rpa[rpa] = metricas_subgrafo
    
    # --- MUDANÇA: Comente o loop de print ---
    # for rpa, metricas in resultados_rpa.items():
    #     if metricas:
    #         print(f"  > {rpa}: Ordem={metricas['ordem']}, Tamanho={metricas['tamanho']}, Densidade={metricas['densidade']:.4f}")
    # --- FIM DA MUDANÇA ---

    try:
        resultados_lista = []
        for rpa, metricas in resultados_rpa.items():
            if metricas:
                metricas['microrregiao'] = rpa 
                resultados_lista.append(metricas)

        with open(FILE_OUT_MICRO, 'w', encoding='utf-8') as f:
            json.dump(resultados_lista, f, indent=4, ensure_ascii=False)
        print(f"Resultados salvos em '{FILE_OUT_MICRO}'")
    except Exception as e:
        print(f"Erro ao salvar '{FILE_OUT_MICRO}': {e}")

    return resultados_rpa

def analisar_ego_redes(grafo_principal: Grafo, df_adjacencias: pd.DataFrame):
    """
    Ponto 3 da entrega: Calcula métricas da ego-rede para cada bairro
    e salva em 'out/ego_bairro.csv'.
    """
    print("\n--- 3. Análise: Ego-Rede por Bairro ---")
    resultados_ego = []

    if not hasattr(grafo_principal, 'get_todos_os_nos') or not hasattr(grafo_principal, 'get_vizinhos'):
        print("Erro: A classe 'Grafo' precisa dos métodos 'get_todos_os_nos()' e 'get_vizinhos(nome_no)'.")
        return None

    for bairro_v in grafo_principal.get_todos_os_nos():
        try:
            vizinhos = set()
            vizinhos_com_peso = grafo_principal.get_vizinhos(bairro_v)
            if vizinhos_com_peso:
                 for vizinho, peso in vizinhos_com_peso:
                    vizinhos.add(vizinho)

            grau = len(vizinhos) # A linha do SyntaxError que corrigimos
            nos_da_ego_rede = set(vizinhos)
            nos_da_ego_rede.add(bairro_v) 

            ordem_ego = len(nos_da_ego_rede) 

            tamanho_ego = 0
            for index, linha in df_adjacencias.iterrows():
                u, v = linha['bairro_origem'], linha['bairro_destino']
                if u in nos_da_ego_rede and v in nos_da_ego_rede:
                    tamanho_ego += 1
                    
            if ordem_ego > 1:
                densidade_ego = (2 * tamanho_ego) / (ordem_ego * (ordem_ego - 1))
            else:
                densidade_ego = 0.0

            resultados_ego.append({
                'bairro': bairro_v, 'grau': grau,
                'ordem_ego': ordem_ego, 'tamanho_ego': tamanho_ego,
                'densidade_ego': densidade_ego
            })
        
        except Exception as e:
            print(f"Erro ao processar ego-rede de '{bairro_v}': {e}")
            continue

    df_ego_final = pd.DataFrame(resultados_ego)
    
    # --- MUDANÇA: Comente os prints da amostra ---
    # print("Tabela de ego-redes gerada (amostra):")
    # print(df_ego_final.head())
    # --- FIM DA MUDANÇA ---
    
    try:
        df_ego_final.to_csv(FILE_OUT_EGO, index=False)
        print(f"Tabela completa salva em '{FILE_OUT_EGO}'")
    except Exception as e:
        print(f"Erro ao salvar '{FILE_OUT_EGO}': {e}")
    
    return df_ego_final


'''
    Graus e Rankings ( Pergunta 4 )

'''

def analisar_graus_e_rankings(grafo_principal: Grafo):
    """
    Ponto 4 da entrega: Calculando graus, gerando ranking e identificando bairro MAIS DENSO(maior densidade_ego) e bairro com MAIOR GRAU.

    Salvar em out/graus.csv
    
    """

    print("\n--- 4. Análise: Graus e Rankings")

    lista_graus = []
    for bairro in grafo_principal.get_todos_os_nos():
        # Adding every bairo's grau
        vizinhos = grafo_principal.get_vizinhos(bairro)
        grau = len(vizinhos) if vizinhos is not None else 0 #gotta be a better way to write this though. checklater

        lista_graus.append({"bairro": bairro, "grau": grau})
    
    df_graus = pd.DataFrame(lista_graus)


    # Save
    try:
        df_graus.to_csv(FILE_OUT_GRAUS, index = False)
        print(f"Lista de graus salva em '{FILE_OUT_GRAUS}'")
    except Exception as e:
        print(f"Erro ao salvar '{FILE_OUT_GRAUS}': {e}")

    #Highest grau

    try:
        idx_max_grau = df_graus['grau'].idxmax() #indexMax
        bairro_max_grau = df_graus.loc[idx_max_grau, 'bairro']
        max_grau= df_graus.loc[idx_max_grau, 'grau']

        print(f"\n Bairro com o maior grau {bairro_max_grau}, onde grau = {max_grau}")

    except Exception as e:
        print(f"Erro ao encontrar maior grau: {e}")

    #Highest density 
    if not df_graus.empty:
        idx_max_grau = df_graus['grau'].idxmax()
        bairro_max_grau = df_graus.loc[idx_max_grau, 'bairro']
        max_grau = df_graus.loc[idx_max_grau, 'grau']
        print(f"\nBairro com maior grau: {bairro_max_grau} (grau = {max_grau})")

    #Highest densidade_ego

    try:
        df_ego = pd.read_csv(FILE_OUT_EGO)
        if not df_ego.empty and 'densidade_ego' in df_ego.columns:
            idx_max_densidade = df_ego['densidade_ego'].idxmax()
            bairro_max_densidade = df_ego.loc[idx_max_densidade, 'bairro']
            max_densidade = df_ego.loc[idx_max_densidade, 'densidade_ego']
            print(f"Bairro mais denso (maior densidade_ego): {bairro_max_densidade} (densidade_ego = {max_densidade:.4f})")
        else:
            print("não foi possível determinar o bairro mais denso. Verifique 'ego_bairro.csv'")
    except Exception as e:
        print(f"Erro ao ler '{FILE_OUT_EGO}' para ranking de densidade: {e}")

    return df_graus;
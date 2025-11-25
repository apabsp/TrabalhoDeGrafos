# Em: src/solve.py

import pandas as pd
import json
import os 
import time

from .graphs.graph import Grafo 
from .graphs.io import carregar_dados_principais, carregar_dataset_parte2
from .graphs.algorithms import dijkstra_path, dijkstra_path_length  

from .viz import exportar_arvore_percurso_png, exportar_arvore_percurso_destacada, mapa_cores_por_grau, histograma_graus, ranking_densidade_por_microrregiao, gerar_grafo_interativo

# Define os caminhos de saída obrigatórios
OUTPUT_DIR = 'out'
FILE_OUT_GLOBAL = os.path.join(OUTPUT_DIR, 'recife_global.json')
FILE_OUT_MICRO = os.path.join(OUTPUT_DIR, 'microrregioes.json')
FILE_OUT_EGO = os.path.join(OUTPUT_DIR, 'ego_bairro.csv')
FILE_OUT_GRAUS = os.path.join(OUTPUT_DIR, 'graus.csv')
FILE_IN_ENDERECOS = os.path.join('data', 'enderecos.csv')          
FILE_OUT_DIST = os.path.join(OUTPUT_DIR, 'distancias_enderecos.csv')
FILE_OUT_JSON = os.path.join(OUTPUT_DIR, 'percurso_nova_descoberta_setubal.json')     

FILE_IN_PARES_PARTE2 = os.path.join('data\dataset_parte2', 'pares_parte2.csv')
FILE_OUT_PARTE2_DIJKSTRA_CSV = os.path.join(OUTPUT_DIR, 'parte2_dijkstra.csv')
FILE_OUT_PARTE2_DIJKSTRA_JSON = os.path.join(OUTPUT_DIR, 'parte2_dijkstra.json')
FILE_OUT_PARTE2_REPORT = os.path.join(OUTPUT_DIR, 'parte2_report.json')

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

        #Print abaixo comentado, pois o resultado já é exibido em Highest density
        #print(f"\n Bairro com o maior grau {bairro_max_grau}, onde grau = {max_grau}")

    except Exception as e:
        print(f"Erro ao encontrar maior grau: {e}")

    #Highest density 
    if not df_graus.empty:
        idx_max_grau = df_graus['grau'].idxmax()
        bairro_max_grau = df_graus.loc[idx_max_grau, 'bairro']
        max_grau = df_graus.loc[idx_max_grau, 'grau']
        #print(f"\nBairro com maior grau: {bairro_max_grau} (grau = {max_grau})\n")

    #Highest densidade_ego

    try:
        df_ego = pd.read_csv(FILE_OUT_EGO)
        if not df_ego.empty and 'densidade_ego' in df_ego.columns:
            idx_max_densidade = df_ego['densidade_ego'].idxmax()
            bairro_max_densidade = df_ego.loc[idx_max_densidade, 'bairro']
            max_densidade = df_ego.loc[idx_max_densidade, 'densidade_ego']
            #print(f"Bairro mais denso (maior densidade_ego): {bairro_max_densidade} (densidade_ego = {max_densidade:.4f})")

            # Mostrar todos os bairros com a mesma densidade máxima
            bairros_max_densidade = [b for b in df_ego[df_ego['densidade_ego'] == max_densidade]['bairro'].tolist() if b != bairro_max_densidade]
            #if len(bairros_max_densidade) > 1:
                #print("Outros bairros com a mesma densidade máxima:", ", ".join(bairros_max_densidade))

        else:
            print("não foi possível determinar o bairro mais denso. Verifique 'ego_bairro.csv'")
    except Exception as e:
        print(f"Erro ao ler '{FILE_OUT_EGO}' para ranking de densidade: {e}")

    return df_graus;

# Dijkstra para calcular distâncias entre os bairros (enderecos.csv)
def calcular_distancias_enderecos(grafo):
    
    print("\n--- 6. Distância entre endereços (pares origem-destino) ---")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        df_in = pd.read_csv(FILE_IN_ENDERECOS, header=None, names=['origem', 'destino'])
    except Exception as e:
        print(f"Erro ao ler '{FILE_IN_ENDERECOS}': {e}")
        return None

    resultados = []
    for _, row in df_in.iterrows():
        origem = str(row['origem']).strip().lower()
        destino = str(row['destino']).strip().lower()
        try:
            caminho = dijkstra_path(grafo, origem, destino, weight="weight")
            distancia = dijkstra_path_length(grafo, origem, destino, weight="weight")

            resultados.append({
                "X": origem,
                "Y": destino,
                "custo": distancia,
                "caminho": " -> ".join(caminho)
            })

            # salva .json do percurso nova descoberta-setúbal
            if origem == "nova descoberta" and destino == "setubal":
                with open(FILE_OUT_JSON, 'w', encoding='utf-8') as fjson:
                    json.dump({"origem": origem, "destino": destino, "caminho": caminho, "distancia": distancia},
                              fjson, ensure_ascii=False, indent=4)
                print(f"Arquivo '{FILE_OUT_JSON}' salvo com sucesso.")

        except Exception as e:
            resultados.append({
                "X": origem,
                "Y": destino,
                "custo": None,
                "caminho": f"ERRO: {e}"
            })
            print(f"  ! Falha em ({origem} -> {destino}): {e}")

    df_out = pd.DataFrame(resultados)

    # exibindo resultados no terminal - não precisa mostrar!
    '''
    print("\nResultados calculados:\n")
    for _, row in df_out.iterrows():
        print(f"{row['X']} → {row['Y']}")
        print(f"  Custo total: {row['custo']}")
        print(f"  Caminho: {row['caminho']}\n")
    '''
    try:
        df_out.to_csv(FILE_OUT_DIST, index=False)
        print(f"Resultados salvos em '{FILE_OUT_DIST}'")
    except Exception as e:
        print(f"Erro ao salvar '{FILE_OUT_DIST}': {e}")

    return df_out

# --- 7. Transformar o percurso obrigatório em árvore e mostrar ---

def gerar_arvore_percurso(grafo):

    print("\n--- 7. Árvore de percurso estática Nova Descoberta --> Setúbal ---")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    origem = "nova descoberta"
    destino = "setubal"   
    caminho = dijkstra_path(grafo, origem, destino, weight="weight")
    exportar_arvore_percurso_png(
        caminho,
        os.path.join(OUTPUT_DIR, "arvore_percurso.png")
    )
    exportar_arvore_percurso_destacada(
        grafo,
        caminho,
        raiz="nova descoberta",
        out_png=os.path.join(OUTPUT_DIR, "arvore_percurso_destacada.png")
    )

def exploracoes_visuais(df_graus, grafo):

    print("\n--- 8. Gerando explorações e visualizações analíticas ---")

    # 8.1 – mapa de cores por grau
    try:
        mapa_cores_por_grau(df_graus)
    except Exception as e:
        print(f"Erro ao gerar mapa de cores por grau: {e}")

    # 8.2 – distribuição dos graus (histograma)
    try:
        histograma_graus(df_graus)
    except Exception as e:
        print(f"Erro ao gerar histograma de graus: {e}")
    
    # 8.3 – ranking de densidade de ego-subrede por microrregião
    try:
        ranking_densidade_por_microrregiao()
    except Exception as e:
        print(f"Erro ao gerar ranking de densidade por microrregião: {e}")

    # 9 – grafo interativo
    print("\n--- 9. Gerando Visualização Interativa ---")

    # recarregar dataframes
    try:
        df_bairros = pd.read_csv('data/bairros_unique.csv')
        df_adjacencias = pd.read_csv('data/adjacencias_bairros.csv')
        df_ego = pd.read_csv(FILE_OUT_EGO) # arquivo ego_bairro.csv gerado no Ponto 3

        gerar_grafo_interativo(grafo, df_adjacencias, df_bairros, df_ego) 

    except Exception as e:
        print(f"Erro na visualização interativa (Ponto 9): {e}. Verifique se os arquivos de dados foram gerados.")
    
def construir_grafo_parte2():

    df_rotas, arestas = carregar_dataset_parte2()
    if df_rotas is None:
        print("Falha ao carregar o dataset da Parte 2.")
        return None, None

    # Grafo dirigido para representar as rotas aéreas
    grafo = Grafo(dirigido=True)

    for origem, destino, peso in arestas:
        grafo.add_edge(origem, destino, peso)

    #print(f"Grafo Parte 2 construído: {grafo.get_numero_de_nos()} nós, {grafo.get_numero_de_arestas()} arestas.")
    print(f"Grafo construído. Iniciando análises...")
    return grafo, df_rotas

def carregar_pares_parte2():

    try:
        df_pares = pd.read_csv(FILE_IN_PARES_PARTE2)
    except Exception as e:
        print(f"Erro ao ler '{FILE_IN_PARES_PARTE2}': {e}")
        return []

    if not {'origem', 'destino'}.issubset(df_pares.columns):
        print(f"Erro: CSV da Parte 2 precisa ter colunas 'origem' e 'destino'.")
        return []

    pares = []
    for _, row in df_pares.iterrows():
        origem = str(row['origem']).strip()
        destino = str(row['destino']).strip()
        if origem and destino:
            pares.append((origem, destino))

    return pares

def executar_dijkstra_parte2(pares=None):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    grafo, df_rotas = construir_grafo_parte2()
    if grafo is None:
        print("Não foi possível construir o grafo da Parte 2.")
        return None

    if pares is None:
        try:
            df_pares = pd.read_csv(FILE_IN_PARES_PARTE2)
        except Exception as e:
            print(f"Erro ao ler '{FILE_IN_PARES_PARTE2}': {e}")
            return None

        if not {'origem', 'destino'}.issubset(df_pares.columns):
            print(f"Erro: '{FILE_IN_PARES_PARTE2}' deve ter colunas 'origem' e 'destino'.")
            return None

        pares = []
        for _, row in df_pares.iterrows():
            origem = str(row['origem']).strip()
            destino = str(row['destino']).strip()
            if origem and destino:
                pares.append((origem, destino))

        if not pares:
            print(f"Nenhum par válido encontrado em '{FILE_IN_PARES_PARTE2}'.")
            return None

    resultados = []
    tempos = []

    for origem, destino in pares:
        origem = str(origem).strip()
        destino = str(destino).strip()

        try:
            t0 = time.perf_counter()

            caminho = dijkstra_path(grafo, origem, destino, weight="weight")
            custo = dijkstra_path_length(grafo, origem, destino, weight="weight")

            elapsed = time.perf_counter() - t0
            status = "ok"

            resultados.append({
                "origem": origem,
                "destino": destino,
                "custo": custo,
                "caminho": " -> ".join(caminho),
                "status": status
            })

            tempos.append({
                "algoritmo": "dijkstra",
                "origem": origem,
                "destino": destino,
                "tempo_segundos": elapsed
            })

        except Exception as e:
            msg_erro = str(e)
            
            print(f"{origem} -> {destino}  **ERRO**  {msg_erro}")
            resultados.append({
                "origem": origem,
                "destino": destino,
                "custo": None,
                "caminho": "",
                "status": f"erro: {msg_erro}"
            })

            tempos.append({
                "algoritmo": "dijkstra",
                "origem": origem,
                "destino": destino,
                "tempo_segundos": None,
                "erro": msg_erro
            })

    # salva parte2_dijkstra
    try:
        df_out = pd.DataFrame(resultados)
        df_out.to_csv(FILE_OUT_PARTE2_DIJKSTRA_CSV, index=False)
        print(f"Resultados Dijkstra salvos em '{FILE_OUT_PARTE2_DIJKSTRA_CSV}'")
    except Exception as e:
        print(f"Erro ao salvar CSV da Parte 2: {e}")
        df_out = None

    # salva parte2_dijkstra.json
    try:
        with open(FILE_OUT_PARTE2_DIJKSTRA_JSON, 'w', encoding='utf-8') as fj:
            json.dump(resultados, fj, ensure_ascii=False, indent=4)
        print(f"Resultados Dijkstra salvos em '{FILE_OUT_PARTE2_DIJKSTRA_JSON}'")
    except Exception as e:
        print(f"Erro ao salvar JSON da Parte 2: {e}")
    
    # salva parte2_report.json
    try:
        report = {
            "algoritmo": "dijkstra",
            "dataset": {
                "num_nos": grafo.get_numero_de_nos(),
                "num_arestas": grafo.get_numero_de_arestas(),
            },
            "tarefas": tempos
        }
        with open(FILE_OUT_PARTE2_REPORT, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=4)
        print(f"\nMétricas salvas em '{FILE_OUT_PARTE2_REPORT}'")
    except Exception as e:
        print(f"Erro ao salvar relatório de desempenho da Parte 2: {e}")

    return df_out


# ===================================================================
# PARTE 2: BFS, DFS, e Bellman-Ford Analysis
# ===================================================================

def executar_bfs_parte2(num_sources=3):
    """
    Execute BFS from multiple sources on the Part 2 dataset.

    Requirements:
    - Run BFS from at least 3 different sources
    - Report order (number of nodes visited) and layers/levels
    """
    from .graphs.algorithms import bfs

    print("\n--- Executando BFS (Parte 2) ---")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    grafo, df_rotas = construir_grafo_parte2()
    if grafo is None:
        print("Não foi possível construir o grafo da Parte 2.")
        return None

    # Get some source nodes from the graph
    todos_nos = grafo.get_todos_os_nos()
    if len(todos_nos) < num_sources:
        num_sources = len(todos_nos)

    # Select sources: first, middle, and last nodes (for variety)
    sources = [
        todos_nos[0],
        todos_nos[len(todos_nos) // 2],
        todos_nos[-1]
    ][:num_sources]

    resultados = []
    tempos = []

    for source in sources:
        print(f"\nBFS a partir de: {source}")

        try:
            t0 = time.perf_counter()
            result = bfs(grafo, source)
            elapsed = time.perf_counter() - t0

            num_visitados = len(result['visited'])
            num_niveis = max(result['levels'].values()) if result['levels'] else 0

            # Count nodes at each level
            niveis_count = {}
            for node, level in result['levels'].items():
                niveis_count[level] = niveis_count.get(level, 0) + 1

            print(f"  Nós visitados: {num_visitados}")
            print(f"  Níveis/camadas: {num_niveis + 1}")
            print(f"  Tempo: {elapsed:.6f}s")

            resultados.append({
                "algoritmo": "BFS",
                "source": source,
                "nos_visitados": num_visitados,
                "num_niveis": num_niveis + 1,
                "niveis_distribuicao": niveis_count,
                "tempo_segundos": elapsed
            })

            tempos.append({
                "algoritmo": "BFS",
                "source": source,
                "tempo_segundos": elapsed
            })

        except Exception as e:
            print(f"  Erro ao executar BFS de {source}: {e}")
            resultados.append({
                "algoritmo": "BFS",
                "source": source,
                "erro": str(e)
            })

    # Save results
    try:
        output_file = os.path.join(OUTPUT_DIR, 'parte2_bfs.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=4)
        print(f"\nResultados BFS salvos em '{output_file}'")
    except Exception as e:
        print(f"Erro ao salvar resultados BFS: {e}")

    return resultados


def executar_dfs_parte2(num_sources=3):
    """
    Execute DFS from multiple sources on the Part 2 dataset.

    Requirements:
    - Run DFS from at least 3 different sources
    - Report order, cycles detected, edge classifications
    """
    from .graphs.algorithms import dfs

    print("\n--- Executando DFS (Parte 2) ---")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    grafo, df_rotas = construir_grafo_parte2()
    if grafo is None:
        print("Não foi possível construir o grafo da Parte 2.")
        return None

    # Get some source nodes
    todos_nos = grafo.get_todos_os_nos()
    if len(todos_nos) < num_sources:
        num_sources = len(todos_nos)

    # Select sources: first, middle, and last nodes
    sources = [
        todos_nos[0],
        todos_nos[len(todos_nos) // 2],
        todos_nos[-1]
    ][:num_sources]

    resultados = []
    tempos = []

    for source in sources:
        print(f"\nDFS a partir de: {source}")

        try:
            t0 = time.perf_counter()
            result = dfs(grafo, source)
            elapsed = time.perf_counter() - t0

            num_visitados = len(result['visited'])
            has_cycle = result['has_cycle']

            # Count edge types
            edge_types_count = {}
            for edge, edge_type in result['edge_classification'].items():
                edge_types_count[edge_type] = edge_types_count.get(edge_type, 0) + 1

            print(f"  Nós visitados: {num_visitados}")
            print(f"  Ciclo detectado: {has_cycle}")
            print(f"  Classificação de arestas: {edge_types_count}")
            print(f"  Tempo: {elapsed:.6f}s")

            resultados.append({
                "algoritmo": "DFS",
                "source": source,
                "nos_visitados": num_visitados,
                "tem_ciclo": has_cycle,
                "classificacao_arestas": edge_types_count,
                "tempo_segundos": elapsed
            })

            tempos.append({
                "algoritmo": "DFS",
                "source": source,
                "tempo_segundos": elapsed
            })

        except Exception as e:
            print(f"  Erro ao executar DFS de {source}: {e}")
            resultados.append({
                "algoritmo": "DFS",
                "source": source,
                "erro": str(e)
            })

    # Save results
    try:
        output_file = os.path.join(OUTPUT_DIR, 'parte2_dfs.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=4)
        print(f"\nResultados DFS salvos em '{output_file}'")
    except Exception as e:
        print(f"Erro ao salvar resultados DFS: {e}")

    return resultados


def executar_bellman_ford_parte2(pares=None):
    """
    Execute Bellman-Ford on Part 2 dataset.

    Requirements:
    - At least one case with negative weight (without negative cycle)
    - At least one case with negative cycle (detected)
    - Compare performance with Dijkstra
    """
    from .graphs.algorithms import bellman_ford, bellman_ford_path, bellman_ford_path_length

    print("\n--- Executando Bellman-Ford (Parte 2) ---")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Build graph for Bellman-Ford (we'll add some negative weights)
    grafo, df_rotas = construir_grafo_parte2()
    if grafo is None:
        print("Não foi possível construir o grafo da Parte 2.")
        return None

    print("\nNOTA: O dataset original tem apenas pesos positivos.")
    print("Para testar Bellman-Ford com pesos negativos, vamos criar casos sintéticos:\n")

    # Load pairs from CSV if not provided
    if pares is None:
        pares = carregar_pares_parte2()
        if not pares:
            print("Nenhum par encontrado. Usando pares padrão do dataset.")
            todos_nos = grafo.get_todos_os_nos()
            pares = [
                (todos_nos[0], todos_nos[10]),
                (todos_nos[50], todos_nos[100]),
                (todos_nos[200], todos_nos[300])
            ] if len(todos_nos) > 300 else [(todos_nos[0], todos_nos[-1])]

    resultados = []
    tempos = []

    # Test 1: Normal positive weights (same as Dijkstra)
    print("=== Teste 1: Pesos Positivos (sem ciclo negativo) ===")
    for origem, destino in pares[:3]:  # Use first 3 pairs
        try:
            t0 = time.perf_counter()
            result = bellman_ford(grafo, origem)
            elapsed = time.perf_counter() - t0

            if destino in result['distances']:
                distancia = result['distances'][destino]
                tem_ciclo_negativo = result['has_negative_cycle']

                print(f"{origem} -> {destino}: custo={distancia}, ciclo_neg={tem_ciclo_negativo}, tempo={elapsed:.6f}s")

                resultados.append({
                    "caso": "pesos_positivos",
                    "algoritmo": "Bellman-Ford",
                    "origem": origem,
                    "destino": destino,
                    "custo": distancia,
                    "tem_ciclo_negativo": tem_ciclo_negativo,
                    "tempo_segundos": elapsed
                })

                tempos.append({
                    "algoritmo": "Bellman-Ford",
                    "caso": "pesos_positivos",
                    "origem": origem,
                    "destino": destino,
                    "tempo_segundos": elapsed
                })

        except Exception as e:
            print(f"{origem} -> {destino}: ERRO - {e}")

    # Test 2: Create a small graph with negative weights (NO negative cycle)
    print("\n=== Teste 2: Pesos Negativos SEM Ciclo Negativo ===")
    print("Criando grafo sintético com pesos negativos...")

    grafo_neg = Grafo(dirigido=True)
    grafo_neg.add_edge('A', 'B', 10.0)
    grafo_neg.add_edge('A', 'C', 5.0)
    grafo_neg.add_edge('B', 'D', -8.0)  # Negative weight
    grafo_neg.add_edge('C', 'D', -3.0)  # Negative weight
    grafo_neg.add_edge('D', 'E', 2.0)

    try:
        t0 = time.perf_counter()
        result = bellman_ford(grafo_neg, 'A')
        elapsed = time.perf_counter() - t0

        print(f"  A -> E: custo={result['distances']['E']}")
        print(f"  Ciclo negativo detectado: {result['has_negative_cycle']}")
        print(f"  Tempo: {elapsed:.6f}s")

        resultados.append({
            "caso": "pesos_negativos_sem_ciclo",
            "algoritmo": "Bellman-Ford",
            "origem": "A",
            "destino": "E",
            "custo": result['distances']['E'],
            "tem_ciclo_negativo": result['has_negative_cycle'],
            "tempo_segundos": elapsed,
            "descricao": "Grafo sintético: A->B(10), A->C(5), B->D(-8), C->D(-3), D->E(2)"
        })

    except Exception as e:
        print(f"  Erro: {e}")

    # Test 3: Create graph WITH negative cycle
    print("\n=== Teste 3: Com Ciclo Negativo (Detectado) ===")
    print("Criando grafo sintético com ciclo negativo...")

    grafo_ciclo = Grafo(dirigido=True)
    grafo_ciclo.add_edge('X', 'Y', 1.0)
    grafo_ciclo.add_edge('Y', 'Z', 1.0)
    grafo_ciclo.add_edge('Z', 'X', -5.0)  # Creates negative cycle: X->Y->Z->X = 1+1+(-5) = -3

    try:
        t0 = time.perf_counter()
        result = bellman_ford(grafo_ciclo, 'X')
        elapsed = time.perf_counter() - t0

        print(f"  Ciclo negativo detectado: {result['has_negative_cycle']}")
        print(f"  Ciclo: {result['negative_cycle']}")
        print(f"  Tempo: {elapsed:.6f}s")

        resultados.append({
            "caso": "ciclo_negativo",
            "algoritmo": "Bellman-Ford",
            "origem": "X",
            "tem_ciclo_negativo": result['has_negative_cycle'],
            "ciclo_negativo": result['negative_cycle'],
            "tempo_segundos": elapsed,
            "descricao": "Grafo sintético: X->Y(1), Y->Z(1), Z->X(-5), total=-3"
        })

    except Exception as e:
        print(f"  Erro: {e}")

    # Save results
    try:
        output_file = os.path.join(OUTPUT_DIR, 'parte2_bellman_ford.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=4)
        print(f"\nResultados Bellman-Ford salvos em '{output_file}'")
    except Exception as e:
        print(f"Erro ao salvar resultados Bellman-Ford: {e}")

    return resultados


def executar_parte2_completa():
    print("\n" + "="*60)
    print("BFS, DFS, Dijkstra e Bellman-Ford")
    print("="*60)

    # Rodar todos
    resultados_bfs = executar_bfs_parte2()
    resultados_dfs = executar_dfs_parte2()
    resultados_dijkstra = executar_dijkstra_parte2()
    resultados_bf = executar_bellman_ford_parte2()

    print("\n--- Atualizando relatório completo da Parte 2 ---")

    try:

        report = {}
        if os.path.exists(FILE_OUT_PARTE2_REPORT):
            with open(FILE_OUT_PARTE2_REPORT, 'r', encoding='utf-8') as f:
                report = json.load(f)

        # Add BFS, DFS, and Bellman-Ford results
        report['bfs'] = resultados_bfs if resultados_bfs else []
        report['dfs'] = resultados_dfs if resultados_dfs else []
        report['bellman_ford'] = resultados_bf if resultados_bf else []

        # Save updated report
        with open(FILE_OUT_PARTE2_REPORT, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=4)

        print(f"Relatório completo atualizado em '{FILE_OUT_PARTE2_REPORT}'")

    except Exception as e:
        print(f"Erro ao atualizar relatório: {e}")

    print("\n" + "="*60)
    print("Análise da Parte 2 concluída!")
    print("="*60)
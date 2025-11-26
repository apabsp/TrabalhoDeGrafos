"""
- DFS: detecção de ciclos e classificação de arestas
- DFS: Executar a partir de >= 3 origens no dataset da Parte 2
"""

import sys
import os

# Muda para o diretório raiz do projeto para que os paths relativos funcionem
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(project_root)
sys.path.insert(0, project_root)

from src.graphs.graph import Grafo
from src.graphs.algorithms import dfs, dfs_full
from src.graphs.io import carregar_dados_principais, carregar_dataset_parte2


def test_dfs_recife_graph():
    print("\nDFS no Grafo de Recife")

    df_bairros, df_adjacencias = carregar_dados_principais()
    assert df_bairros is not None, "Falha ao carregar dados de bairros"
    assert df_adjacencias is not None, "Falha ao carregar dados de adjacências"

    G = Grafo()
    for bairro in df_bairros['bairro'].unique():
        G.add_node(bairro)

    for _, linha in df_adjacencias.iterrows():
        G.add_edge(
            linha['bairro_origem'],
            linha['bairro_destino'],
            linha['peso']
        )

    source = 'boa viagem'
    result = dfs(G, source)

    assert source in result['visited'], f"{source} deve estar no conjunto visitado"
    assert result['parent'][source] is None, f"{source} não deve ter pai"
    assert len(result['visited']) > 1, "Deve visitar múltiplos bairros"

    for node in result['visited']:
        assert node in result['discovery_time'], f"Nó {node} deve ter tempo de descoberta"
        assert node in result['finish_time'], f"Nó {node} deve ter tempo de finalização"
        assert result['discovery_time'][node] < result['finish_time'][node], \
            f"Tempo de descoberta deve ser antes do tempo de finalização para {node}"

    print(f"  -> DFS a partir de '{source}' visitou {len(result['visited'])} bairros")
    print(f"  -> Tem ciclo: {result['has_cycle']}")
    print("PASSOU test_dfs_recife_graph")


def test_dfs_cycle_detection_recife():
    print("\nDetecção de Ciclos DFS no Grafo de Recife")

    df_bairros, df_adjacencias = carregar_dados_principais()

    G = Grafo()
    for bairro in df_bairros['bairro'].unique():
        G.add_node(bairro)

    for _, linha in df_adjacencias.iterrows():
        G.add_edge(
            linha['bairro_origem'],
            linha['bairro_destino'],
            linha['peso']
        )

    source = 'recife'
    result = dfs(G, source)

    print(f"  -> Ciclo detectado: {result['has_cycle']}")

    edge_types = {}
    for edge, edge_type in result['edge_classification'].items():
        edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

    print(f"  -> Classificação de arestas: {edge_types}")

    assert 'tree_edge' in edge_types, "Deve ter arestas de árvore"
    assert edge_types['tree_edge'] > 0, "Deve ter pelo menos uma aresta de árvore"

    print("PASSOU test_dfs_cycle_detection_recife")


def test_dfs_edge_classification():
    print("\nClassificação de Arestas DFS")

    df_bairros, df_adjacencias = carregar_dados_principais()

    G = Grafo()
    for bairro in df_bairros['bairro'].unique():
        G.add_node(bairro)

    for _, linha in df_adjacencias.iterrows():
        G.add_edge(
            linha['bairro_origem'],
            linha['bairro_destino'],
            linha['peso']
        )

    source = 'santo antonio'
    result = dfs(G, source)

    edge_counts = {'tree_edge': 0, 'back_edge': 0, 'forward_edge': 0, 'cross_edge': 0}
    for edge, edge_type in result['edge_classification'].items():
        if edge_type in edge_counts:
            edge_counts[edge_type] += 1

    print(f"  -> Arestas de árvore: {edge_counts['tree_edge']}")
    print(f"  -> Arestas de retorno: {edge_counts['back_edge']}")
    print(f"  -> Arestas de avanço: {edge_counts['forward_edge']}")
    print(f"  -> Arestas de cruzamento: {edge_counts['cross_edge']}")

    assert edge_counts['tree_edge'] > 0, "Deve classificar algumas arestas como arestas de árvore"

    print("PASSOU test_dfs_edge_classification")


def test_dfs_europe_air_routes():
    print("\nDFS nas Rotas Aéreas da Europa")

    df_rotas, arestas = carregar_dataset_parte2()
    assert df_rotas is not None, "Falha ao carregar dados das rotas aéreas da Europa"

    G = Grafo(dirigido=True)
    for origem, destino, peso in arestas:
        G.add_edge(origem, destino, peso)

    num_nodes = G.get_numero_de_nos()
    num_edges = G.get_numero_de_arestas()

    print(f"  Dataset: {num_nodes} nós, {num_edges} arestas")

    todos_nos = G.get_todos_os_nos()
    sources = [todos_nos[0], todos_nos[len(todos_nos)//2], todos_nos[-1]]

    for i, source in enumerate(sources[:3], 1):
        result = dfs(G, source)

        assert len(result['visited']) > 0, "Deve visitar pelo menos um nó"
        assert source in result['visited'], f"{source} deve estar visitado"

        edge_types = {}
        for edge, edge_type in result['edge_classification'].items():
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

        print(f"  -> Origem {i} ({source}): visitou {len(result['visited'])} nós")
        print(f"    Ciclo detectado: {result['has_cycle']}, Tipos de arestas: {edge_types}")

    print("PASSOU test_dfs_europe_air_routes")


def test_dfs_discovery_finish_times():
    print("\nTempos de Descoberta/Finalização DFS")

    df_bairros, df_adjacencias = carregar_dados_principais()

    G = Grafo()
    for bairro in df_bairros['bairro'].unique():
        G.add_node(bairro)

    for _, linha in df_adjacencias.iterrows():
        G.add_edge(
            linha['bairro_origem'],
            linha['bairro_destino'],
            linha['peso']
        )

    source = 'boa vista'
    result = dfs(G, source)

    for node in result['visited']:
        disc_time = result['discovery_time'][node]
        finish_time = result['finish_time'][node]
        assert disc_time < finish_time, \
            f"Tempo de descoberta ({disc_time}) deve ser antes do tempo de finalização ({finish_time}) para {node}"

    assert result['discovery_time'][source] == 1, "Origem deve ter tempo de descoberta 1"

    print(f"  -> Todos os {len(result['visited'])} nós têm tempos de descoberta/finalização válidos")
    print("PASSOU test_dfs_discovery_finish_times")


def test_dfs_source_not_in_graph():
    print("\nDFS com Origem Inválida")

    df_bairros, df_adjacencias = carregar_dados_principais()

    G = Grafo()
    for bairro in df_bairros['bairro'].unique():
        G.add_node(bairro)

    try:
        dfs(G, 'bairro_inexistente_xyz')
        assert False, "Deveria ter lançado exceção"
    except Exception as e:
        assert "not found in graph" in str(e)
        print(f"  -> Exceção lançada corretamente: {e}")

    print("PASSOU test_dfs_source_not_in_graph")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Executando Testes do DFS")
    print("="*60)

    test_dfs_recife_graph()
    test_dfs_cycle_detection_recife()
    test_dfs_edge_classification()
    test_dfs_europe_air_routes()
    test_dfs_discovery_finish_times()
    test_dfs_source_not_in_graph()

    print("\n" + "="*60)
    print("Todos os Testes do DFS Passaram!")
    print("="*60 + "\n")

"""
- BFS: níveis corretos em grafo pequeno
- BFS: Executar a partir de >= 3 origens no dataset da Parte 2
"""

import sys
import os

# Muda para o diretório raiz do projeto para que os paths relativos funcionem
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(project_root)
sys.path.insert(0, project_root)

from src.graphs.graph import Grafo
from src.graphs.algorithms import bfs, bfs_path
from src.graphs.io import carregar_dados_principais, carregar_dataset_parte2


def test_bfs_recife_graph():
    print("\nBFS no Grafo de Recife")

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

    origem = 'boa viagem'
    resultado = bfs(G, origem)

    assert origem in resultado['visited'], f"{origem} deve estar no conjunto visitado"
    assert resultado['levels'][origem] == 0, f"{origem} deve estar no nível 0"
    assert resultado['parent'][origem] is None, f"{origem} não deve ter pai"
    assert len(resultado['visited']) > 1, "Deve visitar múltiplos bairros"

    for no in resultado['visited']:
        assert no in resultado['levels'], f"Nó {no} deve ter um nível"
        assert resultado['levels'][no] >= 0, f"Nível deve ser não-negativo"

    print(f"  -> BFS a partir de '{origem}' visitou {len(resultado['visited'])} bairros")
    print(f"  -> Nível máximo: {max(resultado['levels'].values())}")
    print("PASSOU test_bfs_recife_graph")


def test_bfs_path_nova_descoberta_setubal():
    print("\nCaminho BFS Nova Descoberta -> Setúbal")

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

    origem = 'nova descoberta'
    destino = 'setubal'
    caminho = bfs_path(G, origem, destino)

    assert caminho is not None, f"Deve encontrar um caminho de {origem} para {destino}"
    assert caminho[0] == origem, "Caminho deve começar na origem"
    assert caminho[-1] == destino, "Caminho deve terminar no destino"
    assert len(caminho) >= 2, "Caminho deve ter pelo menos 2 nós"

    print(f"  -> Encontrou caminho com {len(caminho)} nós")
    print(f"  -> Caminho: {' -> '.join(caminho)}")
    print("PASSOU test_bfs_path_nova_descoberta_setubal")


def test_bfs_levels_consistency():
    print("\nConsistência dos Níveis do BFS")

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

    origem = 'recife'
    resultado = bfs(G, origem)

    for no in resultado['visited']:
        if no == origem:
            continue

        pai = resultado['parent'][no]
        assert pai is not None, f"Nó {no} deve ter um pai"

        nivel_filho = resultado['levels'][no]
        nivel_pai = resultado['levels'][pai]
        assert nivel_filho == nivel_pai + 1, \
            f"Filho {no} no nível {nivel_filho} deve estar no nível do pai {pai} + 1"

    print(f"  -> Todos os {len(resultado['visited'])} nós têm níveis consistentes")
    print("PASSOU test_bfs_levels_consistency")


def test_bfs_europe_air_routes():
    print("\nBFS nas Rotas Aéreas da Europa")

    df_rotas, arestas = carregar_dataset_parte2()
    assert df_rotas is not None, "Falha ao carregar dados das rotas aéreas da Europa"

    G = Grafo(dirigido=True)
    for origem, destino, peso in arestas:
        G.add_edge(origem, destino, peso)

    num_nos = G.get_numero_de_nos()
    num_arestas = G.get_numero_de_arestas()

    print(f"  Dataset: {num_nos} nós, {num_arestas} arestas")

    todos_nos = G.get_todos_os_nos()
    origens = [todos_nos[0], todos_nos[len(todos_nos)//2], todos_nos[-1]]

    for i, origem in enumerate(origens, 1):
        resultado = bfs(G, origem)

        assert origem in resultado['visited'], f"{origem} deve estar visitado"
        assert resultado['levels'][origem] == 0, f"{origem} deve estar no nível 0"

        nivel_max = max(resultado['levels'].values()) if resultado['levels'] else 0

        print(f"  -> Origem {i} ({origem}): visitou {len(resultado['visited'])} nós, {nivel_max + 1} níveis")

    print("PASSOU test_bfs_europe_air_routes")


def test_bfs_source_not_in_graph():
    print("\nBFS com Origem Inválida")

    df_bairros, df_adjacencias = carregar_dados_principais()

    G = Grafo()
    for bairro in df_bairros['bairro'].unique():
        G.add_node(bairro)

    try:
        bfs(G, 'bairro_inexistente_xyz')
        assert False, "Deveria ter lançado exceção"
    except Exception as e:
        assert "not found in graph" in str(e)
        print(f"  -> Exceção lançada corretamente: {e}")

    print("PASSOU test_bfs_source_not_in_graph")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Executando Testes do BFS")
    print("="*60)

    test_bfs_recife_graph()
    test_bfs_path_nova_descoberta_setubal()
    test_bfs_levels_consistency()
    test_bfs_europe_air_routes()
    test_bfs_source_not_in_graph()

    print("\n" + "="*60)
    print("Todos os Testes do BFS Passaram!")
    print("="*60 + "\n")

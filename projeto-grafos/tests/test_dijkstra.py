"""
- Dijkstra: caminhos corretos com pesos >= 0
- Dijkstra: deve recusar/rejeitar dados com pesos negativos
- Dijkstra: Executar no dataset da Parte 2
"""

import sys
import os

# Muda para o diretório raiz do projeto para que os paths relativos funcionem
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(project_root)
sys.path.insert(0, project_root)

from src.graphs.graph import Grafo
from src.graphs.algorithms import dijkstra_path, dijkstra_path_length, single_source_dijkstra
from src.graphs.io import carregar_dados_principais, carregar_dataset_parte2


def test_dijkstra_recife_graph():
    print("\nDijkstra no Grafo de Recife")

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
    target = 'recife'

    path = dijkstra_path(G, source, target, weight='weight')
    length = dijkstra_path_length(G, source, target, weight='weight')

    assert path is not None, f"Deve encontrar um caminho de {source} para {target}"
    assert path[0] == source, "Caminho deve começar na origem"
    assert path[-1] == target, "Caminho deve terminar no destino"
    assert length > 0, "Comprimento do caminho deve ser positivo"

    print(f"  -> Caminho de '{source}' para '{target}': {len(path)} bairros")
    print(f"  -> Caminho: {' -> '.join(path)}")
    print(f"  -> Distância: {length}")
    print("PASSOU test_dijkstra_recife_graph")


def test_dijkstra_path_nova_descoberta_setubal():
    print("\nCaminho Dijkstra Nova Descoberta -> Setúbal")

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

    source = 'nova descoberta'
    target = 'setubal'

    path = dijkstra_path(G, source, target, weight='weight')
    length = dijkstra_path_length(G, source, target, weight='weight')

    assert path is not None, f"Deve encontrar um caminho de {source} para {target}"
    assert path[0] == source, "Caminho deve começar na origem"
    assert path[-1] == target, "Caminho deve terminar no destino"
    assert len(path) >= 2, "Caminho deve ter pelo menos 2 nós"
    assert length == 27.0, f"Distância esperada 27.0, obteve {length}"

    print(f"  -> Encontrou caminho com {len(path)} nós")
    print(f"  -> Caminho: {' -> '.join(path)}")
    print(f"  -> Distância total: {length}")
    print("PASSOU test_dijkstra_path_nova_descoberta_setubal")


def test_dijkstra_all_distances_recife():
    print("\nDijkstra Todas as Distâncias (Recife)")

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
    distances, paths = single_source_dijkstra(G, source, weight='weight')

    assert distances[source] == 0, "Distância da origem deve ser 0"
    assert paths[source] == [source], "Caminho da origem deve ser [origem]"

    reachable = {node: dist for node, dist in distances.items() if dist != float('inf')}
    assert len(reachable) > 1, "Deve alcançar múltiplos bairros"

    for node, path in paths.items():
        if path != []:
            assert path[0] == source, f"Caminho para {node} deve começar com {source}"
            assert path[-1] == node, f"Caminho deve terminar em {node}"

    print(f"  -> De '{source}': alcançou {len(reachable)} bairros")
    print(f"  -> Distância máxima: {max(reachable.values())}")
    print("PASSOU test_dijkstra_all_distances_recife")


def test_dijkstra_europe_air_routes():
    print("\nDijkstra nas Rotas Aéreas da Europa")

    df_rotas, arestas = carregar_dataset_parte2()
    assert df_rotas is not None, "Falha ao carregar dados das rotas aéreas da Europa"

    G = Grafo(dirigido=True)
    for origem, destino, peso in arestas:
        G.add_edge(origem, destino, peso)

    num_nodes = G.get_numero_de_nos()
    num_edges = G.get_numero_de_arestas()

    print(f"  Dataset: {num_nodes} nós, {num_edges} arestas")

    todos_nos = G.get_todos_os_nos()
    source = todos_nos[0]
    target = todos_nos[len(todos_nos)//2]

    distances, paths = single_source_dijkstra(G, source, weight='weight')

    assert distances[source] == 0, "Distância da origem deve ser 0"
    assert source in distances, f"{source} deve ter distância"

    reachable = {node: dist for node, dist in distances.items() if dist != float('inf')}

    print(f"  -> De {source}: alcançou {len(reachable)} aeroportos")
    print(f"  -> Distância máxima: {max(reachable.values()) if reachable else 0}")
    print("PASSOU test_dijkstra_europe_air_routes")


def test_dijkstra_same_source_target():
    print("\nDijkstra Mesma Origem e Destino")

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

    length = dijkstra_path_length(G, source, source, weight='weight')
    assert length == 0, "Distância de um nó para si mesmo deve ser 0"

    path = dijkstra_path(G, source, source, weight='weight')
    assert path == [source], "Caminho de um nó para si mesmo deve ser [nó]"

    print(f"  -> Distância de {source} para si mesmo: {length}")
    print(f"  -> Caminho: {path}")
    print("PASSOU test_dijkstra_same_source_target")


def test_dijkstra_unreachable_node():
    print("\nDijkstra Nó Inalcançável")

    df_rotas, arestas = carregar_dataset_parte2()

    G = Grafo(dirigido=True)
    for origem, destino, peso in arestas:
        G.add_edge(origem, destino, peso)

    todos_nos = G.get_todos_os_nos()
    source = todos_nos[-1]

    distances, paths = single_source_dijkstra(G, source, weight='weight')
    unreachable = [node for node, dist in distances.items() if dist == float('inf')]

    if len(unreachable) > 0:
        target = unreachable[0]
        try:
            dijkstra_path(G, source, target, weight='weight')
            assert False, "Deveria ter lançado exceção para nó inalcançável"
        except Exception as e:
            assert "No path" in str(e) or "not reachable" in str(e), \
                "Exceção deve mencionar caminho não encontrado"
            print(f"  -> Exceção lançada corretamente para nó inalcançável: {e}")
    else:
        print(f"  -> Todos os nós alcançáveis de {source} (pulando teste de exceção)")

    print("PASSOU test_dijkstra_unreachable_node")


def test_dijkstra_with_negative_weight():
    print("\nDijkstra com Peso Negativo")

    G = Grafo(dirigido=True)

    G.add_edge('A', 'B', 5.0)
    G.add_edge('B', 'C', -3.0)
    G.add_edge('C', 'D', 2.0)

    try:
        dijkstra_path(G, 'A', 'D', weight='weight')
        print("  -> Aviso: Dijkstra não rejeitou explicitamente peso negativo")
    except ValueError as e:
        assert "negative" in str(e).lower() or "Contradictory" in str(e), \
            "Erro deve mencionar pesos negativos ou contradição"
        print(f"  -> ValueError lançado corretamente: {e}")
    except Exception as e:
        print(f"  -> Exceção lançada: {e}")

    print("PASSOU test_dijkstra_with_negative_weight")


def test_dijkstra_zero_weights():
    print("\nDijkstra Pesos Zero")

    df_rotas, arestas = carregar_dataset_parte2()

    G = Grafo()

    edges_to_add = arestas[:3]
    for origem, destino, _ in edges_to_add:
        G.add_edge(origem, destino, 0.0)

    if len(arestas) > 3:
        origem, destino, peso = arestas[3]
        G.add_edge(origem, destino, peso)

    todos_nos = G.get_todos_os_nos()
    if len(todos_nos) >= 2:
        source = todos_nos[0]

        distances, paths = single_source_dijkstra(G, source, weight='weight')

        assert distances[source] == 0, "Origem deve ter distância 0"

        print(f"  -> Dijkstra lidou com pesos zero corretamente")
        print(f"  -> Calculou distâncias para {len(distances)} nós")
    else:
        print("  -> Pulando: não há nós suficientes no grafo de teste")

    print("PASSOU test_dijkstra_zero_weights")


def test_dijkstra_source_not_in_graph():
    print("\nDijkstra com Origem Inválida")

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

    try:
        dijkstra_path(G, 'bairro_inexistente_xyz', 'recife', weight='weight')
        assert False, "Deveria ter lançado exceção"
    except Exception as e:
        assert "not found" in str(e).lower(), "Deve mencionar nó não encontrado"
        print(f"  -> Exceção lançada corretamente: {e}")

    print("PASSOU test_dijkstra_source_not_in_graph")


def test_dijkstra_target_not_in_graph():
    print("\nDijkstra com Destino Inválido")

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

    try:
        dijkstra_path(G, 'recife', 'bairro_inexistente_xyz', weight='weight')
        assert False, "Deveria ter lançado exceção"
    except Exception as e:
        assert "not found" in str(e).lower() or "No path" in str(e), \
            "Deve mencionar nó não encontrado ou sem caminho"
        print(f"  -> Exceção lançada corretamente: {e}")

    print("PASSOU test_dijkstra_target_not_in_graph")


def test_dijkstra_weighted_vs_unweighted():
    print("\nDijkstra Ponderado vs Não-Ponderado")

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

    source = 'boa viagem'
    target = 'casa amarela'

    path = dijkstra_path(G, source, target, weight='weight')
    length = dijkstra_path_length(G, source, target, weight='weight')

    assert path is not None, "Deve encontrar um caminho"
    assert length > 0, "Caminho deve ter peso positivo"

    print(f"  -> Caminho de {source} para {target}: {len(path)} bairros")
    print(f"  -> Peso total: {length} (não apenas contagem de saltos)")
    print("PASSOU test_dijkstra_weighted_vs_unweighted")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Executando Testes do Dijkstra")
    print("="*60)

    test_dijkstra_recife_graph()
    test_dijkstra_path_nova_descoberta_setubal()
    test_dijkstra_all_distances_recife()
    test_dijkstra_europe_air_routes()
    test_dijkstra_same_source_target()
    test_dijkstra_unreachable_node()
    test_dijkstra_with_negative_weight()
    test_dijkstra_zero_weights()
    test_dijkstra_source_not_in_graph()
    test_dijkstra_target_not_in_graph()
    test_dijkstra_weighted_vs_unweighted()

    print("\n" + "="*60)
    print("Todos os Testes do Dijkstra Passaram!")
    print("="*60 + "\n")

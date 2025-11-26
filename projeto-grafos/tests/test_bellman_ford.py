"""
- Bellman-Ford: lidar com pesos negativos e detectar ciclos negativos
- Bellman-Ford: Executar no dataset da Parte 2 com vários cenários de pesos
"""

import sys
import os

# Muda para o diretório raiz do projeto para que os paths relativos funcionem
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(project_root)
sys.path.insert(0, project_root)

from src.graphs.graph import Grafo
from src.graphs.algorithms import bellman_ford, bellman_ford_path, bellman_ford_path_length
from src.graphs.io import carregar_dados_principais, carregar_dataset_parte2


def test_bellman_ford_recife_graph():
    #Testa Bellman-Ford no grafo real dos bairros de Recife
    print("\nBellman-Ford no Grafo de Recife")

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

    # Testa Bellman-Ford a partir de boa viagem
    source = 'boa viagem'
    result = bellman_ford(G, source)

    # ABAIXO SÃO VERIFICAÇÕES
    assert result['distances'][source] == 0, f"{source} deve ter distância 0"
    assert result['predecessors'][source] is None, f"{source} não deve ter predecessor"

    # Verifica que calculamos distâncias para múltiplos nós
    reachable = [node for node, dist in result['distances'].items() if dist != float('inf')]
    assert len(reachable) > 1, "Deve alcançar múltiplos bairros"

    # Com todos os pesos positivos, não deve haver ciclo negativo
    assert result['has_negative_cycle'] == False, "Grafo de Recife tem apenas pesos positivos"

    print(f"  -> Bellman-Ford a partir de '{source}' alcançou {len(reachable)} bairros")
    print(f"  -> Tem ciclo negativo: {result['has_negative_cycle']}")
    print("PASSOU test_bellman_ford_recife_graph")


def test_bellman_ford_path_nova_descoberta_setubal():
#Testa caminho Bellman-Ford para a rota exigida: Nova Descoberta -> Setúbal.
    print("\nTeste: Caminho Bellman-Ford Nova Descoberta -> Setúbal")

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

    path = bellman_ford_path(G, source, target)
    length = bellman_ford_path_length(G, source, target)

    assert path is not None, f"Deve encontrar um caminho de {source} para {target}"
    assert path[0] == source, "Caminho deve começar na origem"
    assert path[-1] == target, "Caminho deve terminar no destino"
    assert len(path) >= 2, "Caminho deve ter pelo menos 2 nós"
    assert length > 0, "Comprimento do caminho deve ser positivo"

    print(f"  -> Encontrou caminho com {len(path)} nós")
    print(f"  -> Caminho: {' -> '.join(path)}")
    print(f"  -> Distância total: {length}")
    print("PASSOU test_bellman_ford_path_nova_descoberta_setubal")


def test_bellman_ford_europe_air_routes_positive_weights():
#Testa Bellman-Ford nas rotas aéreas da Europa com pesos positivos
    print("\n Bellman-Ford nas no EuropeAirRoutes (Pesos Positivos)")

    df_rotas, arestas = carregar_dataset_parte2()
    assert df_rotas is not None, "Falha ao carregar dados das rotas aéreas da Europa"

    G = Grafo(dirigido=True)
    for origem, destino, peso in arestas:
        G.add_edge(origem, destino, peso)

    num_nodes = G.get_numero_de_nos()
    num_edges = G.get_numero_de_arestas()

    print(f"  Dataset: {num_nodes} nós, {num_edges} arestas")

    # primeiro aeroporto como origem
    todos_nos = G.get_todos_os_nos()
    source = todos_nos[0]

    result = bellman_ford(G, source)

    assert result['has_negative_cycle'] == False, "Pesos positivos não devem criar ciclo negativo"

    reachable = [node for node, dist in result['distances'].items() if dist != float('inf')]
    assert len(reachable) > 0, "Deve alcançar pelo menos o nó origem"
    assert source in reachable, f"{source} deve ser alcançável a partir de si mesmo"
    assert result['distances'][source] == 0, "Distância da origem deve ser 0"

    print(f"  -> De {source}: alcançou {len(reachable)} aeroportos")
    print(f"  -> Tem ciclo negativo: {result['has_negative_cycle']}")
    print("PASSOU test_bellman_ford_europe_air_routes_positive_weights")


def test_bellman_ford_with_negative_weights_no_cycle():
#Testa Bellman-Ford com pesos negativos mas SEM ciclo negativo
    print("\n Teste Bellman-Ford com Pesos Negativos (Sem Ciclo)")

    df_rotas, arestas = carregar_dataset_parte2()

    G = Grafo(dirigido=True)
    for i, (origem, destino, peso) in enumerate(arestas[:5]):
        # Torna uma aresta sim, outra não negativa
        if i % 2 == 1:
            peso = -abs(peso) / 2  # não criar ciclo
        G.add_edge(origem, destino, peso)

    todos_nos = G.get_todos_os_nos()
    if len(todos_nos) == 0:
        print("  -> Pulando: nenhum nó no subgrafo")
        return

    source = todos_nos[0]
    result = bellman_ford(G, source)

    print(f"  -> De {source}: has_negative_cycle = {result['has_negative_cycle']}")
    print(f"  -> Processou {len(result['distances'])} nós")
    print("PASSOU test_bellman_ford_with_negative_weights_no_cycle")


def test_bellman_ford_negative_cycle_detection():
#Testa detecção de ciclo negativo do Bellman-Ford com ciclo sintético
    print("\nTeste de Detecção de Ciclo Negativo Bellman-Ford")

    G = Grafo(dirigido=True)
    #A -> B -> C -> A com peso total < 0
    G.add_edge('A', 'B', 1.0)
    G.add_edge('B', 'C', 1.0)
    G.add_edge('C', 'A', -5.0)  # peso total = 1 + 1 + (-5) = -3

    result = bellman_ford(G, 'A')

    assert result['has_negative_cycle'] == True, "Deve detectar ciclo negativo"
    assert len(result['negative_cycle']) > 0, "Deve retornar o ciclo negativo"

    print(f"  -> Ciclo negativo detectado: {result['has_negative_cycle']}")
    print(f"  -> Ciclo: {result['negative_cycle']}")
    print("PASSOU test_bellman_ford_negative_cycle_detection")


def test_bellman_ford_path_raises_on_negative_cycle():
#Testa que bellman_ford_path lança exceção quando existe ciclo negativo.
    print("\nTeste de Caminho Bellman-Ford com Ciclo Negativo")

    G = Grafo(dirigido=True)
    G.add_edge('A', 'B', 1.0)
    G.add_edge('B', 'C', 1.0)
    G.add_edge('C', 'A', -5.0)

    try:
        bellman_ford_path(G, 'A', 'B')
        assert False, "Deveria ter lançado exceção para ciclo negativo"
    except Exception as e:
        assert "negative cycle" in str(e).lower(), "Exceção deve mencionar ciclo negativo"
        print(f"  -> Exceção lançada corretamente: {e}")

    print("PASSOU test_bellman_ford_path_raises_on_negative_cycle")


def test_bellman_ford_unreachable_nodes():
#Testa Bellman-Ford com nós inalcançáveis em grafo real."""
    print("\n Teste de Bellman-Ford: Nós Inalcançáveis")

    df_rotas, arestas = carregar_dataset_parte2()
    G = Grafo(dirigido=True)
    for origem, destino, peso in arestas:
        G.add_edge(origem, destino, peso)

    todos_nos = G.get_todos_os_nos()
    source = todos_nos[-1]  # último nó como origem

    result = bellman_ford(G, source)

    # Conta alcançáveis vs inalcançáveis
    reachable = [node for node, dist in result['distances'].items() if dist != float('inf')]
    unreachable = [node for node, dist in result['distances'].items() if dist == float('inf')]

    print(f"  -> De {source}: {len(reachable)} alcançáveis, {len(unreachable)} inalcançáveis")

    # Origem deve sempre ser alcançável a partir de si mesma
    assert source in reachable, "Origem deve ser alcançável"
    assert result['distances'][source] == 0, "Distância da origem deve ser 0"

    print("PASSOU test_bellman_ford_unreachable_nodes")


def test_bellman_ford_same_source_target():
    """Testa Bellman-Ford quando origem é igual ao destino."""
    print("\n--- Teste: Bellman-Ford Mesma Origem e Destino ---")

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

    length = bellman_ford_path_length(G, source, source)
    assert length == 0, "Distância de um nó para si mesmo deve ser 0"

    path = bellman_ford_path(G, source, source)
    assert path == [source], "Caminho de um nó para si mesmo deve ser [nó]"

    print(f"  -> Distância de {source} para si mesmo: {length}")
    print(f"  -> Caminho: {path}")
    print("PASSOU test_bellman_ford_same_source_target")


def test_bellman_ford_source_not_in_graph():
    """Testa Bellman-Ford com origem inválida."""
    print("\n--- Teste: Bellman-Ford com Origem Inválida ---")

    df_bairros, df_adjacencias = carregar_dados_principais()

    G = Grafo()
    for bairro in df_bairros['bairro'].unique():
        G.add_node(bairro)

    try:
        bellman_ford(G, 'bairro_inexistente_xyz')
        assert False, "Deveria ter lançado exceção"
    except Exception as e:
        assert "not found in graph" in str(e), "Deve mencionar nó não encontrado"
        print(f"  -> Exceção lançada corretamente: {e}")

    print("PASSOU test_bellman_ford_source_not_in_graph")


def test_bellman_ford_vs_dijkstra_positive_weights():
    """Testa que Bellman-Ford dá os mesmos resultados que Dijkstra para pesos positivos."""
    print("\n--- Teste: Bellman-Ford vs Dijkstra (Pesos Positivos) ---")

    from src.graphs.algorithms import dijkstra_path_length

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

    # Testa uma rota específica
    source = 'boa viagem'
    target = 'recife'

    # Ambos os algoritmos devem dar os mesmos resultados com pesos positivos
    bf_length = bellman_ford_path_length(G, source, target)
    dijk_length = dijkstra_path_length(G, source, target, weight='weight')

    assert bf_length == dijk_length, \
        f"Bellman-Ford ({bf_length}) e Dijkstra ({dijk_length}) devem concordar"

    print(f"  -> Distância Bellman-Ford: {bf_length}")
    print(f"  -> Distância Dijkstra: {dijk_length}")
    print(f"  -> Ambos os algoritmos concordam!")
    print("PASSOU test_bellman_ford_vs_dijkstra_positive_weights")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Executando Testes do Bellman-Ford")
    print("="*60)

    test_bellman_ford_recife_graph()
    test_bellman_ford_path_nova_descoberta_setubal()
    test_bellman_ford_europe_air_routes_positive_weights()
    test_bellman_ford_with_negative_weights_no_cycle()
    test_bellman_ford_negative_cycle_detection()
    test_bellman_ford_path_raises_on_negative_cycle()
    test_bellman_ford_unreachable_nodes()
    test_bellman_ford_same_source_target()
    test_bellman_ford_source_not_in_graph()
    test_bellman_ford_vs_dijkstra_positive_weights()

    print("\n" + "="*60)
    print("Todos os Testes do Bellman-Ford Passaram!")
    print("="*60 + "\n")

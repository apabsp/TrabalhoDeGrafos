import math
import matplotlib.pyplot as plt
import os
from collections import deque, defaultdict


def exportar_arvore_percurso_png(path, out_png="out/arvore_percurso.png"):

    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)

    if not path or len(path) == 0:
        print("Caminho vazio.")
        return

    n = len(path)

    espacamento = 2.0  # distância horizontal entre vértices 
    xs = [i * espacamento for i in range(n)]
    ys = [0] * n

    # ajustar o tamanho da figura conforme o número de nós e espaçamento
    largura = max(6, n * 1.5)
    plt.figure(figsize=(largura, 2.8))

    # arestas
    for i in range(n - 1):
        plt.plot([xs[i], xs[i + 1]], [ys[i], ys[i + 1]], linewidth=4, color="#2b8a3e", zorder=1)

    # nós
    for i, bairro in enumerate(path):
        if i == 0:
            cor = "#1f77b4"  # azul (início)
        elif i == n - 1:
            cor = "#d62728"  # vermelho (fim)
        else:
            cor = "#cfead6"  # intermediário

        plt.scatter(xs[i], ys[i], s=260, color=cor, edgecolor="black", zorder=3)
        plt.text(xs[i], ys[i] + 0.18, bairro, ha="center", va="bottom", fontsize=11)

    plt.axis("off")
    plt.xlim(-espacamento, xs[-1] + espacamento)
    plt.ylim(-0.6, 1.0)
    plt.tight_layout()
    plt.savefig(out_png, dpi=220, bbox_inches="tight")
    plt.close()
    print(f"Árvore do percurso salva em {out_png}")

def exportar_arvore_percurso_destacada(grafo, path, raiz="nova descoberta",
                                              out_png="out/arvore_percurso_destacada.png"):

    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)

    nos = grafo.get_todos_os_nos()
    if not nos:
        print("Grafo vazio.")
        return

    raiz = str(raiz).strip().lower()
    visited, level, parent = set(), {}, {}
    q = deque()

    if raiz not in nos:
        print(f"Atenção: raiz '{raiz}' não encontrada. Usando primeiro nó do grafo.")
        raiz = nos[0]

    visited.add(raiz)
    level[raiz] = 0
    parent[raiz] = None
    q.append(raiz)

    while q:
        u = q.popleft()
        for v, _w in grafo.get_vizinhos(u):
            if v not in visited:
                visited.add(v)
                level[v] = level[u] + 1
                parent[v] = u
                q.append(v)

    max_lvl = max(level.values())
    for v in nos:
        if v not in level:
            max_lvl += 1
            level[v] = max_lvl
            parent[v] = None  # sem pai (componente separado)

    niveis = defaultdict(list)
    for v in nos:
        niveis[level[v]].append(v)

    pos = {}
    x_gap, y_gap = 2.2, 1.3  # espaçamentos
    for l in sorted(niveis.keys()):
        grupo = sorted(niveis[l])
        h = (len(grupo) - 1) * y_gap
        for i, v in enumerate(grupo):
            x = l * x_gap
            y = -h/2 + i * y_gap
            pos[v] = (x, y)

    # arestas
    plt.figure(figsize=(max(7, (max(level.values())+1)*1.8), 7))
    for v in nos:
        p = parent.get(v)
        if p is None:
            continue
        x1, y1 = pos[p]
        x2, y2 = pos[v]
        plt.plot([x1, x2], [y1, y2], linewidth=1.4, color="#d0d7de", zorder=1)

    # nós
    for v in nos:
        x, y = pos[v]
        plt.scatter([x], [y], s=140, color="#eef3f7", edgecolor="black",
                    linewidth=0.6, zorder=2)
        plt.text(x+0.18, y, v, ha="left", va="center", fontsize=8.5, color="#222", zorder=3)

    # destaque para o caminho
    if path and len(path) >= 2:

        # arestas
        for u, v in zip(path[:-1], path[1:]):
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            plt.plot([x1, x2], [y1, y2], linewidth=4, color="#2b8a3e", zorder=4)

        # nós
        for i, b in enumerate(path):
            x, y = pos[b]
            if i == 0:
                cor, tam = "#1f77b4", 260  # início
            elif i == len(path) - 1:
                cor, tam = "#d62728", 260  # fim
            else:
                cor, tam = "#cfead6", 220
            plt.scatter([x], [y], s=tam, color=cor, edgecolor="black",
                        linewidth=0.8, zorder=5)

    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out_png, dpi=240, bbox_inches="tight")
    plt.close()
    print(f"Árvore do percurso destacada salva em {out_png}")

def mapa_cores_por_grau(df_graus, out_png="out/mapa_cores_grau.png"):

    if df_graus is None or df_graus.empty:
        print("DataFrame de graus vazio. Nada a plotar.")
        return

    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)

    # ordenação dos bairros
    df_plot = df_graus.sort_values(by="grau", ascending=False)

    bairros = df_plot["bairro"].tolist()
    graus = df_plot["grau"].tolist()

    # normalização
    max_grau = max(graus) if graus else 1
    valores_norm = [g / max_grau for g in graus]

    cmap = plt.cm.Greens
    cores = [cmap(v) for v in valores_norm]

    altura = max(6, len(bairros) * 0.2)
    plt.figure(figsize=(10, altura))

    plt.barh(bairros, graus, color=cores, height=0.4)
    ax = plt.gca()
    ax.margins(y=0)  # remove o espaço acima e abaixo
    plt.xlabel("Grau (número de conexões)")
    plt.ylabel("Bairro")
    plt.title("Mapa de cores - Graus dos bairros")

    plt.tight_layout()
    plt.savefig(out_png, dpi=220, bbox_inches="tight")
    plt.close()
    print(f"Mapa de cores por grau salvo em '{out_png}'")

def histograma_graus(df_graus, out_png="out/histograma_graus.png"):

    if df_graus is None or df_graus.empty:
        print("DataFrame de graus vazio. Nada a plotar (histograma).")
        return

    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)

    # pega apenas a coluna de graus
    graus = df_graus["grau"]

    min_grau = int(graus.min())
    max_grau = int(graus.max())

    # bins inteiros: [min, min+1, ..., max]
    bins = range(min_grau, max_grau + 2)  # +2 para incluir o último

    plt.figure(figsize=(8, 5))

    plt.hist(graus, bins=bins, edgecolor="black", alpha=0.8, color="green")

    plt.xlabel("Grau (número de conexões)")
    plt.ylabel("Quantidade de bairros")
    plt.title("Distribuição dos graus dos bairros (histograma)")
    plt.xticks(range(min_grau, max_grau + 1))
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig(out_png, dpi=220, bbox_inches="tight")
    plt.close()
    print(f"Histograma de graus salvo em '{out_png}'")

import math
import matplotlib.pyplot as plt
import os
import pandas as pd

def ranking_densidade_por_microrregiao(
    ego_csv="out/ego_bairro.csv",
    bairros_csv="data/bairros_unique.csv",
    out_png="out/ranking_densidade_microrregiao.png"
):
    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)

    # carrega densidades por bairro
    try:
        df_ego = pd.read_csv(ego_csv)
    except Exception as e:
        print(f"Erro ao ler '{ego_csv}': {e}")
        return

    # carrega mapeamento bairro -> microrregião
    try:
        df_bairros = pd.read_csv(bairros_csv)
    except Exception as e:
        print(f"Erro ao ler '{bairros_csv}': {e}")
        return

    if "bairro" not in df_bairros.columns or "microrregiao" not in df_bairros.columns:
        print("Arquivo de bairros não contém as colunas 'bairro' e 'microrregiao'.")
        return

    # junta ego_bairro com microrregião
    df_merge = pd.merge(
        df_ego,
        df_bairros[["bairro", "microrregiao"]],
        on="bairro",
        how="left"
    )

    # cálculo: densidade média por microrregião
    df_agrupado = (
        df_merge.groupby("microrregiao")["densidade_ego"]
                .mean()
                .sort_values(ascending=True)  
    )

    plt.figure(figsize=(10, 6))
    df_agrupado.plot(kind="barh")

    ax = plt.gca()

    plt.title("Densidade média de ego-subrede por microrregião")
    plt.xlabel("Densidade média da ego-subrede")
    plt.ylabel("Microrregião")

    # valores ao lado das barras
    for i, (microrregiao, valor) in enumerate(df_agrupado.items()):
        ax.text(
            valor + 0.01,     
            i,                
            f"{valor:.3f}",  
            va="center",
            fontsize=9
        )
 

    plt.tight_layout()
    plt.savefig(out_png, dpi=300)
    plt.close()

    print(f"Ranking de densidade média de ego-subrede por microrregião salvo em: {out_png}")

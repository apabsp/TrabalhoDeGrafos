import math
import matplotlib.pyplot as plt
import os


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
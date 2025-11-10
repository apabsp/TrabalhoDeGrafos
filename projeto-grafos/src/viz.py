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
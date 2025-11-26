import math
import matplotlib.pyplot as plt
import os
from collections import deque, defaultdict
import pandas as pd
from pyvis.network import Network
import json
from .graphs.graph import Grafo

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

def gerar_grafo_interativo(grafo: Grafo, df_adjacencias: pd.DataFrame, df_bairros: pd.DataFrame, df_ego: pd.DataFrame):
    
    # juntar dados dos bairros com as métricas de ego-rede
    df_nodes = df_bairros.merge(df_ego, on='bairro', how='left').fillna({'grau': 0, 'densidade_ego': 0, 'microrregiao': 'N/A'})
    df_nodes['bairro'] = df_nodes['bairro'].str.lower()
    df_nodes = df_nodes.set_index('bairro')
    
    # cada microrregião tem uma cor diferente
    color_map = {
        '1.1': '#1f77b4', '1.2': '#ff7f0e', '1.3': '#2ca02c', '2.1': '#d62728', 
        '2.2': '#9467bd', '2.3': '#8c564b', '3.1': '#e377c2', '3.2': '#7f7f7f', 
        '3.3': '#bcbd22', '4.1': '#17becf', '4.2': '#a0522d', '4.3': '#ffebcd', 
        '5.1': '#adff2f', '5.2': '#4682b4', '5.3': '#db7093', '6.1': '#f08080', 
        '6.2': '#008080', '6.3': '#daa520', 'N/A': '#cccccc'
    }

    # caminho padrão
    target_path_str = 'nova descoberta -> alto do mandu -> monteiro -> iputinga -> cordeiro -> prado -> afogados -> imbiribeira -> boa viagem -> setubal'
    target_path_nodes = [bairro.strip() for bairro in target_path_str.split('->')]

    # criar grafo interativo com pyvis
    net = Network(
        height='800px', 
        width='100%', 
        notebook=False, 
        cdn_resources='remote',
        select_menu=True,
        filter_menu=False,
        bgcolor='#ffffff',
        font_color='#2c3e50'
    )
    
    # adicionar nós ao pyvis
    for node in grafo.get_todos_os_nos():
        if node in df_nodes.index:
            data = df_nodes.loc[node]
            microrregiao = str(data['microrregiao'])
            cor = color_map.get(microrregiao, '#999999')
            
            # adiciona o nó com cor
            net.add_node(
                node, 
                label=node.title(),
                color=cor,
                size=15,
                borderWidth=2,
                borderWidthSelected=4,
                font={'size': 14, 'face': 'Segoe UI'}
            )
        
    # adicionar arestas ao pyvis
    for _, row in df_adjacencias.iterrows():
        origem = row['bairro_origem'].lower()
        destino = row['bairro_destino'].lower()
        peso = row.get('peso', 1.0)
        net.add_edge(origem, destino, value=peso)

    # configurações de física e interação do grafo
    options_json = {
        "physics": {
            "enabled": True,
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "centralGravity": 0.01,
                "springLength": 100,
                "springConstant": 0.08
            },
            "stabilization": {"iterations": 150}
        },
        "interaction": {
            "hover": True,
            "tooltipDelay": 100,
            "navigationButtons": True,
            "keyboard": True
        },
        "nodes": {
            "borderWidth": 2,
            "size": 15,
            "font": {"size": 14, "face": "Segoe UI"}
        },
        "edges": {
            "color": {"inherit": False, "color": "#848484"},
            "smooth": {"type": "continuous"}
        }
    }
    net.set_options(json.dumps(options_json))

    # salvar html temporário
    temp_file = os.path.join('out', 'temp_grafo.html')
    os.makedirs('out', exist_ok=True)
    net.save_graph(temp_file)
    
    # ler o html gerado
    with open(temp_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # preparar dados dos nós pra usar no javascript
    nodes_data = {}
    microregioes_count = {}
    
    for node in grafo.get_todos_os_nos():
        if node in df_nodes.index:
            data = df_nodes.loc[node]
            microrregiao = str(data['microrregiao'])
            
            nodes_data[node] = {
                'grau': int(data['grau']),
                'densidade': float(data['densidade_ego']),
                'microrregiao': microrregiao,
                'cor': color_map.get(microrregiao, '#cccccc')
            }
            
            # contar bairros por microrregião
            if microrregiao not in microregioes_count:
                microregioes_count[microrregiao] = 0
            microregioes_count[microrregiao] += 1
    
    # lista de todos os bairros para o dropdown
    all_bairros = sorted(grafo.get_todos_os_nos())
    
    # lista de todas as microrregiões únicas
    all_microregioes = sorted([mr for mr in set([info['microrregiao'] for info in nodes_data.values()]) if mr != 'N/A'])
    
    # Função para calcular se texto deve ser branco ou preto
    def get_text_color(hex_color):
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return '#fff' if brightness < 155 else '#000'
    
    # gerar botões coloridos para cada RPA
    botoes_rpa_html = ""
    for mr in all_microregioes:
        cor = color_map.get(mr, '#3498db')
        text_color = get_text_color(cor)
        
        botoes_rpa_html += f'''        <button onclick="filtrarPorMicrorregiao('{mr}')" class="btn btn-filter" id="btn-{mr}" 
            style="background: {cor} !important; color: {text_color} !important; border: 2px solid {cor};">
            RPA {mr}
        </button>\n'''
    
    # gerar HTML da legenda colorida
    legenda_html = ""
    for mr in sorted(all_microregioes):
        if mr in microregioes_count:
            cor = color_map.get(mr, '#cccccc')
            text_color = get_text_color(cor)
            count = microregioes_count[mr]
            
            legenda_html += f'''
        <div style="display: flex; align-items: center; margin: 8px 0;">
            <div style="width: 30px; height: 30px; background: {cor}; border-radius: 5px; margin-right: 12px; border: 2px solid #333;"></div>
            <div style="flex: 1;">
                <strong>RPA {mr}</strong> - {count} bairros
                <br><small style="color: #666;">{cor}</small>
            </div>
        </div>\n'''
    
    # cabeçalho e estilos
    header_and_css = """
<style>
    body { 
        margin: 0; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: #f5f7fa;
    }
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .header-subtitle {
        font-size: 14px;
        opacity: 0.9;
    }
    .controls-container {
        background: white;
        padding: 20px 30px;
        border-bottom: 1px solid #e1e8ed;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .control-section {
        margin-bottom: 20px;
        padding-bottom: 20px;
        border-bottom: 1px solid #e1e8ed;
    }
    .control-section:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    .section-title {
        font-size: 14px;
        font-weight: bold;
        color: #667eea;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .btn {
        padding: 10px 20px;
        border: none;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-right: 8px;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .btn-highlight {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    .btn-reset {
        background: #e74c3c;
        color: white;
    }
    .btn-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .btn-filter {
        background: #3498db;
        color: white;
    }
    .btn-filter.active {
        box-shadow: 0 0 0 4px rgba(46, 204, 113, 0.4) !important;
        transform: scale(1.05);
    }
    .input-group {
        display: inline-block;
        margin-right: 10px;
        margin-bottom: 10px;
    }
    .input-group label {
        display: block;
        font-size: 12px;
        color: #666;
        margin-bottom: 5px;
        font-weight: 600;
    }
    .input-group select {
        padding: 8px 12px;
        border: 2px solid #e1e8ed;
        border-radius: 6px;
        font-size: 13px;
        min-width: 200px;
        cursor: pointer;
    }
    .legend-container {
        background: white;
        padding: 15px 30px;
        border-top: 1px solid #e1e8ed;
        font-size: 12px;
        color: #666;
    }
    .legend-item {
        display: inline-block;
        margin-right: 20px;
    }
    #mynetwork {
        margin-top: 0 !important;
    }
    #stats-panel {
        position: fixed;
        right: 20px;
        top: 120px;
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        min-width: 280px;
        max-width: 350px;
        display: none;
        z-index: 1000;
        max-height: 70vh;
        overflow-y: auto;
    }
    #stats-panel h3 {
        margin-top: 0;
        color: #667eea;
        border-bottom: 2px solid #667eea;
        padding-bottom: 10px;
    }
    #stats-content {
        font-size: 14px;
        line-height: 1.8;
    }
    #legend-panel {
        position: fixed;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        min-width: 400px;
        max-width: 500px;
        display: none;
        z-index: 10000;
        max-height: 80vh;
        overflow-y: auto;
    }
    #legend-panel h3 {
        margin-top: 0;
        color: #667eea;
        border-bottom: 2px solid #667eea;
        padding-bottom: 10px;
        font-size: 20px;
    }
    .overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: none;
        z-index: 9999;
    }
</style>

<div class="header-container">
    <div class="header-title">Grafo Interativo dos Bairros do Recife</div>
    <div class="header-subtitle">Projeto Final - Teoria dos Grafos | Parte 1 - Ponto 9 + Bônus Visual/UX</div>
</div>

<div class="controls-container">
    
    <!-- SEÇÃO 1: CAMINHO PERSONALIZADO -->
    <div class="control-section">
        <div class="section-title">1. Destaque de Caminho Personalizado</div>
        <div class="input-group">
            <label>Origem:</label>
            <select id="path-origin">
                <option value="">Selecione o bairro de origem...</option>
""" + ''.join([f'                <option value="{b}">{b.title()}</option>\n' for b in all_bairros]) + """
            </select>
        </div>
        <div class="input-group">
            <label>Destino:</label>
            <select id="path-destination">
                <option value="">Selecione o bairro de destino...</option>
""" + ''.join([f'                <option value="{b}">{b.title()}</option>\n' for b in all_bairros]) + """
            </select>
        </div>
        <button onclick="calcularERealcarCaminho()" class="btn btn-highlight">
            🔍 Calcular e Realçar Caminho
        </button>
        <button onclick="realcarCaminhoDefault()" class="btn btn-highlight">
            📍 Realçar Nova Descoberta → Setúbal
        </button>
        <button onclick="resetHighlight()" class="btn btn-reset">
            ❌ Remover Realce
        </button>
    </div>
    
    <!-- SEÇÃO 2: FILTROS POR MICRORREGIÃO -->
    <div class="control-section">
        <div class="section-title">2. Filtrar por Microrregião</div>
        <button onclick="filtrarPorMicrorregiao('todas')" class="btn btn-filter active" id="btn-todas" 
                style="background: #2ecc71 !important; color: white !important;">
            ✓ Todas
        </button>
""" + botoes_rpa_html + """
    </div>
    
    <!-- SEÇÃO 3: INFORMAÇÕES -->
    <div class="control-section">
        <div class="section-title">ℹ3. Informações</div>
        <button onclick="showInfo()" class="btn btn-info">
            📊 Estatísticas do Grafo
        </button>
        <button onclick="mostrarLegendaCores()" class="btn btn-info">
            🎨 Legenda de Cores
        </button>
    </div>
    
</div>

<!-- Overlay escuro -->
<div class="overlay" id="overlay" onclick="fecharLegenda()"></div>

<!-- Painel de legenda colorida -->
<div id="legend-panel">
    <h3>🎨 Legenda de Cores por Microrregião</h3>
    <div id="legend-content">
""" + legenda_html + """
    </div>
    <button onclick="fecharLegenda()" class="btn btn-reset" style="width: 100%; margin-top: 20px;">
        Fechar
    </button>
</div>

<!-- Painel lateral de estatísticas -->
<div id="stats-panel">
    <h3>📊 Estatísticas do Bairro</h3>
    <div id="stats-content"></div>
    <button onclick="fecharStats()" class="btn btn-reset" style="width: 100%; margin-top: 15px;">
        Fechar
    </button>
</div>
"""
    
    footer_html = """
<div class="legend-container">
    <span style="font-weight: bold; margin-right: 15px;">💡 Dicas de Uso:</span>
    <span class="legend-item">Arraste os nós para reorganizar</span>
    <span class="legend-item">Ctrl+Scroll para zoom</span>
    <span class="legend-item">Passe o mouse sobre os nós para ver detalhes</span>
    <span class="legend-item">Clique em um bairro para ver estatísticas completas</span>
</div>
"""
    
    # javascript (continua no próximo comentário devido ao limite)
    js_code = """
<script type="text/javascript">
var pathNodesDefault = """ + json.dumps(target_path_nodes) + """;
var nodesData = """ + json.dumps(nodes_data) + """;
var colorMap = """ + json.dumps(color_map) + """;
var isHighlighted = false;
var currentHighlightedPath = [];
var tooltipElement = null;
var hoverTimeout = null;
var clickedNode = null;
var currentFilter = 'todas';

function createTooltip(nodeId, x, y) {
    var nodeInfo = nodesData[nodeId];
    if (!nodeInfo) return;
    
    removeTooltip();
    
    var network = window.network;
    var canvasNode = network.body.nodes[nodeId];
    
    var bgColor = '#cccccc';
    if (canvasNode && canvasNode.options && canvasNode.options.color) {
        var colorObj = canvasNode.options.color;
        if (typeof colorObj === 'string') {
            bgColor = colorObj;
        } else if (colorObj.background) {
            bgColor = colorObj.background;
        } else if (colorObj.color) {
            bgColor = colorObj.color;
        }
    }
    
    var textColor = getTextColor(bgColor);
    
    tooltipElement = document.createElement('div');
    tooltipElement.id = 'custom-tooltip';
    tooltipElement.style.cssText = `
        position: fixed;
        left: ${x + 15}px;
        top: ${y + 15}px;
        padding: 14px;
        background: ${bgColor};
        border-radius: 10px;
        color: ${textColor};
        font-family: Arial, sans-serif;
        min-width: 240px;
        box-shadow: 0 6px 16px rgba(0,0,0,0.4);
        z-index: 999999;
        pointer-events: none;
        border: 2px solid rgba(0,0,0,0.15);
    `;
    
    tooltipElement.innerHTML = `
        <div style="font-size: 17px; font-weight: bold; margin-bottom: 10px; 
                    border-bottom: 2px solid rgba(${textColor === '#fff' ? '255,255,255' : '0,0,0'},0.3); padding-bottom: 6px;">
            ${nodeId.toUpperCase()}
        </div>
        <div style="font-size: 14px; line-height: 1.8;">
            <div style="margin: 4px 0;"><b>Grau:</b> ${nodeInfo.grau} conexões</div>
            <div style="margin: 4px 0;"><b>Microrregião:</b> ${nodeInfo.microrregiao}</div>
            <div style="margin: 4px 0;"><b>Densidade:</b> ${nodeInfo.densidade.toFixed(4)}</div>
        </div>
    `;
    
    document.body.appendChild(tooltipElement);
}

function getTextColor(hexColor) {
    var r = parseInt(hexColor.substr(1,2), 16);
    var g = parseInt(hexColor.substr(3,2), 16);
    var b = parseInt(hexColor.substr(5,2), 16);
    var brightness = (r * 299 + g * 587 + b * 114) / 1000;
    return brightness > 155 ? '#000' : '#fff';
}

function removeTooltip() {
    if (tooltipElement && tooltipElement.parentNode) {
        tooltipElement.parentNode.removeChild(tooltipElement);
        tooltipElement = null;
    }
}

function mostrarStats(nodeId) {
    var nodeInfo = nodesData[nodeId];
    if (!nodeInfo) return;
    
    var network = window.network;
    var connectedNodes = network.getConnectedNodes(nodeId);
    var vizinhosHTML = '';
    
    if (connectedNodes.length > 0) {
        vizinhosHTML = '<p><strong>Vizinhos conectados:</strong></p><ul style="margin: 5px 0; padding-left: 20px;">';
        connectedNodes.slice(0, 10).forEach(function(v) {
            vizinhosHTML += '<li>' + v.charAt(0).toUpperCase() + v.slice(1) + '</li>';
        });
        if (connectedNodes.length > 10) {
            vizinhosHTML += '<li><em>... e mais ' + (connectedNodes.length - 10) + ' bairros</em></li>';
        }
        vizinhosHTML += '</ul>';
    }
    
    document.getElementById('stats-panel').style.display = 'block';
    document.getElementById('stats-content').innerHTML = `
        <p><strong>Bairro:</strong> ${nodeId.toUpperCase()}</p>
        <p><strong>Grau:</strong> ${nodeInfo.grau} conexões</p>
        <p><strong>Microrregião:</strong> RPA ${nodeInfo.microrregiao}</p>
        <p><strong>Densidade Ego:</strong> ${nodeInfo.densidade.toFixed(4)}</p>
        <hr style="margin: 15px 0; border: none; border-top: 1px solid #e1e8ed;">
        ${vizinhosHTML}
    `;
}

function fecharStats() {
    document.getElementById('stats-panel').style.display = 'none';
}

function mostrarLegendaCores() {
    document.getElementById('legend-panel').style.display = 'block';
    document.getElementById('overlay').style.display = 'block';
}

function fecharLegenda() {
    document.getElementById('legend-panel').style.display = 'none';
    document.getElementById('overlay').style.display = 'none';
}

function filtrarPorMicrorregiao(microrregiao) {
    var network = window.network;
    var nodeData = network.body.data.nodes;
    var edgeData = network.body.data.edges;
    var updates = [];
    var edgeUpdates = [];
    
    currentFilter = microrregiao;
    
    document.querySelectorAll('.btn-filter').forEach(function(btn) {
        btn.classList.remove('active');
    });
    document.getElementById('btn-' + microrregiao).classList.add('active');
    
    if (microrregiao === 'todas') {
        nodeData.forEach(function(node) {
            updates.push({
                id: node.id,
                opacity: 1.0,
                size: 15,
                hidden: false
            });
        });
        edgeData.forEach(function(edge) {
            edgeUpdates.push({
                id: edge.id,
                hidden: false,
                color: '#848484'
            });
        });
    } else {
        var nodesVisiveis = new Set();
        
        nodeData.forEach(function(node) {
            var nodeInfo = nodesData[node.id];
            if (!nodeInfo) return;
            
            if (nodeInfo.microrregiao === microrregiao) {
                nodesVisiveis.add(node.id);
                updates.push({
                    id: node.id,
                    opacity: 1.0,
                    size: 20,
                    hidden: false
                });
            } else {
                updates.push({
                    id: node.id,
                    opacity: 0.1,
                    size: 8,
                    hidden: false
                });
            }
        });
        
        edgeData.forEach(function(edge) {
            if (nodesVisiveis.has(edge.from) && nodesVisiveis.has(edge.to)) {
                edgeUpdates.push({
                    id: edge.id,
                    hidden: false,
                    color: '#059669',
                    width: 2
                });
            } else {
                edgeUpdates.push({
                    id: edge.id,
                    hidden: true
                });
            }
        });
    }
    
    nodeData.update(updates);
    edgeData.update(edgeUpdates);
    
    if (microrregiao !== 'todas') {
        var nodesToFit = Array.from(nodesVisiveis);
        if (nodesToFit.length > 0) {
            setTimeout(function() {
                network.fit({ nodes: nodesToFit, animation: { duration: 800 } });
            }, 100);
        }
    }
}

function dijkstraJS(graph, start, end) {
    var distances = {};
    var previous = {};
    var unvisited = new Set();
    
    for (var node in graph) {
        distances[node] = Infinity;
        previous[node] = null;
        unvisited.add(node);
    }
    distances[start] = 0;
    
    while (unvisited.size > 0) {
        var current = null;
        var minDist = Infinity;
        unvisited.forEach(function(node) {
            if (distances[node] < minDist) {
                minDist = distances[node];
                current = node;
            }
        });
        
        if (current === null || distances[current] === Infinity) break;
        if (current === end) break;
        
        unvisited.delete(current);
        
        if (graph[current]) {
            graph[current].forEach(function(neighbor) {
                if (unvisited.has(neighbor.to)) {
                    var alt = distances[current] + neighbor.weight;
                    if (alt < distances[neighbor.to]) {
                        distances[neighbor.to] = alt;
                        previous[neighbor.to] = current;
                    }
                }
            });
        }
    }
    
    if (distances[end] === Infinity) return null;
    
    var path = [];
    var current = end;
    while (current !== null) {
        path.unshift(current);
        current = previous[current];
    }
    
    return path;
}

function calcularERealcarCaminho() {
    var origem = document.getElementById('path-origin').value;
    var destino = document.getElementById('path-destination').value;
    
    if (!origem || !destino) {
        alert('⚠️ Por favor, selecione tanto a origem quanto o destino!');
        return;
    }
    
    if (origem === destino) {
        alert('⚠️ Origem e destino devem ser diferentes!');
        return;
    }
    
    var network = window.network;
    var edgeData = network.body.data.edges;
    var graph = {};
    
    edgeData.forEach(function(edge) {
        if (!graph[edge.from]) graph[edge.from] = [];
        if (!graph[edge.to]) graph[edge.to] = [];
        
        var weight = edge.value || 1;
        graph[edge.from].push({ to: edge.to, weight: weight });
        graph[edge.to].push({ to: edge.from, weight: weight });
    });
    
    var caminho = dijkstraJS(graph, origem, destino);
    
    if (!caminho) {
        alert('❌ Não foi possível encontrar um caminho entre ' + origem.toUpperCase() + ' e ' + destino.toUpperCase() + '!');
        return;
    }
    
    highlightPath(caminho);
    
    alert('✅ Caminho encontrado com ' + caminho.length + ' bairros!\\n\\n📍 Caminho: ' + 
          caminho.map(function(b) { return b.toUpperCase(); }).join(' → '));
}

function realcarCaminhoDefault() {
    highlightPath(pathNodesDefault);
}

function highlightPath(pathNodes) {
    if (isHighlighted) {
        resetHighlight();
    }
    
    var network = window.network;
    var nodeData = network.body.data.nodes;
    var edgeData = network.body.data.edges;
    var updates = [];
    var edgeUpdates = [];
    
    currentHighlightedPath = pathNodes;
    
    for (var i = 0; i < pathNodes.length; i++) {
        var nodeId = pathNodes[i];
        var currentNode = nodeData.get(nodeId);
        
        if (currentNode) {
            var originalColor = currentNode.color;
            if (typeof originalColor === 'object' && originalColor.background) {
                originalColor = originalColor.background;
            }
            
            var progress = i / (pathNodes.length - 1);
            var r = Math.round(16 + (5 - 16) * progress);
            var g = Math.round(185 + (150 - 185) * progress);
            var b = Math.round(129 + (105 - 129) * progress);
            var greenShade = 'rgb(' + r + ',' + g + ',' + b + ')';
            
            updates.push({
                id: nodeId,
                originalColor: originalColor,
                color: { border: '#059669', background: greenShade },
                borderWidth: 4,
                size: 30,
                font: { size: 16, bold: true }
            });
        }
    }
    nodeData.update(updates);
    
    for (var i = 0; i < pathNodes.length - 1; i++) {
        var u = pathNodes[i];
        var v = pathNodes[i + 1];
        
        var edgeId = edgeData.getIds({
            filter: function (item) {
                return (item.from === u && item.to === v) || (item.from === v && item.to === u);
            }
        })[0];
        
        if (edgeId) {
            edgeUpdates.push({ id: edgeId, color: '#059669', width: 6 });
        }
    }
    edgeData.update(edgeUpdates);
    
    setTimeout(function() {
        network.fit({ nodes: pathNodes, animation: { duration: 1000 } });
    }, 100);
    
    isHighlighted = true;
}

function resetHighlight() {
    if (!isHighlighted) {
        alert('ℹ️ Nenhum caminho está realçado no momento!');
        return;
    }
    
    var network = window.network;
    var nodeData = network.body.data.nodes;
    var edgeData = network.body.data.edges;
    var updates = [];
    var edgeUpdates = [];
    
    nodeData.forEach(function(node) {
        var resetColor = node.originalColor || node.color;
        if (typeof resetColor === 'object' && resetColor.background) {
            resetColor = resetColor.background;
        }
        updates.push({
            id: node.id,
            color: resetColor,
            borderWidth: 2,
            size: 15,
            font: { size: 14, bold: false }
        });
    });
    nodeData.update(updates);
    
    edgeData.forEach(function(edge) {
        edgeUpdates.push({ id: edge.id, color: '#848484', width: 1 });
    });
    edgeData.update(edgeUpdates);
    
    network.fit({ animation: { duration: 1000 } });
    isHighlighted = false;
    currentHighlightedPath = [];
    
    if (currentFilter !== 'todas') {
        filtrarPorMicrorregiao(currentFilter);
    }
}

function showInfo() {
    var total = Object.keys(nodesData).length;
    var totalArestas = window.network.body.data.edges.length;
    
    alert(
        '📊 INFORMAÇÕES DO GRAFO\\n' +
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n\\n' +
        '🏘️  Total de Bairros: ' + total + '\\n' +
        '🔗 Total de Conexões: ' + totalArestas + '\\n\\n' +
        '📍 CAMINHO PADRÃO:\\n' +
        'Nova Descoberta → Alto do Mandu → Monteiro →\\n' +
        'Iputinga → Cordeiro → Prado → Afogados →\\n' +
        'Imbiribeira → Boa Viagem → Setúbal\\n\\n' +
        '💡 Use os controles acima para explorar!'
    );
}

function setupTooltips() {
    var network = window.network;
    
    network.on("hoverNode", function(params) {
        if (hoverTimeout) clearTimeout(hoverTimeout);
        if (clickedNode !== params.node) {
            createTooltip(params.node, params.pointer.DOM.x, params.pointer.DOM.y);
        }
    });
    
    network.on("blurNode", function(params) {
        if (clickedNode !== params.node) {
            hoverTimeout = setTimeout(function() {
                removeTooltip();
            }, 100);
        }
    });
    
    network.on("click", function(params) {
        if (params.nodes.length > 0) {
            var nodeId = params.nodes[0];
            mostrarStats(nodeId);
            clickedNode = nodeId;
            createTooltip(nodeId, params.pointer.DOM.x, params.pointer.DOM.y);
            
            setTimeout(function() {
                if (clickedNode === nodeId) {
                    clickedNode = null;
                    removeTooltip();
                }
            }, 3000);
        } else {
            fecharStats();
            clickedNode = null;
            removeTooltip();
        }
    });
    
    network.on("hoverEdge", function() {
        if (!clickedNode) removeTooltip();
    });
}

function traduzirInterface() {
    setTimeout(function() {
        var labels = document.querySelectorAll('label');
        labels.forEach(function(label) {
            if (label.textContent.includes('Select a Node by ID')) {
                label.textContent = 'Buscar Bairro por Nome';
            }
        });
        
        var selects = document.querySelectorAll('select');
        selects.forEach(function(select) {
            if (select.options[0] && select.options[0].value === '') {
                if (select.options[0].text.includes('Select a Node')) {
                    select.options[0].text = 'Digite o nome do bairro...';
                }
            }
        });
        
        var buttons = document.querySelectorAll('button');
        buttons.forEach(function(btn) {
            if (btn.textContent.trim() === 'Reset Selection') {
                btn.textContent = 'Limpar';
            }
        });
    }, 800);
}

window.addEventListener('load', function() {
    setupTooltips();
    traduzirInterface();
});

</script>
"""
    
    # injetar tudo no html
    if '<meta charset="utf-8">' not in html_content:
        html_content = html_content.replace('<head>', '<head>\n<meta charset="utf-8">')
    
    html_content = html_content.replace('</head>', '\n</head>')
    
    body_pos = html_content.find('<body>')
    if body_pos != -1:
        close_body = html_content.find('>', body_pos) + 1
        html_content = html_content[:close_body] + '\n' + header_and_css + '\n' + html_content[close_body:]
    
    html_content = html_content.replace('</body>', '\n' + footer_html + '\n' + js_code + '\n</body>')
    
    # salvar arquivo final
    output_file = os.path.join('out', 'grafo_interativo.html')
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Grafo interativo salvo em '{output_file}'")
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    except Exception as e:
        print(f"Erro ao salvar '{output_file}': {e}")
        
    return html_content
# Projeto Final - GRAFOS

## Requisitos

- Bibliotecas Python (requirements.txt)
  - pandas
  - matplotlib
  - pyvis
  - numpy

## Como instalar

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd projeto-grafos
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

## 📁 Estrutura do Projeto



## 🎯 Como Executar

### Execução Completa (Parte 1 + Parte 2)

```bash
python -m src.cli
```

Isso irá:
1. Processar os dados dos bairros do Recife
2. Calcular métricas do grafo (ordem, tamanho, densidade)
3. Gerar visualizações e análises (Parte 1)
4. Executar análises com os 4 algoritmos no dataset maior (Parte 2)

### Executar Apenas os Testes

```
python tests/test_bfs.py
python tests/test_dfs.py
python tests/test_dijkstra.py
python tests/test_bellman_ford.py
```

## 📊 Saídas Geradas

### Parte 1: Grafo dos Bairros do Recife

**JSONs:**
- `out/recife_global.json` - Métricas globais (ordem, tamanho, densidade)
- `out/microrregioes.json` - Métricas por microrregião
- `out/percurso_nova_descoberta_setubal.json` - Caminho obrigatório

**CSVs:**
- `out/ego_bairro.csv` - Métricas de ego-rede por bairro
- `out/graus.csv` - Lista de graus de todos os bairros
- `out/distancias_enderecos.csv` - Distâncias entre pares de endereços

**Visualizações (PNG):**
- `out/arvore_percurso.png` - Visualização linear do percurso
- `out/arvore_percurso_destacada.png` - Árvore BFS completa com caminho destacado
- `out/mapa_cores_grau.png` - Mapa de cores por grau dos bairros
- `out/histograma_graus.png` - Distribuição dos graus
- `out/ranking_densidade_microrregiao.png` - Ranking de densidade por microrregião

**Interativo (HTML):**
- `out/grafo_interativo.html` - Grafo interativo com busca e destaque de caminhos

### Parte 2: Dataset Maior e Comparação de Algoritmos

**JSONs:**
- `out/parte2_report.json` - Relatório completo com métricas de todos os algoritmos
- `out/parte2_bfs.json` - Resultados das execuções BFS
- `out/parte2_dfs.json` - Resultados das execuções DFS
- `out/parte2_dijkstra.json` - Resultados Dijkstra
- `out/parte2_bellman_ford.json` - Resultados Bellman-Ford (incluindo testes com pesos negativos)

**CSVs:**
- `out/parte2_dijkstra.csv` - Resultados tabulares Dijkstra

## 🧪 Algoritmos Implementados

Todos os algoritmos foram implementados **do zero** (sem usar bibliotecas como networkx):

### 1. **BFS (Breadth-First Search)**
- Busca em largura
- Calcula níveis/camadas a partir da fonte
- Retorna ordem de visitação

### 2. **DFS (Depth-First Search)**
- Busca em profundidade
- Detecta ciclos (back edges)
- Classifica arestas (tree, back, forward, cross)
- Calcula tempos de descoberta e finalização

### 3. **Dijkstra**
- Caminho mínimo com pesos não-negativos
- Usa heap (heapq) para otimização
- Detecta pesos negativos (levanta erro)
- Complexidade: O((V + E) log V)

### 4. **Bellman-Ford**
- Caminho mínimo com pesos negativos permitidos
- Detecta ciclos negativos
- Retorna o ciclo quando detectado
- Complexidade: O(V × E)

## 📝 Casos de Teste

O projeto inclui **43 testes unitários** cobrindo:

- **BFS**: 8 testes (níveis corretos, caminhos, grafos desconectados)
- **DFS**: 11 testes (detecção de ciclos, classificação de arestas, tempos)
- **Dijkstra**: 12 testes (caminhos corretos, rejeição de pesos negativos)
- **Bellman-Ford**: 12 testes (pesos negativos sem ciclo, detecção de ciclo negativo)

## 🎨 Visualizações

### Grafo Interativo (Parte 1)

Abra `out/grafo_interativo.html` no navegador para:
- Visualizar o grafo completo dos bairros
- Buscar bairros específicos
- Ver tooltips com informações (grau, microrregião, densidade)
- Destacar o caminho "Nova Descoberta → Setúbal"

### Mapas e Rankings

Todas as visualizações estáticas estão em formato PNG na pasta `out/`.

## Definição dos Pesos

Os pesos das arestas no grafo dos bairros (arquivo `data/adjacencias_bairros.csv`) foram definidos com base na categoria das vias:

- **Peso 1.0**: Travessas e ladeiras
- **Peso 2.0**: Pontes e viadutos
- **Peso 3.0**: Ruas e estradas
- **Peso 4.0**: Avenidas
- **Peso 5.0**: BR

## Desempenho dos algoritmos

Resultados típicos no dataset da Parte 2 (810 nós, 16.148 arestas):

- **BFS**: 0.01-0.05s por fonte
- **DFS**: 0.01-0.05s por fonte
- **Dijkstra**: 0.008-0.04s por par origem-destino
- **Bellman-Ford**: 0.5-2s por fonte (mais lento, mas lida com pesos negativos)

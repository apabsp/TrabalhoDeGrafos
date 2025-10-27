# Em: src/graphs/graph.py

class Grafo: 
    def __init__(self):
        self.adj = {}
        self.num_arestas = 0  # Correto!
    
    def add_node(self, bairro):
        if bairro not in self.adj:
            self.adj[bairro] = []

    def add_edge(self, origem, destino, peso):
        
        self.add_node(origem)
        self.add_node(destino)

        self.adj[origem].append((destino, peso))
        # print(self)  # <-- COMENTE OU APAGUE ESTA LINHA
        self.adj[destino].append((origem, peso))
        # print(self)  # <-- COMENTE OU APAGUE ESTA LINHA

        self.num_arestas += 1 # Correto!

    # ----------------------------------------------------
    # VERSÃO CORRIGIDA DOS MÉTODOS GET
    # ----------------------------------------------------

    def get_numero_de_nos(self):
        """ Retorna o número de nós (vértices) no grafo. """
        return len(self.adj)

    def get_numero_de_arestas(self):
        """ Retorna o número de arestas no grafo. """
        return self.num_arestas

    def get_todos_os_nos(self):
        """ Retorna uma lista com todos os nomes dos nós. """
        return list(self.adj.keys())

    def get_vizinhos(self, nome_no):
        """ Retorna a lista de vizinhos (com pesos) de um nó. """
        if nome_no in self.adj:
            return self.adj[nome_no] 
        else:
            return []
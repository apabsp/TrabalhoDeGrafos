class Grafo: 
    def __init__(self):
        self.adj = {}
    
    def add_node(self, bairro):
        if bairro not in self.adj:
            self.adj[bairro] = []

    def add_edge(self, origem, destino, peso):
        
        self.add_node(origem)
        self.add_node(destino)

        self.adj[origem].append((destino, peso))
        print(self)
        self.adj[destino].append((origem, peso))
        print(self)



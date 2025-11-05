import os
from src import solve 

# Define o nome da pasta de saída
OUTPUT_DIR = 'out'

def main():
    """
    Função principal que executa o projeto.
    """
    print("Iniciando a execução via 'cli.py'...")

    # --- NOVO TRECHO: Garantir que a pasta 'out/' existe ---
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Diretório '{OUTPUT_DIR}' criado com sucesso.")
    # --- FIM DO NOVO TRECHO ---

    # 1. Construir o grafo (chamando a função de solve.py)
    print("Construindo grafo principal...")
    G, df_bairros, df_adj = solve.construir_grafo_principal()
    
    if G:
        print("Grafo construído. Iniciando análises...")
        # 2. Rodar as análises (chamando as funções de solve.py)
        # (Agora essas funções vão salvar os arquivos)
        solve.analisar_grafo_completo(G)
        solve.analisar_microrregioes(df_bairros, df_adj)
        solve.analisar_ego_redes(G, df_adj)
        solve.analisar_graus_e_rankings(G)            # exibe bairro com maior grau e bairro mais denso
        
        print(f"\nAnálise concluída. Arquivos de saída gerados em '{OUTPUT_DIR}/'.")
    else:
        print("Falha na construção do grafo. Verifique seus arquivos em 'data/'.")

if __name__ == "__main__":
    # Este é o único arquivo que deve ter o bloco __main__
    main()
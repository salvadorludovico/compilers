import csv

def carregar_tabelas_csv(caminho_csv):
    tabela_acoes = {}
    tabela_desvios = {}
    
    with open(caminho_csv, newline='', encoding='utf-8') as csvfile:
        reader = list(csv.reader(csvfile))
        cabecalho = reader[0]

        idx_estado = 0
        idx_primeira_acao = 1
        idx_ultima_acao = 24
        idx_primeiro_desvio = 25  
        idx_ultimo_desvio = 43    

        for linha in reader[1:]:
            if not linha or not linha[0].isdigit():
                continue  

            estado = int(linha[idx_estado])

            
            for i in range(idx_primeira_acao, idx_ultima_acao + 1):
                simbolo_terminal = cabecalho[i]
                acao = linha[i].strip()
                if acao:
                    tabela_acoes[(estado, simbolo_terminal)] = acao

            
            for i in range(idx_primeiro_desvio, idx_ultimo_desvio + 1):
                simbolo_nao_terminal = cabecalho[i]
                desvio = linha[i].strip()
                if desvio:
                    tabela_desvios[(estado, simbolo_nao_terminal)] = int(desvio)

    return tabela_acoes, tabela_desvios

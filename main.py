import sys
from mapeador_tabela_analise import carregar_tabelas_csv
from scanner import lexic_scanner
from parser import Parser

producoes = {
    0:  ("P'", ["P"]),
    1:  ("P", ["inicio", "V", "A"]),
    2:  ("V", ["varinicio", "LV"]),
    3:  ("LV", ["D", "LV"]),
    4:  ("LV", ["varfim", "ptv"]),
    5:  ("D", ["L", "TIPO", "ptv"]),
    6:  ("L", ["id", "vir", "L"]),
    7:  ("L", ["id"]),
    8:  ("TIPO", ["int"]),
    9:  ("TIPO", ["real"]),
    10: ("TIPO", ["lit"]),  
    11: ("A", ["ES", "A"]),
    12: ("ES", ["leia", "id", "ptv"]),
    13: ("ES", ["escreva", "ARG", "ptv"]),
    14: ("ARG", ["lit"]),
    15: ("ARG", ["num"]),
    16: ("ARG", ["id"]),
    17: ("A", ["CMD", "A"]),
    18: ("CMD", ["id", "rcb", "LD", "ptv"]),
    19: ("LD", ["OPRD", "opm", "OPRD"]),
    20: ("LD", ["OPRD"]),
    21: ("OPRD", ["id"]),
    22: ("OPRD", ["num"]),
    23: ("A", ["COND", "A"]),
    24: ("COND", ["CAB", "CP"]),
    25: ("CAB", ["se", "ab_p", "EXP_R", "fc_p", "entao"]),
    26: ("EXP_R", ["OPRD", "opr", "OPRD"]),
    27: ("CP", ["ES", "CP"]),
    28: ("CP", ["CMD", "CP"]),
    29: ("CP", ["COND", "CP"]),
    30: ("CP", ["fimse"]),
    31: ("A", ["R", "A"]),
    32: ("R", ["faca-ate", "ab_p", "EXP_R", "fc_p", "CP_R"]),
    33: ("CP_R", ["ES", "CP_R"]),
    34: ("CP_R", ["CMD", "CP_R"]),
    35: ("CP_R", ["COND", "CP_R"]),
    36: ("CP_R", ["fimfaca"]),
    37: ("A", ["fim"]),
}

simbolos_sincronismo = { 'ptv', 'fimse', 'fimfaca', 'varfim', 'fim', '$' }

token_para_msg = {
    "inicio": "início do programa",
    "varinicio": "início da declaração de variáveis",
    "varfim": "fim da declaração de variáveis",
    "ptv": "ponto e vírgula (;)",
    "id": "identificador",
    "vir": "vírgula (',')",
    "int": "tipo inteiro",
    "real": "tipo real",
    "lit": "literal",
    "leia": "comando leia",
    "escreva": "comando escreva",
    "num": "número",
    "rcb": "atribuição (<-)",
    "opm": "operador aritmético (+, -, *, /)",
    "se": "comando se",
    "ab_p": "abre parêntese '('",
    "fc_p": "fecha parêntese ')'",
    "entao": "então",
    "opr": "operador relacional (<, >, >=, <=, =, <>)",
    "fimse": "fim do comando se",
    "faca-ate": "comando faça até",
    "fimfaca": "fim do comando faça",
    "fim": "fim do programa",
    "$": "fim da entrada"
}

def main():
    """Função principal do compilador"""
    if len(sys.argv) != 2:
        print("Uso: python compilador.py <arquivo_fonte.alg>")
        sys.exit(1)
    
    codigo_fonte = sys.argv[1]
    
    try:
        print("🔍 Iniciando Compilação...")
        print(f"📄 Arquivo fonte: {codigo_fonte}")
        print("=" * 60)
        
        print("\n🔤 FASE 1: Análise Léxica")
        tokens = lexic_scanner(codigo_fonte)
        
        if not tokens:
            print("❌ Erro: Nenhum token foi gerado pela análise léxica.")
            return False
        
        print("\n📊 FASE 2: Carregamento das Tabelas de Análise")
        try:
            tabela_acoes, tabela_desvios = carregar_tabelas_csv("TABELA_ACOES_DESVIOS.csv")
            print("✅ Tabelas de análise carregadas com sucesso!")
        except FileNotFoundError:
            print("❌ Erro: Arquivo 'TABELA_ACOES_DESVIOS.csv' não encontrado.")
            return False
        except Exception as e:
            print(f"❌ Erro ao carregar tabelas: {e}")
            return False
        
        print("\n🔗 FASE 3: Análise Sintática e Semântica")
        parser = Parser(
            tokens,
            tabela_acoes,
            tabela_desvios,
            producoes,
            token_para_msg,
            simbolos_sincronismo,
            "panico"
        )
        
        sucesso = parser.analisar()
        
        if sucesso:
            print("\n🎉 COMPILAÇÃO CONCLUÍDA COM SUCESSO!")
            print("✅ Arquivo PROGRAMA.C gerado!")
            print("\n💡 Para testar o código gerado:")
            print("   gcc PROGRAMA.C -o programa")
            print("   ./programa")
        else:
            print("\n❌ COMPILAÇÃO FALHOU!")
            print("💡 Corrija os erros e tente novamente.")
        
        return sucesso
        
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo '{codigo_fonte}' não encontrado.")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado durante a compilação: {e}")
        return False

if __name__ == "__main__":
    main()
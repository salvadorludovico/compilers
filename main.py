import sys
from parser import Parser
from mapeador_tabela_analise import carregar_tabelas_csv
from scanner import lexic_scanner

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
    9: ("TIPO", ["real"]),
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

tabela_acoes, tabela_desvios = carregar_tabelas_csv("TABELA_ACOES_DESVIOS.csv")

codigo_fonte= sys.argv[1]
tokens = lexic_scanner(codigo_fonte)

parser = Parser(
  tokens,
  tabela_acoes,
  tabela_desvios,
  producoes,
  token_para_msg,
  simbolos_sincronismo,
  "panico"
)

parser.analisar()




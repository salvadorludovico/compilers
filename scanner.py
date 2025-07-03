import pandas as pd

palavras_reservadas = ["inicio", "varinicio", "varfim", "escreva", "leia", "se", "entao", "fimse", "faca-ate", "fimfaca", "fim", "int", "lit", "real"]

class TabelaDeSimbolos:
    def __init__(self):
        self.tabela = {}
    
    # def inserir(self, token):
    #     lexema = token["lexema"]

    #     if lexema in palavras_reservadas:
    #         return self.tabela[lexema]

    #     for _, token_na_tabela in self.tabela.items():
    #         if token_na_tabela["lexema"] == lexema:
    #             return token_na_tabela

    #     if lexema not in self.tabela:
    #         self.tabela[lexema] = token
    #         return token
        
    #     return self.tabela[lexema]
    def inserir(self, token):
        lexema = token["lexema"]
        # Não insere palavras reservadas e verifica se já existe
        if lexema in palavras_reservadas or lexema in self.tabela:
            return self.tabela.get(lexema)
        
        # Insere o novo token
        self.tabela[lexema] = token
        return token
        
    # def buscar(self, token):
        # return self.tabela.get(token["classe"])
    
    def buscar(self, lexema):
      # A busca DEVE ser feita pelo lexema!
      return self.tabela.get(lexema)

    def atualizar_tipo(self, lexema, tipo):
        # Função útil para as regras de declaração
        if lexema in self.tabela:
            self.tabela[lexema]['tipo'] = tipo
        else:
            # Isso indicaria um erro lógico, a variável deveria ter sido inserida primeiro
            pass

    def imprimir(self):
      print("\n✳️  Tabela de Símbolos:\n")
      print(f"{'Classe':^10} | {'Lexema':^25} | {'Tipo':^10} | {'Linha':^5} | {'Coluna':^6}")
      print("-" * 70)
      for simbolo in self.tabela.values():
          classe = str(simbolo['classe'])
          lexema = str(simbolo['lexema'])
          tipo = str(simbolo['tipo']) if simbolo['tipo'] is not None else 'None'
          linha = str(simbolo['l'])
          coluna = str(simbolo['c'])
          print(f"{classe:^10} | {lexema:^25} | {tipo:^10} | {linha:^5} | {coluna:^6}")

      print("\n")


class ErroLexico:
    def __init__(self, mensagem, linha, coluna, caractere):
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        self.caractere = caractere

    def __str__(self):
        return f"{self.mensagem}: '{self.caractere}' na linha {self.linha}, coluna {self.coluna}"


class Erros:
    def __init__(self):
        self._erros = []

    def adicionar_erro(self, erro):
        self._erros.append(erro)

    def tem_erros(self):
        return len(self._erros) > 0

    def __str__(self):
        return "\n".join(str(e) for e in self._erros)


class AFD:
    def __init__(self, tabela_simbolos=None):
        
        self.mapeamento_de_erros = {
            "1": "Literal Incompleta",               
            "2": "Comentário Incompleto",            
            "3": "Num - Real Incompleto",            
            "4": "Num - Notação Cientifica Incompleta", 
            "5": "Num - Notação Cientifica Sinal Sem Dígito", 
            "6": "Caractere inesperado"
        }

        self.estados = {
            "q0": {
                "info": "Estado Inicial",
                "transicoes": {
                    "LETRA": "q1",
                    "\"": "q2",
                    "{": "q4",
                    "EOF": "q6",
                    "<": "q7",
                    "=": "q8",
                    ">": "q9",
                    "+": "q11",
                    "-": "q11",
                    "*": "q11",
                    "/": "q11",
                    "(": "q12",
                    ")": "q13",
                    ";": "q14",
                    ",": "q15",
                    "DIGITO": "q16",
                }
            },
            "q1": {
                "info": "id",
                "tipo": None,
                "transicoes": {
                    "LETRA": "q1",
                    "DIGITO": "q1",
                    "_": "q1",
                    "-": "q1",
                }
            },
            "q2": {
                "info": "Literal Incompleta",
                "transicoes": {
                    "QUALQUER COISA": "q2",
                    "\"": "q3",
                }
            },
            "q3": {
                "info": "lit",
                "tipo": "lit",
                "transicoes": {}
            },
            "q4": {
                "info": "Comentário Incompleto",
                "transicoes": {
                    "QUALQUER COISA": "q4",
                    "}": "q5",
                }
            },
            "q5": {
                "info": "Comentário",
                "transicoes": {}
            },
            "q6": {
                "info": "EOF",
                "tipo": "EOF",
                "transicoes": {}
            },
            "q7": {
                "info": "opr",
                "tipo": None,
                "transicoes": {
                    "=": "q8",
                    ">": "q8",
                    "-": "q10",
                }
            },
            "q8": {
                "info": "opr",
                "tipo": None,
                "transicoes": {}
            },
            "q9": {
                "info": "opr",
                "tipo": None,
                "transicoes": {
                    "=": "q8",
                }
            },
            "q10": {
                "info": "rcb",
                "tipo": None,
                "transicoes": {}
            },
            "q11": {
                "info": "opm",
                "tipo": None,
                "transicoes": {}
            },
            "q12": {
                "info": "ab_p",
                "tipo": None,
                "transicoes": {}
            },
            "q13": {
                "info": "fc_p",
                "tipo": None,
                "transicoes": {}
            },
            "q14": {
                "info": "ptv",
                "tipo": None,
                "transicoes": {}
            },
            "q15": {
                "info": "vir",
                "tipo": None,
                "transicoes": {}
            },
            "q16": {
                "info": "num",
                "tipo": "int",
                "transicoes": {
                    "DIGITO": "q16",
                    ".": "q17",
                    "E": "q19",
                    "e": "q19",
                }
            },
            "q17": {
                "info": "num - Real Incompleto",
                "transicoes": {
                    "DIGITO": "q18",
                }
            },
            "q18": {
                "info": "num",
                "tipo": "real",
                "transicoes": {
                    "DIGITO": "q18",
                }
            },
            "q19": {
                "info": "num - Notação Cientifica Incompleta",
                "transicoes": {
                    "DIGITO": "q18",
                    "+": "q21",
                    "-": "q21",
                }
            },
            "q20": {
                "info": "num",
                "tipo": "Notação Cientifica",
                "transicoes": {
                    "DIGITO": "q20",
                }
            },
            "q21": {
                "info": "num - Notação Cientifica Sinal Sem Dígito",
                "transicoes": {
                    "DIGITO": "q20",
                }
            },
        }

        self.lexema = ""
        self.simbolo = ""
        self.linha_inicio_lexema = None
        self.coluna_inicio_lexema = None
        self.estado_atual_id = "q0"
        
        self.estados_erro_ids = ["q2", "q4", "q17", "q19", "q21"]
        self.estados_finais_ids = ["q1", "q3", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "q12", "q13", "q14", "q15", "q16", "q18", "q20"]
        self.estados_tabela_simbolos = ["q1", "q3", "q16", "q18", "q20"]

        self.tabela_simbolos = tabela_simbolos if tabela_simbolos else TabelaDeSimbolos()
        self.erros = Erros()

    def mapear_erro(self, info):
        for codigo, mensagem in self.mapeamento_de_erros.items():
            if mensagem == info:
                return codigo
        return None
    
    def imprimir_linha_automato(self, caractere, linha, coluna):
        if caractere == '\n':
            caractere_visivel = '\\n'
        elif caractere == '\t':
            caractere_visivel = '\\t'
        elif caractere == ' ':
            caractere_visivel = "' '"
        else:
            caractere_visivel = caractere
        print(f"{caractere_visivel:^12} | {linha:^5} | {coluna:^6} | {self.estado_atual_id:^4} | {self.lexema:<20}")
    def salvar_loc_inicio_lexema(self, l, c):
        self.linha_inicio_lexema = l
        self.coluna_inicio_lexema = c

    def transitar(self, caractere, linha, coluna):
        self.linha = linha
        self.coluna = coluna
        
        if caractere in (" ", "\t", "\n") and self.estado_atual_id == "q0":
            return None
        
        if caractere == "EOF":
            token = {
                "classe": "EOF",
                "lexema": "EOF",
                "tipo": None,
                "l": linha,
                "c": coluna
            }
            return token

        
        transicoes_disponiveis = self.estados[self.estado_atual_id]["transicoes"]

        
        if caractere.isalpha():
            self.simbolo = "LETRA"
        elif caractere.isdigit():
            self.simbolo = "DIGITO"
        else:
            self.simbolo = caractere

        
        if self.simbolo in transicoes_disponiveis:
            if (self.estado_atual_id == "q0"): 
                self.salvar_loc_inicio_lexema(linha, coluna)
            self.estado_atual_id = transicoes_disponiveis[self.simbolo]
            self.lexema += caractere
            return None
        elif "QUALQUER COISA" in transicoes_disponiveis:
            if (self.estado_atual_id == "q0"): 
                self.salvar_loc_inicio_lexema(linha, coluna)
            self.estado_atual_id = transicoes_disponiveis["QUALQUER COISA"]
            self.lexema += caractere
            return None

        
        info = self.estados[self.estado_atual_id]["info"]

        estado_atual_eh_final = self.estado_atual_id in self.estados_finais_ids
        estado_atual_eh_erro = self.estado_atual_id in self.estados_erro_ids
        
        if estado_atual_eh_erro:
            erro = ErroLexico(info, linha, coluna, caractere)
            self.erros.adicionar_erro(erro)
            print(f"Erro: {info} na linha {linha}, coluna {coluna} - caractere: '{caractere}'")
            
            codigo_erro = self.mapear_erro(info)
            token = {
                "classe": "ERRO",
                "lexema": codigo_erro,
                "tipo": None,
                "l": linha,
                "c": coluna
            }
            
            self.estado_atual_id = "q0"
            self.lexema = ""
            
            return token        
        elif estado_atual_eh_final:
            if self.estado_atual_id == "q1" and self.lexema in palavras_reservadas:
                token = {
                    "classe": self.lexema, 
                    "lexema": self.lexema, 
                    "tipo": self.lexema,
                    "l": self.linha_inicio_lexema,
                    "c": self.coluna_inicio_lexema
                }
                
                self.estado_atual_id = "q0"
                self.lexema = ""
                return token
            
            token = {
                "classe": info,
                "lexema": self.lexema,
                "tipo": self.estados[self.estado_atual_id]["tipo"],
                "l": self.linha_inicio_lexema,
                "c": self.coluna_inicio_lexema
            }
            if (self.estado_atual_id in self.estados_tabela_simbolos):
                self.tabela_simbolos.inserir(token)
            
            
            self.estado_atual_id = "q0"
            self.lexema = ""
            return token

        
        erro = ErroLexico("Caractere inesperado", linha, coluna, caractere)
        self.erros.adicionar_erro(erro)
        token = {
            "classe": "ERRO",
            "lexema": "6",  
            "tipo": None,
            "l": linha,
            "c": coluna
        }
        
        self.estado_atual_id = "q0"
        self.lexema = ""
        return token

def imprimir_lista_caracteres(lista_caracteres):
        print(f"{'Valor':^7} | {'Linha':^7} | {'Coluna':^7}")
        print("-" * 25)
        for caractere in lista_caracteres:
            valor = caractere['valor']
            # Para tornar quebras de linha e tabulações legíveis:
            if valor == '\n':
                valor_visivel = '\\n'
            elif valor == '\t':
                valor_visivel = '\\t'
            elif valor == ' ':
                valor_visivel = "' '"
            else:
                valor_visivel = valor
            print(f"{valor_visivel:^7} | {caractere['linha']:^7} | {caractere['coluna']:^7}")

def scanner(caminho_arquivo):
    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
        conteudo = arquivo.read()

                
    linha = 1
    coluna = 1
    qtd_espacos_tab = 4
    lista_caracteres = []
    
    for caractere in conteudo:
        if caractere == '\n':
            lista_caracteres.append({
                "valor": caractere, 
                "coluna": coluna, 
                "linha": linha
            })
            linha += 1
            coluna = 0
        elif caractere == '\t':
            lista_caracteres.append({
                "valor": caractere, 
                "coluna": coluna, 
                "linha": linha
            })
            coluna += qtd_espacos_tab - ((coluna - 1) % qtd_espacos_tab)
        else:
            lista_caracteres.append({
                "valor": caractere, 
                "coluna": coluna, 
                "linha": linha
            })
            coluna += 1
    
    return lista_caracteres


def executar_afd(lista_caracteres, afd):
    tokens = []
    i = 0

    while i < len(lista_caracteres):
        caractere = lista_caracteres[i]["valor"]
        linha = lista_caracteres[i]["linha"]
        coluna = lista_caracteres[i]["coluna"]

        token = afd.transitar(caractere, linha, coluna)

        if token is not None and token["classe"] != "ERRO":
            tokens.append(token)
            if token["classe"] != "ERRO":
                continue

        i += 1

    
    info = afd.estados[afd.estado_atual_id]["info"]

    estado_atual_eh_final = afd.lexema and afd.estado_atual_id in afd.estados_finais_ids
    estado_atual_eh_erro = afd.lexema and afd.estado_atual_id in afd.estados_erro_ids

    if estado_atual_eh_final:
        if (afd.lexema in palavras_reservadas):
            tokens.append({
                "classe": afd.lexema,
                "lexema": afd.lexema,
                "tipo": afd.lexema,
                "l": afd.linha,
                "c": afd.coluna
            }) 
        else:
            tokens.append({
                "classe": info,
                "lexema": afd.lexema,
                "tipo": None,
                "l": afd.linha,
                "c": afd.coluna
            })
    if estado_atual_eh_erro:
        afd.erros.adicionar_erro(
            ErroLexico(info, linha, coluna, afd.lexema)
        )

    
    token_eof = afd.transitar("EOF", linha, coluna + 1)
    if token_eof:
        tokens.append(token_eof)

    return tokens

def imprimir_tokens(tokens):
    print("\n✳️  Tokens Reconhecidos:\n")
    print(f"{'Classe':^10} | {'Lexema':^25} | {'Tipo':^10} | {'Linha':^5} | {'Coluna':^6}")
    print("-" * 70)
    for token in tokens:
        classe = str(token['classe'])
        lexema = str(token['lexema'])
        tipo = str(token['tipo']) if token['tipo'] is not None else 'None'
        linha = str(token['l'])
        coluna = str(token['c'])
        print(f"{classe:^10} | {lexema:^25} | {tipo:^10} | {linha:^5} | {coluna:^6}")
    print("\n")


def lexic_scanner(codigo_fonte = "Font.ALG"):    
    tabela_de_simbolos = TabelaDeSimbolos()
    afd = AFD(tabela_de_simbolos)
    
    lista_caracteres = scanner(codigo_fonte)
    tokens = executar_afd(lista_caracteres, afd)

    if afd.erros.tem_erros():
        print("\n⚠️  Erros léxicos encontrados:\n")
        print(afd.erros)

    imprimir_tokens(tokens)

    tabela_de_simbolos.imprimir()

    return tokens, tabela_de_simbolos

if __name__ == "__main__":
    lexic_scanner("Font.ALG")
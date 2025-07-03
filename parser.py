class Parser:
    def __init__(
            self,
            tokens, 
            tabela_acoes,
            tabela_desvios,
            producoes,
            token_para_msg,
            simbolos_sincronismo,
            semantico,
            metodo_recuperacao_erro="panico",
            max_tentativas=10
        ):

        tokens[-1]["classe"] = "$"
        tokens[-1]["lexema"] = "$"
        tokens[-1]["tipo"] = None

        self.tokens = tokens
        self.tabela_acoes = tabela_acoes
        self.tabela_desvios = tabela_desvios
        self.producoes = producoes
        self.pilha = [0]
        self.ip = 0
        self.erros = []
        self.metodo_recuperacao_erro = metodo_recuperacao_erro
        self.max_tentativas = max_tentativas 
        self.tentativas_recuperacao = 0
        self.token_para_msg = token_para_msg
        self.simbolos_sincronismo = simbolos_sincronismo
        self.semantico = semantico

    def analisar(self):
        print("✳️  Análise Sintática Shift-Reduce:\n")
        print(f"📊  Método de recuperação de erro: {self.metodo_recuperacao_erro.upper()}\n")
        
        while True:
            estado = self.pilha[-1]
            token_atual = self.tokens[self.ip]
            simbolo = token_atual["classe"]
            
            acao = self.tabela_acoes.get((estado, simbolo), "erro")
            
            # print("s: ", estado)
            # print("a: ", simbolo)
            # print("ação: ", acao)
            
            if acao.startswith("s"):
                prox_estado = int(acao[1:])
                self.pilha.append(prox_estado) 
                self.semantico.pilha_semantica.append(token_atual) # empilha Token com seus atributos
                self.ip += 1
                # print(f"▷ SHIFT: '{simbolo}' → Estado {prox_estado}")
            elif acao.startswith("r"):

                num_regra_de_producao = int(acao[1:])
                simbolo_do_lado_esquerdo, sequencia_lado_direito = self.producoes[num_regra_de_producao]
                tamanho_sequencia_lado_direito = len(sequencia_lado_direito)
                for _ in range(tamanho_sequencia_lado_direito):
                    self.pilha.pop()

                estado_topo = self.pilha[-1]
                prox_estado = self.tabela_desvios.get((estado_topo, simbolo_do_lado_esquerdo))
                if prox_estado is None:
                    print(f"❌ Erro de produção sintática: não foi possível realizar transição GOTO para o não-terminal '{simbolo_do_lado_esquerdo}' no estado {estado_topo}.")
                    return False
                self.pilha.append(prox_estado)
                # print(f"◁ REDUCE: {simbolo_do_lado_esquerdo} → {' '.join(sequencia_lado_direito)} → GOTO {prox_estado}") 

                atributos_desempilhados = []
                for _ in range(tamanho_sequencia_lado_direito):
                  atributos_desempilhados.insert(0, self.semantico.pilha_semantica.pop()) # Insere no início para manter a ordem

                print(f"◁ {simbolo_do_lado_esquerdo} → {' '.join(sequencia_lado_direito)}")
                # TODO: Chama uma função que executará as regras semânticas à regra sintática que foi reduzida
                self.semantico.acao_semantica(num_regra_de_producao)
            elif acao == "acc":
                if(len(self.erros) == 0): 
                    print("✅ Sentença reconhecida com sucesso!")
                    self.semantico.gerar_arquivo_saida()
                    return True
                else:
                    self.imprimir_relatorio_erros()
                    for erro in self.semantico.erros_semanticos:
                      print(erro)
                    return False
                
            else:
                if simbolo == "$":
                    msg =f"Fim de arquivo inesperado na linha {self.tokens[-1]['l']}, coluna {self.tokens[-1]['c']}."
                    self.registrar_erro(
                        tipo="Fim de arquivo inesperado",
                        mensagem=msg,
                        linha=self.tokens[-2]['l'],
                        coluna=self.tokens[-2]['c']+1,
                    )
                    print(msg)
                    break
                else:
                    nome_token = self.token_para_msg.get(simbolo, simbolo)
                    tokens_esperados = self.obter_tokens_esperados(estado)
                    tokens_esperados_legiveis = self.traduzir_tokens(tokens_esperados, self.token_para_msg)

                    msg = f"Token inesperado '{nome_token}' na linha {token_atual['l']}, coluna {token_atual['c']}."
                    self.registrar_erro(
                        tipo="Token inesperado",
                        mensagem=msg,
                        linha=token_atual['l'],
                        coluna=token_atual['c'],
                        token=nome_token,
                        tokens_esperados=tokens_esperados_legiveis
                    )
                    print(f"❌ Erro sintático: {msg}")

                if self.metodo_recuperacao_erro == "frase":
                    if not self.recuperar_erro_frase(estado):
                        print(f"⚠️ Recuperação por frase falhou. Tentando recuperação no modo pânico...")
                        if not self.recuperar_erro_panico():
                            return False
                elif self.metodo_recuperacao_erro == "panico":
                    if not self.recuperar_erro_panico():
                        return False
        self.imprimir_relatorio_erros()

    def recuperar_erro_panico(self):
        while True:
            token_atual = self.tokens[self.ip]
            simbolo_atual = token_atual["classe"]
            simbolo_atual_eh_de_sincronismo = simbolo_atual in self.simbolos_sincronismo

            if simbolo_atual_eh_de_sincronismo:
                break
            else:
                self.ip += 1
                
                if self.ip >= len(self.tokens):
                    return False

        token_de_sincronismo = self.tokens[self.ip]
        simbolo_de_sincronismo = token_de_sincronismo["classe"]
        fim_da_entrada = simbolo_de_sincronismo == "$"

        if not fim_da_entrada:
            self.ip += 1

        return True
    
    def recuperar_erro_frase(self, estado):
        tokens_esperados = self.obter_tokens_esperados(estado)
        excedeu_as_tentativas_de_recuperacao = self.tentativas_recuperacao > self.max_tentativas

        if (excedeu_as_tentativas_de_recuperacao):
            return False

        if tokens_esperados:
            token_esperado = tokens_esperados[0]
            token_atual = self.tokens[self.ip - 1]

            print(f"⚠️ Recuperação: inserindo token esperado '{token_esperado}' para continuar a análise., Token Atual: '{token_atual}'")

            token_ficticio = {
                "classe": token_esperado,
                "lexema": token_esperado,
                "tipo": None,
                "l": token_atual["l"],
                "c": token_atual["c"] + len(token_atual['lexema'])
            }

            self.tokens.insert(self.ip, token_ficticio)
            self.tentativas_recuperacao += 1
            return True

        print(f"❌ Não foi possível realizar recuperação em nível de frase. Falta de tokens esperados.")
        return False    
    
    def obter_tokens_esperados(self, estado):
        tokens_terminais = ["inicio", "varinicio", "varfim", "ptv", "id", "vir", "int", "real", "lit", "leia", "escreva", "num", "rcb", "opm", "se", "ab_p", "fc_p", "entao", "opr", "fimse", "faca-ate", "fimfaca", "fim"]
        
        tokens_esperados = []
        for token in tokens_terminais:
            tem_acao_para_o_token_neste_estado = (estado, token) in self.tabela_acoes
            if tem_acao_para_o_token_neste_estado:
                tokens_esperados.append(token)

        return tokens_esperados
    
    def traduzir_tokens(self, tokens, mapa):
        return [mapa.get(t, t) for t in tokens]
    
    def registrar_erro(self, tipo, mensagem, linha=None, coluna=None, token=None, tokens_esperados=None):
        erro = {
            "tipo": tipo,
            "mensagem": mensagem,
            "linha": linha,
            "coluna": coluna,
            "token": token,
            "tokens_esperados": tokens_esperados or []
        }
        self.erros.append(erro)

    def imprimir_relatorio_erros(self):
        if not self.erros:
            print("Nenhum erro sintático detectado.")
            return
        
        
        print("\n❌ -------------------- Relatório de Erros Sintáticos -------------------- ❌\n")
        for i, erro in enumerate(self.erros, 1):
            print(f"{i}. {erro['mensagem']}")
            if erro['tokens_esperados']:
                print(f"   Tokens esperados:")
                for t in erro['tokens_esperados']:
                    print(f"     - {t}")
            print()
 # type: ignore
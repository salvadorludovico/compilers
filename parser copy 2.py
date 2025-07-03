class AnalisadorSemantico:
    def __init__(self, tabela_simbolos):
        self.tabela_simbolos = tabela_simbolos
        self.pilha_semantica = []
        self.arquivo_objeto = []
        self.contador_variaveis_temp = 0
        self.erros_semanticos = []
        self.tipos_declarados = {}  # Para tracking de tipos
        self.variaveis_temporarias_usadas = set()  # Conjunto de variáveis temporárias usadas
        self.dentro_programa = False
        self.ids_aguardando_tipo = []  # Lista de IDs esperando tipo
        
        # Mapeamento de tipos para C
        self.tipo_para_c = {
            'int': 'int',
            'real': 'double', 
            'lit': 'literal'
        }
        
        # Headers do programa C
        self.headers = [
            "#include<stdio.h>",
            "typedef char literal[256];",
            "void main(void)",
            "{"
        ]
    
    def gerar_variavel_temporaria(self, tipo='int'):
        """Gera uma nova variável temporária e registra seu uso"""
        var_nome = f"T{self.contador_variaveis_temp}"
        self.contador_variaveis_temp += 1
        self.variaveis_temporarias_usadas.add((var_nome, tipo))
        return var_nome
    
    def empilhar_token(self, token):
        """Empilha token na pilha semântica durante shift"""
        self.pilha_semantica.append(token)
    
    def executar_regra_semantica(self, num_producao, tamanho_lado_direito):
        """Executa regras semânticas baseadas no número da produção"""
        # Desempilha elementos da pilha semântica correspondentes ao lado direito
        elementos = []
        for _ in range(tamanho_lado_direito):
            if self.pilha_semantica:
                elementos.append(self.pilha_semantica.pop())
        elementos.reverse()  # Para manter a ordem original
        
        # Executa a regra semântica específica
        resultado = self._aplicar_regra(num_producao, elementos)
        
        # Empilha o resultado (símbolo do lado esquerdo com atributos)
        if resultado:
            self.pilha_semantica.append(resultado)
    
    def _aplicar_regra(self, num_producao, elementos):
        """Aplica a regra semântica específica"""
        if num_producao == 1:  # P → inicio V A
            self._iniciar_programa()
            return {"simbolo": "P"}
            
        elif num_producao == 4:  # LV → varfim;
            self._finalizar_declaracoes()
            return {"simbolo": "LV"}
            
        elif num_producao == 5:  # D → L TIPO;
            # Na produção D → L TIPO;, o TIPO está na posição 1 (índice 1)
            if len(elementos) >= 2:
                tipo_elem = elementos[1]  # TIPO está na segunda posição
                if tipo_elem.get("simbolo") == "TIPO" and "tipo" in tipo_elem:
                    self._processar_declaracao_tipo(tipo_elem["tipo"])
            return {"simbolo": "D"}
            
        elif num_producao == 6:  # L → id, L
            if elementos and elementos[0].get("classe") == "id":
                self.ids_aguardando_tipo.append(elementos[0])
            return {"simbolo": "L"}
            
        elif num_producao == 7:  # L → id
            if elementos and elementos[0].get("classe") == "id":
                self.ids_aguardando_tipo.append(elementos[0])
            return {"simbolo": "L"}
            
        elif num_producao == 8:  # TIPO → int
            return {"simbolo": "TIPO", "tipo": "int", "tipo_c": "int"}
            
        elif num_producao == 9:  # TIPO → real
            return {"simbolo": "TIPO", "tipo": "real", "tipo_c": "double"}
            
        elif num_producao == 10:  # TIPO → lit
            return {"simbolo": "TIPO", "tipo": "lit", "tipo_c": "literal"}
            
        elif num_producao == 12:  # ES → leia id;
            if len(elementos) >= 2 and elementos[1].get("classe") == "id":
                self._processar_leia(elementos[1])
            return {"simbolo": "ES"}
            
        elif num_producao == 13:  # ES → escreva ARG;
            if len(elementos) >= 2:
                arg = elementos[1]
                self._processar_escreva(arg)
            return {"simbolo": "ES"}
            
        elif num_producao == 14:  # ARG → lit
            if elementos:
                return {"simbolo": "ARG", "lexema": elementos[0].get("lexema", ""), 
                       "tipo": "lit", "classe": "lit"}
                       
        elif num_producao == 15:  # ARG → num
            if elementos:
                return {"simbolo": "ARG", "lexema": elementos[0].get("lexema", ""), 
                       "tipo": elementos[0].get("tipo", "int"), "classe": "num"}
                       
        elif num_producao == 16:  # ARG → id
            if elementos:
                id_token = elementos[0]
                if self._verificar_declaracao(id_token):
                    return {"simbolo": "ARG", "lexema": id_token.get("lexema", ""), 
                           "tipo": self.tipos_declarados.get(id_token.get("lexema", "")), 
                           "classe": "id"}
            return {"simbolo": "ARG"}
            
        elif num_producao == 18:  # CMD → id rcb LD;
            if len(elementos) >= 3:
                id_token = elementos[0]
                ld_token = elementos[2]
                self._processar_atribuicao(id_token, ld_token)
            return {"simbolo": "CMD"}
            
        elif num_producao == 19:  # LD → OPRD opm OPRD
            if len(elementos) >= 3:
                return self._processar_operacao_aritmetica(elementos[0], elementos[1], elementos[2])
            return {"simbolo": "LD"}
            
        elif num_producao == 20:  # LD → OPRD
            if elementos:
                return elementos[0]  # Propaga atributos
            return {"simbolo": "LD"}
            
        elif num_producao == 21:  # OPRD → id
            if elementos:
                id_token = elementos[0]
                if self._verificar_declaracao(id_token):
                    return {"simbolo": "OPRD", "lexema": id_token.get("lexema", ""), 
                           "tipo": self.tipos_declarados.get(id_token.get("lexema", "")), 
                           "classe": "id"}
            return {"simbolo": "OPRD"}
            
        elif num_producao == 22:  # OPRD → num
            if elementos:
                return {"simbolo": "OPRD", "lexema": elementos[0].get("lexema", ""), 
                       "tipo": elementos[0].get("tipo", "int"), "classe": "num"}
                       
        elif num_producao == 25:  # CAB → se (EXP_R) entao
            if len(elementos) >= 3:
                exp_r = elementos[2]
                self._processar_inicio_se(exp_r)
            return {"simbolo": "CAB"}
            
        elif num_producao == 24:  # COND → CAB CP
            self._processar_fim_se()
            return {"simbolo": "COND"}
            
        elif num_producao == 26:  # EXP_R → OPRD opr OPRD
            if len(elementos) >= 3:
                return self._processar_expressao_relacional(elementos[0], elementos[1], elementos[2])
            return {"simbolo": "EXP_R"}
            
        elif num_producao == 37:  # A → fim
            self._finalizar_programa()
            return {"simbolo": "A"}
        
        # Regras que não fazem nada (símbolo -)
        return {"simbolo": "DEFAULT"}
    
    def _iniciar_programa(self):
        """Inicia a geração do programa C"""
        self.dentro_programa = True
        for header in self.headers:
            self.arquivo_objeto.append(header)
    
    def _finalizar_declaracoes(self):
        """Finaliza declarações - variáveis temporárias serão adicionadas no final"""
        # Adiciona 3 linhas brancas conforme especificação
        self.arquivo_objeto.extend(["", "", ""])
    
    def _processar_declaracao_tipo(self, tipo):
        """Processa declaração de tipo para variáveis aguardando"""
        # Processa todos os IDs que estão aguardando tipo
        for id_elem in self.ids_aguardando_tipo:
            lexema = id_elem["lexema"]
            if lexema not in self.tipos_declarados:
                self.tipos_declarados[lexema] = tipo
                
                # Adiciona declaração no arquivo objeto
                tipo_c = self.tipo_para_c.get(tipo, tipo)
                self.arquivo_objeto.append(f"{tipo_c} {lexema};")
        
        # Limpa a lista após processar
        self.ids_aguardando_tipo = []
    
    def _verificar_declaracao(self, id_token):
        """Verifica se uma variável foi declarada"""
        lexema = id_token.get("lexema", "")
        if lexema not in self.tipos_declarados:
            linha = id_token.get("l", 0)
            coluna = id_token.get("c", 0)
            self.erros_semanticos.append(
                f"Erro: Variável '{lexema}' não declarada na linha {linha}, coluna {coluna}"
            )
            return False
        return True
    
    def _processar_leia(self, id_token):
        """Processa comando leia"""
        if not self._verificar_declaracao(id_token):
            return
            
        lexema = id_token.get("lexema", "")
        tipo = self.tipos_declarados.get(lexema)
        
        if tipo == "lit":
            self.arquivo_objeto.append(f'scanf("%s",{lexema});')
        elif tipo == "int":
            self.arquivo_objeto.append(f'scanf("%d",&{lexema});')
        elif tipo == "real":
            self.arquivo_objeto.append(f'scanf("%lf",&{lexema});')
    
    def _processar_escreva(self, arg):
        """Processa comando escreva"""
        lexema = arg.get("lexema", "")
        classe = arg.get("classe", "")
        tipo = arg.get("tipo", "")
        
        if classe == "lit":
            # Remove aspas se existirem
            if lexema.startswith('"') and lexema.endswith('"'):
                lexema = lexema[1:-1]
            self.arquivo_objeto.append(f'printf("{lexema}");')
        elif classe == "num":
            if tipo == "real":
                self.arquivo_objeto.append(f'printf("%lf",{lexema});')
            else:
                self.arquivo_objeto.append(f'printf("%d",{lexema});')
        elif classe == "id":
            if tipo == "lit":
                self.arquivo_objeto.append(f'printf("%s",{lexema});')
            elif tipo == "int":
                self.arquivo_objeto.append(f'printf("%d",{lexema});')
            elif tipo == "real":
                self.arquivo_objeto.append(f'printf("%lf",{lexema});')
    
    def _processar_atribuicao(self, id_token, ld_token):
        """Processa comando de atribuição"""
        if not self._verificar_declaracao(id_token):
            return
            
        id_lexema = id_token.get("lexema", "")
        id_tipo = self.tipos_declarados.get(id_lexema)
        ld_tipo = ld_token.get("tipo")
        ld_lexema = ld_token.get("lexema", "")
        
        # Verificação de tipos
        if id_tipo != ld_tipo:
            linha = id_token.get("l", 0)
            coluna = id_token.get("c", 0)
            self.erros_semanticos.append(
                f"Erro: Tipos diferentes para atribuição na linha {linha}, coluna {coluna}"
            )
            return
        
        self.arquivo_objeto.append(f"{id_lexema}={ld_lexema};")
    
    def _processar_operacao_aritmetica(self, oprd1, opm, oprd2):
        """Processa operação aritmética"""
        tipo1 = oprd1.get("tipo")
        tipo2 = oprd2.get("tipo")
        
        # Verificação de tipos
        if tipo1 != tipo2 or tipo1 == "lit" or tipo2 == "lit":
            self.erros_semanticos.append(
                "Erro: Operandos com tipos incompatíveis"
            )
            return {"simbolo": "LD", "lexema": "", "tipo": "erro"}
        
        # Gera variável temporária
        var_temp = self.gerar_variavel_temporaria(tipo1)
        lexema1 = oprd1.get("lexema", "")
        lexema2 = oprd2.get("lexema", "")
        operador = opm.get("lexema", "")
        
        self.arquivo_objeto.append(f"{var_temp}={lexema1}{operador}{lexema2};")
        
        return {"simbolo": "LD", "lexema": var_temp, "tipo": tipo1}
    
    def _processar_inicio_se(self, exp_r):
        """Processa início de comando se"""
        lexema = exp_r.get("lexema", "")
        self.arquivo_objeto.append(f"if({lexema})")
        self.arquivo_objeto.append("{")
    
    def _processar_fim_se(self):
        """Processa fim de comando se"""
        self.arquivo_objeto.append("}")
    
    def _processar_expressao_relacional(self, oprd1, opr, oprd2):
        """Processa expressão relacional"""
        tipo1 = oprd1.get("tipo")
        tipo2 = oprd2.get("tipo")
        
        # Verificação de tipos
        if tipo1 != tipo2:
            self.erros_semanticos.append(
                "Erro: Operandos com tipos incompatíveis"
            )
            return {"simbolo": "EXP_R", "lexema": "", "tipo": "erro"}
        
        # Gera variável temporária booleana
        var_temp = self.gerar_variavel_temporaria("int")  # bool como int em C
        lexema1 = oprd1.get("lexema", "")
        lexema2 = oprd2.get("lexema", "")
        operador = opr.get("lexema", "")
        
        self.arquivo_objeto.append(f"{var_temp}={lexema1}{operador}{lexema2};")
        
        return {"simbolo": "EXP_R", "lexema": var_temp, "tipo": "int"}
    
    def _finalizar_programa(self):
        """Finaliza o programa C"""
        self.arquivo_objeto.append("}")
    
    def _preparar_codigo_final(self):
        """Prepara o código final inserindo variáveis temporárias apenas uma vez"""
        if not self.variaveis_temporarias_usadas:
            return
            
        # Encontra o índice onde estão as 3 linhas brancas (após varfim;)
        indice_insercao = -1
        linhas_brancas_consecutivas = 0
        
        for i, linha in enumerate(self.arquivo_objeto):
            if linha.strip() == "":
                linhas_brancas_consecutivas += 1
                if linhas_brancas_consecutivas == 3:
                    indice_insercao = i + 1
                    break
            else:
                linhas_brancas_consecutivas = 0
        
        if indice_insercao != -1:
            # Prepara as linhas das variáveis temporárias
            linhas_temp = ["/*----Variaveis temporarias----*/"]
            for var_nome, tipo in sorted(self.variaveis_temporarias_usadas):
                tipo_c = self.tipo_para_c.get(tipo, tipo)
                linhas_temp.append(f"{tipo_c} {var_nome};")
            linhas_temp.append("/*------------------------------*/")
            
            # Insere as variáveis temporárias no local correto
            for i, linha in enumerate(linhas_temp):
                self.arquivo_objeto.insert(indice_insercao + i, linha)
    
    def gerar_arquivo_objeto(self, nome_arquivo="PROGRAMA.C"):
        """Gera o arquivo objeto final"""
        if self.erros_semanticos:
            print("\n❌ Erros semânticos encontrados. Arquivo objeto não será gerado.")
            for erro in self.erros_semanticos:
                print(f"   {erro}")
            return False
        
        # Prepara o código final uma única vez
        self._preparar_codigo_final()
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                for linha in self.arquivo_objeto:
                    f.write(linha + '\n')
            print(f"\n✅ Arquivo objeto '{nome_arquivo}' gerado com sucesso!")
            return True
        except Exception as e:
            print(f"\n❌ Erro ao gerar arquivo objeto: {e}")
            return False
    
    def imprimir_codigo_gerado(self):
        """Imprime o código gerado na tela"""
        print("\n✳️  Código Objeto Gerado:\n")
        for linha in self.arquivo_objeto:
            print(linha)

class ParserSemantico:
    def __init__(
            self,
            tokens, 
            tabela_acoes,
            tabela_desvios,
            producoes,
            token_para_msg,
            simbolos_sincronismo,
            metodo_recuperacao_erro="panico", 
            max_tentativas=10
        ):

        # Configuração do parser sintático
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
        
        
        
        # Configuração do analisador semântico
        # Extrai tabela de símbolos dos tokens
        tabela_simbolos = {}
        for token in tokens:
            if token.get("classe") == "id":
                tabela_simbolos[token["lexema"]] = token
        
        self.analisador_semantico = AnalisadorSemantico(tabela_simbolos)
        self.analisador_semantico._iniciar_programa()

    def analisar(self):
        print("✳️  Análise Sintática Shift-Reduce com Análise Semântica:\n")
        print(f"📊  Método de recuperação de erro: {self.metodo_recuperacao_erro.upper()}\n")
        
        while True:
            estado = self.pilha[-1]
            token_atual = self.tokens[self.ip]
            simbolo = token_atual["classe"]
            
            acao = self.tabela_acoes.get((estado, simbolo), "erro")
            
            if acao.startswith("s"):
                prox_estado = int(acao[1:])
                self.pilha.append(prox_estado)
                
                # EMPILHA token na pilha semântica
                self.analisador_semantico.empilhar_token(token_atual)
                
                self.ip += 1
                
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
                print(f"◁ {simbolo_do_lado_esquerdo} → {' '.join(sequencia_lado_direito)}")
                
                # EXECUTA regras semânticas
                self.analisador_semantico.executar_regra_semantica(
                    num_regra_de_producao, 
                    tamanho_sequencia_lado_direito
                )
                
            elif acao == "acc":
                if len(self.erros) == 0 and len(self.analisador_semantico.erros_semanticos) == 0:
                    print("✅ Sentença reconhecida com sucesso!")
                    
                    # Gera arquivo objeto
                    self.analisador_semantico.imprimir_codigo_gerado()
                    sucesso = self.analisador_semantico.gerar_arquivo_objeto()
                    return sucesso
                else:
                    if self.erros:
                        self.imprimir_relatorio_erros()
                    if self.analisador_semantico.erros_semanticos:
                        print("\n❌ Erros semânticos encontrados:")
                        for erro in self.analisador_semantico.erros_semanticos:
                            print(f"   {erro}")
                    return False
                
            else:
                # Tratamento de erros (mesmo código do parser original)
                if simbolo == "$":
                    msg = f"Fim de arquivo inesperado na linha {self.tokens[-1]['l']}, coluna {self.tokens[-1]['c']}."
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
        return False

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

        if excedeu_as_tentativas_de_recuperacao:
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

class Parser:
    def __init__(
            self,
            tokens, 
            tabela_acoes,
            tabela_desvios,
            producoes,
            token_para_msg,
            simbolos_sincronismo,
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
                # TODO: EMPILHA token com seus atributos
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
                print(f"◁ {simbolo_do_lado_esquerdo} → {' '.join(sequencia_lado_direito)}")
                # TODO: Chama uma função que executará as regras semânticas à regra sintática que foi reduzida
                # Gerar um PROGRAMA.C se não tiver erro (código objeto)
            elif acao == "acc":
                if(len(self.erros) == 0): 
                    print("✅ Sentença reconhecida com sucesso!")
                    return True
                else:
                    self.imprimir_relatorio_erros()
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
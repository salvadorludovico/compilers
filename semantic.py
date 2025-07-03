class Semantic:
  def __init__(
      self,
      tabela_de_simbolos,
    ):
    self.tabela_de_simbolos = tabela_de_simbolos
    self.pilha_semantica = []
    self.codigo_objeto = []
    self.erros_semanticos = []
    self.contador_temp = 0 # para variáveis temporárias t0, t1, t2, ...

    # Listas separadas para o código
    self.codigo_declaracoes_vars = []
    self.codigo_comandos = []

  def gerar_variavel_temporaria(self, tipo):
    # Gera um novo nome de variável temporária (ex: T0)
    nome_temp = f"T{self.contador_temp}"
    self.contador_temp += 1
    # Adiciona a declaração da temporária na tabela de símbolos
    self.tabela_simbolos[nome_temp] = {'tipo': tipo, 'declarada': True}
    # Retorna o nome e o tipo para ser usado nas ações
    return {'lexema': nome_temp, 'tipo': tipo}

  def registrar_erro(self, mensagem, linha, coluna):
        erro = f"Erro Semântico: {mensagem} na linha {linha}, coluna {coluna}."
        self.erros_semanticos.append(erro)
        print(f"❌ {erro}")

  # Em analisador_semantico.py
  def gerar_arquivo_saida(self, nome_arquivo="PROGRAMA.C"):
      # Cabeçalho padrão do C
      cabecalho = [
          "#include<stdio.h>\n",
          "typedef char literal[256];\n",
          "void main(void) {\n"
      ]

      # Declaração de variáveis temporárias
      declaracoes_temp = []
      for i in range(self.contador_temp):
          # Assumindo que todas temporárias são int, ajuste se necessário
          declaracoes_temp.append(f"    int T{i};\n")

      # Monta o arquivo final
      with open(nome_arquivo, "w") as f:
          f.writelines(cabecalho)
          f.writelines(declaracoes_temp) # Declara as T0, T1, etc.

          # Escreve o código gerado pelas ações semânticas
          # CUIDADO: o código de declaração de variáveis normais e o código de comandos
          # podem ter sido misturados. Você precisa de uma forma de separá-los durante a geração.
          # Uma boa abordagem é ter listas separadas: self.codigo_declaracoes e self.codigo_comandos
          f.writelines(self.codigo_objeto)

          f.write("}\n")
      print(f"✅ Arquivo '{nome_arquivo}' gerado com sucesso.")

  def acao_semantica(self, numero_regra, atributos):
        metodos_acoes = {
          5: self._acao_5,
          6: self._acao_6,
          # ...
          9: self._acao_9,
          10: self._acao_10,
          11: self._acao_11,
          # ...
        }
        
        funcao_acao = metodos_acoes.get(numero_regra)
        if funcao_acao:
            funcao_acao()
        # Se não houver ação para a regra, nada acontece, como diz o PDF ("-")

  def _acao_9(self):
    # TIPO.tipo <- inteiro.tipo
    self.pilha_semantica.append({'tipo': 'int'})
    # Imprimir(TIPO.tipo)
    self.codigo_objeto.append("int ") # Deixa um espaço para o nome da variável
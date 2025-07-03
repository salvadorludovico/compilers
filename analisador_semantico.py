class AnalisadorSemantico:
    def __init__(self, tabela_de_simbolos):
        self.tabela = tabela_de_simbolos
        self.codigo = []
        self.declaracoes = []
        self.variaveis_temp = []
        self.temp_count = 0
        self.erros = []
        self.obj_gerado = False
        self.gerar_cabecalho()

    def gerar_cabecalho(self):
        self.codigo.append("#include <stdio.h>")
        self.codigo.append("typedef char literal[256];")
        self.codigo.append("void main(void) {")
        self.codigo.append("   /*----Variaveis temporarias----*/")

    def gerar_temp(self):
        nome = f"T{self.temp_count}"
        self.temp_count += 1
        self.variaveis_temp.append(nome)
        return nome

    def registrar_erro(self, msg, linha, coluna):
        erro = f"Erro semântico: {msg} (linha {linha}, coluna {coluna})"
        self.erros.append(erro)
        print(f"❌ {erro}")

    def salvar_arquivo(self, nome="PROGRAMA.C"):
        if self.erros:
            print("⚠️  Código não gerado devido a erro(s) semântico(s).")
            return
        self.finalizar_codigo()
        with open(nome, "w", encoding="utf-8") as f:
            for linha in self.codigo:
                f.write(linha + "\n")
        print(f"✅ Arquivo {nome} gerado com sucesso!")
        self.obj_gerado = True

    def finalizar_codigo(self):
        for t in self.variaveis_temp:
            self.codigo.append(f"   int {t};")
        self.codigo.append("   /*------------------------------*/")
        self.codigo.extend(self.declaracoes)
        self.codigo.append("}")

    def executar(self, regra, atributos):
        match regra:

            case 5:  # LV → varfim ;
                self.codigo.append("")
                self.codigo.append("")
                self.codigo.append("")

            case 6 | 7 | 8:  # D → TIPO L ; / L → id , L / L → id
                tipo = atributos.get("TIPO.tipo")
                ids = atributos.get("L.ids", [])
                for token in ids:
                    simbolo = self.tabela.buscar(token)
                    if simbolo:
                        simbolo["tipo"] = tipo
                        if tipo == "literal":
                            self.declaracoes.append(f"   literal {token['lexema']};")
                        elif tipo in ["int", "inteiro"]:
                            self.declaracoes.append(f"   int {token['lexema']};")
                        elif tipo == "real":
                            self.declaracoes.append(f"   double {token['lexema']};")

            case 9:
                atributos["TIPO.tipo"] = "int"
            case 10:
                atributos["TIPO.tipo"] = "real"
            case 11:
                atributos["TIPO.tipo"] = "literal"

            case 13:  # leia id;
                id_token = atributos["id"]
                simbolo = self.tabela.buscar(id_token)
                if not simbolo or not simbolo.get("tipo"):
                    self.registrar_erro("Variável não declarada", id_token["l"], id_token["c"])
                    return
                tipo = simbolo["tipo"]
                lexema = id_token["lexema"]
                if tipo == "literal":
                    self.codigo.append(f'   scanf("%s", {lexema});')
                elif tipo == "int":
                    self.codigo.append(f'   scanf("%d", &{lexema});')
                elif tipo == "real":
                    self.codigo.append(f'   scanf("%lf", &{lexema});')

            case 14:
                atributos["ARG.lexema"] = atributos["lit"]["lexema"]

            case 15:
                atributos["ARG.lexema"] = atributos["num"]["lexema"]

            case 16:  # ARG → id
                id_token = atributos["id"]
                simbolo = self.tabela.buscar(id_token)
                if not simbolo or not simbolo.get("tipo"):
                    self.registrar_erro("Variável não declarada", id_token["l"], id_token["c"])
                    return
                atributos["ARG.lexema"] = id_token["lexema"]

            case 17:
                atributos["ARG.lexema"] = atributos["id"]["lexema"]

            case 14 | 15 | 16 | 17:  # escreva ARG;
                if "ARG.lexema" in atributos:
                    self.codigo.append(f'   printf("{atributos["ARG.lexema"]}");')

            case 19:  # CMD → id rcb LD ;
                id_token = atributos["id"]
                simbolo = self.tabela.buscar(id_token)
                if not simbolo or not simbolo.get("tipo"):
                    self.registrar_erro("Variável não declarada", id_token["l"], id_token["c"])
                    return
                tipo_id = simbolo["tipo"]
                tipo_ld = atributos.get("LD.tipo")
                lex_ld = atributos.get("LD.lexema")

                if tipo_id != tipo_ld:
                    self.registrar_erro("Tipos diferentes para atribuição", id_token["l"], id_token["c"])
                    return

                self.codigo.append(f"   {id_token['lexema']} = {lex_ld};")

            case 20:  # LD → OPRD opm OPRD
                op1 = atributos["op1"]
                op2 = atributos["op2"]
                tipo1 = op1.get("tipo")
                tipo2 = op2.get("tipo")
                lex1 = op1.get("lexema")
                lex2 = op2.get("lexema")
                op = atributos["opm"]

                if tipo1 != tipo2 or tipo1 == "literal":
                    self.registrar_erro("Operandos com tipos incompatíveis", op["l"], op["c"])
                    return

                temp = self.gerar_temp()
                self.codigo.append(f"   {temp} = {lex1} {op['lexema']} {lex2};")
                atributos["LD.lexema"] = temp
                atributos["LD.tipo"] = tipo1

            case 21:  # LD → OPRD
                atributos["LD.lexema"] = atributos["OPRD.lexema"]
                atributos["LD.tipo"] = atributos["OPRD.tipo"]

            case 22:  # OPRD → id
                id_token = atributos["id"]
                simbolo = self.tabela.buscar(id_token)
                if not simbolo or not simbolo.get("tipo"):
                    self.registrar_erro("Variável não declarada", id_token["l"], id_token["c"])
                    return
                atributos["OPRD.lexema"] = id_token["lexema"]
                atributos["OPRD.tipo"] = simbolo["tipo"]

            case 23:  # OPRD → num
                atributos["OPRD.lexema"] = atributos["num"]["lexema"]
                atributos["OPRD.tipo"] = atributos["num"]["tipo"]

            case 25:  # CAB → se ( EXP_R ) então
                lex = atributos["EXP_R.lexema"]
                self.codigo.append(f"   if ({lex}) {{")

            case 24:  # COND → CAB CP
                self.codigo.append("   }")

            case 27:  # EXP_R → OPRD opr OPRD
                op1 = atributos["op1"]
                op2 = atributos["op2"]
                tipo1 = op1.get("tipo")
                tipo2 = op2.get("tipo")
                lex1 = op1.get("lexema")
                lex2 = op2.get("lexema")
                op = atributos["opr"]

                if tipo1 != tipo2:
                    self.registrar_erro("Operandos com tipos incompatíveis", op["l"], op["c"])
                    return

                temp = self.gerar_temp()
                self.codigo.append(f"   {temp} = {lex1} {op['lexema']} {lex2};")
                atributos["EXP_R.lexema"] = temp
                atributos["EXP_R.tipo"] = "bool"

            case 33:  # facaAte ( EXP_R ) CP_R
                lex = atributos["EXP_R.lexema"]
                self.codigo.append(f"   do {{")
                atributos["FIM_FACA"] = f"   }} while (!({lex}));"

            case 37:  # fimfaca
                if "FIM_FACA" in atributos:
                    self.codigo.append(atributos["FIM_FACA"])

            case _:
                pass

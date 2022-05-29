# Módulo que precisa implementar as classes: usuário, livro e acervo
from abc import ABC, abstractmethod
from tkinter import E

data_atual = ""

ARQ_EMPRESTIMO = "database/emprestimos.dat"
ARQ_USUARIO = "database/usuarios.dat"
ARQ_ACERVO = "database/acervo.dat"

def armazena_data_atual(primeira_linha):
    dados = primeira_linha.split("-->")
    
    global data_atual
    data_atual = dados[1].replace("\n", "")

class Utils():
    @staticmethod
    def preparar_dados(dados):
        return dados.replace('\n', '')

    @staticmethod
    def ler_arquivo(nome_arquivo):
        dados = ""
        with open(nome_arquivo, 'r', encoding="UTF-8") as arq:
            dados = arq.readlines()
        return dados

    @staticmethod
    def escrever_arquivo(nome_arquivo, dados):
        with open(nome_arquivo, 'a', encoding="UTF-8") as arq: #leitura e escrita
            arq.write(f"{dados}\n")

class PUCoin():
    def __init__(self, valor):
        self.valor = valor

    def __add__(self,obj):
        if isinstance(obj, PUCoin):
            novo = self.valor + obj.valor
        else:
            novo = self.valor + obj
        return novo

    def __mult__(self, obj):
        if isinstance(obj,int):
            novo = self.valor * obj
        else:
            novo = self.valor * obj.valor
        return novo  
        
    def __str__(self):
        return str(self.valor)

class Usuario(ABC):
    #"A classe usuario cadastra usuarios e retorna os dados do usuario"
    def __init__(self, nome, cpf, matricula):
        self.nome = nome
        self.cpf = cpf
        self.matricula = matricula
        self.multa = PUCoin(0.0)

    @property
    def multa(self): 
        return self._multa

    @multa.setter
    def multa(self, valor):
        self._multa = PUCoin(valor)

    @abstractmethod
    def cadastra(self):
        pass

    @abstractmethod
    def calcula_multa(self, dias_atraso):
        pass

    def procura_usuario(identificador):
        dados = ""
        with open(ARQ_USUARIO, 'r', encoding="UTF-8") as arq:
            for linha in arq:
                if identificador in linha:
                    dados = linha
        
        return Utils.preparar_dados(dados)
    
    def valida_dados(self):
        if(len(self.matricula) != 8 or self.matricula.isnumeric() == False):
            raise ErroMatriculaInvalida(self.matricula)
        elif(len(self.cpf) != 11 or self.cpf.isnumeric() == False):
            raise ErroCpfInvalido(self.cpf)
        elif(Usuario.procura_usuario(self.cpf) != ""):
            raise ErroCpfJaCadastrado(self.cpf)

class Aluno(Usuario): 
    def __init__(self, nome, cpf, matricula, curso):
        self.curso = curso
        Usuario.__init__(self, nome, cpf, matricula)

    def cadastra(self):
        Usuario.valida_dados(self)
        Utils.escrever_arquivo(ARQ_USUARIO, f"aluno__{self.nome}__{self.cpf}__{self.matricula}__{self.curso}__{self.multa}")

        return f"Nome: {self.nome}\nCurso: {self.curso}"
          

    def calcula_multa(self, dias_atraso):
        if(dias_atraso > 20):
            self.multa = PUCoin(self._multa + (dias_atraso - 20) * 0.25)

class Funcionario(Usuario):
    def __init__(self, nome, cpf, matricula, departamento):
        self.departamento = departamento
        Usuario.__init__(self, nome, cpf, matricula)

    def cadastra(self):
        Usuario.valida_dados(self)
        Utils.escrever_arquivo(ARQ_USUARIO, f"funcionario__{self.nome}__{self.cpf}__{self.matricula}__{self.departamento}__{self._multa}")
        return f"Nome: {self.nome}\nDepartamento: {self.departamento}"

    def calcula_multa(self, dias_atraso):
        if(dias_atraso > 10):
            self.multa = PUCoin(self._multa + (dias_atraso - 10) * 0.5)

class Livro():
    devolucoes_realizadas = 0
    emprestimos_realizados = 0

    def __init__(self, titulo, autor, ano):
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.exemplares = 0

    @property
    def codigo(self):
        return self._codigo
    
    @codigo.setter
    def codigo(self, valor):
        self._codigo = valor

    @staticmethod
    def emprestimo(cod_livro, cpf, data):
        # pegar dados do livro pelo codigo
        dados_livro = Acervo.pesquisar_livro(cod_livro)
        dados_usuario = Usuario.procura_usuario(cpf)

        if(dados_livro == ""):
            raise ErroLivroNaoCadastrado(cod_livro)
        elif(dados_usuario == ""):
            raise ErroUsuarioNaoCadastrado(cpf)
        else:
            exemplares = dados_livro.split("__")[-1]
            multa = dados_usuario.split("__")[-1]
            
            if(int(exemplares) <= 1):
                raise ErroLivroIndisponivel(cod_livro) 
            elif(multa == 0.0):
                raise ErroUsuarioPossuiMulta(cpf) 
            else:
                Acervo.remover_livro(cod_livro)
                dados_livro = dados_livro.split("__")
                dados_usuario = dados_usuario.split("__")

                titulo_livro = dados_livro[1]
                nome_usuario = dados_usuario[1]

                Utils.escrever_arquivo(ARQ_EMPRESTIMO, f"{cod_livro}__{titulo_livro}__{nome_usuario}__{cpf}__{data}")

                Livro.emprestimos_realizados += 1
                return f"Livro: {titulo_livro}\nUsuario: {nome_usuario}"
                
    
    @staticmethod
    def devolucao(cod_livro, cpf, data_devolucao):
        if(Acervo.pesquisar_livro(cod_livro) != ""): #retorna dados 
            data_emprestimo = Livro.busca_data_emprestimo(cod_livro, cpf)
            if(data_emprestimo == ""):
                raise ErroSemRegistroDeEmprestimo(cod_livro)
            else:
                intervalo_dias = Livro.calc_diferenca_dias(data_emprestimo, data_devolucao)

                dados_usuario = Usuario.procura_usuario(cpf)   

                if(dados_usuario == ""):   
                    raise ErroUsuarioNaoCadastrado(cpf)    
                else:
                    dados_usuario = dados_usuario.split("__")
                    tipo_usuario = dados_usuario[0]

                    usuario = None

                    multa_antiga = dados_usuario[-1]
                    multa_atualizada = multa_antiga

                    if tipo_usuario == "funcionario":
                        usuario = Funcionario(*dados_usuario[1:5])
                    elif tipo_usuario == "aluno":
                        usuario = Aluno(*dados_usuario[1:5])

                    usuario.multa = PUCoin(float(dados_usuario[-1]))

                    usuario.calcula_multa(intervalo_dias)
                    multa_atualizada = usuario.multa

                    if(multa_antiga != multa_atualizada):
                        usuarios = Utils.ler_arquivo(ARQ_USUARIO)

                        with open(ARQ_USUARIO, 'w', encoding="UTF-8") as arq:
                            for linha in usuarios:
                                if(cpf in linha):
                                    linha = linha.split("__")
                                    linha[-1] = str(multa_atualizada) + "\n"
                                    linha = "__".join(linha)

                                arq.write(linha)

                    dados_emprestimo = []
                    ja_tirou = 0
                    titulo_livro = ""
                    nome_usuario = dados_usuario[1]
                    
                    with open(ARQ_EMPRESTIMO, "r", encoding="UTF-8") as arq:
                        linhas = arq.readlines()
                        
                        for linha in linhas:
                            if cod_livro in linha and cpf in linha and ja_tirou == 0:
                                titulo_livro = linha.split("__")[1]
                                ja_tirou = 1
                                continue
                            dados_emprestimo.append(linha)
                              
                    with open(ARQ_EMPRESTIMO, 'w', encoding="UTF-8") as arq:
                            for linha in dados_emprestimo:
                                arq.write(linha)


                    # Devolve um exemplar
                    Acervo.adicionar_exemplar(cod_livro)
                    Livro.devolucoes_realizadas += 1
                    return f"Livro: {titulo_livro}\nUsuario: {nome_usuario}"
                    
    
    @staticmethod
    def calc_diferenca_dias(data_emprestimo, data_devolucao):
        dia_devolucao, mes_devolucao, ano_devolucao = (int(x) for x in data_devolucao.split("-"))
        dia_emprestimo, mes_emprestimo, ano_emprestimo = (int(x) for x in data_emprestimo.split("-"))

        dias = dia_devolucao - dia_emprestimo
        meses_dias = (mes_devolucao - mes_emprestimo) * 30
        anos_dias = (ano_devolucao - ano_emprestimo) * 360

        dias_de_diferenca = dias + meses_dias + anos_dias

        return dias_de_diferenca

    @staticmethod
    def busca_data_emprestimo(cod_livro, cpf):
        arq_emp = Utils.ler_arquivo(ARQ_EMPRESTIMO)
        arq_emp.reverse()
        data = ""

        for linha in arq_emp:
            if(cod_livro in linha and cpf in linha):
                linha = linha.replace("\n", "")
                data = linha[-10:]

        return data

class Acervo():  
    @staticmethod
    def adicionar_livro(titulo, autor, ano, exemplares):
        if(int(ano) > int(data_atual[-4:])):
            raise ErroLivroAnoInvalido(ano)
        else:
            livro_existe =  Acervo.pesquisar_livro(titulo) != ""

            if(livro_existe): 
                codigo, exemplares = Acervo.adicionar_exemplar(titulo)
                return f"Livro: {codigo} - {titulo}\nNovo numero de exemplares: {exemplares}"
            else:
                codigo = Acervo.gerar_codigo()
                Utils.escrever_arquivo(ARQ_ACERVO, f"{codigo}__{titulo}__{autor}__{ano}__{exemplares}")
                return f"Livro: {codigo} - {titulo}\nExemplares: {exemplares}"

    @staticmethod
    def adicionar_exemplar(identificador):
        acervo = Utils.ler_arquivo(ARQ_ACERVO)
        dados = []
        with open(ARQ_ACERVO, 'w', encoding="UTF-8") as arq:
            for linha in acervo:
                if identificador in linha:
                    linha = linha.split("__")
                    linha[-1] = str((int(linha[-1]) + 1)) + "\n"

                    dados = [linha[0], linha[-1]]

                    linha = "__".join(linha)

                arq.write(linha)
        return dados

    @staticmethod      
    def remover_livro(cod_livro):
        acervo = Utils.ler_arquivo(ARQ_ACERVO)

        with open(ARQ_ACERVO, 'w', encoding="UTF-8") as arq:
            for linha in acervo:
                if cod_livro in linha:
                    linha = linha.split("__")
                    linha[-1] = str((int(linha[-1]) - 1)) + "\n"
                    linha = "__".join(linha)

                arq.write(linha)

    @staticmethod
    def pesquisar_livro(identificador):
        dados = ""

        with open(ARQ_ACERVO, 'r', encoding="UTF-8") as arq:
            for line in arq:
                if identificador in line:
                    dados = line

        return dados

    @staticmethod
    def gerar_codigo():
        linhas = Utils.ler_arquivo(ARQ_ACERVO)

        ultimo_codigo = linhas[-1][0:5]
        zeros = (5-len(str(int(ultimo_codigo))))*'0'
        numero = int(ultimo_codigo) + 1
        novo_codigo = f"{zeros}{numero}"

        return novo_codigo

class ErroGenerico(Exception):
    def __init__(self, value):
        self.value = value

    def get_message(self):
        value = self.value.replace('\n', '')
        return f"{type(self).__name__} ({value})"

    def salva(self, comando):
        
        with open("./log.err", "a", encoding="UTF-8") as arq:
            arq.write(f"{(40 * '-')}\nComando => {comando}\n{self.get_message()}\n{(40 * '-')}\n")

class ErroCpfJaCadastrado(ErroGenerico):
    pass

class ErroUsuarioNaoCadastrado(ErroGenerico):
    pass

class ErroLivroNaoCadastrado(ErroGenerico):
    pass
    
class ErroSemRegistroDeEmprestimo(ErroGenerico):
    pass

class ErroLivroAnoInvalido(ErroGenerico):
    pass

class ErroMatriculaInvalida(ErroGenerico):
    pass

class ErroCpfInvalido(ErroGenerico):
    pass

class ErroLivroIndisponivel(ErroGenerico):
    pass

class ErroUsuarioPossuiMulta(ErroGenerico):
    pass



class ErroInformacoes(ErroGenerico):
    pass

class ErroDevolucao(ErroGenerico):
    pass
  
class ErroEmprestimo(ErroGenerico):
    pass


""" def controle(self, info):
    # Método que faz o controle de quantos exemplares de livros foram emprestados e quantos foram devolvidos
    if info == "devolução":
        conta_devolucao = conta_devolucao + 1
        return conta_devolucao
    elif info == "emprestimo":
        conta_emprestimo = conta_emprestimo + 1
        return conta_emprestimo  """

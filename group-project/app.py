from biblioteca import bibSys
import sys
import traceback
 
#Função que recebe cada linha como uma lista e encaminha para a operação correspondente:
def operacoes(comando):
    comando = bibSys.Utils.preparar_dados(comando)

    comando_lista = comando.split("-->") 
    acao = ""
    sem_erro = True
    mensagem = ""
    try:
        if comando_lista[0] == "cadastra":
            if comando_lista[1] == "livro":
                acao = "Cadastro livro"
                mensagem = bibSys.Acervo.adicionar_livro(*comando_lista[2:])
            else:
                if("aluno" in comando_lista[1]):
                    acao = "Cadastro aluno"
                    aluno = bibSys.Aluno(*comando_lista[2:])
                    mensagem = aluno.cadastra()
                else:
                    acao = "Cadastro funcionario"
                    funcionario = bibSys.Funcionario(*comando_lista[2:])
                    mensagem = funcionario.cadastra()

        else:
            if comando_lista[0] == "devolve":
                acao = "Devolucao"
                mensagem = bibSys.Livro.devolucao(*comando_lista[1:], bibSys.data_atual)
            else:
                acao = "Emprestimo"
                mensagem = bibSys.Livro.emprestimo(*comando_lista[1:], bibSys.data_atual)

    except bibSys.ErroGenerico as e:
        sem_erro = False
        mensagem = e.get_message()
        e.salva(comando)

    print(f"{(40 * '-')}\nComando => {comando}\n{(40 * '-')}\n{acao} {('OK' if sem_erro else 'ERRO')}\n{mensagem}\n")

    mensagem = ""
    sem_erro = True


def ler_arquivos(*args):
    args = args[0][1:]
    
    for arquivo in args:
        with open(arquivo, 'r+', encoding="UTF-8") as arq:
            bibSys.armazena_data_atual(arq.readline())

            for linha in arq.readlines():
                operacoes(linha)

    print(f"\nEmpréstimos bem-sucedidos: {bibSys.Livro.emprestimos_realizados}\nDevoluções bem-sucedidas: {bibSys.Livro.devolucoes_realizadas}")
            

#mostrar o total de operações de emprestimos e de devoluções realizadas (obtidas da classe livros)
""" def mensagem():
    total_emprestimos = int(bibSys.Livro().controle("emprestimo")) - 1 
    total_devolucao = int(bibSys.Livro().controle("devolução")) - 1 
    print("O total de empréstimos foi de " + total_emprestimos + " e o total de devoluções foi de: " + total_devolucao) """

ler_arquivos(sys.argv)

""" mensagem = mensagem()
print(mensagem)  """
import sys

import grpc

from biblioteca.gRPC import biblioteca_pb2_grpc, biblioteca_pb2

stub: biblioteca_pb2_grpc.PortalBibliotecaStub = None

def run():
    porta = int(sys.argv[1])
    global stub
    stub = connect_stub(porta)

    while True:
        print("""
Opções:
0 - Sair
1 - Realizar empréstimo
2 - Realizar devolução
              """)
        match int(input("Digite um número: ")):
            case 0:
                break
            case 1:
                emprestimo()
            case 2:
                devolucao()
            
def emprestimo():
    print("Realizando empréstimo")
    lista: list[biblioteca_pb2.UsuarioLivro] = []
    while input("Registrar novo empréstimo? [s/n] ") == "s":
        cpf = biblioteca_pb2.Identificador(id=input("cpf: "))
        isbn = biblioteca_pb2.Identificador(id=input("isbn: "))
        lista.append(biblioteca_pb2.UsuarioLivro(usuario=cpf, livro=isbn))

    status = stub.RealizaEmprestimo(iter(lista))
    if status.status == 0:
        print("Empréstimos realizados com sucesso!")
    else:
        print(status.msg)


def connect_stub(porta: int) -> biblioteca_pb2_grpc.PortalBibliotecaStub:
    channel = grpc.insecure_channel(f"localhost:{porta}")
    return biblioteca_pb2_grpc.PortalBibliotecaStub(channel)
import sys

import grpc

from biblioteca.gRPC import cadastro_pb2, cadastro_pb2_grpc

stub: cadastro_pb2_grpc.PortalCadastroStub = None

def run():
    porta = int(sys.argv[1])
    global stub
    stub = connect_stub(porta)

    while True:
        print("""
Opções:
0 - Sair
1 - Criar usuário     | 5 - Criar livro
2 - Deletar usuário   | 6 - Deletar livro
3 - Atualizar usuário | 7 - Atualizar livro
4 - Buscar usuário    | 8 - Buscar livro
              """)
        match int(input("Digite um número: ")):
            case 0:
                break
            case 1:
                criarUsuario()
            case 2:
                deletarUsuario()
            case 3:
                atualizarUsuario()
            case 4:
                buscarUsuario()
            case 5:
                criarLivro()
            case 6:
                deletarLivro()
            case 7:
                atualizarLivro()
            case 8:
                buscarLivro()

def criarUsuario():
        print("Criando usuário")
        usuario = cadastro_pb2.Usuario(cpf=input("cpf: "), nome=input("nome: "))
        status = stub.NovoUsuario(usuario)
        if (status.status == 0):
            print("Usuário criado com sucesso!")
        else:
            print(status.msg)

def deletarUsuario():
        print("Deletando usuário")
        status = stub.RemoveUsuario(cadastro_pb2.Identificador(id=input("cpf: ")))
        if (status.status == 0):
            print("Usuário deletado com sucesso!")
        else:
             print(status.msg)
        
def atualizarUsuario():
    print("Atualizando usuário")
    status = stub.EditaUsuario(cadastro_pb2.Usuario(cpf=input("cpf: "), nome=input("novo nome: ")))
    if (status.status == 0):
        print("Usuário atualizado com sucesso!")
    else:
        print(status.msg)

def buscarUsuario():
        print("Buscando usuário")
        usuario = stub.ObtemUsuario(cadastro_pb2.Identificador(id=input("cpf: ")))
        print("Usuário encontrado:")
        print(usuario)

def criarLivro():
        print("Criando livro")
        livro = cadastro_pb2.Livro(isbn=input("isbn: "), titulo=input("título: "), autor=input("autor: "), total=int(input("total: ")))
        status = stub.NovoLivro(livro)
        if (status.status == 0):
            print("Livro criado com sucesso!")
        else:
            print(status.msg)

def deletarLivro():
        print("Deletando livro")
        status = stub.RemoveLivro(cadastro_pb2.Identificador(id=input("isbn: ")))
        if (status.status == 0):
            print("Livro deletado com sucesso!")
        else:
             print(status.msg)
        
def atualizarLivro():
    print("Atualizando livro")
    status = stub.EditaLivro(cadastro_pb2.Livro(isbn=input("isbn: "), titulo=input("novo título: "), 
                                                autor=input("novo autor: "), total=int(input("novo total: "))))
    if (status.status == 0):
        print("Livro atualizado com sucesso!")
    else:
        print(status.msg)

def buscarLivro():
        print("Buscando livro")
        livro = stub.ObtemLivro(cadastro_pb2.Identificador(id=input("isbn: ")))
        print("Livro encontrado:")
        print(livro)

def connect_stub(porta: int) -> cadastro_pb2_grpc.PortalCadastroStub:
    channel = grpc.insecure_channel(f"localhost:{porta}")
    return cadastro_pb2_grpc.PortalCadastroStub(channel)

if __name__ == '__main__':
    run()
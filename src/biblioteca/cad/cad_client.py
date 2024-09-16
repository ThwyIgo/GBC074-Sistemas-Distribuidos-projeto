import sys

import grpc

from biblioteca.gRPC import cadastro_pb2, cadastro_pb2_grpc

stub: cadastro_pb2_grpc.PortalCadastroStub = None

def run():
    porta = int(sys.argv[1])
    global stub
    stub = connect_stub(porta)

    # Loop só para testes
    while True:
        print("""
Opções:
0 - Sair
1 - Criar usuário
2 - Deletar usuário
3 - Atualizar usuário
4 - Buscar usuário
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

def connect_stub(porta: int) -> cadastro_pb2_grpc.PortalCadastroStub:
    channel = grpc.insecure_channel(f"localhost:{porta}")
    return cadastro_pb2_grpc.PortalCadastroStub(channel)

if __name__ == '__main__':
    run()
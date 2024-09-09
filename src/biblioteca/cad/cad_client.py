import sys

import grpc

from biblioteca import lib
from biblioteca.gRPC import cadastro_pb2, cadastro_pb2_grpc

def run():
    porta = int(sys.argv[1])
    stub = connect_stub(porta)

    # Loop só para testes
    while True:
        print("criar")
        cpf = input("cpf: ")
        usuario = cadastro_pb2.Usuario(cpf=cpf, nome=input("nome: "))

        status = stub.NovoUsuario(usuario)
        print(status)
        print("ler")
        status = stub.ObtemUsuario(cadastro_pb2.Identificador(id=cpf))
        print(status)
        print("atualizar")
        status = stub.EditaUsuario(cadastro_pb2.Usuario(cpf=cpf, nome=input("novo nome: ")))
        print(status)
        print("ler")
        status = stub.ObtemUsuario(cadastro_pb2.Identificador(id=cpf))
        print(status)
        if input("remover? [s]") == "s":
            status = stub.RemoveUsuario(cadastro_pb2.Identificador(id=cpf))
            print(status)

def connect_stub(porta: int) -> cadastro_pb2_grpc.PortalCadastroStub:
    channel = grpc.insecure_channel(f"localhost:{porta}")
    return cadastro_pb2_grpc.PortalCadastroStub(channel)

if __name__ == '__main__':
    run()
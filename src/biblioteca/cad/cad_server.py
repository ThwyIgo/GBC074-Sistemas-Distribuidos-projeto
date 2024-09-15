from concurrent import futures
import sys

import grpc

from biblioteca.cad.UsuariosServicer import UsuariosServicer
from biblioteca.cad.LivrosServicer import LivrosServicer
from biblioteca.gRPC import cadastro_pb2_grpc
from biblioteca.cad.Usuario import Usuario
from biblioteca.cad.Livro import Livro
from biblioteca import lib

def run():
    if len(sys.argv) != 2:
        print("Forneça a porta como argumento da linha de comando")
        return
    
    porta = int(sys.argv[1])
    usuarios: set[Usuario] = set()
    livros: set[Livro] = set()

    serve(porta, usuarios, livros)

def serve(porta: int, usuarios: set[Usuario], livros: set[Livro]):
    mqtt = lib.connect_mqtt("cad_server", porta)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cadastro_pb2_grpc.add_PortalCadastroServicer_to_server(LivrosServicer(livros, mqtt, porta), server)
    cadastro_pb2_grpc.add_PortalCadastroServicer_to_server(UsuariosServicer(usuarios, mqtt, porta), server)
    server.add_insecure_port(f"localhost:{porta}")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    run()
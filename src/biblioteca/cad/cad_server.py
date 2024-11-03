from concurrent import futures
import sys

import grpc

from biblioteca.cad import PortalCadastroServicer
from biblioteca.gRPC import cadastro_pb2_grpc

def run():
    if len(sys.argv) != 4:
        print("""
Forneça as seguintes portas como argumentos da linha de comando nesta ordem:
gRPC
base de dados de usuários
base de dados de livros e empréstimos
""")
        return
    
    rpcPort = int(sys.argv[1])
    dbUsrPort = int(sys.argv[2])
    dbLivPort = int(sys.argv[3])

    serve(rpcPort, dbUsrPort, dbLivPort)

def serve(rpcPort: int, dbUsrPort: int, dbLivPort: int):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cadastro_pb2_grpc.add_PortalCadastroServicer_to_server(PortalCadastroServicer(dbUsrPort, dbLivPort), server)
    server.add_insecure_port(f'localhost:{rpcPort}')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    run()
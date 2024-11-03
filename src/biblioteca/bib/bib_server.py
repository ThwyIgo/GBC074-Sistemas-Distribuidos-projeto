from concurrent import futures
import sys

import grpc
from biblioteca.gRPC import biblioteca_pb2_grpc

from biblioteca.bib.PortalBibliotecaServicer import PortalBibliotecaServicer

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

def serve(rpcPort: int, dbUsrPort: int, dbLivPort: int) -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    biblioteca_pb2_grpc.add_PortalBibliotecaServicer_to_server(PortalBibliotecaServicer(dbUsrPort, dbLivPort), server)
    server.add_insecure_port(f'localhost:{rpcPort}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    run()
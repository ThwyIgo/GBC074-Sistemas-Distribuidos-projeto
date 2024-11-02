from concurrent import futures
import sys

import grpc
from biblioteca.gRPC import biblioteca_pb2_grpc

from biblioteca.bib.PortalBibliotecaServicer import PortalBibliotecaServicer

def run():
    if len(sys.argv) != 3:
        print("Forneça a porta rpc como 1º argumento e a porta da base de dados com o 2º.")
        return
    
    rpcPort = int(sys.argv[1])
    dbPort = int(sys.argv[2])

    serve(rpcPort, dbPort)

def serve(rpcPort: int, dbPort: int):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    biblioteca_pb2_grpc.add_PortalBibliotecaServicer_to_server(PortalBibliotecaServicer(dbPort), server)
    server.add_insecure_port(f'localhost:{rpcPort}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    run()
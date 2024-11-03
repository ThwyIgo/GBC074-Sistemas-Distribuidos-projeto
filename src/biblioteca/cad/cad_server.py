from concurrent import futures
import sys

import grpc

from biblioteca.cad import PortalCadastroServicer
from biblioteca.gRPC import cadastro_pb2_grpc

def run():
    if len(sys.argv) != 3:
        print("Forneça a porta rpc como 1º argumento e a porta da base de dados com o 2º.")
        return
    
    rpcPort = int(sys.argv[1])
    dbPort = int(sys.argv[2])

    serve(rpcPort, dbPort)

def serve(rpcPort: int, dbPort: int):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cadastro_pb2_grpc.add_PortalCadastroServicer_to_server(PortalCadastroServicer(dbPort), server)
    server.add_insecure_port(f'localhost:{rpcPort}')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    run()
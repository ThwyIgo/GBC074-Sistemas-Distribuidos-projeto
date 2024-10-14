from concurrent import futures
import sys

import grpc

from biblioteca.cad import PortalCadastroServicer
from biblioteca.gRPC import cadastro_pb2_grpc

def run():
    if len(sys.argv) < 2:
        print("Forneça a porta como 1º argumento da linha de comando e as portas dos outros cad-server.")
        return

    serve(sys.argv[1], sys.argv[2:])

def serve(selfPorta: str, otherPortas: list[str]):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cadastro_pb2_grpc.add_PortalCadastroServicer_to_server(PortalCadastroServicer(selfPorta, otherPortas), server)
    server.add_insecure_port('localhost:'+selfPorta)
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    run()
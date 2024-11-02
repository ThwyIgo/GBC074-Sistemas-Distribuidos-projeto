from concurrent import futures
import sys

import grpc

from biblioteca.cad import PortalCadastroServicer
from biblioteca.gRPC import cadastro_pb2_grpc

def run():
    if len(sys.argv) < 3:
        print("Forneça a porta rpc como 1º argumento, porta pysyncobj como 2º, e as portas dos outros cad-server.")
        return

    serve(sys.argv[1:3], sys.argv[3:])

def serve(selfPortas: list[str], otherPortas: list[str]):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cadastro_pb2_grpc.add_PortalCadastroServicer_to_server(PortalCadastroServicer(selfPortas[1], otherPortas), server)
    server.add_insecure_port('localhost:'+selfPortas[0])
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    run()
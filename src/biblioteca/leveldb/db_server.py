from collections.abc import Iterable
from concurrent import futures
import sys

import grpc

from biblioteca.gRPC import database_pb2_grpc
from biblioteca.leveldb.DatabaseServicer import DatabaseServicer

def run():
    if len(sys.argv) != 3:
        print("Forneça o id da réplica como 1º argumento e número do cluster como 2º.")
        return
    
    idReplica = int(sys.argv[1])
    numCluster = int(sys.argv[2])
    ids = [0,1,2]
    ids.remove(idReplica)

    rpcPort = 4000 + numCluster * 10 + idReplica
    selfPort = 4100 + numCluster * 10 + idReplica

    otherPorts = map(lambda id: 4100 + numCluster * 10 + id, ids)

    print("Porta rpc:", rpcPort)

    serve(rpcPort, selfPort, otherPorts)

def serve(rpcPort: int, selfPort: int, otherPorts: Iterable[int]):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    database_pb2_grpc.add_DatabaseServicer_to_server(DatabaseServicer(selfPort, otherPorts), server)
    server.add_insecure_port(f'localhost:{rpcPort}')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    run()
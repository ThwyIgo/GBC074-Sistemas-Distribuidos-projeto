from concurrent import futures
import sys

import grpc
from paho.mqtt import client as mqtt_client
from biblioteca.gRPC import biblioteca_pb2_grpc

from biblioteca import lib
from biblioteca.bib.PortalBibliotecaServicer import PortalBibliotecaServicer

def run():
    if len(sys.argv) != 2:
        print("Forneça a porta como argumento da linha de comando")
        return
    
    porta = int(sys.argv[1])
    mqtt = lib.connect_mqtt("bib_server", porta)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    biblioteca_pb2_grpc.add_PortalBibliotecaServicer_to_server(PortalBibliotecaServicer(mqtt, porta), server)
    server.add_insecure_port(f"localhost:{porta}")
    server.start()
    server.wait_for_termination()
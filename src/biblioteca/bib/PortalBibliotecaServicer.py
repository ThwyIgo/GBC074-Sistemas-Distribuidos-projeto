from collections.abc import Iterable
import json

from biblioteca.gRPC import biblioteca_pb2_grpc, biblioteca_pb2

class PortalBibliotecaServicer(biblioteca_pb2_grpc.PortalBibliotecaServicer):
    def __init__(self, id: int) -> None:
        super().__init__()
    
    def RealizaEmprestimo(self, request_iterator: Iterable[biblioteca_pb2.UsuarioLivro], context) -> biblioteca_pb2.Status:
        pass
        
    def RealizaDevolucao(self, request_iterator: Iterable[biblioteca_pb2.UsuarioLivro], context) -> biblioteca_pb2.Status:
        pass

    def BloqueiaUsuarios(self, request: biblioteca_pb2.Vazia, context) -> biblioteca_pb2.Status:
        pass

    def LiberaUsuarios(self, request: biblioteca_pb2.Vazia, context) -> biblioteca_pb2.Status:
        pass

    def ListaUsuariosBloqueados(self, request: biblioteca_pb2.Vazia, context):
        pass

    def ListaLivrosEmprestados(self, request: biblioteca_pb2.Vazia, context):
        pass

    def ListaLivrosEmFalta(self, request: biblioteca_pb2.Vazia, context):
        pass

    def PesquisaLivro(self, request: biblioteca_pb2.Criterio, context):
        pass
import json

from paho.mqtt import client as mqtt_client

from biblioteca.gRPC import biblioteca_pb2_grpc, biblioteca_pb2
from biblioteca.cad import SyncMQTT, SyncMQTTOps, Livro

class PortalBibliotecaServicer(biblioteca_pb2_grpc.PortalBibliotecaServicer, SyncMQTTOps[biblioteca_pb2.Livro]):
    def __init__(self, mqtt: mqtt_client.Client, id: int) -> None:
        super().__init__()
        self.mqtt = mqtt
        self.emprestimos: dict[str, set[biblioteca_pb2.Livro]] = dict()
        self.livros: dict[str, Livro] = dict()
        self.syncMQTT = SyncMQTT(self, self.mqtt, -id)
        self.mqtt.loop_start() # TODO

    def getTopico(self) -> str:
        return "cad_server/livro"

    def criar(self, request: str, propagate: bool) -> biblioteca_pb2.Status:
        livro = self.parseT(request)
        self.livros[livro.isbn] = livro
        return biblioteca_pb2.Status(status=0)

    def parseT(self, string: str) -> biblioteca_pb2.Livro:
        payload = json.loads(string)
        return biblioteca_pb2.Livro(isbn=payload['isbn'], titulo=payload['titulo'], autor=payload['autor'], total=payload['total']);
        
    def RealizaEmprestimo(self, request_iterator, context) -> biblioteca_pb2.Status:
        for usuarioLivro in request_iterator:
            livro: biblioteca_pb2.Livro = self.livros[usuarioLivro.livro.id]
            if (livro.total <= 0):
                return biblioteca_pb2.Status(status=1,
                                              msg="Não há estoque suficiente para emprestar o livro com isbn=" 
                                              + livro.isbn)

            if usuarioLivro.usuario.id in self.emprestimos:
                livros = self.emprestimos[usuarioLivro.usuario.id]
                if len(livros) == 0:
                    livros = set()
                    self.emprestimos[usuarioLivro.usuario.id] = livros
            else:
                livros = set()
                self.emprestimos[usuarioLivro.usuario.id] = livros

            livros.add(Livro(livro))
            return biblioteca_pb2.Status(status=0)
from paho.mqtt import client as mqtt_client

from biblioteca.gRPC import biblioteca_pb2_grpc, biblioteca_pb2

class PortalBibliotecaServicer(biblioteca_pb2_grpc.PortalBibliotecaServicer):
    def __init__(self, mqtt: mqtt_client.Client, id: int) -> None:
        super().__init__()
        self.mqtt = mqtt
        self.emprestimos: dict[biblioteca_pb2.Usuario, set[biblioteca_pb2.Livro]] = dict()
        
    def RealizaEmprestimo(self, request_iterator, context) -> biblioteca_pb2.Status:
        for usuarioLivro in request_iterator:
            livro: biblioteca_pb2.Livro = usuarioLivro.livro
            if (livro.total <= 0):
                return biblioteca_pb2.Status(status=1,
                                              msg="Não há estoque suficiente para emprestar o livro com isbn=" 
                                              + livro.isbn)

            livros = self.emprestimos[usuarioLivro.usuario]
            if len(livros) == 0:
                livros = set()

            livros.add(livro)
            return biblioteca_pb2.Status(status=0)
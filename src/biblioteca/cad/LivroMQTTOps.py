import json

from paho.mqtt import client as mqtt_client

from biblioteca.cad import Livro, SyncMQTT, SyncMQTTOps, CRUD
from biblioteca.gRPC import cadastro_pb2

# Funções do SyncMQTTOps são implementadas, e as do gRPC simplesmente as chamam
class LivroMQTTOps(SyncMQTTOps[Livro]):
    def __init__(self, mqtt: mqtt_client.Client, id: int) -> None:
        super().__init__()
        self.livros: set[Livro] = set()
        self.mqtt = mqtt
        self.syncMQTT = SyncMQTT(self, self.mqtt, id)

    def getTopico(self) -> str:
        return "cad_server/livro"
    
    def parseT(self, string: str) -> Livro:
        payload = json.loads(string)
        return Livro(cadastro_pb2.Livro(isbn=payload['isbn'], titulo=payload['titulo'], autor=payload['autor'], total=payload['total']))
    
    def pub(self, msg: Livro, operacao: str, topico: str):
        """Publicar uma operação de usuário no broker MQTT"""
        payload = json.dumps({
            'remetente': self.mqtt.port,
            'isbn': msg.livro_pb2.isbn,
            'titulo': msg.livro_pb2.titulo,
            'autor': msg.livro_pb2.autor,
            'total': msg.livro_pb2.total
        })
        self.mqtt.publish(topico + "/" + operacao, payload)

    def criar(self, request: str, propagate: bool) -> cadastro_pb2.Status:
        livro = self.parseT(request)
        if not livro.isValido():
            return cadastro_pb2.Status(status=1, msg="Livro inválido")
        if livro in self.livros:
            return cadastro_pb2.Status(status=1, msg="Livro já existe")

        if propagate:    
            self.pub(livro, CRUD.criar, self.getTopico())
        self.livros.add(livro)
        return cadastro_pb2.Status(status=0)
    
    def atualizar(self, request: Livro, propagate: bool) -> cadastro_pb2.Status:
        livroExistente: Livro | None = None
        for l in self.livros:
            if l == request:
                livroExistente = l
                break

        if livroExistente != None:
            if propagate:
                self.pub(request, CRUD.atualizar, self.getTopico())

            self.livros.remove(livroExistente)
            self.livros.add(request)
            return cadastro_pb2.Status(status=0)
        else:
            return cadastro_pb2.Status(status=1, msg="Livro não encontrado.")
    
    def deletar(self, request: cadastro_pb2.Identificador, propagate: bool) -> cadastro_pb2.Status:
        livro: Livro | None = None
        for l in self.livros:
            if l.livro_pb2.isbn == request.id:
                livro = l
                break

        if livro != None:
            if propagate:
                self.pub(livro, CRUD.deletar, self.getTopico())

            self.livros.remove(livro)
            return cadastro_pb2.Status(status=0)
        else:
            return cadastro_pb2.Status(status=1, msg="Livro não encontrado.")

    def ObtemLivro(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Usuario:
        for livro in self.livros:
            if livro.livro_pb2.isbn == request.id:
                return livro.livro_pb2
            
        return cadastro_pb2.Livro()
    
    def ObtemTodosLivros(self, request: cadastro_pb2.Vazia, context):
        for livro in self.livros:
            yield livro.livro_pb2

    #################################

    def getTodos(self) -> set[Livro]:
        return self.livros

    def deletarTodos(self) -> None:
        self.livros = set()
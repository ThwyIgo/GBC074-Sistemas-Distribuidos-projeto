import jsonpickle
import threading
from biblioteca.gRPC import cadastro_pb2

from biblioteca.common import Livro

from biblioteca.gRPC import database_pb2_grpc, database_pb2

class LivroManager():
    def __init__(self, stub: database_pb2_grpc.DatabaseStub):
        self.livros: list[Livro] = list()
        self.stub = stub
        
        def updateCache(p = True):
            jsons = list(self.stub.getPrefix(database_pb2.String(value='L')))
            self.livros = list(map(lambda j: jsonpickle.decode(j), jsons)) # type: ignore

            print("Cache atualizado")

            if p:
                threading.Timer(5, updateCache).start()

        updateCache()
        self.updateCache = updateCache

    def contains(self, livro: Livro) -> bool:
        return livro in self.livros
    
    def add(self, livro: Livro) -> None:
        self.livros.append(livro)
        self.stub.put(database_pb2.String2(fst='L'+livro.livro_pb2.isbn, snd=jsonpickle.encode(livro)))
        self.updateCache(False)

    def remove(self, livro: Livro) -> None:
        self.livros.remove(livro)
        self.stub.deletar(database_pb2.String(value='L'+livro.livro_pb2.isbn))
        self.updateCache(False)

    def update(self, livro: Livro) -> None:
        self.livros[self.livros.index(livro)] = livro
        self.stub.put(database_pb2.String2(fst='L'+livro.livro_pb2.isbn, snd=jsonpickle.encode(livro)))
        self.updateCache(False)

    def get(self, isbn: str) -> Livro:
        for livro in self.livros:
            if livro.livro_pb2.isbn == isbn:
                return livro
            
        return Livro(cadastro_pb2.Livro())
    
    def getAll(self) -> list[Livro]:
        return self.livros
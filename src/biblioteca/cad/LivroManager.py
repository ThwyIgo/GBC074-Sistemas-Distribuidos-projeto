from collections.abc import Iterable
from pysyncobj import SyncObj, replicated
from biblioteca.gRPC import cadastro_pb2

from biblioteca.common import Livro

class LivroManager(SyncObj):
    def __init__(self, selfAddr: str, otherAddrs: Iterable[str]):
        super().__init__(selfAddr, otherAddrs)
        self.livros: list[Livro] = list()

    def contains(self, livro: Livro) -> bool:
        return livro in self.livros
    
    @replicated
    def add(self, livro: Livro) -> None:
        self.livros.append(livro)

    @replicated
    def remove(self, livro: Livro) -> None:
        self.livros.remove(livro)

    @replicated
    def update(self, livro: Livro) -> None:
        self.livros[self.livros.index(livro)] = livro

    def get(self, isbn: str) -> Livro:
        for livro in self.livros:
            if livro.livro_pb2.isbn == isbn:
                return livro
            
        return Livro(cadastro_pb2.Livro())
    
    def getAll(self) -> list[Livro]:
        return self.livros
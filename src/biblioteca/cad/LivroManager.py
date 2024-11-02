from biblioteca.gRPC import cadastro_pb2

from biblioteca.common import Livro

class LivroManager():
    def __init__(self):
        self.livros: list[Livro] = list()

    def contains(self, livro: Livro) -> bool:
        return livro in self.livros
    
    def add(self, livro: Livro) -> None:
        self.livros.append(livro)

    def remove(self, livro: Livro) -> None:
        self.livros.remove(livro)

    def update(self, livro: Livro) -> None:
        self.livros[self.livros.index(livro)] = livro

    def get(self, isbn: str) -> Livro:
        for livro in self.livros:
            if livro.livro_pb2.isbn == isbn:
                return livro
            
        return Livro(cadastro_pb2.Livro())
    
    def getAll(self) -> list[Livro]:
        return self.livros
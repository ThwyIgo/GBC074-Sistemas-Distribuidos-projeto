from dataclasses import dataclass

from biblioteca.gRPC import cadastro_pb2

@dataclass
class Livro():
    livro_pb2: cadastro_pb2.Livro

    def isValido(self):
        return all(
            [ len(self.livro_pb2.isbn) == 13 or len(self.livro_pb2.isbn) == 10
            , self.livro_pb2.isbn.isdigit()
            , self.livro_pb2.total >= 0
            ])
    
    def __hash__(self) -> int:
        return hash(self.livro_pb2.isbn)
    
    def __eq__(self, value: object) -> bool:
        if type(value) == type(self):
            return self.livro_pb2.isbn == value.livro_pb2.isbn
        if type(value) == cadastro_pb2.Livro:
            return self.livro_pb2.isbn == value.isbn
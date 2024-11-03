from dataclasses import dataclass

from biblioteca.common import Livro, Usuario

@dataclass
class Emprestimo():
    usuario: Usuario
    livro: Livro
    timestamp: int

    def __eq__(self, value: object) -> bool:
        if type(self) == type(value):
            return self.usuario == value.usuario and self.livro == value.livro
from dataclasses import dataclass

from biblioteca.common import Livro, Usuario

@dataclass
class Emprestimo():
    usuario: Usuario
    livro: Livro
    timestamp: int
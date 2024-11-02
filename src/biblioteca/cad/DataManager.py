from multimethod import multimethod
from collections.abc import Iterable
from pysyncobj import SyncObj, replicated

from biblioteca.cad import UsuarioManager, LivroManager
from biblioteca.common import Usuario, Livro

class DataManager(SyncObj):
    def __init__(self, selfAddr: str, otherAddrs: Iterable[str]):
        super().__init__(selfAddr, otherAddrs)
        self.usuarioManager = UsuarioManager()
        self.livroManager = LivroManager()

    @multimethod
    def contains(self, usuario: Usuario) -> bool:
        return self.usuarioManager.contains(usuario)
    
    @multimethod
    def contains(self, livro: Livro) -> bool:
        return self.livroManager.contains(livro)

    @replicated
    def addUsuario(self, usuario: Usuario) -> None:
        self.usuarioManager.add(usuario)

    @replicated
    def addLivro(self, livro: Livro) -> None:
        self.livroManager.add(livro)

    @replicated
    def removeUsuario(self, usuario: Usuario) -> None:
        self.usuarioManager.remove(usuario)

    @replicated
    def removeLivro(self, livro: Livro) -> None:
        self.livroManager.remove(livro)
    
    @replicated
    def updateUsuario(self, usuario: Usuario) -> None:
        self.usuarioManager.update(usuario)

    @replicated
    def updateLivro(self, livro: Livro) -> None:
        self.livroManager.update(livro)
    
    def getUsuario(self, cpf: str) -> Usuario:
        return self.usuarioManager.get(cpf)
    
    def getLivro(self, cpf: str) -> Livro:
        return self.livroManager.get(cpf)
    
    def getAllUsuario(self) -> list[Usuario]:
        return self.usuarioManager.getAll()
    
    def getAllLivro(self) -> list[Livro]:
        return self.livroManager.getAll()
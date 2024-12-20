from multimethod import multimethod
import grpc

from biblioteca.cad import UsuarioManager, LivroManager
from biblioteca.common import Usuario, Livro

from biblioteca.gRPC import database_pb2_grpc

class DataManager():
    def __init__(self, dbUsrPort: int, dbLivPort: int):
        self.stubUsr = database_pb2_grpc.DatabaseStub(grpc.insecure_channel(f'localhost:{dbUsrPort}'))
        self.stubLiv = database_pb2_grpc.DatabaseStub(grpc.insecure_channel(f'localhost:{dbLivPort}'))
        self.usuarioManager = UsuarioManager(self.stubUsr)
        self.livroManager = LivroManager(self.stubLiv)

    @multimethod
    def contains(self, usuario: Usuario) -> bool: # type: ignore
        return self.usuarioManager.contains(usuario)
    
    @multimethod
    def contains(self, livro: Livro) -> bool:
        return self.livroManager.contains(livro)

    def addUsuario(self, usuario: Usuario) -> None:
        self.usuarioManager.add(usuario)

    def addLivro(self, livro: Livro) -> None:
        self.livroManager.add(livro)

    def removeUsuario(self, usuario: Usuario) -> None:
        self.usuarioManager.remove(usuario)

    def removeLivro(self, livro: Livro) -> None:
        self.livroManager.remove(livro)
    
    def updateUsuario(self, usuario: Usuario) -> None:
        self.usuarioManager.update(usuario)

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
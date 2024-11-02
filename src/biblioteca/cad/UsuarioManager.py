from collections.abc import Iterable
from pysyncobj import SyncObj, replicated
from biblioteca.gRPC import cadastro_pb2

from biblioteca.common import Usuario

class UsuarioManager(SyncObj):
    def __init__(self, selfAddr: str, otherAddrs: Iterable[str]):
        super().__init__(selfAddr, otherAddrs)
        self.usuarios: list[Usuario] = list()

    def contains(self, usuario: Usuario) -> bool:
        return usuario in self.usuarios

    @replicated
    def add(self, usuario: Usuario) -> None:
        self.usuarios.append(usuario)
    
    @replicated
    def remove(self, usuario: Usuario) -> None:
        self.usuarios.remove(usuario)
    
    @replicated
    def update(self, usuario: Usuario) -> None:
        self.usuarios[self.usuarios.index(usuario)] = usuario
    
    def get(self, cpf: str) -> Usuario:
        for usuario in self.usuarios:
            if usuario.usuario_pb2.cpf == cpf:
                return usuario
            
        return Usuario(cadastro_pb2.Usuario())
    
    def getAll(self) -> list[Usuario]:
        return self.usuarios
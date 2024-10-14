from pysyncobj import SyncObj, replicated
from biblioteca.gRPC import biblioteca_pb2

from biblioteca.common import Usuario

class UsuarioManager(SyncObj):
    def __init__(self, selfAddr: str, otherAddrs: list[str]):
        super().__init__(selfAddr, otherAddrs)
        self.usuarios: list[Usuario] = list()

    @replicated
    def add(self, usuario: Usuario) -> biblioteca_pb2.Status:
        if usuario in self.usuarios:
            return biblioteca_pb2.Status(status=1, msg="Usuário já existe")
        
        self.usuarios.append(usuario)
        return biblioteca_pb2.Status(status=0)
    
    @replicated
    def remove(self, usuario: Usuario) -> biblioteca_pb2.Status:
        if usuario not in self.usuarios:
            return biblioteca_pb2.Status(status=1, msg="Usuário não existe")
        
        self.usuarios.remove(usuario)
        return biblioteca_pb2.Status(status=0)
    
    @replicated
    def update(self, usuario: Usuario) -> biblioteca_pb2.Status:
        if usuario not in self.usuarios:
            return biblioteca_pb2.Status(status=1, msg="Usuário não existe")
        
        self.usuarios[self.usuarios.index(usuario)] = usuario
        return biblioteca_pb2.Status(status=0)
    
    def get(self, cpf: str) -> Usuario:
        return next([u for u in self.usuarios if u.usuario_pb2.cpf == cpf],
                    Usuario())
    
    def getAll(self) -> list[Usuario]:
        return self.usuarios
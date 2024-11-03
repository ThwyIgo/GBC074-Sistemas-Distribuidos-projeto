import jsonpickle
import threading
from biblioteca.gRPC import cadastro_pb2

from biblioteca.common import Usuario

from biblioteca.gRPC import database_pb2_grpc, database_pb2

class UsuarioManager():
    def __init__(self, stub: database_pb2_grpc.DatabaseStub):
        self.usuarios: list[Usuario] = list()
        self.stub = stub
        
        def updateCache(p = True):
            jsons: list[database_pb2.String] = list(self.stub.getPrefix(database_pb2.String(value='U')))
            self.usuarios = list(map(lambda j: jsonpickle.decode(j.value), jsons)) # type: ignore

            print("Cache usuários atualizado")

            if p:
                threading.Timer(5, updateCache).start()

        updateCache()
        self.updateCache = updateCache

    def contains(self, usuario: Usuario) -> bool:
        return usuario in self.usuarios

    def add(self, usuario: Usuario) -> None:
        self.usuarios.append(usuario)
        self.stub.put(database_pb2.String2(fst='U'+usuario.usuario_pb2.cpf, snd=jsonpickle.encode(usuario))) # Falha aqui
        self.updateCache(False)
    
    def remove(self, usuario: Usuario) -> None:
        self.usuarios.remove(usuario)
        self.stub.deletar(database_pb2.String(value='U'+usuario.usuario_pb2.cpf))
        self.updateCache(False)
    
    def update(self, usuario: Usuario) -> None:
        self.usuarios[self.usuarios.index(usuario)] = usuario
        self.stub.put(database_pb2.String2(fst='U'+usuario.usuario_pb2.cpf, snd=jsonpickle.encode(usuario)))
        self.updateCache(False)
    
    def get(self, cpf: str) -> Usuario:
        for usuario in self.usuarios:
            if usuario.usuario_pb2.cpf == cpf:
                return usuario
            
        return Usuario(cadastro_pb2.Usuario())
    
    def getAll(self) -> list[Usuario]:
        return self.usuarios
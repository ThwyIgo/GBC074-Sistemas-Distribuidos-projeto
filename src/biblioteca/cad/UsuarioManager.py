from biblioteca.gRPC import cadastro_pb2

from biblioteca.common import Usuario

class UsuarioManager():
    def __init__(self):
        self.usuarios: list[Usuario] = list()

    def contains(self, usuario: Usuario) -> bool:
        return usuario in self.usuarios

    def add(self, usuario: Usuario) -> None:
        self.usuarios.append(usuario)
    
    def remove(self, usuario: Usuario) -> None:
        self.usuarios.remove(usuario)
    
    def update(self, usuario: Usuario) -> None:
        self.usuarios[self.usuarios.index(usuario)] = usuario
    
    def get(self, cpf: str) -> Usuario:
        for usuario in self.usuarios:
            if usuario.usuario_pb2.cpf == cpf:
                return usuario
            
        return Usuario(cadastro_pb2.Usuario())
    
    def getAll(self) -> list[Usuario]:
        return self.usuarios
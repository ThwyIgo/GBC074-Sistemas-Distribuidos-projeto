from dataclasses import dataclass, field

from biblioteca.gRPC import cadastro_pb2

@dataclass
class Usuario():
    usuario_pb2: cadastro_pb2.Usuario
    bloqueado: bool = False

    def isValido(self):
        return all(
            [ len(self.usuario_pb2.cpf) == 11
            , self.usuario_pb2.cpf.isdigit() 
            ])
    
    def __hash__(self) -> int:
        return hash(self.usuario_pb2.cpf)
    
    def __eq__(self, value: object) -> bool:
        if type(value) == type(self):
            return self.usuario_pb2.cpf == value.usuario_pb2.cpf
        if type(value) == cadastro_pb2.Usuario:
            return self.usuario_pb2.cpf == value.cpf
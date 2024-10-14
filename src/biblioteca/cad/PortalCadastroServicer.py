from biblioteca.gRPC import cadastro_pb2, cadastro_pb2_grpc
from biblioteca.common import Usuario, Livro
from biblioteca.cad import UsuarioManager

class PortalCadastroServicer(cadastro_pb2_grpc.PortalCadastroServicer):
    def __init__(self, selfPorta: str, otherPortas: list[str]) -> None:
        super().__init__()
        self.usuarioManager = UsuarioManager('localhost:'+selfPorta, map(lambda a: 'localhost:'+a, otherPortas))

    def NovoUsuario(self, request: cadastro_pb2.Usuario, context) -> cadastro_pb2.Status:
        return self.usuarioManager.add(Usuario(request))

    def EditaUsuario(self, request: cadastro_pb2.Usuario, context) -> cadastro_pb2.Status:
        return self.usuarioManager.update(Usuario(request))
    
    def RemoveUsuario(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Status:
        return self.usuarioManager.remove(Usuario(request))
    
    def ObtemUsuario(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Usuario:
        return self.usuarioManager.get(request.id)
    
    def ObtemTodosUsuarios(self, request: cadastro_pb2.Vazia, context):
        return self.usuarioManager.getAll()
    
    def NovoLivro(self, request: cadastro_pb2.Livro, context) -> cadastro_pb2.Status:
        pass
    
    def EditaLivro(self, request: cadastro_pb2.Livro, context) -> cadastro_pb2.Status:
        pass
    
    def RemoveLivro(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Status:
        pass
    
    def ObtemLivro(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Usuario:
        pass
    
    def ObtemTodosLivros(self, request: cadastro_pb2.Vazia, context):
        pass
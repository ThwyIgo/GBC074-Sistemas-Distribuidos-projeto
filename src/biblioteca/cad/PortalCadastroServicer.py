from biblioteca.gRPC import cadastro_pb2, cadastro_pb2_grpc
from biblioteca.common import Usuario, Livro
from biblioteca.cad import UsuarioManager, LivroManager

class PortalCadastroServicer(cadastro_pb2_grpc.PortalCadastroServicer):
    def __init__(self, selfPorta: str, otherPortas: list[str]) -> None:
        super().__init__()
        otherAddrs = map(lambda a: 'localhost:'+a, otherPortas)
        self.usuarioManager = UsuarioManager('localhost:'+selfPorta, otherAddrs)
        self.livroManager = LivroManager('localhost:'+selfPorta, otherAddrs)

    def NovoUsuario(self, request: cadastro_pb2.Usuario, context) -> cadastro_pb2.Status:
        usuario = Usuario(request)
        if self.usuarioManager.contains(usuario):
            return cadastro_pb2.Status(status=1, msg="Usuário já existe")
        
        self.usuarioManager.add(usuario)
        return cadastro_pb2.Status(status=0)

    def EditaUsuario(self, request: cadastro_pb2.Usuario, context) -> cadastro_pb2.Status:
        usuario = Usuario(request)
        if not self.usuarioManager.contains(usuario):
            return cadastro_pb2.Status(status=1, msg="Usuário não existe")
        
        self.usuarioManager.update(usuario)
        return cadastro_pb2.Status(status=0)
    
    def RemoveUsuario(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Status:
        usuario = Usuario(cadastro_pb2.Usuario(cpf=request.id))
        if not self.usuarioManager.contains(usuario):
            return cadastro_pb2.Status(status=1, msg="Usuário não existe")
        
        self.usuarioManager.remove(usuario)
        return cadastro_pb2.Status(status=0)
    
    def ObtemUsuario(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Usuario:
        return self.usuarioManager.get(request.id).usuario_pb2
    
    def ObtemTodosUsuarios(self, request: cadastro_pb2.Vazia, context):
        for usuario in self.usuarioManager.getAll():
            yield usuario.usuario_pb2
    
    def NovoLivro(self, request: cadastro_pb2.Livro, context) -> cadastro_pb2.Status:
        livro = Livro(request)
        if self.livroManager.contains(livro):
            return cadastro_pb2.Status(status=1, msg="Livro já existe")
        
        self.livroManager.add(livro)
        return cadastro_pb2.Status(status=0)
    
    def EditaLivro(self, request: cadastro_pb2.Livro, context) -> cadastro_pb2.Status:
        livro = Livro(request)
        if not self.livroManager.contains(livro):
            return cadastro_pb2.Status(status=1, msg="Livro não existe")
        
        self.livroManager.update(livro)
        return cadastro_pb2.Status(status=0)
    
    def RemoveLivro(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Status:
        livro = Livro(cadastro_pb2.Livro(isbn=request.id))
        if not self.livroManager.contains(livro):
            return cadastro_pb2.Status(status=1, msg="Livro não existe")
        
        self.livroManager.remove(livro)
        return cadastro_pb2.Status(status=0)
    
    def ObtemLivro(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Livro:
        return self.livroManager.get(request.id).livro_pb2
    
    def ObtemTodosLivros(self, request: cadastro_pb2.Vazia, context):
        for usuario in self.usuarioManager.getAll():
            yield usuario.usuario_pb2
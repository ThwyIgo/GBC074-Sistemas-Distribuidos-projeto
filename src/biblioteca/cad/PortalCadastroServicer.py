from biblioteca.gRPC import cadastro_pb2, cadastro_pb2_grpc
from biblioteca.common import Usuario, Livro
from biblioteca.cad import DataManager

class PortalCadastroServicer(cadastro_pb2_grpc.PortalCadastroServicer):
    def __init__(self, selfPorta: str, otherPortas: list[str]) -> None:
        super().__init__()
        otherAddrs = map(lambda a: 'localhost:'+a, otherPortas)
        self.dataManager = DataManager('localhost:'+selfPorta, otherAddrs)

    def NovoUsuario(self, request: cadastro_pb2.Usuario, context) -> cadastro_pb2.Status:
        usuario = Usuario(request)
        if self.dataManager.contains(usuario):
            return cadastro_pb2.Status(status=1, msg="Usuário já existe")
        
        self.dataManager.add(usuario)
        return cadastro_pb2.Status(status=0)

    def EditaUsuario(self, request: cadastro_pb2.Usuario, context) -> cadastro_pb2.Status:
        usuario = Usuario(request)
        if not self.dataManager.contains(usuario):
            return cadastro_pb2.Status(status=1, msg="Usuário não existe")
        
        self.dataManager.update(usuario)
        return cadastro_pb2.Status(status=0)
    
    def RemoveUsuario(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Status:
        usuario = Usuario(cadastro_pb2.Usuario(cpf=request.id))
        if not self.dataManager.contains(usuario):
            return cadastro_pb2.Status(status=1, msg="Usuário não existe")
        
        self.dataManager.remove(usuario)
        return cadastro_pb2.Status(status=0)
    
    def ObtemUsuario(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Usuario:
        return self.dataManager.getUsuario(request.id).usuario_pb2
    
    def ObtemTodosUsuarios(self, request: cadastro_pb2.Vazia, context):
        for usuario in self.dataManager.getAllUsuario():
            yield usuario.usuario_pb2
    
    def NovoLivro(self, request: cadastro_pb2.Livro, context) -> cadastro_pb2.Status:
        livro = Livro(request)
        if self.dataManager.contains(livro):
            return cadastro_pb2.Status(status=1, msg="Livro já existe")
        
        self.dataManager.add(livro)
        return cadastro_pb2.Status(status=0)
    
    def EditaLivro(self, request: cadastro_pb2.Livro, context) -> cadastro_pb2.Status:
        livro = Livro(request)
        if not self.dataManager.contains(livro):
            return cadastro_pb2.Status(status=1, msg="Livro não existe")
        
        self.dataManager.update(livro)
        return cadastro_pb2.Status(status=0)
    
    def RemoveLivro(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Status:
        livro = Livro(cadastro_pb2.Livro(isbn=request.id))
        if not self.dataManager.contains(livro):
            return cadastro_pb2.Status(status=1, msg="Livro não existe")
        
        self.dataManager.remove(livro)
        return cadastro_pb2.Status(status=0)
    
    def ObtemLivro(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Livro:
        return self.dataManager.getLivro(request.id).livro_pb2
    
    def ObtemTodosLivros(self, request: cadastro_pb2.Vazia, context):
        for livro in self.dataManager.getAllLivro():
            yield livro.livro_pb2
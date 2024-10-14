import json

from biblioteca.gRPC import cadastro_pb2, cadastro_pb2_grpc
from biblioteca.cad import Usuario, Livro

class PortalCadastroServicer(cadastro_pb2_grpc.PortalCadastroServicer):
    def __init__(self, id: int) -> None:
        super().__init__()

    def NovoUsuario(self, request: cadastro_pb2.Usuario, context) -> cadastro_pb2.Status:
        req = json.dumps({
            'cpf': request.cpf,
            'nome': request.nome,
        })
        return self.usuariosServicer.criar(req, True)
    
    def EditaUsuario(self, request: cadastro_pb2.Usuario, context) -> cadastro_pb2.Status:
        reqU = Usuario(request)
        return self.usuariosServicer.atualizar(reqU, True)
    
    def RemoveUsuario(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Status:
        return self.usuariosServicer.deletar(request, True)
    
    def ObtemUsuario(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Usuario:
        return self.usuariosServicer.ObtemUsuario(request, context)
    
    def ObtemTodosUsuarios(self, request: cadastro_pb2.Vazia, context):
        return self.usuariosServicer.ObtemTodosUsuarios(request, context)
    
    def NovoLivro(self, request: cadastro_pb2.Livro, context) -> cadastro_pb2.Status:
        req = json.dumps({
            'remetente': self.mqtt.port,
            'isbn': request.isbn,
            'titulo': request.titulo,
            'autor': request.autor,
            'total': request.total
        })
        return self.livrosServicer.criar(req, True)
    
    def EditaLivro(self, request: cadastro_pb2.Livro, context) -> cadastro_pb2.Status:
        reqU = Livro(request)
        return self.livrosServicer.atualizar(reqU, True)
    
    def RemoveLivro(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Status:
        return self.livrosServicer.deletar(request, True)
    
    def ObtemLivro(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Usuario:
        return self.livrosServicer.ObtemLivro(request, context)
    
    def ObtemTodosLivros(self, request: cadastro_pb2.Vazia, context):
        return self.livrosServicer.ObtemTodosLivros(request, context)
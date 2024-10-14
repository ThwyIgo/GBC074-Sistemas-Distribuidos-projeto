import json

from biblioteca.gRPC import biblioteca_pb2_grpc, biblioteca_pb2
from biblioteca.cad import Livro

class PortalBibliotecaServicer(biblioteca_pb2_grpc.PortalBibliotecaServicer):
    def __init__(self, id: int) -> None:
        super().__init__()
        # Dict de cpf, isbn
        self.emprestimos: dict[str, set[str]] = dict()
        self.livros: dict[str, Livro] = dict()

    def criar(self, request: str, propagate: bool) -> biblioteca_pb2.Status:
        livro = self.parseT(request)
        self.livros[livro.isbn] = livro
        return biblioteca_pb2.Status(status=0)

    def parseT(self, string: str) -> biblioteca_pb2.Livro:
        payload = json.loads(string)
        return biblioteca_pb2.Livro(isbn=payload['isbn'], titulo=payload['titulo'], autor=payload['autor'], total=payload['total']);
        
    def RealizaEmprestimo(self, request_iterator, context) -> biblioteca_pb2.Status:
        for usuarioLivro in request_iterator:
            if usuarioLivro.livro.id not in self.livros:
                return biblioteca_pb2.Status(status=1, msg="Livro não encontrado")
            livro: biblioteca_pb2.Livro = self.livros[usuarioLivro.livro.id]
            if (livro.total <= 0):
                return biblioteca_pb2.Status(status=1,
                                              msg="Não há estoque suficiente para emprestar o livro com isbn=" 
                                              + livro.isbn)

            if usuarioLivro.usuario.id in self.emprestimos:
                livros = self.emprestimos[usuarioLivro.usuario.id]
                if len(livros) == 0:
                    livros = set()
                    self.emprestimos[usuarioLivro.usuario.id] = livros
            else:
                livros = set()
                self.emprestimos[usuarioLivro.usuario.id] = livros

            livros.add(livro.isbn)
            return biblioteca_pb2.Status(status=0)
        
    def RealizaDevolucao(self, request_iterator, context) -> biblioteca_pb2.Status:
        for usuarioLivro in request_iterator:
            if usuarioLivro.usuario.id in self.emprestimos:
                livros = self.emprestimos[usuarioLivro.usuario.id]
                try:
                    livros.remove(usuarioLivro.livro.id)
                    return biblioteca_pb2.Status(status=0)
                except KeyError:
                    return biblioteca_pb2.Status(status=1,
                                                 msg="O livro com isbn " 
                                                 + usuarioLivro.livro.id
                                                 + " não está emprestado ao usuário "
                                                 + usuarioLivro.usuario.id)
            else:
                return biblioteca_pb2.Status(status=1,
                                             msg="Não há nenhum empréstimo ao usuário "
                                             + usuarioLivro.usuario.id)
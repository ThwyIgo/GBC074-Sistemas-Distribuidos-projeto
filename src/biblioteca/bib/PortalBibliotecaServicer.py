from collections.abc import Iterable
from datetime import datetime
import jsonpickle
import threading

import grpc

from biblioteca.bib.Emprestimo import Emprestimo
from biblioteca.gRPC import biblioteca_pb2_grpc, biblioteca_pb2, database_pb2_grpc, database_pb2
from biblioteca.common import Usuario, Livro

class PortalBibliotecaServicer(biblioteca_pb2_grpc.PortalBibliotecaServicer):
    def __init__(self, dbPort: int) -> None:
        super().__init__()
        self.stub = database_pb2_grpc.DatabaseStub(grpc.insecure_channel(f'localhost:{dbPort}'))
        self.usuarios: list[Usuario] = list()
        self.livros: list[Livro] = list()
        self.emprestimos: list[Emprestimo] = list()
        
        def updateCache(p = True):
            jsons: list[database_pb2.String] = list(self.stub.getPrefix(database_pb2.String(value='U')))
            self.usuarios = list(map(lambda j: jsonpickle.decode(j.value), jsons)) # type: ignore
            jsons = list(self.stub.getPrefix(database_pb2.String(value='L')))
            self.livros = list(map(lambda j: jsonpickle.decode(j.value), jsons)) # type: ignore
            jsons = list(self.stub.getPrefix(database_pb2.String(value='E')))
            self.emprestimos = list(map(lambda j: jsonpickle.decode(j.value), jsons)) # type: ignore

            print("Cache atualizado")

            if p:
                threading.Timer(5, updateCache).start()

        updateCache()
        self.updateCache = updateCache
    
    def RealizaEmprestimo(self, request_iterator: Iterable[biblioteca_pb2.UsuarioLivro], context) -> biblioteca_pb2.Status:
        for usrLiv in request_iterator:
            usuario: Usuario | None = next(filter(lambda u: u.usuario_pb2.cpf == usrLiv.usuario.id, self.usuarios), None)
            livro: Livro | None = next(filter(lambda l: l.livro_pb2.isbn == usrLiv.livro.id, self.livros), None)

            if usuario == None or livro == None:
                return biblioteca_pb2.Status(status=1, msg="Usuário ou livro não encontrado")
            if livro.livro_pb2.total <= 0:
                return biblioteca_pb2.Status(status=1, msg=f"Livro {livro.livro_pb2.titulo} não tem quantidade suficiente para realizar empréstimo")
            if usuario.bloqueado:
                return biblioteca_pb2.Status(status=1, msg=f"Usuário {usuario.usuario_pb2.nome} está bloqueado")
            
            emprestimo = Emprestimo(usuario, livro, int(datetime.now().timestamp()))

            if emprestimo in self.emprestimos:
                return biblioteca_pb2.Status(status=1, msg="Empréstimo já existe")
            
            livro.livro_pb2.total -= 1
            self.stub.put(database_pb2.String2(
                fst='L'+livro.livro_pb2.isbn,
                snd=jsonpickle.encode(livro)
            ))
            
            self.stub.put(database_pb2.String2(
                fst='E'+usuario.usuario_pb2.cpf,
                snd=jsonpickle.encode(emprestimo)
            ))

            self.updateCache(False)

        return biblioteca_pb2.Status(status=0)
        
    def RealizaDevolucao(self, request_iterator: Iterable[biblioteca_pb2.UsuarioLivro], context) -> biblioteca_pb2.Status:
        for usrLiv in request_iterator:
            usuario: Usuario | None = next(filter(lambda u: u.usuario_pb2.cpf == usrLiv.usuario.id, self.usuarios), None)
            livro: Livro | None = next(filter(lambda l: l.livro_pb2.isbn == usrLiv.livro.id, self.livros), None)

            if usuario == None or livro == None:
                return biblioteca_pb2.Status(status=1, msg="Usuário ou livro não encontrado")
            if next(filter(lambda e: e.usuario == usuario and e.livro == livro, self.emprestimos), None) == None:
                return biblioteca_pb2.Status(status=1, msg="Empréstimo não encontrado")
            
            livro.livro_pb2.total += 1
            self.stub.put(database_pb2.String2(
                fst='L'+livro.livro_pb2.isbn,
                snd=jsonpickle.encode(livro)
            ))
            
            self.stub.deletar(database_pb2.String(value='E'+usuario.usuario_pb2.cpf))
            #TODO desbloquear usuário se ele não tiver livros atrasados
            self.updateCache(False)
            
        return biblioteca_pb2.Status(status=0)

    def BloqueiaUsuarios(self, request: biblioteca_pb2.Vazia, context) -> biblioteca_pb2.Status:
        pass

    def LiberaUsuarios(self, request: biblioteca_pb2.Vazia, context) -> biblioteca_pb2.Status:
        pass

    def ListaUsuariosBloqueados(self, request: biblioteca_pb2.Vazia, context):
        pass

    def ListaLivrosEmprestados(self, request: biblioteca_pb2.Vazia, context):
        for livro in set(map(lambda e: e.livro, self.emprestimos)):
            yield livro.livro_pb2

    def ListaLivrosEmFalta(self, request: biblioteca_pb2.Vazia, context):
        for livro in filter(lambda l: l.livro_pb2.total <= 0, self.livros):
            yield livro.livro_pb2

    def PesquisaLivro(self, request: biblioteca_pb2.Criterio, context):
        pass
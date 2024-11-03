from collections.abc import Iterable
from datetime import datetime
import jsonpickle
import threading

import grpc

from biblioteca.bib.Emprestimo import Emprestimo
from biblioteca.gRPC import biblioteca_pb2_grpc, biblioteca_pb2, database_pb2_grpc, database_pb2
from biblioteca.common import Usuario, Livro

class PortalBibliotecaServicer(biblioteca_pb2_grpc.PortalBibliotecaServicer):
    def __init__(self, dbUsrPort: int, dbLivPort: int) -> None:
        super().__init__()
        self.stubUsr = database_pb2_grpc.DatabaseStub(grpc.insecure_channel(f'localhost:{dbUsrPort}'))
        self.stubLiv = database_pb2_grpc.DatabaseStub(grpc.insecure_channel(f'localhost:{dbLivPort}'))
        self.usuarios: list[Usuario] = list()
        self.livros: list[Livro] = list()
        self.emprestimos: list[Emprestimo] = list()
        
        def updateCache(p = True):
            jsons: list[database_pb2.String] = list(self.stubUsr.getPrefix(database_pb2.String(value='')))
            self.usuarios = list(map(lambda j: jsonpickle.decode(j.value), jsons)) # type: ignore
            jsons = list(self.stubLiv.getPrefix(database_pb2.String(value='L')))
            self.livros = list(map(lambda j: jsonpickle.decode(j.value), jsons)) # type: ignore
            jsons = list(self.stubLiv.getPrefix(database_pb2.String(value='E')))
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
            self.stubLiv.put(database_pb2.String2(
                fst='L'+livro.livro_pb2.isbn,
                snd=jsonpickle.encode(livro)
            ))
            
            self.stubLiv.put(database_pb2.String2(
                fst='E'+usuario.usuario_pb2.cpf+livro.livro_pb2.isbn,
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
            self.stubLiv.put(database_pb2.String2(
                fst='L'+livro.livro_pb2.isbn,
                snd=jsonpickle.encode(livro)
            ))
            
            self.stubLiv.deletar(database_pb2.String(value='E'+usuario.usuario_pb2.cpf))
            #TODO desbloquear usuário se ele não tiver livros atrasados
            self.updateCache(False)
            
        return biblioteca_pb2.Status(status=0)

    def BloqueiaUsuarios(self, request: biblioteca_pb2.Vazia, context) -> biblioteca_pb2.Status:
        qtd = 0
        agora = int(datetime.now().timestamp())
        for emprestimo in self.emprestimos:
            if agora > emprestimo.timestamp + 10:
                usr = next(filter(lambda u: u == emprestimo.usuario, self.usuarios))
                usr.bloqueado = True
                self.stubUsr.put(database_pb2.String2(fst=usr.usuario_pb2.cpf, snd=jsonpickle.encode(usr)))
                qtd += 1

        return biblioteca_pb2.Status(status=qtd)

    def LiberaUsuarios(self, request: biblioteca_pb2.Vazia, context) -> biblioteca_pb2.Status:
        pass

    def ListaUsuariosBloqueados(self, request: biblioteca_pb2.Vazia, context):
        agora = int(datetime.now().timestamp())

        for usuario in self.usuarios:
            if usuario.bloqueado:
                usrCad = usuario.usuario_pb2
                usrBib = biblioteca_pb2.Usuario(cpf=usrCad.cpf, nome=usrCad.nome, bloqueado=True)
                emprestimos = filter(lambda e: e.usuario == usuario, self.emprestimos)
                livrosVencidos = map(lambda l: biblioteca_pb2.Livro(isbn=l.isbn, titulo=l.titulo, autor=l.autor, total=l.total),
                                      map(lambda e: e.livro.livro_pb2, 
                                          filter(lambda e: agora > e.timestamp + 10, emprestimos)))
                yield biblioteca_pb2.UsuarioBloqueado(usuario=usrBib, livros=livrosVencidos)

    def ListaLivrosEmprestados(self, request: biblioteca_pb2.Vazia, context):
        for livro in set(map(lambda e: e.livro, self.emprestimos)):
            yield livro.livro_pb2

    def ListaLivrosEmFalta(self, request: biblioteca_pb2.Vazia, context):
        for livro in filter(lambda l: l.livro_pb2.total <= 0, self.livros):
            yield livro.livro_pb2

    def PesquisaLivro(self, request: biblioteca_pb2.Criterio, context):
        criterio2: str | None = None
        op: str | None = None

        [campo1, tail] = request.criterio.split(':', 1)
        if '&' in tail:
            [valor1, criterio2] = tail.split('&', 1)
            op = '&'
        elif '|' in tail:
            [valor1, criterio2] = tail.split('|', 1)
            op = '|'
        else:
            valor1 = tail

        if criterio2 == None:
            for livro in self.buscaCampo(campo1, valor1):
                yield livro.livro_pb2
        else:
            [campo2, valor2] = criterio2.split(':', 1)
            for livro in self.buscaCampo(campo1, valor1, campo2, valor2, op):
                yield livro.livro_pb2


    def buscaCampo(self, campo1: str, valor1: str, campo2: str | None = None, valor2: str | None = None, op: str | None = None) -> Iterable[Livro]:
        if campo1 == "isbn":
            filtro1 = lambda l: l.livro_pb2.isbn == valor1
        elif campo1 == "titulo":
            filtro1 = lambda l: l.livro_pb2.titulo == valor1
        elif campo1 == "autor":
            filtro1 = lambda l: l.livro_pb2.autor == valor1

        if op != None:
            if campo2 == "isbn":
                filtro2 = lambda l: l.livro_pb2.isbn == valor2
            elif campo2 == "titulo":
                filtro2 = lambda l: l.livro_pb2.titulo == valor2
            elif campo2 == "autor":
                filtro2 = lambda l: l.livro_pb2.autor == valor2

            if op == '&':
                filtro = lambda l: filtro1(l) and filtro2(l)
            elif op == '|':
                filtro = lambda l: filtro1(l) or filtro2(l)
            
            return filter(filtro, self.livros)

        return filter(filtro1, self.livros)
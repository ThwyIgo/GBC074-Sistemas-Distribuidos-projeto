import json

from paho.mqtt import client as mqtt_client

from biblioteca.cad import Usuario, SyncMQTT, SyncMQTTOps, CRUD
from biblioteca.gRPC import cadastro_pb2

# Funções do SyncMQTTOps são implementadas, e as do gRPC simplesmente as chamam
class UsuarioMQTTOps(SyncMQTTOps[Usuario]):
    def __init__(self, mqtt: mqtt_client.Client, id: int) -> None:
        super().__init__()
        self.usuarios: set[Usuario] = set()
        self.mqtt = mqtt
        self.syncMQTT = SyncMQTT(self, self.mqtt, id)

    def getTopico(self) -> str:
        return "cad_server/usuario"
    
    def parseT(self, string: str) -> Usuario:
        payload = json.loads(string)
        return Usuario(cadastro_pb2.Usuario(cpf=payload['cpf'], nome=payload['nome']), payload['bloqueado'])
    
    def pub(self, msg: Usuario, operacao: str, topico: str):
        """Publicar uma operação de usuário no broker MQTT"""
        payload = json.dumps({
            'remetente': self.syncMQTT.id,
            'cpf': msg.usuario_pb2.cpf,
            'nome': msg.usuario_pb2.nome,
            'bloqueado': msg.bloqueado
        })
        self.mqtt.publish(topico + "/" + operacao, payload)

    def criar(self, request: str, propagate: bool) -> cadastro_pb2.Status:
        payload = json.loads(request)
        user = Usuario(cadastro_pb2.Usuario(cpf=payload['cpf'], nome=payload['nome']))
        if not user.isValido():
            return cadastro_pb2.Status(status=1, msg="Usuário inválido")
        if user in self.usuarios:
            return cadastro_pb2.Status(status=1, msg="Usuário já existe")

        if propagate:    
            self.pub(user, CRUD.criar, self.getTopico())
        self.usuarios.add(user)
        return cadastro_pb2.Status(status=0)
    
    def atualizar(self, request: Usuario, propagate: bool) -> cadastro_pb2.Status:
        usuarioExistente: Usuario | None = None
        for u in self.usuarios:
            if u == request:
                usuarioExistente = u
                break

        if usuarioExistente != None:
            if propagate:
                self.pub(request, CRUD.atualizar, self.getTopico())

            self.usuarios.remove(usuarioExistente)
            self.usuarios.add(request)
            return cadastro_pb2.Status(status=0)
        else:
            return cadastro_pb2.Status(status=1, msg="Usuário não encontrado.")
    
    def deletar(self, request: cadastro_pb2.Identificador, propagate: bool) -> cadastro_pb2.Status:
        usuario: Usuario | None = None
        for u in self.usuarios:
            if u.usuario_pb2.cpf == request.id:
                usuario = u
                break

        if usuario != None:
            if propagate:
                self.pub(usuario, CRUD.deletar, self.getTopico())

            self.usuarios.remove(usuario)
            return cadastro_pb2.Status(status=0)
        else:
            return cadastro_pb2.Status(status=1, msg="Usuário não encontrado.")

    def ObtemUsuario(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Usuario:
        for usuario in self.usuarios:
            if usuario.usuario_pb2.cpf == request.id:
                return usuario.usuario_pb2
            
        return cadastro_pb2.Usuario()
    
    def ObtemTodosUsuarios(self, request: cadastro_pb2.Vazia, context):
        for usuario in self.usuarios:
            yield usuario.usuario_pb2

    #################################

    def getTodos(self) -> set[Usuario]:
        return self.usuarios

    def deletarTodos(self) -> None:
        self.usuarios = set()
from abc import abstractmethod
import json
import threading

from paho.mqtt import client as mqtt_client

from biblioteca.cad.Usuario import Usuario
from biblioteca.gRPC import cadastro_pb2
from biblioteca import lib
from biblioteca.lib import CRUD

class SyncMQTTOps():
    @abstractmethod
    def criar(self, request: str, propagate: bool) -> cadastro_pb2.Status:
        pass
   
    @abstractmethod
    def atualizarUsuario(self, request: Usuario, propagate: bool) -> cadastro_pb2.Status:
        pass
    
    @abstractmethod
    def deletarUsuario(self, request: cadastro_pb2.Identificador, propagate: bool) -> cadastro_pb2.Status:
        pass

    @abstractmethod
    def deletarTodosUsuarios(self) -> None:
        pass

    @abstractmethod
    def getTodosUsuarios(self) -> set[Usuario]:
        pass

    @abstractmethod
    def getTopico(self) -> str:
        pass

    @abstractmethod
    def pub(self, msg: Usuario, operacao: str, topico: str):
        pass

class SyncMQTT():
    """Funções que garantem que o estado dos diversos servidores esteja coerente"""
    def __init__(self, porta: int, portalCadastroServicer: SyncMQTTOps, mqtt: mqtt_client.Client) -> None:
        self.porta = porta
        self.portalCadastroServicer = portalCadastroServicer
        self.mqtt = mqtt
        self.mqtt.subscribe("cad_server/#")
        self.espelho = ""
        self.atualizado = False
        self.mqtt.publish(self.portalCadastroServicer.getTopico() + "/sync", f'{self.porta}')

        """Se ninguém se oferecer para ser a base de dados após 3s,
          assume-se que ninguém tem dados ainda e não há necessidade de sincronização """
        def timeout():
            if self.espelho == "":
                self.atualizado = True
                print("Sincronização concluída, nada para sincronizar")
        threading.Timer(3, timeout).start()

        @self.mqtt.topic_callback(self.portalCadastroServicer.getTopico() + "/sync/" + str(self.porta) + "/ack")
        def _(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            """Escolher um espelho com o qual irá se sincronizar"""
            if msg.payload.decode() == "fim":
                self.atualizado = True
                print("Sincronização concluída")
                return
            if self.espelho != "":
                return
            
            self.espelho = msg.payload.decode()
            self.portalCadastroServicer.deletarTodosUsuarios()
            self.mqtt.publish(self.portalCadastroServicer.getTopico() + "/sync/" + str(self.porta) + "/ack", "ack " + self.espelho)

        @self.mqtt.topic_callback(self.portalCadastroServicer.getTopico() + "/" + CRUD.criar)
        def criarUsuarioCallback(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            req = msg.payload.decode()
            payload = json.loads(req)
            if payload['remetente'] == self.porta:
                return
            
            self.portalCadastroServicer.criar(req, False)

        @self.mqtt.topic_callback(self.portalCadastroServicer.getTopico() + "/sync/" + str(self.porta))
        def _(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            """Sincronizando usuários..."""
            criarUsuarioCallback(client, userdata, msg)

        @self.mqtt.topic_callback(self.portalCadastroServicer.getTopico() + "/sync")
        def _(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            """Me oferecer como espelho caso eu esteja atualizado"""
            if not self.atualizado:
                return
            
            portaRequisitante = msg.payload.decode()
            if portaRequisitante == str(self.porta):
                return
            
            mqtt.publish(self.portalCadastroServicer.getTopico() + "/sync/" + portaRequisitante + "/ack", str(self.porta))

            def callback(client: mqtt_client.Client, userdata, msgC: mqtt_client.MQTTMessage):
                if msgC.payload.decode() == "ack " + str(self.porta):
                    usuarios = self.portalCadastroServicer.getTodosUsuarios()
                    for usuario in usuarios:
                        self.portalCadastroServicer.pub(usuario, portaRequisitante, self.portalCadastroServicer.getTopico() + "/sync/")
                    
                    self.mqtt.publish(self.portalCadastroServicer.getTopico() + "/sync/" + portaRequisitante + "/ack", "fim")
                    
            mqtt.message_callback_add(self.portalCadastroServicer.getTopico() + "/sync/" + portaRequisitante + "/ack", callback)

        @self.mqtt.topic_callback(self.portalCadastroServicer.getTopico() + "/" + CRUD.atualizar)
        def _(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            payload = json.loads(msg.payload.decode())
            if payload['remetente'] == self.porta:
                return
            
            user = Usuario(cadastro_pb2.Usuario(cpf=payload['cpf'], nome=payload['nome']), payload['bloqueado'])
            self.portalCadastroServicer.atualizarUsuario(user, False)

        @self.mqtt.topic_callback(self.portalCadastroServicer.getTopico() + "/" + CRUD.deletar)
        def _(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            payload = json.loads(msg.payload.decode())
            if payload['remetente'] == self.porta:
                return
            
            self.portalCadastroServicer.deletarUsuario(cadastro_pb2.Identificador(id=payload['cpf']), False)

        self.mqtt.loop_start()
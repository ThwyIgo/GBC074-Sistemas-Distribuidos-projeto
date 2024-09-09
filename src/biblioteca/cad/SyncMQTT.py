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
    def criarUsuario(self, request: cadastro_pb2.Usuario, propagate: bool) -> cadastro_pb2.Status:
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

class SyncMQTT():
    """Funções que garantem que o estado dos diversos servidores esteja coerente"""
    def pubUsuario(self, msg: Usuario, operacao: str, topico: str = "cad_server/usuario/"):
        """Publicar uma operação de usuário no broker MQTT"""
        payload = json.dumps({
            'remetente': self.porta,
            'cpf': msg.usuario_pb2.cpf,
            'nome': msg.usuario_pb2.nome,
            'bloqueado': msg.bloqueado
        })
        self.mqtt.publish(topico + operacao, payload)

    def __init__(self, porta: int, portalCadastroServicer: SyncMQTTOps, mqtt: mqtt_client.Client) -> None:
        self.porta = porta
        self.portalCadastroServicer = portalCadastroServicer
        self.mqtt = mqtt
        self.mqtt.subscribe("cad_server/#")
        self.espelho = ""
        self.atualizado = False
        self.mqtt.publish("cad_server/usuario/sync", f'{self.porta}')

        """Se ninguém se oferecer para ser a base de dados após 3s,
          assume-se que ninguém tem dados ainda e não há necessidade de sincronização """
        def timeout():
            if self.espelho == "":
                self.atualizado = True
                print("Sincronização concluída, nada para sincronizar")
        threading.Timer(3, timeout).start()

        @self.mqtt.topic_callback("cad_server/usuario/sync/" + str(self.porta) + "/ack")
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
            self.mqtt.publish("cad_server/usuario/sync/" + str(self.porta) + "/ack", "ack " + self.espelho)

        @self.mqtt.topic_callback("cad_server/usuario/"+CRUD.criar)
        def criarUsuarioCallback(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            payload = json.loads(msg.payload.decode())
            if payload['remetente'] == self.porta:
                return
            
            user = cadastro_pb2.Usuario(cpf=payload['cpf'], nome=payload['nome'])
            self.portalCadastroServicer.criarUsuario(user, False)

        @self.mqtt.topic_callback("cad_server/usuario/sync/" + str(self.porta))
        def _(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            """Sincronizando usuários..."""
            criarUsuarioCallback(client, userdata, msg)

        @self.mqtt.topic_callback("cad_server/usuario/sync")
        def _(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            """Me oferecer como espelho caso eu esteja atualizado"""
            if not self.atualizado:
                return
            
            portaRequisitante = msg.payload.decode()
            if portaRequisitante == str(self.porta):
                return
            
            mqtt.publish("cad_server/usuario/sync/" + portaRequisitante + "/ack", str(self.porta))

            def callback(client: mqtt_client.Client, userdata, msgC: mqtt_client.MQTTMessage):
                if msgC.payload.decode() == "ack " + str(self.porta):
                    usuarios = self.portalCadastroServicer.getTodosUsuarios()
                    for usuario in usuarios:
                        self.pubUsuario(usuario, portaRequisitante, "cad_server/usuario/sync/")
                    
                    self.mqtt.publish("cad_server/usuario/sync/" + portaRequisitante + "/ack", "fim")
                    
            mqtt.message_callback_add("cad_server/usuario/sync/" + portaRequisitante + "/ack", callback)

        @self.mqtt.topic_callback("cad_server/usuario/"+CRUD.atualizar)
        def _(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            payload = json.loads(msg.payload.decode())
            if payload['remetente'] == self.porta:
                return
            
            user = Usuario(cadastro_pb2.Usuario(cpf=payload['cpf'], nome=payload['nome']), payload['bloqueado'])
            self.portalCadastroServicer.atualizarUsuario(user, False)

        @self.mqtt.topic_callback("cad_server/usuario/"+CRUD.deletar)
        def _(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            payload = json.loads(msg.payload.decode())
            if payload['remetente'] == self.porta:
                return
            
            self.portalCadastroServicer.deletarUsuario(cadastro_pb2.Identificador(id=payload['cpf']), False)

        self.mqtt.loop_start()
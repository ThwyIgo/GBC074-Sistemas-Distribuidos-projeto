from abc import abstractmethod
import json
import threading
from typing import TypeVar, Generic

from paho.mqtt import client as mqtt_client

from biblioteca.gRPC import cadastro_pb2
from biblioteca.lib import CRUD

T = TypeVar('T')
class SyncMQTTOps(Generic[T]):
    @abstractmethod
    def criar(self, request: str, propagate: bool) -> cadastro_pb2.Status:
        pass
   
    @abstractmethod
    def atualizar(self, request: T, propagate: bool) -> cadastro_pb2.Status:
        pass
    
    @abstractmethod
    def deletar(self, request: cadastro_pb2.Identificador, propagate: bool) -> cadastro_pb2.Status:
        pass

    @abstractmethod
    def deletarTodos(self) -> None:
        pass

    @abstractmethod
    def getTodos(self) -> set[T]:
        pass

    @abstractmethod
    def getTopico(self) -> str:
        pass

    @abstractmethod
    def pub(self, msg: T, operacao: str, topico: str):
        pass

    @abstractmethod
    def parseT(self, string: str) -> T:
        pass

class SyncMQTT():
    """Funções que garantem que o estado dos diversos servidores esteja coerente"""
    def __init__(self, servicer: SyncMQTTOps, mqtt: mqtt_client.Client, id: int) -> None:
        self.id = id
        self.servicer = servicer
        self.mqtt = mqtt
        self.mqtt.subscribe("cad_server/#")
        self.espelho = ""
        self.atualizado = False
        self.mqtt.publish(self.servicer.getTopico() + "/sync", f'{self.id}')

        """Se ninguém se oferecer para ser a base de dados após 3s,
          assume-se que ninguém tem dados ainda e não há necessidade de sincronização """
        def timeout():
            if self.espelho == "":
                self.atualizado = True
                print("Sincronização concluída, nada para sincronizar")
        threading.Timer(3, timeout).start()

        @self.mqtt.topic_callback(self.servicer.getTopico() + "/sync/" + str(self.id) + "/ack")
        def _(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            """Escolher um espelho com o qual irá se sincronizar"""
            if msg.payload.decode() == "fim":
                self.atualizado = True
                print("Sincronização concluída")
                return
            if self.espelho != "":
                return
            
            self.espelho = msg.payload.decode()
            self.servicer.deletarTodos()
            self.mqtt.publish(self.servicer.getTopico() + "/sync/" + str(self.id) + "/ack", "ack " + self.espelho)

        @self.mqtt.topic_callback(self.servicer.getTopico() + "/" + CRUD.criar)
        def criarCallback(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            req = msg.payload.decode()
            payload = json.loads(req)
            if payload['remetente'] == self.id:
                return
            
            self.servicer.criar(req, False)

        @self.mqtt.topic_callback(self.servicer.getTopico() + "/sync/" + str(self.id))
        def _(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            """Sincronizando usuários..."""
            criarCallback(client, userdata, msg)

        @self.mqtt.topic_callback(self.servicer.getTopico() + "/sync")
        def _(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            """Me oferecer como espelho caso eu esteja atualizado"""
            if not self.atualizado:
                return
            
            portaRequisitante = msg.payload.decode()
            if portaRequisitante == str(self.id):
                return
            
            mqtt.publish(self.servicer.getTopico() + "/sync/" + portaRequisitante + "/ack", str(self.id))

            def callback(client: mqtt_client.Client, userdata, msgC: mqtt_client.MQTTMessage):
                if msgC.payload.decode() == "ack " + str(self.id):
                    data = self.servicer.getTodos()
                    for d in data:
                        self.servicer.pub(d, portaRequisitante, self.servicer.getTopico() + "/sync")
                    
                    self.mqtt.publish(self.servicer.getTopico() + "/sync/" + portaRequisitante + "/ack", "fim")
                    
            mqtt.message_callback_add(self.servicer.getTopico() + "/sync/" + portaRequisitante + "/ack", callback)

        @self.mqtt.topic_callback(self.servicer.getTopico() + "/" + CRUD.atualizar)
        def _(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            payload = json.loads(msg.payload.decode())
            if payload['remetente'] == self.id:
                return
            
            user = self.servicer.parseT(msg.payload.decode())
            self.servicer.atualizar(user, False)

        @self.mqtt.topic_callback(self.servicer.getTopico() + "/" + CRUD.deletar)
        def _(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            payload = json.loads(msg.payload.decode())
            if payload['remetente'] == self.id:
                return
            
            self.servicer.deletar(cadastro_pb2.Identificador(id=payload['cpf']), False)

        self.mqtt.loop_start()
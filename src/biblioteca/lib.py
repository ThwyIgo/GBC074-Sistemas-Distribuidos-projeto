from paho.mqtt import client as mqtt_client

class CRUD():
    criar = 'criar'
    ler = 'ler'
    atualizar = 'atualizar'
    deletar = 'deletar'

def connect_mqtt(prefixo_id: str, id: int) -> mqtt_client.Client:
    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client_id = f'{prefixo_id}-{id}'
    client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.connect("localhost")
    return client
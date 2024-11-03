from collections.abc import Iterable
from biblioteca.gRPC import database_pb2_grpc, database_pb2
from biblioteca.leveldb.LevelDB import LevelDB

class DatabaseServicer(database_pb2_grpc.DatabaseServicer):
    def __init__(self, selfPorta: int, otherPortas: Iterable[int]) -> None:
        super().__init__()
        self.db = LevelDB(f'/tmp/db/{selfPorta}', f'localhost:{selfPorta}', map(lambda a: f'localhost:{a}', otherPortas))

    def put(self, request: database_pb2.String2, context) -> None:
        return self.db.put(request.fst, request.snd)
    
    def get(self, request: database_pb2.String, context) -> database_pb2.MaybeString:
        res = self.db.get(request.value)
        if res == None:
            return database_pb2.MaybeString(status=1)
        else:
            return database_pb2.MaybeString(value=res, status=0)
        
    def deletar(self, request: database_pb2.String, context):
        return self.db.delete(request.value)
    
    def getPrefix(self, request: database_pb2.String, context):
        for s in self.db.getPrefix(request.value):
            yield database_pb2.String(value=s)
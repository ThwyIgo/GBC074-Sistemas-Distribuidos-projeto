import json
from collections.abc import Iterable
from types import SimpleNamespace
import plyvel
from pysyncobj import SyncObj, replicated_sync

class LevelDB(SyncObj):
    def __init__(self, dir: str, selfAddr: str, otherAddrs: Iterable[str]) -> None:
        super().__init__(selfAddr, otherAddrs)
        self.db = plyvel.DB(dir, create_if_missing=True)

    @replicated_sync
    def put(self, key: str, val: object) -> None:
        self.db.put(key.encode(), json.dumps(val).encode())

    def get(self, key: str) -> object | None:
        got: bytes | None = self.db.get(key.encode())
        if got == None:
            return None
        
        return json.loads(got.decode(), object_hook=lambda d: SimpleNamespace(**d))
    
    @replicated_sync
    def delete(self, key: str) -> None:
        return self.db.delete(key.encode())
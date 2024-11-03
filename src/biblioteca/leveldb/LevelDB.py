from collections.abc import Iterable
from pathlib import Path
import plyvel
from pysyncobj import SyncObj, replicated_sync
import atexit

class LevelDB(SyncObj):
    def __init__(self, dir: str, selfAddr: str, otherAddrs: Iterable[str]) -> None:
        super().__init__(selfAddr, otherAddrs)
        Path(dir).mkdir(parents=True, exist_ok=True)
        self.db = plyvel.DB(dir, create_if_missing=True)
        atexit.register(self.db.close)

    @replicated_sync
    def put(self, key: str, val: str) -> None:
        self.db.put(key.encode(), val.encode())

    def get(self, key: str) -> str | None:
        got: bytes | None = self.db.get(key.encode())
        if got == None:
            return None
        
        return got.decode()
    
    @replicated_sync
    def delete(self, key: str) -> None:
        self.db.delete(key.encode())
    
    def getPrefix(self, prefix: str) -> list[str]:
        res: list[str] = list()

        for key, value in self.db:
            keyS: str = key.decode()
            if key.startswith(prefix.encode()):
                res.append(value.decode())

        return res
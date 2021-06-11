from pathlib import Path
import yaml


class ServerConfig:
    def __init__(self,
                 host: str,
                 port: int,
                 client_max_size: int,
                 openapi: str):
        self._host = host
        self._port = port
        self._client_max_size = client_max_size
        self._openapi = openapi

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def client_max_size(self) -> int:
        return self._client_max_size

    @property
    def openapi(self) -> str:
        return self._openapi

    @staticmethod
    def load(path: Path):
        with path.open(encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            return ServerConfig(**config)


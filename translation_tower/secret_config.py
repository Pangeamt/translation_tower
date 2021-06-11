from pathlib import Path
import yaml


class SecretConfig:
    def __init__(self, bing_apikey: str, deepl_apikey: str):
        self._bing_apikey = bing_apikey
        self._deepl_apikey = deepl_apikey

    @property
    def bing_apikey(self) -> str:
        return self._bing_apikey

    @property
    def deepl_apikey(self) -> str:
        return self._deepl_apikey

    @staticmethod
    def load(path: Path):
        with path.open(encoding="utf-8") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            return SecretConfig(**config)

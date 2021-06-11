from pathlib import Path
import yaml


class TranslationCacheConfig:
    def __init__(self,
                 path: str,
                 size_limit: int):
        self._path = path
        self._size_limit = size_limit

    @property
    def path(self) -> str:
        return self._path

    @property
    def size_limit(self) -> int:
        return self._size_limit

    @staticmethod
    def load(path: Path):
        with path.open(encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            return TranslationCacheConfig(**config)


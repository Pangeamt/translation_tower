from pathlib import Path
import yaml


class TranslationAppConfig:
    def __init__(
        self,
        bing_limit_concurrent_request: int,
        bing_limit_texts_per_request: int,
        bing_limit_chars_per_request: int,
        bing_limit_chars_per_text: int,
        deepl_limit_concurrent_request: int,
        deepl_limit_texts_per_request: int,
        deepl_limit_chars_per_request: int,
        deepl_limit_chars_per_text: int,
    ):
        self._bing_limit_concurrent_request = bing_limit_concurrent_request
        self._bing_limit_texts_per_request = bing_limit_texts_per_request
        self._bing_limit_chars_per_request = bing_limit_chars_per_request
        self._bing_limit_chars_per_text = bing_limit_chars_per_text
        self._deepl_limit_concurrent_request = deepl_limit_concurrent_request
        self._deepl_limit_texts_per_request = deepl_limit_texts_per_request
        self._deepl_limit_chars_per_request = deepl_limit_chars_per_request
        self._deepl_limit_chars_per_text = deepl_limit_chars_per_text

    @property
    def bing_limit_concurrent_request(self) -> int:
        return self._bing_limit_concurrent_request

    @property
    def bing_limit_texts_per_request(self) -> int:
        return self._bing_limit_texts_per_request

    @property
    def bing_limit_chars_per_request(self) -> int:
        return self._bing_limit_chars_per_request

    @property
    def bing_limit_chars_per_text(self) -> int:
        return self._bing_limit_chars_per_text

    @property
    def deepl_limit_concurrent_request(self) -> int:
        return self._deepl_limit_concurrent_request

    @property
    def deepl_limit_texts_per_request(self) -> int:
        return self._deepl_limit_texts_per_request

    @property
    def deepl_limit_chars_per_request(self) -> int:
        return self._deepl_limit_chars_per_request

    @property
    def deepl_limit_chars_per_text(self) -> int:
        return self._deepl_limit_chars_per_text

    @staticmethod
    def load(path: Path):
        with path.open(encoding="utf-8") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            return TranslationAppConfig(**config)

from diskcache import Cache
from translation_tower.translation_cache_config import TranslationCacheConfig
from typing import NamedTuple
from hashlib import blake2b
from translation_tower.logger import logger
from translation_tower.format_traceback import format_traceback
from translation_tower.translator import Translator, translator_to_string


class CachedTranslation(NamedTuple):
    text: str
    translation: str
    source_language: str
    target_language: str
    translator_name: str
    translator_html_mode: bool
    translator_fake_mode: bool


class TranslationCache:
    def __init__(self, config: TranslationCacheConfig):
        self._config = config
        self._cache = Cache(self._config.path, size_limit=self._config.size_limit)

    @staticmethod
    def key(
        text, source_language: str, target_language: str, translator: Translator
    ) -> str:
        h = blake2b()
        h.update(bytes(text, encoding="utf-8"))
        h.update(bytes(source_language, encoding="utf-8"))
        h.update(bytes(target_language, encoding="utf-8"))
        h.update(bytes(translator_to_string(translator), encoding="utf-8"))
        return h.hexdigest()

    def get(
        self, text, source_language: str, target_language: str, translator: Translator
    ):
        try:
            key = self.key(text, source_language, target_language, translator)
            if key not in self._cache:
                return None
            else:
                return self._cache.get(key)

        except Exception as e:
            logger.error(format_traceback(e))
            return None

    def set(
        self,
        text,
        translation,
        source_language: str,
        target_language: str,
        translator: Translator,
    ):
        try:
            key = self.key(
                text,
                source_language,
                target_language,
                translator,
            )
            self._cache.set(
                key,
                CachedTranslation(
                    text=text,
                    translation=translation,
                    source_language=source_language,
                    target_language=target_language,
                    translator_name=translator.name,
                    translator_html_mode=translator.html_mode,
                    translator_fake_mode=translator.fake_mode,
                ),
            )

        except Exception as e:
            logger.error(format_traceback(e))

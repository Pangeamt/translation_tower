from asyncio import Event
from typing import Optional
from translation_tower.translator import Translator
from translation_tower.deep_text import DeepText
from dataclasses import dataclass, field


@dataclass()
class TranslationJob:
    request_id: str

    # index of the job in the request
    index: int

    # Source
    source: DeepText = field(default_factory=DeepText)

    # Target
    target: DeepText = field(default_factory=DeepText)

    # Translator
    translator: Translator = field(default_factory=Translator)

    # Text send to the translate
    to_translator: str = None

    # Text received from the translate
    from_translator: str = None

    # Use cache
    use_cache = False

    # If the translation comes from cache
    from_cache = False

    # Metadata to rebuild translated annotations
    annotation_rebuild = None

    # Event to notify that the job translation has completed
    done: Optional[Event] = None

    error: bool = False
    error_message: str = ""

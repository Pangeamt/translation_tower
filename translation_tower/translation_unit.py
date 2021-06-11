from typing import Tuple, Dict, Set, Optional
from translation_tower.deep_text import DeepText
from dataclasses import dataclass, field


@dataclass()
class Translator:
    name: str = ""
    use_html_mode: bool = False


@dataclass()
class TranslationUnit:
    source: DeepText = field(default_factory=DeepText)
    target: DeepText = field(default_factory=DeepText)
    translator: str = field(default_factory=Translator)
    annotations_rebuild: Optional[Tuple[Dict[str, Set[int]], Dict[int, str]]] = None

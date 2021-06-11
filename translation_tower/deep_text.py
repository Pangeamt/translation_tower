from typing import List, Optional
from dataclasses import dataclass
from translation_tower.annotation import Annotation


@dataclass()
class DeepText:
    text: Optional[str] = None
    language: Optional[str] = None
    annotations: Optional[List[Annotation]] = None


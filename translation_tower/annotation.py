from typing import NamedTuple, Dict, Optional


class Annotation(NamedTuple):
    label: str
    start: int
    stop: int
    origin: Optional[int] = None


def annotation_to_dict(a: Annotation) -> Dict:
    d = dict(
        label=a.label,
        start=a.start,
        stop=a.stop,
    )
    if a.origin is not None:
        d['origin'] = a.origin
    return d


def annotation_from_dict(d: dict) -> Annotation:
    return Annotation(
        label=d["label"],
        start=d["start"],
        stop=d["stop"]
    )

from dataclasses import dataclass


@dataclass()
class Translator:
    name: str = ""
    html_mode: bool = False
    fake_mode: bool = False


def translator_to_string(translator: Translator) -> str:
    html = f" html" if translator.html_mode else ""
    fake = f" fake" if translator.fake_mode else ""
    return f"{translator.name}{html}{fake}"

from typing import List, Tuple
from cassis import Cas, TypeSystem
from dkpro_cassis_tools import TOKEN_NS, SENTENCE_NS, NAMED_ENTITY_NS
from translation_tower.deep_text import DeepText
from translation_tower.annotation import Annotation


def deep_texts_to_cas(
    deep_texts: List[DeepText],
    type_system: TypeSystem,
) -> Cas:

    cas = Cas(typesystem=type_system)

    current_start = 0
    starts = []
    sofa_string = ""

    # Create sofa string
    for annotated_text in deep_texts:
        starts.append(current_start)
        text = annotated_text.text
        if not text.endswith("\n"):
            text += "\n"
        sofa_string += text
        current_start += len(text)

    cas.sofa_string = sofa_string

    # # Tokens
    # for annotated_text, start in zip(annotated_texts, starts):
    #     for token in annotated_text.tokens:
    #         annotation = cas.typesystem.get_type(TOKEN_NS)(
    #             begin=start + token.start,
    #             end=start + token.stop)
    #         cas.add_annotation(annotation)

    # Sentences
    for annotated_text, start in zip(deep_texts, starts):
        annotation = cas.typesystem.get_type(SENTENCE_NS)(
            begin=start, end=start + len(annotated_text.text)
        )
        cas.add_annotation(annotation)

    # Annotations
    for annotated_text, start in zip(deep_texts, starts):
        for annotation in annotated_text.annotations:
            annotation = cas.typesystem.get_type(NAMED_ENTITY_NS)(
                value=annotation.label,
                begin=start + annotation.start,
                end=start + annotation.stop,
            )
            cas.add_annotation(annotation)

    return cas


def cas_to_deep_texts(cas: Cas) -> List[DeepText]:
    deep_texts = list()

    for i, sentence in enumerate(cas.select(SENTENCE_NS)):
        # Text
        text = sentence.get_covered_text()

        # Annotations
        annotations = list()
        for a in cas.select_covered(NAMED_ENTITY_NS, sentence):
            annotations.append(Annotation(
                label=a.value,
                start=a.begin - sentence.begin,
                stop=a.end - sentence.begin

            ))
        deep_text = DeepText()
        deep_text.text = text
        deep_text.annotations = annotations
        deep_texts.append(deep_text)
    return deep_texts


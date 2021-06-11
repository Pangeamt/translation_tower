from typing import List, Tuple, Dict
from itertools import groupby
from typing import Optional, Set
from lxml import etree
from lxml.html import html5parser
from itertools import chain
import functools
import operator
from translation_tower.annotation import Annotation


def annotated_text_to_html(
    text: str,
    annotations: List[Annotation],
) -> Tuple[str, Tuple[Dict[str, Set[int]], Dict[int, str]]]:
    """
    :param text:
    :param annotations:
    :return: (xml, rebuild)
    """
    #  For each char of the text, get the set of annotations that the char belong to
    chars: List[
        Tuple[int, str, Optional[Set[int]]]
    ] = list()  # (char index, char, set of annotations (a set of annotations ids))
    for i, c in enumerate(text):
        if not c.isspace():
            annotations_set = set()
            for annotation_id, annotation in enumerate(annotations):
                if annotation.start <= i < annotation.stop:
                    annotations_set.add(annotation_id)
            if annotations_set:
                chars.append((i, c, annotations_set))
            else:
                chars.append((i, c, None))
        else:
            chars.append((i, c, None))

    tag_id = 0
    root = etree.Element("p")
    tag_id_to_annotations_set = dict()

    #  Group the consecutive chars that share a same set of annotations
    for set_of_annotations, chars in groupby(chars, key=lambda ch: ch[2]):
        chars = list(chars)
        text_part = text[chars[0][0] : chars[-1][0] + 1]
        if set_of_annotations:
            # Create a child element
            tag = etree.Element("b")
            tag.set("id", str(tag_id))
            tag.text = text_part
            root.append(tag)

            # Save relation between tag id and annotations
            tag_id_to_annotations_set[str(tag_id)] = set_of_annotations

            tag_id += 1
        else:
            # Create text node
            if len(root):
                root[-1].tail = text_part
            else:
                root.text = text_part

    # Annotation id to label
    annotation_id_to_label = dict(
        [(i, annotation.label) for i, annotation in enumerate(annotations)]
    )

    return (
        str(etree.tostring(root, encoding="unicode")),
        (
            tag_id_to_annotations_set,
            annotation_id_to_label,
        ),
    )


def html_to_annotated_text(
    html: str, rebuild: Tuple[Dict[str, Set[int]], Dict[int, str]]
) -> Tuple[str, List[Annotation]]:
    # Create useful objects to rebuild annotations
    element_id_to_annotation_set, annotation_id_to_label = rebuild

    chars = list()
    char_index = 0
    all_annotations_ids = set()

    root = html5parser.fragment_fromstring(html, create_parent=True)
    for element in root.iter():
        for text, is_text in [(element.text, True), (element.tail, False)]:
            if text:
                element_ids = _get_ancestors_ids(element, include_element=is_text)
                annotations_ids = set()
                for element_id in element_ids:
                    if element_id in element_id_to_annotation_set:
                        annotations_ids = annotations_ids.union(
                            element_id_to_annotation_set[element_id]
                        )
                all_annotations_ids = all_annotations_ids.union(annotations_ids)
                for char in text:
                    if char.isspace():
                        chars.append((char_index, char, set()))
                    else:
                        chars.append((char_index, char, annotations_ids))
                    char_index += 1

    # Extract text
    text = functools.reduce(operator.add, map(lambda c: c[1], chars))

    # Extract annotations
    annotations = list()
    non_space_chars = list(filter(lambda c: not c[1].isspace(), chars))

    for index in all_annotations_ids:
        for is_char_involved_in_annotation, chars in groupby(
            non_space_chars, key=lambda c: True if index in c[2] else False
        ):
            if is_char_involved_in_annotation:
                chars = list(chars)
                annotations.append(
                    Annotation(
                        label=annotation_id_to_label[index],
                        start=chars[0][0],
                        stop=chars[-1][0] + 1,
                        origin=index,
                    )
                )

    return text, annotations


def _get_ancestors_ids(element, include_element: bool = False) -> Set[str]:
    ids = set()
    for ancestor in chain(
        [element] if include_element else list(), element.iterancestors()
    ):
        id_ = ancestor.get("id")
        if id_ is not None:
            ids.add(id_)
    return ids

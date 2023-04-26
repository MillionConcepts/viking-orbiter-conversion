"""functions implementing our XML template markup processing."""
import re
from operator import contains
from typing import (
    Sequence,
    Collection,
    Optional,
    TypeVar,
    Callable,
    Mapping,
    Any,
    Union,
)


def _check_deletion(
    line: str, delete_tag: Optional[str], targets: Collection[str]
) -> [bool, Optional[str]]:
    # always delete template comments.
    if "<!--" in line:
        return False, delete_tag

    # we are not in deletion mode.
    if delete_tag is None:
        # case 1: encountered an unmatched stop command. delete it and move on.
        if "{stop:" in line:
            return False, delete_tag
        # case 2: encountered a deletion start tag. check if we should turn
        # deletion mode on (and always delete the deletion command itself)
        if "{delete:" in line:
            delete_tag = re.search(r"{delete:(\w.*?)}", line).group(1)
            if not any((contains(target, delete_tag) for target in targets)):
                delete_tag = None
            return False, delete_tag
        # case 3: it's just a regular line. write it.
        return True, delete_tag

    # we are in deletion mode.
    # case 1: did not encounter stop tag. continue deleting.
    if "{stop" not in line:
        return False, delete_tag
    # case 2: encountered stop tag. if it matches opening deletion tag,
    # turn off deletion mode. always delete the stop command itself.
    if delete_tag == re.search(r"{stop:(\w.*?)}", line).group(1):
        return False, None
    return False, delete_tag


def process_deletions(
    lines: Sequence[str], targets: Collection[str]
) -> list[str]:
    output_lines, delete_tag = [], None
    for line in lines:
        write_line, delete_tag = _check_deletion(line, delete_tag, targets)
        if write_line:
            output_lines.append(line)
    return output_lines


TemplateParameter = TypeVar(
    "TemplateParameter",
    str,
    tuple[str, Union[str, int]],
    tuple[str, Callable[[Any], str]],
    tuple[str, Callable[[Any], str], Union[str, int]],
)


def prep_tagdict(tagdict: Mapping[str, TemplateParameter]):
    """
    format a human-written tag dictionary for label conversion.
    legal signatures for values of dictionary:
        key: str -> metaget(key)
        (key: str, func: Callable) -> func(metaget(key))
        (key: str, subkey: Union[str, int])
            -> metaget(key)][subkey] (for quantities etc.)
        (key: str, func: Callable, subkey: Union[str, int)
            -> func(metaget(key)[subkey])
    """
    prepped = {}
    for tag, parameter in tagdict.items():
        if isinstance(parameter, str):
            prepped[tag] = (parameter, None, None)
        elif len(parameter) == 3:
            prepped[tag] = parameter
        elif isinstance(parameter[1], Callable):
            prepped[tag] = (parameter[0], parameter[1], None)
        else:
            prepped[tag] = (parameter[0], None, parameter[1])
    return prepped


def xmlwrap(element_name, **element_attributes):
    """
    designed for cases in which the parameters present in a source label are
    widely variable even within a single 'product type' and so variability
    cannot be cleanly handled with deletion tags.
    """
    attribute_string = ""
    if len(element_attributes) > 0:
        attribute_string += " "
        attribute_string += " ".join(
            [f"{attr}={value}" for attr, value in element_attributes.items()]
        )
    opening = f"<{element_name}{attribute_string}>"
    closing = f"</{element_name}>"

    def wrap_in_xml(content):
        return f"{opening}{content}{closing}"

    return wrap_in_xml


def skipna(func):
    """skip not-found or N/A values"""
    def skipper(content, *args, **kwargs):
        if content in ("N/A", None):
            return ""
        return func(content, *args, **kwargs)

    return skipper

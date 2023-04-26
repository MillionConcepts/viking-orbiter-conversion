import os
import re
from pathlib import Path
from typing import (
    Any,
    Collection,
    Callable,
    Mapping,
    MutableMapping,
    Optional,
    Union,
    MutableSequence,
)
import xml.dom.minidom

from cytoolz import merge, keyfilter
from pdr import Data, Metadata

from templating import prep_tagdict, process_deletions


class PDSVersionConverter:
    """
    base class for implementing PDS3 -> PDS4 conversion processes. wraps a
    pdr.Data object and associates it with data and metadata conversion rules.
    should in general be subclassed for specific product types, although it is
    viable to attach rules directly to the base class.
    """
    def __init__(
        self,
        filename: Union[str, Path, None] = None,
        skip_load=False,
        **pdr_kwargs,
    ):
        # note: must always be pointed at the label file.
        if (skip_load is False) and (filename is not None):
            self.data = Data(
                filename,
                label_fn=filename,
                skip_existence_check=True,
                **pdr_kwargs,
            )
            self.metadata = self.data.metadata
            self.output_stem = Path(filename).stem.lower()
        for mapping_attr in (
            "processors",
            "analyzers",
            "output_paths",
            "object_cache",
        ):
            if getattr(self, mapping_attr) is None:
                setattr(self, mapping_attr, {})
        for collection_attr in ("parameter_dicts", "deletion_targets"):
            if getattr(self, collection_attr) is None:
                setattr(self, collection_attr, [])

    @classmethod
    def from_converter(cls, input_converter):
        converter = super().__new__(cls)
        for attr in (
            "data",
            "metadata",
            "associations",
            "object_cache",
            "deletion_targets",
            "output_stem",
            "output_paths"
        ):
            setattr(converter, attr, getattr(input_converter, attr))
        return converter

    def _metaget_template_value(
        self,
        key: str,
        formatter: Optional[Callable[[Any], str]],
        subkey: Optional[str],
    ):
        """
        use pdr.Metadata to select a label parameter to populate a template,
        applying any inline formatting or selection specified in a template tag
        dictionary parameter.
        """
        element = self.metadata.metaget(key)
        if subkey is not None:
            element = element[subkey]
        if formatter is not None:
            element = formatter(element)
        return element

    def convert_label(self, pprint_xml=True):
        self._make_associations()
        with open(self.template) as stream:
            template = stream.readlines()
        template = process_deletions(template, self.deletion_targets)
        associations = {
            "{" + k + "}": str(v) for k, v in self.associations.items()
        }
        output_lines = []
        for line in template:
            for k, v in keyfilter(lambda k: k in line, associations).items():
                line = line.replace(k, str(v))
            if not re.match(r"\s+\n", line):
                output_lines.append(line)
        if pprint_xml is False:
            self.pds4_label = "".join(output_lines)
            return
        tree = xml.dom.minidom.parseString("".join(output_lines))
        self.pds4_label = re.sub(
            r"(?<=\n) *\n", "", tree.toprettyxml(indent=" "), flags=re.M
        )

    def write_label(self, output_directory: Union[str, Path]):
        self.pds4_label_path = Path(
            output_directory, f"{self.output_stem}.xml"
        )
        with self.pds4_label_path.open("w") as stream:
            stream.write(self.pds4_label)

    def format_object(self, name: str, purge: bool = True, **kwargs):
        obj = self.data[name]
        if name in self.processors.keys():
            formatted = self.processors[name](obj, **kwargs)
        else:
            formatted = obj
        if purge is True:
            self.data.__delattr__(name)
        return formatted

    def load_object(
        self,
        name: str,
        format_inline: bool = True,
        purge: bool = True,
        **format_kwargs,
    ):
        self.data.load(name)
        if name in self.analyzers.keys():
            self._make_associations(reset=False)
            self.associations |= self.analyzers[name](self.data[name])
        if (format_inline is False) or (name not in self.processors.keys()):
            self.object_cache[name] = self.data[name]
            if purge is True:
                self.data.__delattr__(name)
            return
        self.object_cache[name] = self.format_object(
            name, purge, **format_kwargs
        )

    def load_objects(
        self, format_inline: bool = True, purge: bool = True, **format_kwargs
    ):
        if self.object_names is None:
            return
        for name in self.object_names:
            self.load_object(name, format_inline, purge, **format_kwargs)

    @property
    def output_filestat(self):
        return {
            name: os.stat(path) for name, path in self.output_paths.items()
        }

    @property
    def output_filesize_tags(self):
        tags = {}
        for f, stat in self.output_filestat.items():
            try:
                tags[f"{f}_file_size"] = str(stat.st_size)
            except (KeyError, FileNotFoundError):
                continue
        return tags

    @property
    def tagdict(
        self,
    ) -> dict[str, tuple[str, Optional[Callable[[Any], str]], Optional[str]]]:
        return merge((prep_tagdict(dict_) for dict_ in self.parameter_dicts))

    def _make_associations(self, reset=False, join=False):
        if (self.associations is None) or (reset is True) or (join is True):
            associations = {
                output_tag: self._metaget_template_value(*input_param)
                for output_tag, input_param in self.tagdict.items()
            }
            if (reset is True) or (self.associations is None):
                self.associations = associations
            else:
                self.associations = associations | self.associations
        self.associations |= self.output_filesize_tags

    pds4_label_path: Optional[Path] = None
    associations: Optional[MutableMapping[str, Union[str, int, float]]] = None
    object_cache: Optional[MutableMapping[str, Any]] = None
    processors: Optional[Mapping[str, Callable]] = None
    analyzers: Optional[
        Mapping[str, Callable[[tuple[Any, MutableMapping]], None]]
    ] = None
    pds4_label = None
    object_names: Collection[str] = None
    parameter_dicts: Optional[Collection[Mapping]] = None
    template: Optional[Union[str, Path]] = None
    output_paths: Optional[MutableMapping[str, Path]] = None
    deletion_targets: MutableSequence[str] = None
    data: Optional[Data] = None
    metadata: Optional[Metadata] = None

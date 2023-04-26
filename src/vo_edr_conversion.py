"""
objects for converting PDS3 Viking Orbiter EDR products to PDS4. note that
this module assumes input products have been decompressed from their archived
format. See decompress.py for a script that uses archived binaries to
decompress the files.
"""

import re
import shutil
import warnings
from typing import Mapping

import numpy as np
from scipy.ndimage import maximum_filter, median_filter

from converter import PDSVersionConverter
import datetime as dt
from pathlib import Path
from astropy.io import fits
from types import MappingProxyType

from templating import xmlwrap

THIS_DIRECTORY = Path(__file__).parent.absolute()


def viking_classic_browse_filter(image):
    max_res = maximum_filter(image, size=4)
    mixed = np.logical_and(max_res != 0, image == 0)
    masked = np.ma.masked_array(image, mask=mixed)
    return median_filter(masked, size=4)


def parse_exposure_duration(val):
    if isinstance(val, Mapping):
        return xmlwrap("img:exposure_duration", unit='"s"')(val["value"])
    elif val == "UNKNOWN":
        return "UNKNOWN"


LABEL_VALUES = MappingProxyType(
    {
        "image_id": "IMAGE_ID",
        "orbiter_number": ("SPACECRAFT_NAME", lambda n: n.split("_")[-1]),
        "image_time": "IMAGE_TIME",
        "camera_letter_upper": ("INSTRUMENT_NAME", lambda c: c.split("_")[-1]),
        "camera_letter_lower": (
            "INSTRUMENT_NAME",
            lambda c: c.split("_")[-1].lower(),
        ),
        "filter_name": ("FILTER_NAME", str.lower),
        "product_id_lower": ("IMAGE_ID", str.lower),
        "orbit_number": "ORBIT_NUMBER",
        "earth_received_time": "EARTH_RECEIVED_TIME",
        "mission_phase_name": "MISSION_PHASE_NAME",
        "gain_mode": "GAIN_MODE_ID",
        "exposure_duration": ("EXPOSURE_DURATION", parse_exposure_duration),
        "note": "NOTE",
        "eng_rows": ("ENGINEERING_TABLE", "ROWS"),
        "lh_rows": ("LINE_HEADER_TABLE", "ROWS"),
        "samples": "LINE_SAMPLES",
        "lines": "LINES",
        "offset_mode": "OFFSET_MODE_ID",
        "flood_mode": "FLOOD_MODE_ID",
        "image_number": "IMAGE_NUMBER",
    }
)

TARGET_TAGS = MappingProxyType(
    {
        "MARS": {
            "target_name": "Mars",
            "target_type": "Planet",
            "target_lidvid": "urn:nasa:pds:context:target:planet.mars::1.2",
        },
        "STAR": {
            "target_name": "Star",
            "target_type": "Calibration Field",
            "target_lidvid": "urn:nasa:pds:context:target:calibration_field.star::1.0",
        },
        "PHOBOS": {
            "target_name": "Phobos",
            "target_type": "Satellite",
            "target_lidvid": "urn:nasa:pds:context:target:satellite.mars.phobos::1.1",
        },
        "DEIMOS": {
            "target_name": "Deimos",
            "target_type": "Satellite",
            "target_lidvid": "urn:nasa:pds:context:target:satellite.mars.deimos::1.1",
        },
        "UNKNOWN": {
            "target_name": "Unknown",
            "target_type": "Calibrator",
            "target_lidvid": "urn:nasa:pds:context:target:calibrator.unk::1.0",
        },
        "N/A": {
            "target_name": "TEST_IMAGE",
            "target_type": "Calibrator",
            "target_lidvid": "urn:nasa:pds:context:target:calibrator.test_image::1.0",
        },
    }
)


def write_fits(array, outpath):
    fits.PrimaryHDU(array).writeto(outpath, overwrite=True)


def convert_dqi(dqi):
    if dqi == "000":
        return "bad data"
    elif dqi == "001":
        return "SNR low, GCF block bad"
    elif dqi == "010":
        return "SNR good, GCF block bad"
    elif dqi == "011":
        return "SNR low, GCF block good"
    elif dqi == "100":
        return "SNR good, GCF block good"
    return "Invalid DQI value"


class VikingEDRConverter(PDSVersionConverter):
    """converter for EDR products."""
    def __init__(self, filename, **pdr_kwargs):
        super().__init__(filename, **pdr_kwargs)
        self._make_associations()

    def _write_image(self, output_directory, purge):
        self.load_object("IMAGE")
        outpath = Path(output_directory, self.output_stem + ".fits")
        write_fits(self.object_cache["IMAGE"], outpath)
        self.output_paths["image"] = outpath
        self.associations["image_file_name"] = outpath.name
        if purge is True:
            del self.object_cache["IMAGE"]

    def _check_cathode(self):
        cathode_flag = self.object_cache["ENGINEERING_TABLE"][
            "TRANSMITTED_CODE_WORD1"
        ].item()[2]
        if cathode_flag == "0":
            return "OFF"
        if cathode_flag == "1":
            return "ON"
        raise ValueError(
            "cathode_current_flag is now Schrodinger's flag: neither "
            "on nor off"
        )

    def _write_eng_table(self, output_directory, purge):
        self.load_object("ENGINEERING_TABLE")
        outpath = Path(output_directory, self.output_stem + "_eng.csv")
        tw1_dqi = self.object_cache[
            "ENGINEERING_TABLE"
        ].TRANSMITTED_CODE_WORD1.item()[1]
        tw2_dqi = self.object_cache[
            "ENGINEERING_TABLE"
        ].TRANSMITTED_CODE_WORD2.item()[1]
        rw1_dqi = self.object_cache[
            "ENGINEERING_TABLE"
        ].RECEIVED_CODE_WORD1.item()[1]
        self.associations["cathode_current_flag"] = self._check_cathode()
        self.object_cache["ENGINEERING_TABLE"][
            "TRANSMITTED_CODE_WORD_1_DQI"
        ] = convert_dqi(tw1_dqi)
        self.object_cache["ENGINEERING_TABLE"][
            "TRANSMITTED_CODE_WORD_2_DQI"
        ] = convert_dqi(tw2_dqi)
        self.object_cache["ENGINEERING_TABLE"][
            "RECEIVED_CODE_WORD_1_DQI"
        ] = convert_dqi(rw1_dqi)
        self.object_cache["ENGINEERING_TABLE"] = self.object_cache[
            "ENGINEERING_TABLE"
        ].drop(
            [
                "PHYSICAL_SEQUENCE_NUMBER",
                "LOGICAL_SEQUENCE_NUMBER",
                "FIRST_ERT",
                "FIRST_ERT_MINUTE",
                "FIRST_ERT_MILLISECOND",
                "LAST_ERT",
                "LAST_ERT_MINUTE",
                "LAST_ERT_MILLISECOND",
                "FILL_IN",
                "TRACK_PRESENCE_MASK",
                "AVERAGE_PIXEL",
                "UNUSED_1",
                "UNUSED_2",
                "UNUSED_3",
                "UNUSED_4",
                "UNUSED_5",
                "UNUSED_6",
                "IMAGE_ID",
                "TRANSMITTED_CODE_WORD1",
                "TRANSMITTED_CODE_WORD2",
                "RECEIVED_CODE_WORD1",
            ],
            axis=1,
        )
        for column in ("DISK_ID", "EDR_ID"):
            val = self.object_cache["ENGINEERING_TABLE"].loc[0, column]
            try:
                if (val == b"") or (b"\x10" in val):
                    val = b"UNKNOWN"
                self.object_cache["ENGINEERING_TABLE"].loc[
                    0, column
                ] = val.decode("ascii")
            except UnicodeDecodeError:
                self.object_cache["ENGINEERING_TABLE"].loc[
                    0, column
                ] = "unknown -- likely bad table"
        self.object_cache["ENGINEERING_TABLE"].to_csv(outpath, index=None)
        self.output_paths["eng_table"] = outpath
        self.associations["eng_table_file_name"] = outpath.name
        with open(outpath) as stream:
            self.associations["eng_header_length"] = str(len(next(stream)))
        if purge is True:
            del self.object_cache["ENGINEERING_TABLE"]

    def _write_lh_table(self, output_directory, purge):
        self.load_object("LINE_HEADER_TABLE")
        outpath = Path(output_directory, self.output_stem + "_lh.csv")
        self.object_cache["LINE_HEADER_TABLE"] = self.object_cache[
            "LINE_HEADER_TABLE"
        ].drop(columns=["FILL_IN", "AVERAGE_PIXEL", "EMBEDDED_SCIENCE_DATA_7"])
        self.object_cache["LINE_HEADER_TABLE"].to_csv(outpath, index=False)
        self.output_paths["lh_table"] = outpath
        self.associations["lh_table_file_name"] = outpath.name
        with open(outpath) as stream:
            self.associations["lh_header_length"] = str(len(next(stream)))
        if purge is True:
            del self.object_cache["LINE_HEADER_TABLE"]

    def write_file(self, name, output_directory, purge=False):
        if name == "image":
            return self._write_image(output_directory, purge)
        if name == "eng_table":
            return self._write_eng_table(output_directory, purge)
        if name == "lh_table":
            return self._write_lh_table(output_directory, purge)
        raise ValueError(f"unknown object {name}")

    def _make_associations(self, reset=False, join=True):
        super()._make_associations(reset, join)
        if self.associations["earth_received_time"] == "UNKNOWN":
            self.deletion_targets.append("no_ert")
        if self.associations["exposure_duration"] == "UNKNOWN":
            self.deletion_targets.append("no_exposure")
        if "pds4_lid" not in self.associations.keys():
            # this is intended to facilitate efficient messing-with of the
            # output stem for weird errata cases.
            if self.associations["orbit_number"] == 0:
                if self.associations["image_id"][-3] in ("C", "D"):
                    orbit = "cccc"
                else:
                    orbit = "uuuu"
            else:
                orbit = str(self.associations["orbit_number"]).zfill(4)
            self.output_stem = (
                f"e_{orbit}_{self.associations['orbiter_number']}_"
                f"{self.associations['camera_letter_lower']}_"
                f"{self.associations['filter_name'][0]}_"
            )
            if self.associations["image_time"] == "UNKNOWN":
                self.associations[
                    "start_date_time"
                ] = '<start_date_time xsi:nil="true" nilReason="unknown" />'
                self.output_stem += "uu_uu_uu_uu_uu_uu"
            else:
                self.associations["start_date_time"] = xmlwrap(
                    "start_date_time"
                )(self.associations["image_time"])
                self.output_stem += re.sub(
                    "[:tT-]", "_", self.associations["image_time"][2:-1]
                ).lower()
            self.output_stem += f"_{self.associations['image_id'].lower()}"
            self.associations["pds4_lid"] = self.output_stem
        self.associations |= TARGET_TAGS[self.metadata.metaget("TARGET_NAME")]
        self.associations[
            "product_creation_time"
        ] = dt.datetime.now().isoformat()
        self.associations |= self.output_filesize_tags

    object_names = ("image", "eng_table", "lh_table")
    parameter_dicts = (LABEL_VALUES,)
    template = Path(THIS_DIRECTORY, "templates", "vo_edr_template.xml")


class VikingEDRBrowseWriter(PDSVersionConverter):
    """
    Browse writer for EDR products. must be initialized from a
    VikingEDRConverter; propagates values from the observational data product
    into the browse product.
    """
    def __new__(cls, input_converter):
        return cls.from_converter(input_converter)

    # noinspection PyMissingConstructor
    def __init__(self, input_converter):
        self.pds4_lid = self.output_stem + "_browse"
        self.input_converter = input_converter

    def _write_image(self, output_directory):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.data.load("IMAGE", reload=True)
        # check if this is a dark enough image we don't want to clip it
        clip = (0.25, 0.5) if (np.percentile(self.data.IMAGE, 99) != 0) else 0
        settings = {
            "_base": {"image_clip": clip, "mask_color": None},
            "_masked": {"image_clip": clip},
            # WARNING: hacky! be careful if you reorder this later!
            "": {"image_clip": clip, "mask_color": None},
        }
        output_paths = {}
        self.data.specials["IMAGE"] = {"missing": 0}
        for name, dump_kwargs in settings.items():
            output_path = Path(
                output_directory, f"{self.output_stem}{name}.png"
            )
            # WARNING: hacky! be careful if you reorder this later!
            if name == "":
                self.data.IMAGE = viking_classic_browse_filter(self.data.IMAGE)
            self.data.dump_browse(
                outpath=output_directory,
                prefix=self.output_stem + name,
                image_format="png",
                **dump_kwargs,
            )
            shutil.move(
                Path(output_directory, f"{self.output_stem}{name}_IMAGE.png"),
                output_path,
            )
            output_paths[f"image{name}"] = output_path
        return output_paths

    def write_file(self, name, output_directory):
        if name == "image":
            output_paths = self._write_image(output_directory)
        else:
            raise ValueError("unknown object")
        self.output_paths |= output_paths

    def write_label(self, output_directory):
        # hacky!
        self.output_stem = self.output_stem + "_browse"
        super().write_label(output_directory)

    object_names = ("image", "image_masked")
    template = Path(THIS_DIRECTORY, "templates", "vo_edr_browse_template.xml")

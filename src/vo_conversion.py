"""
objects for converting PDS3 Viking Orbiter map-projected products to PDS4.
"""
import datetime as dt
import shutil
import textwrap
from types import MappingProxyType
from typing import Mapping
import warnings
from pathlib import Path

from astropy.io import fits
from dustgoggles.pivot import extract_constants
from marslab.imgops.imgutils import normalize_range, eightbit
import numpy as np
import pandas as pd
from pdr import Metadata
from PIL import Image
from pyproj import Geod

from converter import PDSVersionConverter
from templating import xmlwrap

THIS_DIRECTORY = Path(__file__).parent.absolute()


MDIM_DESCRIPTION = (
    "Mosaicked Digital Image Model (MDIM) image made from fused Viking "
    "Orbiter EDRs, presented in a {projection_no_underscore} projection at "
    "1/{resolution} degrees/pixel. Unlike the EDRs, these data have been "
    "processed with a complicated pipeline optimized for cosmetic uniformity, "
    "and are not suitable for radiometric analysis. "
)

MDIM_DESCRIPTION_END = (
    "This is a converted version of a PDS3 product "
    "consisting of an IMG file with an attached PVL header and an embedded "
    "histogram. We have discarded the histogram and PVL label and converted "
    "the image array to FITS format. The PDS3 product was originally "
    "released on CD-ROM in 1992 by a team at USGS."
)

MDIM_HIRES_DESCRIPTION_END = (
    "This is a converted version of a PDS3 product "
    "consisting of an IMG file with an attached PVL header and an embedded "
    "histogram. We have discarded the histogram and PVL label and converted "
    "the image array to FITS format. The PDS3 product was originally "
    "released on CD-ROM in 1999 by a team at USGS as a high-resolution "
    "extension to the VO1/VO2-M-VIS-5-DIM-V1.0 series."
)

DTM_DESCRIPTION = (
    "Tile of a Digital Terrain Model (DTM) constructed from "
    "Viking Orbiter data. This is a converted version of a PDS3 product "
    "released on CD-ROM in 1992 by a team at USGS. Description from original "
    "documentation follows: 'The DTM was compiled by manually digitizing the "
    "contour lines on the 1:2,000,000-scale series of topographic maps "
    "published by the U.S. Geological Survey.  The original contours were at "
    "one kilometer intervals. When drawing the final contour lines the MDIM "
    "map series was used as the base in order to insure proper registration "
    "of the DTM and MDIM. In mose areas of the planet, the DTM and MDIM  "
    "co-register to within one are two pixels. The digitized one kilometer "
    "contour-line vector files were then gridded to form the DTM raster.[...] "
    "The pixel values (DN values) in the DTM images have been offset and "
    "scaled. In order to obtain the elevation from the DTM data, users should "
    "apply the following equation to the DN values: "
    "ELEVATION(METERS) = DN*2.0 - 6000'"
)

VO_MOSAIC_BAND_CODES = {
    "red": "red",
    "sgr": "synthetic_green",
    "vio": "violet",
    "grn": "green",
}

MSPEC_TAGS = {
    "filter_name": "FILTER_NAME",
    "emission_angle": "EMISSION_ANGLE",
    "incidence_angle": "INCIDENCE_ANGLE",
    "phase_angle": "PHASE_ANGLE",
    "image_time": "IMAGE_TIME",
    "lines": "LINES",
    "samples": "LINE_SAMPLES",
    "spacecraft_name": "SPACECRAFT_NAME",
    "orbit_number": "ORBIT_NUMBER",
}


def skipna(func):
    def skippingly(val, *args, **kwargs):
        if val is None:
            return None
        return func(val, *args, **kwargs)

    return skippingly


def dequantize(val):
    if isinstance(val, Mapping):
        return val["value"]
    return val


SINGLE_BAND_TAGS = MappingProxyType(
    {
        "image_id": "IMAGE_ID",
        "data_set_id": "DATA_SET_ID",
        "lines": "LINES",
        "samples": "LINE_SAMPLES",
        "scaling_factor": "SCALING_FACTOR",
        "offset": "OFFSET",
    }
)

CART_TAGS = MappingProxyType(
    {
        "min_lat": "MINIMUM_LATITUDE",
        "max_lat": "MAXIMUM_LATITUDE",
        "min_lon": "MINIMUM_LONGITUDE",
        "max_lon": "MAXIMUM_LONGITUDE",
        "x_off": "X_AXIS_PROJECTION_OFFSET",
        "y_off": "Y_AXIS_PROJECTION_OFFSET",
        "cen_lon": "CENTER_LONGITUDE",
        "cen_lat": "CENTER_LATITUDE",
        "projection": "MAP_PROJECTION_TYPE",
        "scale": ("MAP_SCALE", skipna(lambda s: dequantize(s) * 1000)),
        "resolution": ("MAP_RESOLUTION", dequantize),
        # km to m
        "a_axis_radius": ("A_AXIS_RADIUS", skipna(lambda r: int(r) * 1000)),
        "b_axis_radius": ("B_AXIS_RADIUS", skipna(lambda r: int(r) * 1000)),
        "c_axis_radius": ("C_AXIS_RADIUS", skipna(lambda r: int(r) * 1000)),
        "long_dir": "POSITIVE_LONGITUDE_DIRECTION",
    }
)


def parse_mspec_sources(image_ids):
    elements = []
    parent = xmlwrap("Source_Product_External")
    ident = xmlwrap("external_source_product_identifier")
    desc = xmlwrap("description")("PDS3 version of a band in this product.")
    facility = xmlwrap("curating_facility")("IMG")
    reftype = xmlwrap("reference_type")("data_to_derived_source_product")
    for image_id in image_ids:
        image_id = image_id.replace('"', "")
        ref = ident(f"VO1/VO2-M-VIS-5-DIM-V1.0:{image_id}")
        elements.append(parent(ref + reftype + facility + desc))
    return "\n".join(elements)


def parse_internal_edr_refs(image_ids, edr_lidmap):
    if isinstance(image_ids, str) or (image_ids is None):
        return ""
    # most high-resolution tiles have "'     '" or similar for this value
    if len(image_ids) == 1:
        if list(image_ids)[0].strip('" ') == "":
            return ""
    elements = []
    parent = xmlwrap("Source_Product_Internal")
    ident = xmlwrap("lidvid_reference")
    desc = xmlwrap("comment")(
        "PDS4 version of an EDR source image for this product."
    )
    reftype = xmlwrap("reference_type")("data_to_raw_source_product")
    for image_id in image_ids:
        try:
            image_id = image_id.replace('"', "")
            ref = ident(
                f"urn:nasa:pds:viking_orbiter_imaging:data:"
                f"{edr_lidmap[image_id]}::1.0"
            )
            elements.append(parent(ref + reftype + desc))
        except KeyError:
            warnings.warn(f"{image_id} not found in edr_lidmap.")
    return "\n".join(elements)


def parse_mspec_filters(bands):
    elements = []
    for band in bands:
        elements.append(
            xmlwrap("img:Optical_Filter")(
                xmlwrap("img:filter_name")(band.upper())
            )
        )
    return "\n".join(elements)


def parse_mspec_illumination_geometry(bandset_metadata: pd.DataFrame):
    blocks = []
    parent = xmlwrap("geom:Geometry_Orbiter")
    illumination = xmlwrap("geom:Illumination_Geometry")
    specific = xmlwrap("geom:Illumination_Specific")
    reference = xmlwrap("geom:reference_location")("Boresight Intercept Point")
    for band in VO_MOSAIC_BAND_CODES.values():
        if band not in bandset_metadata["BAND"].tolist():
            continue
        row = bandset_metadata.loc[bandset_metadata["BAND"] == band].iloc[0]
        image_time = xmlwrap("geom:geometry_reference_time_utc")(
            f"{row['IMAGE_TIME']}Z"
        )
        comment = xmlwrap("geom:comment")(
            f"Values from the PDS3 label of the {row['BAND']} image."
        )
        angles = [
            xmlwrap(f"geom:{a}_angle", unit='"deg"')(row[f"{a}_angle".upper()])
            for a in ("incidence", "emission", "phase")
        ]
        i_block = illumination(comment + specific(reference + "".join(angles)))
        blocks.append(parent(image_time + i_block))
    return xmlwrap("geom:Geometry")("".join(blocks))


def format_mdim_description(associations, ending):
    description = MDIM_DESCRIPTION
    for embedded in ("resolution", "projection_no_underscore"):
        val = associations[embedded]
        val = str(val) if not isinstance(val, float) else str(int(val))
        description = description.replace("{" + embedded + "}", val.lower())
    return "\n    ".join(textwrap.wrap(description + ending, 77))


def write_fits(array, outpath):
    fits.PrimaryHDU(array).writeto(outpath, overwrite=True)


def positive_east(degree):
    if degree >= 0:
        return 360 - degree
    if degree < 0:
        return -degree


def sinusoidal_upperleft(resolution, scale, max_lat, y_offset, x_offset):
    upleft_x = (
        resolution * scale * np.cos(max_lat) * (-y_offset + 1.0)
    )  # meters
    upleft_y = x_offset + 1.0 * scale  # meters
    return upleft_x, upleft_y


def non_sinusoidal_upperleft(
    max_lat, west_bound, cen_lon, cen_lat, eq_axis, pol_axis
):
    geoid = Geod(a=eq_axis, b=pol_axis)
    # calculate distance between center lon and upper left corner at the
    # same latitude
    _, _, dist_x = geoid.inv(west_bound, max_lat, cen_lon, max_lat)
    if abs(west_bound - cen_lon) > 180:
        dist_x = -dist_x
    upleft_x = dist_x

    # calculate distance between center lat and upper left corner at the
    # same longitude
    _, _, dist_y = geoid.inv(west_bound, max_lat, west_bound, cen_lat)
    if max_lat < cen_lat:
        dist_y = -dist_y
    upleft_y = dist_y
    return upleft_x, upleft_y


def compute_cart(associations, digits=3):
    if associations["long_dir"] == "WEST":
        associations["long_dir"] = "Positive East"
        # convert to Positive East
        associations["west_bound"] = positive_east(associations["max_lon"])
        associations["east_bound"] = positive_east(associations["min_lon"])
        associations["cen_lon"] = positive_east(associations["cen_lon"])
    else:
        raise ValueError(
            "Some files are in Positive East already; need to add updated "
            "equations."
        )
    # x and y scale and resolution are the same, but are separated here in
    # case we need to change that.
    associations["pixel_resolution_x"] = associations["resolution"]
    associations["pixel_resolution_y"] = associations["resolution"]
    associations["pixel_scale_x"] = associations["scale"]
    associations["pixel_scale_y"] = associations["scale"]
    if associations["projection"] == "SINUSOIDAL":
        associations["projection"] = "Sinusoidal"
        (
            associations["upleft_x"],
            associations["upleft_y"],
        ) = sinusoidal_upperleft(
            associations["resolution"],
            associations["scale"],
            associations["max_lat"],
            associations["y_off"],
            associations["x_off"],
        )
    elif associations["projection"] == "ORTHOGRAPHIC":
        associations["projection"] = "Orthographic"
        (
            associations["upleft_x"],
            associations["upleft_y"],
        ) = non_sinusoidal_upperleft(
            associations["max_lat"],
            associations["west_bound"],
            associations["cen_lon"],
            associations["cen_lat"],
            associations["a_axis_radius"],
            associations["c_axis_radius"],
        )
    elif associations["projection"] == "POLAR_STEREOGRAPHIC":
        associations["projection"] = "Polar_Stereographic"
        (
            associations["upleft_x"],
            associations["upleft_y"],
        ) = non_sinusoidal_upperleft(
            associations["max_lat"],
            associations["west_bound"],
            associations["cen_lon"],
            associations["cen_lat"],
            associations["a_axis_radius"],
            associations["c_axis_radius"],
        )
    else:
        raise ValueError(
            f'Projection type {associations["projection"]} not defined.'
        )
    associations["projection_no_underscore"] = associations[
        "projection"
    ].replace("_", " ")
    for ax in ("x", "y"):
        associations[f"upleft_{ax}"] = round(
            associations[f"upleft_{ax}"], digits
        )
    for card in ("east", "west"):
        associations[f"{card}_bound"] = round(
            associations[f"{card}_bound"], digits
        )
    for ax in ("lat", "lon"):
        associations[f"max_{ax}"] = round(associations[f"max_{ax}"], digits)
    return associations


class VikingDIMConverter(PDSVersionConverter):
    """converter for single-band DIMs and DTMs."""
    def __init__(self, image_file, edr_lidmap=None, **pdr_kwargs):
        super().__init__(image_file, **pdr_kwargs)
        self.edr_lidmap = edr_lidmap

    def _write_image(self, output_directory, purge):
        self.load_object("IMAGE")
        outpath = Path(output_directory, self.output_stem + ".fits")
        write_fits(self.object_cache["IMAGE"], outpath)
        self.output_paths["image"] = outpath
        if purge is True:
            del self.object_cache["IMAGE"]

    def write_file(self, name, output_directory, purge=False):
        if name == "image":
            return self._write_image(output_directory, purge)
        raise ValueError(f"unknown object {name}")

    def _make_associations(self, reset=False, join=False):
        super()._make_associations(reset)
        self.associations["product_id"] = self.output_stem
        if not self.associations["projection"]:
            self.deletion_targets.append("no_cart")
        else:
            self.associations = compute_cart(self.associations)
        if self.associations["projection"] == "Polar_Stereographic":
            # still let it compute scale and stuff but we're not writing
            # a cart block for these
            self.deletion_targets.append("no_cart")
        if self.output_stem.startswith("t"):
            self.associations["description"] = DTM_DESCRIPTION
            self.associations["ftype"] = "DTM"
            self.associations["dtype"] = "UnsignedMSB2"
            self.deletion_targets.append("dtm")
        else:
            self.associations["ftype"] = "MDIM"
            self.deletion_targets.append("not_dtm")
            if self.output_stem.startswith("mk"):
                ending = MDIM_HIRES_DESCRIPTION_END
            else:
                ending = MDIM_DESCRIPTION_END
            self.associations["description"] = format_mdim_description(
                self.associations, ending
            )
            self.associations["dtype"] = "UnsignedByte"
        self.associations[
            "start_time"
        ] = """<start_date_time xsi:nil="true" nilReason="missing" />"""
        if self.edr_lidmap is not None:
            self.associations["edr_references"] = parse_internal_edr_refs(
                self.data.metaget("SOURCE_IMAGE_ID"), self.edr_lidmap
            )
        else:
            self.associations["edr_references"] = ""
            warnings.warn("No edr_lidmap passed, not writing edr references.")
        self.associations[
            "product_creation_time"
        ] = dt.datetime.now().isoformat()
        self.associations |= self.output_filesize_tags

    parameter_dicts = (SINGLE_BAND_TAGS, CART_TAGS)
    template = Path(THIS_DIRECTORY, "templates", "vo_dim_template.xml")


class VikingDIMBrowseWriter(PDSVersionConverter):
    """
    Browse writer for single-band DIMs and DTMs. must be initialized from a
    VikingDIMConverter; propagates values from the observational data product
    into the browse product.
    """
    def __new__(cls, input_converter):
        return cls.from_converter(input_converter)

    # noinspection PyMissingConstructor
    def __init__(self, input_converter):
        self.output_stem = self.output_stem + "_browse"
        self.input_converter = input_converter

    def _write_image(self, output_directory):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.data.load("IMAGE", reload=True)
        # check for appropriate dynamic range clipping
        clip = [None, None]
        centiles = np.percentile(
            self.data.IMAGE[self.data.IMAGE != 0], (1, 99)
        )
        clip[0] = 1 if centiles[0] != 255 else 0
        clip[1] = 1 if centiles[1] != 0 else 0
        self.data.specials["IMAGE"] = {"missing": 0}
        settings = {
            "": {"image_clip": clip, "mask_color": 0},
            "_masked": {"image_clip": clip},
        }
        output_paths = {}
        for name, dump_kwargs in settings.items():
            output_path = Path(
                output_directory, f"{self.output_stem}{name}.png"
            )
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

    object_names = ("image", "image_masked")
    template = Path(THIS_DIRECTORY, "templates", "vo_dim_browse_template.xml")


class VikingAirbrushConverter(PDSVersionConverter):
    """
    converter for cosmetic 'digital airbrush' products. writes them as PDS4
    Product_Browse.
    """
    def __init__(self, filename, **pdr_kwargs):
        super().__init__(filename, **pdr_kwargs)
        self.output_stem = Path(filename).stem.lower()

    def _write_image(self, output_directory, purge=True):
        self.load_object("IMAGE", purge=False)
        self.data.dump_browse(
            outpath=output_directory,
            purge=purge,
            image_format="png",
            image_clip=(0, 0),
        )
        if purge is True:
            del self.object_cache["IMAGE"]
        outpath = Path(output_directory, f"{self.output_stem}.png")
        shutil.move(
            Path(output_directory, f"{self.output_stem}_IMAGE.png"), outpath
        )
        self.output_paths["image"] = outpath

    def write_file(self, name, output_directory, purge=False):
        if name == "image":
            return self._write_image(output_directory, purge)
        raise ValueError(f"unknown object {name}")

    def _make_associations(self, reset=False, join=False):
        super()._make_associations(reset)
        self.associations["product_id"] = self.output_stem
        self.associations[
            "product_creation_time"
        ] = dt.datetime.now().isoformat()

    object_names = ("image",)
    template = Path(THIS_DIRECTORY, "templates", "vo_airbrush_template.xml")
    parameter_dicts = (SINGLE_BAND_TAGS,)


class VikingMspecConverter(PDSVersionConverter):
    """
    converter for multispectral DIMs. must be initialized from a VOBandSet,
    as it wraps multiple input products in order to stack the split-channel
    source products into multichannel images.
    """
    def __init__(self, bandset, edr_lidmap=None):
        super().__init__()
        constants, variables = extract_constants(
            bandset.metadata, drop_constants=True
        )
        self.metadata = Metadata((constants, constants.keys()))
        self.bandset = bandset
        self.edr_lidmap = edr_lidmap
        image_id = bandset.metadata["IMAGE_ID"].iloc[0]
        bandstring = "".join(
            [
                b[0]
                for b in VO_MOSAIC_BAND_CODES.values()
                if b in bandset.metadata["BAND"].tolist()
            ]
        )
        self._make_associations()
        self.output_stem = (
            f"{image_id[1:9]}_{bandstring}_"
            f"{str(self.associations['orbit_number']).zfill(4)}_"
            f"{self.associations['spacecraft_name'][-1]}"
        ).lower()
        self.associations["product_id"] = self.output_stem

    def _write_image(self, output_directory, _purge=False):
        self.bandset.load("all")
        bands = [
            self.bandset.get_band(band)
            for band in self.bandset.metadata["BAND"]
        ]
        outpath = Path(output_directory, self.output_stem + ".fits")
        write_fits(np.dstack(bands), outpath)
        self.output_paths["image"] = outpath

    def write_file(self, name, output_directory, _purge=False):
        if name == "image":
            return self._write_image(output_directory, _purge)
        raise ValueError(f"unknown object {name}")

    def _make_scaling_info(self):
        scaling_info = "\n".join(
            [
                f"      {row['BAND']}: *{row['SCALING_FACTOR']} +{row['OFFSET']}"
                for _, row in self.bandset.metadata.sort_values(
                    by="BAND"
                ).iterrows()
            ]
        )
        return (
            f"scaling factors and offsets used to convert DN to I/F in this "
            f"array were:\n{scaling_info}"
        )

    def _make_associations(self, reset=False, join=True):
        super()._make_associations(reset)
        try:
            self.associations[
                "illumination_geometry"
            ] = parse_mspec_illumination_geometry(self.bandset.metadata)
        except KeyError:
            self.associations["illumination_geometry"] = ""
            self.deletion_targets.append("no_geom")
        self.associations["optical_filters"] = parse_mspec_filters(
            self.bandset.metadata["BAND"]
        )
        if (
            self.edr_lidmap is not None
            and "GEOMETRY_SOURCE_IMAGE_ID" in self.bandset.metadata.columns
        ):
            self.associations["edr_references"] = parse_internal_edr_refs(
                self.bandset.metadata["GEOMETRY_SOURCE_IMAGE_ID"],
                self.edr_lidmap,
            )
        else:
            if self.edr_lidmap is None:
                warnings.warn("no edr_lidmap passed, not writing edr refs.")
            self.associations["edr_references"] = ""
        self.associations["source_image_elements"] = parse_mspec_sources(
            self.bandset.metadata["IMAGE_ID"]
        )
        self.associations["bands"] = str(len(self.bandset.metadata))
        self.associations["scaling_info"] = self._make_scaling_info()
        self.associations[
            "product_creation_time"
        ] = dt.datetime.now().isoformat()
        if self.associations["spacecraft_name"] == "VIKING_ORBITER_2":
            self.deletion_targets.append("no_vo1")
        else:
            self.deletion_targets.append("no_vo2")
        if len(self.bandset.metadata) == 1:
            self.deletion_targets.append("2D")
        else:
            self.deletion_targets.append("3D")
        if not self.associations["projection"]:
            self.deletion_targets.append("no_cart")
        # did we compute cartography already? don't do it again
        elif "pixel_resolution_x" not in self.associations.keys():
            self.associations = compute_cart(self.associations)
        if self.associations["projection"] == "Polar_Stereographic":
            # still let it compute scale and stuff but we're not writing
            # a cart block for these
            self.deletion_targets.append("no_cart")

        self.associations |= self.output_filesize_tags

    parameter_dicts = (MSPEC_TAGS, CART_TAGS)
    template = Path(THIS_DIRECTORY, "templates", "vo_dim_mspec_template.xml")
    object_names = ("image",)


class VikingMspecBrowseWriter(PDSVersionConverter):
    """
    Browse writer for multispectral DIMs. must be initialized from a
    VikingMspecConverter; propagates values from the observational data product
    into the browse product.
    """
    def __new__(cls, input_converter):
        return cls.from_converter(input_converter)

    # noinspection PyMissingConstructor
    def __init__(self, input_converter):
        self.output_stem = self.output_stem + "_browse"
        self.input_converter = input_converter
        self.bandset = self.input_converter.bandset

    def _write_image(self, output_directory, _purge=False):
        channels, bands = {}, []
        available = self.bandset.metadata["BAND"].tolist()
        if "red" in available:
            channels["red"] = self.bandset.get_band("red")
            bands.append("red")
        if "green" in available:
            channels["green"] = self.bandset.get_band("green")
            bands.append("green")
        elif "synthetic_green" in available:
            channels["green"] = self.bandset.get_band("synthetic_green")
            bands.append("synthetic_green")
        if "violet" in available:
            channels["blue"] = self.bandset.get_band("violet")
            bands.append("violet")
        for channel in ("red", "green", "blue"):
            if channel in channels.keys():
                self.bandset.raw[channel] = channels[channel]
                continue
            self.bandset.raw[channel] = np.zeros(
                (self.associations["lines"], self.associations["samples"])
            )
        if any([np.percentile(c, 99.5) == 0 for c in channels.values()]):
            stretch = 0
        else:
            stretch = (0.5, 0.5)
        instruction = {
            "look": "composite",
            "bands": ("red", "green", "blue"),
            "limiter": {
                "function": normalize_range,
                "params": {"bounds": (0, 1), "stretch": stretch},
            },
        }
        self.bandset.make_look_set([instruction])
        self.associations["bands"] = len(bands)
        if len(bands) == 1:
            self.associations["band_names"] = bands[0]
        elif len(bands) == 2:
            self.associations["band_names"] = f"{bands[0]} and {bands[1]}"
        else:
            self.associations[
                "band_names"
            ] = f"{bands[0]}, {bands[1]}, and {bands[2]}"
        outpath = Path(output_directory, self.output_stem + ".png")
        Image.fromarray(eightbit(tuple(self.bandset.looks.values())[0])).save(
            outpath
        )
        self.output_paths["image"] = outpath

    def write_file(self, name, output_directory, _purge=False):
        if name == "image":
            return self._write_image(output_directory, _purge)
        raise ValueError(f"unknown object {name}")

    template = Path(
        THIS_DIRECTORY, "templates", "vo_dim_mspec_browse_template.xml"
    )

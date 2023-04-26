from pathlib import Path

from dustgoggles.structures import unnest
from marslab.bandset import BandSet
from marslab.imgops.loaders import pdr_load
from multidict import MultiDict
import pandas as pd
import pdr

VO_BANDS = {
    "blue": 440,
    "violet": 410,
    "synthetic_green": 518,
    "clear": 525,
    "green": 550,
    "minus_blue": 590,
    "red": 625,
}

VO_FWHM = {
    "blue": 180,
    "violet": 120,
    # pseudo-sensitivity curve is bimodal, FWHM is not meaningful
    "synthetic_green": None,
    "clear": 350,
    "green": 100,
    "minus_blue": 220,
    "red": 150,
}

VO_MOSAIC_BAND_CODES = {
    "red": "red",
    "sgr": "synthetic_green",
    "vio": "violet",
    "grn": "green",
}


class VOBandSet(BandSet):
    def __init__(self, files):
        super().__init__(load_method=pdr_load)
        # doing this convoluted-looking thing to easily enforce an ordering
        suffix_map = {path.suffix[1:]: path for path in map(Path, files)}
        self.precached = {}
        for suffix, code in VO_MOSAIC_BAND_CODES.items():
            if suffix in suffix_map.keys():
                self.precached[code] = pdr.read(suffix_map[suffix])
        file_records = [
            {
                "BAND": band,
                "PATH": data.filename,
                **unnest(data.metadata, mtypes=(dict, MultiDict)),
            }
            for band, data in self.precached.items()
        ]
        self.metadata = pd.DataFrame(file_records)
        cols = self.metadata.columns.tolist()
        newcols = []
        for c in cols:
            if c in ("IMAGE_ID", "IMAGE_TIME", "GEOMETRY_SOURCE_IMAGE_ID"):
                newcols.append(c)
                continue
            for obj in ("IMAGE_HISTOGRAM", "IMAGE", "MAP_PROJECTION_CATALOG"):
                c = c.replace(f"{obj}_", "")
            newcols.append(c)
        self.metadata.columns = newcols

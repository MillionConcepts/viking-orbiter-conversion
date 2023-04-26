"""general utility functions."""
from collections import deque
import datetime as dt
from functools import partial
from pathlib import Path
import re
from sys import stdout

import pandas as pd


def mb(b, round_to=2):
    value = int(b) / 10 ** 6
    if round_to is not None:
        return round(value, round_to)
    return value


def unix2dt(epoch):
    return dt.datetime.fromtimestamp(epoch)


def mtimes(stat):
    return {
        f"{letter.upper()}TIME": unix2dt(getattr(stat, f"st_{letter}time"))
        for letter in ("a", "c", "m")
    }


def lsdashl(directory, include_directories=True):
    listings = []
    for path in Path(directory).iterdir():
        if (include_directories is False) and (path.is_dir()):
            continue
        try:
            stat = path.stat()
        except FileNotFoundError:
            continue
        listings.append(
            {
                "path": str(path),
                "size": mb(stat.st_size, 3),
                "excluded": False,
                "directory": path.is_dir(),
            }
            | mtimes(stat)
        )
    return listings


def check_inclusion(record, skip_directories=()):
    matcher = partial(re.match, string=record["path"])
    if record["directory"] is True and any(map(matcher, skip_directories)):
        record["excluded"] = True
    return record


def index_breadth_first(root):
    discoveries = []
    search_targets = deque([root])
    while len(search_targets) > 0:
        target = search_targets.pop()
        try:
            contents = tuple(map(check_inclusion, lsdashl(target)))
        except PermissionError:
            continue
        discoveries += contents
        for record in contents:
            if (record["directory"] is True) and (record["excluded"] is False):
                search_targets.append(record["path"])
    return discoveries


def print_inline(text, blanks=60):
    stdout.write(" "*blanks+"\r")
    stdout.write(str(str(text)+'\r'))
    stdout.flush()
    return


def make_edr_lidmap(edr_root):
    edrs = pd.DataFrame(index_breadth_first(edr_root))
    edrs = edrs.loc[edrs['path'].str.endswith('fits')]
    edr_paths = edrs['path'].str.split("/", expand=True).iloc[:, -1]
    edrs['image_id'] = edr_paths.str.slice(-11, -5).str.upper()
    edrs['lid'] = edr_paths.str.slice(0,-5)
    return {
        row['image_id']: row['lid']
        for _, row in edrs[['image_id', 'lid']].iterrows()
    }

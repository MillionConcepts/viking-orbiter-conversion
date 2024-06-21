# viking orbiter imaging data conversion

This repository contains software and ancillary materials used to translate 
and modernize imaging data and metadata from the Viking Orbiter 1 and 2
Visual Imaging Subsystems. The 
[primary bundle documentation](document/primary_bundle_documentation.md) 
provides the best introduction to the purpose of the project and the 
contents of the resulting PDS4 bundle. 

[The PDS Imaging Node hosts the completed bundle.](https://pdsimage2.wr.usgs.gov/Viking_Orbiter/PDS4)
This repo is _not_ a complete mirror of that bundle, which is too large to distribute via GitHub. 
It is intended principally as an extension of the documentation provided in the bundle.

## repository contents

### /browse

Browse collection label and inventory.

### /data

Data collection label and inventory.

### /dictionaries

The PDS4 data dictionaries we validated the bundle against.

### /document

Full contents of document collection.

### /pdr_viking_version (and subdirectories)

A 'frozen' fork of [pdr](https://github.com/MillionConcepts/pdr) slightly 
modified from v0.7.2, recording the specific version of `pdr` we used to 
generate the bundle. 

### /src

Software and metadata files used in the conversion process. The Notebooks 
are the top-level handlers. See comments / docstrings in individual files for more details. 
Note that the pcdcomp.exe file in this directory is a decompression utility
from the PDS3 EDR data set. 

### /src/templates

Label templates (marked-up XML, not syntactically valid until processed) 
used by the conversion pipeline.

### /src/format_files

PDS3 .fmt files required to read the engineering and line header tables 
embedded in the PDS3 versions of the EDRs.

## code usage

If you wish to execute the code in this respository, you may use the 
environment.yml file to construct a `conda` environment. Versions are pinned
in this file to record the specific package versions available at the time 
of creation. Up-to-date versions will probably work, but we cannot guarantee
that upstream changes will not substantively change some result of the 
conversion process.

You must then install the 'frozen' fork of `pdr` in this repository into 
that environment (trunk `pdr` will not work).

If you would like to use the `decompress.py` script to decompress source EDRs, 
you will also need to install [DOSBox](https://dosbox.com) and ensure that 
it is executable from your PATH.

NOTE: This code is not compatible with Windows. 

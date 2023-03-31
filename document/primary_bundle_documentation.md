# Overview of the Viking Orbiter Imaging Bundle

## introduction

This bundle contains imaging products created from data taken by the
Viking Orbiter (VO) 1 and 2 Visual Imaging Subsystems (VIS). It
includes both minimally-processed Experiment Data Record (EDR) images
and map-projected, mosaicked Digital Image Model (DIM) and Digital
Terrain Model (DTM) images. It is a concatenated, reformatted,
PDS4-compliant version of all observational data in the PDS Imaging
Node (IMG) VO holdings. 

The EDR corpus includes data from the Viking cruise phase (1975) to the
end of VO1’s life (1980; VO2 expired in 1978). These data consist
largely of images and ancillary data from systematic mapping phases,
but also include images of Phobos and Deimos, non-nadir images of Mars,
images of deep-space targets, and some test and calibration images. 

The map-projected data come in three distinct flavors: single-band DIMs
created from all available VO data for a particular region; DTMs in
elevation units, also created from all available VO data for a
particular region; and multispectral DIMs created from data taken
within one specific orbit (intended to permit comparison across seasons
and weather events). (Note that the DIMs are interchangeably referred
to as “DIMs” or “MDIMs” in source materials, and the “M” is variously
defined as “mosaicked” or “Mars”. We will generally just refer to them
as “DIMs”.)

This document provides a brief description of how we organized and
formatted our versions of these observational products, along with
notes on how they differ from the contents of their PDS3 source data
sets. This document therefore partially deprecates the SIS-like
documents published in the original data sets and included in this
bundle’s document collection. However, it is not intended to duplicate
or supersede their detailed notes on instrument characteristics,
original data collection, physical interpretation of values, etc. 


### notes on provenance

this bundle incorporates products from the following PDS3 data sets:
VO1/VO2-M-VIS-2-EDR-V2.0, VO1/VO2-M-VIS-5-DIM-V1.0, and
VO1/VO2-M-VIS-5-DTM-V1.0.

The EDRs were originally collected, checked for quality and
completeness, and released as a collection of 46 CD-ROMs in 1990
(volume numbers VO_1001-VO_1032 & VO_1051-VO_1064)[^1] by a team
consisting of personnel from Washington University, USGS, and JPL. They
were sourced largely from tapes produced by the JPL Planetary Image
Conversion Task in the mid-1980s, but also include some data recovered
directly from the original Viking Master Data Record (MDR) tapes. 

The map-projected products were originally released in four steps. USGS
and JPL personnel compiled and released the lower-resolution
single-band DIMs as a series of 6 CD-ROMs in 1991 (volume numbers
VO_2001-VO_2006), followed by the multispectrals in 1992
(VO_2008-VO_2014), and the DTMs in 1993 (VO_2007). The
higher-resolution single-band DIMs were created in a separate effort by
USGS personnel and released as a series of 8 CD-ROMs in 1999
(VO_2015 - VO_2022).

All products in this PDS4 bundle are based on the versions of the
VO_1001 - VO_2022 volumes that IMG-USGS makes available through its web
portal. Note that there is also an unfinished second version of the
map-projected data in circulation (VO1/VO2-M-VIS-5-DIM-V2.0). This
project was abandoned in 2001 (after producing new versions of
VO_2001-VO-2006) and never formally archived in the PDS. This PDS4
bundle does not include any products sourced from
VO1/VO2-M-VIS-5-DIM-V2.0.


[^1]: We do not know why the numbers 1033-1050 were not used, but there
is no indication, based on references in the map-projected products,
that there is a large missing swath of EDRs. 


### bundle directory structure

We have not retained the multi-volume organization of the source data
sets. It was optimized for easy distribution on physical media; this
constraint demanded usability compromises (e.g. related products being
split between similarly-named subdirectories on separate volumes) that
are no longer necessary. We have developed a new structure we believe
is more easily navigable. Here is an overview of the directory
structure relative to bundle root:

**/data**

Root directory for the bundle’s data collection.

**/data/dim**

Root directory for single-band DIM products.

**/data/dim/RRRR**

The single-band DIM mosaic has four versions at different resolutions.
These are root directories for each of these versions of the mosaic,
expressed in 0-padded pixels/deg(0016, 0064, 0256, 1024).

**/data/dim/RRRR/L0[ns]**

Directories containing single-band DIM products, organized by the
central latitude of the tile(rounded down to the nearest whole multiple
of 10). An appended ‘n’ or ‘s’ indicates latitude direction. For
instance, /data/dim/0064/10n contains single-band DIM products at 64
pixels/degree, some centered at 10 degrees north and some at 15 degrees
north. 

**/data/dtm** 

Root directory for DTM products.

**/data/dtm/RRRR** 

The DTM mosaic has three versions at different resolutions. These are
root directories for each of these versions of the mosaic, expressed in
0-padded pixels/deg (0004, 0016, 0064).

**/data/dtm/RRRR/L0[ns]** 

Directories containing DTM products, organized by latitude of the tile,
using the same convention as the single-band DIM product directories.

**/data/edr** 

Root directory for EDR products.

**/data/edr/OOOO** 

Directories containing EDR products, organized by 4-digit 0-padded orbit
number. Products with no mission-provided orbit number are
in /data/edr/0000.

**/data/edr/errata** 

Special directory for ‘errata’ EDR products with multiple versions
(see below).

**/data/mspec** 

Root directory for multispectral DIM products. Note that, unlike the
DTMs and single-band DIMs, the multispectral mosaic does not have
multiple versions at separate resolutions.

**/data/mspec/L0[ns]** 

Directories containing tiles of the multispectral DIM mosaic, organized
by latitude of the tile, using the same convention as the single-band
DIM product directories.

**/data/mspec/special** 

Root directory for special-purpose multispectral products that are not
part of the mosaic series (found in ‘special’ and subdirectories on the
original volumes).

**/data/mspec/special/?????** 

Directories containing special-purpose multispectral DIMs. These are
unique sets (or sometimes single tiles), each with a distinct
projection. We have retained the names of these subdirectories from the
source sets, which generally refer to orbit number and orbiter, and
sometimes also include a letter referring to projection type.

**/document** 

Root directory for the bundle’s document collection. This collection has
no subdirectories.

**/browse** 

Root directory for the bundle’s browse collection.

**/browse/airbrush** 

PNG-encoded versions of the shaded relief airbrush mosaic.

**/browse/dim _(and subdirectories)_** 

Browse products for single-band DIMs. This tree follows the structure
of /data/dim (see above).

**/browse/dtm _(and subdirectories)_** 

Browse products for DTMs. This tree follows the structure of /data/dtm
(see above).

**/browse/edr _(and subdirectories)_** 

Browse products for EDRs. This tree follows the structure of /data/edr
(see above).

**/browse/mspec _(and subdirectories)_** 

Browse products for multispectral DIMs. This tree follows the structure
of /data/mspec(see above).


## EDRs

### original EDR format

**compression** 

Individual Viking Orbiter EDR images are intimidatingly large by the
standards of 1975, and unwieldy even by the standards of 1991 (~1.4 MB
counting engineering data). To improve the feasibility of distributing
the EDRs on physical media, the data preparers chose to compress them
with a custom Huffman + first-difference compression algorithm and
include decompression software on the data volumes to permit use.[^2]
This means that each observational product on VO_1001 - VO_1064
consists of a single monolithically compressed file.  This compression
software was highly performant, achieved >60% ratio even on complex
images, and was totally lossless. Unfortunately, the provided
decompression software will not run on any modern operating system,
making the EDRs inaccessible to almost all potential users.
Fortunately, we were able to decompress all EDR files by executing the
PC-DOS version of the binaries in an emulated PC-DOS environment.

**contents** 

Decompressed, each source EDR file contains 5 objects: a PDS3 label, a
raster image, an image histogram table, an “engineering” table, and
a “line header” table. 

We have retained the images, engineering tables, and line header tables;
see the next section for details. We have translated the metadata in
each PDS3 label to PDS4 equivalents but discarded the PDS3 labels
themselves. We have also discarded the image histograms (see appendix
C). 

[^2]: USGS Astrogeology developed a rich suite of in-house fundamental data
processing software in the 1980s and early 1990s; variants of these
tools were used on several other major projects, including Voyager.

### EDR PDS4 product format

Each EDR product in the data collection now consists of four files: 
1. `*.xml` PDS4 label file 
2. `*.fits image` in FITS format 
3. `*_lh.csv`
line header table 
4. `*_eng.csv` engineering table

Note that science validation was not in scope of this project, so
metadata values we generated from values in the PDS3 labels may
propagate errors from these labels. For instance, it is likely that
some TARGET (now `<Target_Identification>` and children) values are
spurious.

All images are 8-bit, single-band, 1056x1204 rasters. The values in
these image arrays are exact copies of the compressed array values from
the source PDS3 objects, which are themselves upsampled versions of the
image components of the 7-bit records from the EDR tapes. We have
formatted them as FITS files with a single (primary) HDU; we chose FITS
because it is a simple, widely-accessible raster format. (It is also
worth noting that, although we did not use the decompression software
to write the FITS headers,  FITS was one of the four ‘realizations’ of
the compressed array values implemented by the software producers.)

Each line header table is 1056 rows. Each row of a line header table
contains metadata for the corresponding line of its associated image
array. We converted these from binary format to CSV to improve
usability. We also discarded columns that contained ‘fill-in’ values,
as well as the average pixel value column. Details on these table
modifications can be found in Appendix A.

The engineering tables are single-row tables containing summary values
and statistics for the observation as a whole. Unlike the images and
line header tables, they were not subjected to intensive quality
control by the producers of the VO1/VO2-M-VIS-2-EDR-V2.0 data set. The
majority of the values in the engineering tables are redundant with the
contents of the line header tables or label metadata, apparently
incorrect (often in spectacular ways), and/or marked as unreliable by
the data providers. If there is useful information in these tables,
retrieving it would require a full-scale recovery effort, and
conversion to PDS4 format would only confuse the issue. For this
reason, we have discarded most of the fields of these tables, and we
suspect that what remains is unreliable: use them with caution if at
all. Like the line header tables, we converted these tables from binary
format to CSV. Details on these table modifications can be found in
Appendix B.


### EDR filenames

EDR ‘stems’ – filenames up to the endings described above – have the
following structure:

`e_{orbit}_{host}_{instrument}_{filter}_ {year}_{month}_{day}_{hour}_{minute}_{second}_{image id}`

**IMPORTANT**: this stem is also used to construct each EDR product’s
PDS4 logical identifier. (This is why some values have been placed in
lowercase, hyphens have been avoided, etc.)

* For most products, ‘orbit’ is a four-digit zero-padded number
  corresponding to the mission-provided orbit number. 
    * ~1% of images have no orbit number: images taken during the cruise
      phase, some other special series, and some images with unclear
      provenance. Images whose metadata indicate that they were taken
      during cruise have ‘cccc’ in this segment. Other images with no
      orbit number have ‘uuuu’ (for ‘unknown’) in this segment.
* ‘host’ is either ‘1’ or ‘2’. It indicates which Viking Orbiter took
   the image.
* ‘instrument’ is either ‘a’ or ‘b’. It indicates which of the Orbiter’s
   cameras took the image. 
* ‘filter’ is a single-letter code indicating the camera’s color filter
   setting. 
    * Options are: ‘c’ : clear, ‘b’: blue , ‘m’: minus blue, ‘v’:
      violet, ‘g’: green, ‘r’: red, ‘u’: unknown.
    * Note that these correspond to the codes used to indicate the
      presence of red, green, and violet bands in the multispectral DIM
      filenames. (The other filters were not used in the production of
      the multispectral tileset.)
* For most products, date and time
  (‘year’, ‘month’, ‘day’, ‘hour’, ‘minute’, ‘second’) are given in ISO
  8601 representation with the ‘T’ and ‘-’ separators replaced with
  underscores. These correspond to mission-reported time of image
  acquisition. All dates and times should be understood as UTC. e.g.,
  `77_09_03_02_25_04` means ‘September 3, 1977, 2:25:04 AM UTC’.
    * Some products, mostly images taken during cruise, have UNKNOWN
      IMAGE_TIME in the source labels. In these files, the date/time
      portion of the filename is set to ‘uu_uu_uu_uu_uu_uu’. 
* ‘image id’ is a lowercase version of IMAGE_ID from the source labels.
   IMAGE_ID (with a leading ‘f’) was used as a filename stem for the
   PDS3 versions of these products, so this field can be used as a
   pointer to those source files.

**examples**

`e_0613_1_b_r_78_02_20_19_16_14_613a62.fits` This is an image taken
during orbit 613 by camera B of VO1’s VIS through its red filter. It
was acquired on February 20, 1978 at 7:16:14 PM UTC and assigned the
IMAGE_ID 613A62.

`e_cccc_2_a_v_uu_uu_uu_uu_uu_uu_218d05_lh.csv` This is the line header
table from an image taken during cruise by camera A of VO2’s VIS
through its violet filter. Like other images taken during cruise, the
onboard electronics did not report an image time. The image was
assigned the IMAGE_ID 218D05.


### ‘errata’ EDRs

Due to the challenges involved in Viking data recovery
(see planetary_image_conversion_task.pdf), many of the EDRs have
confusing artifacts. 6 EDRs were so baffling that the producers of the
original EDR volumes were unable to select a single ‘least bad’
version. They provided two versions of each of those images(on separate
volumes). They noted that both versions were low-quality, but in
different ways, and users should decide which (if either) was most
appropriate for their use case. We have placed these products in a
special ‘errata’ subdirectory. To disambiguate members of a pair from
one another, we have appended a `_v1` and `_v2` to their filename
stems / LIDs. 


## map-projected products

### original map-projected product formats

The source data volumes include four distinct sets of map-projected
products derived from VO EDRs: single-band mosaicked digital image
models (DIM), digital terrain models (DTM), multispectral DIMs, and
shaded relief airbrush maps. All of these products were raster image
files with attached PDS3 labels and embedded image histograms. In all
cases, we have converted the metadata in the PDS3 labels to PDS4
equivalents and discarded the histograms (see appendix C). 

The single-band DIMs were intended to serve as a geodetically- and
radiometrically-controlled “basemap”. Cartographers derived individual
tiles of the DIM from the best-available EDRs for that region of the
Martian surface, often fusing many chronologically-distant EDRs using a
combination of automated and manual techniques. The physical meaning of
the values of these arrays is somewhat unclear from the source
documentation, but they appear to be some type of photometric quantity
scaled and offset for storage as 8-bit unsigned integers.

The multispectral DIMs, by contrast, are a “multi-look” set, designed to
highlight atmospheric and surface variation over time rather than to
work as a stable basemap. Each image in the multispectral DIM set was
produced from EDRs taken through a single filter during a particular
orbital pass, and many regions have coverage at multiple points in
time. Although this is a multispectral set, its products were not
formatted as multiband images: each channel of a ‘potential’
multispectral cube is a distinct file and a distinct PDS3 product. We
have ‘stacked’ each cube into a single PDS4 product (see below for
details). The array values of all multispectral DIMs are scaled,
offset, 0-1 unitless quantities stored as 8-bit unsigned integers;
illumination geometry information is included in the labels for further
photometric processing by end-users. Note that not all multispectral
DIMs have coverage in all bands, and that spatial coregistration is not
always perfect.

The DTMs provide a straightforward elevation model coregistered to the
single-band DIMs. Their array values are scaled, offset elevation
values stored as 16-bit LSB integers.

The shaded airbrush relief maps are lovely, wide-swath images that were
intended primarily for ‘cosmetic’ purposes[^3]. Because they were
basically browse products to start with and lacked sufficient metadata
to straightforwardly convert them to valid PDS4 Product_Observational
products, we have decided to simply include them in this bundle’s
browse collection. 

[^3]: See, for instance, the discussion of airbrush products in McEwen
et al., “Global Color Views of Mars”, LPSC XXV (1995).


### PDS4 map-projected product formats

Each DTM product, single-band DIM product, and multispectral DIM cube
now consists of two files: 
1. `*.xml` PDS4 label file 
2. `*.fits` image
in FITS format

We chose FITS because it is a simple, widely-accessible raster format.
Note that, regardless of product type, all FITS files consist of a
single (primary) FITS HDU. Array size and aspect ratio vary based on
resolution, projection type, geodetic position, and tile swath. The
smallest arrays are around 320x320 and the largest are around
2600x2600; many are highly nonsquare.

The DTMs and single-band DIMs are extremely straightforward FITS
versions of the original rasters. The byteorder of the DTMs has been
swapped (because FITS only supports MSB byteorder), but this makes no
difference from a user’s perspective: the array values of all these
products are exact copies of the array values in the PDS3 source
products. 

We have made somewhat more dramatic changes to the multispectral DIMs.
The data providers clearly intended each multispectral tile to be
interpreted as a multi-band cube. We believe that their choice to store
each channel as a separate file was a nod to the memory limitations of
early-90s workstations, and that ‘stacking’ them into multiband images
better fulfills their original intent than leaving them as split
channels. For this reason, we have concatenated each multispectral DIM
cube into a single multiband array formatted as a single PDS4 product.
Because PDS4 sensibly discourages the use of per-band scaling factors
and offsets, we have applied the conversion factors specified in the
source products before stacking them. Each multispectral DIM image is
now a 1-4 band array of 0-1 I/F values, stored as 16-bit MSB
floating-point. (The number of bands is variable because not all
multispectral DIMs include all bands; also note that tile coverage may
not be the same in all bands, and spatial coregistration is
occasionally imperfect.) We have included the original scaling factor
and offset for each band in the PDS4 labels as structured text in
Product_Observational/File_Area_Observational/Array_3D_Image/description.


### map-projected product filenames

**single-band products** 

For the DTM and single-band DIM products, we simply retained the naming
convention from the PDS3 source products. Filename ‘stems’ – filenames
up to the extensions described above – have the following structure:

`{file type code}{resolution code}{latitude}{latitude direction}{longitude}`

As in the EDRs, this stem is also used as the final portion of the product's
PDS4 LID.

* File type code is ‘m’ for a DIM file, ‘t’ for a DTM file. 
* The resolution code expresses the resolution of the image in
  degrees/pixel. Options are:
    * ‘c’ for 1/4
    * ‘d’ for 1/8
    * ‘e’ for 1/16 
    * ‘f’ for 1/32
    * ‘g’ for 1/64 
    * ‘h’ for 1/128
    * ‘i’ for 1/256
    * ‘j’ for 1/512
    * ‘k’ for 1/1024
* Latitude is the central latitude of the image, rounded down to the
  nearest whole number
* Longitude direction is n for north, s for south
* Longitude is the central longitude of the image, rounded down to the
  nearest whole number. **IMPORTANT**: in order to allow users to
  easily cross-reference auxiliary data and PDS3 source products, the
  longitude portion of these filenames has not been changed to reflect
  the cartographic conversion to Positive East.

**multi-band products** 

We have changed the multispectral DIM naming convention for two reasons.
First, we prefer filename stems to match PDS4 LIDs when possible.
However, many multispectral DIMs have duplicate filenames because they
are views of the same region at different times. (They were
disambiguated in the source volumes by placement in per-orbit
directories). Second, the source filenames contain filter information,
but only in their extensions(e.g. “.red”, “.grn”), and placing
nonstandard extensions on files often creates burdens for end-users. We
have therefore chosen to move orbit and filter information into their
filenames. We also believe this matches the data producers’ intentions
better. It is similar to how they constructed the IMAGE_ID values for
these products; their file naming choices were likely a compromise with
the 8 + 3 filename length restriction of 90s-era operating systems.

The filename convention for multispectral DIMs is:

`{file type code}{resolution code}{latitude}{latitude direction}{longitude}_{filters}_{orbit}_{orbiter}`

* file type code, resolution code, latitude, and longitude mean the same
  things they do in the DTMs and single-band DIMs.
    * **Note:** the data producers used a slightly different naming
        convention for a small number of ‘special’ multispectral
        products that present oblique views of a region. The first
        letter of these images’ filenames indicates geometric
        orientation rather than filetype: ‘n’, ‘s’, ‘e’, ‘w’ for views
        from the North, South, East, and West respectively. We have
        retained this convention.
* ‘filters’ is a 1-4 character string indicating the bands present in
   the image cube. Although the multispectral tile set contains data
   from EDR images taken through the red, green, and violet filters,
   not every tile contains a channel from each filter. Each letter in
   this string is a code that identifies one of the bands in the image.
   The filter codes in the filename appear in the same order their
   associated bands appear in the file. 
    * The codes are: ‘r’: red; ‘s’: synthetic green; ‘v’: violet; ‘g’:
      green. Note that these correspond to the codes used in the EDR
      filenames for red, violet, and green.
    * _What is ‘synthetic green’_? Because a large subset of the
       multispectral tiles were created from only red and violet EDRs,
       the cartographers created ‘synthetic green’ bands for every tile
       with red and violet bands – even if the tile had a ‘real’ green
       band as well – to permit easy color display of red-violet images
       and to facilitate visual comparisons between red-violet and
       red-green-violet tiles. These synthetic green images are the
       result of a series of averaging operations on the I/F values of
       the red and violet images (see mdim_dtm_volinfo_1998.txt for
       more detail). Images without both a red and a violet band have
       no synthetic green band.
* ‘orbit’ is the four-digit 0-padded mission-provided orbit number. It
   corresponds (at least nominally) to the orbit number of the EDRs the
   cartographers used to generate the tile.
* ‘orbiter’ is 1 for VO1, and 2 for VO2.


### cartography conversion to PDS4

The map-projected PDS3 source products include three types of map
projection: sinusoidal equal-area, orthographic, and polar. 

**sinusoidal** 

The vast majority of these products—the ‘primary’ mosaic series—were
sinusoidally projected. The projection transformations for these
products were well-documented within the PDS3 source volumes. However,
PDS4 standards for cartographic information require explicit
specification of Cartesian coordinates for a reference pixel within the
projected array, and these are not given in the source metadata. To
produce these, we followed the transformation equations provided in the
source documentation to convert line and sample offsets to
planetographic degrees, then used the provided scale and resolution
factors to back-calculate the position of the upper-left pixel of each
tile. Also, these projections were originally specified in Positive
West longitude. We dared to go East, following modern conventions for
Martian longitude, and converted all values to Positive East.

**polar** 

The metadata provided in the PDS3 labels and their accompanying
documentation, along with the (quite sparse) information about the
polar projection in documentation, did not result in realistic/reliable
Cartesian coordinates, meaning that we were unable to specify these map
projections to PDS4 standard. For this reason, we did not include
cartographic information in the labels of the polar stereographic
products in this bundle.

**orthographic** 

Although there is almost no documentation available for the handful of
orthographically-projected products (all of which are ‘special’
multispectral DIMs), we were able to determine the geodetic coordinates
of their upper-left pixels using inverse spheroid geodesic
calculations (as implemented in `pyproj` 3.3.0). To find the upper-left
pixel’s y position, we calculated the distance from the intersection of
the projection origin latitude and the west bounding longitude to the
intersection of the north and west lat/lon bounds. To find the
upper-left pixel’s x position, we calculated the distance from the
intersection of the latitude of the north bounding coordinate and the
central meridian to the intersection of the north and west lat/lon
bounds (based on the spheroid geodesic). Like the sinusoidal products,
we also converted the longitude values in these products from Positive
West to Positive East.


### 'errata' map projected products

**incorrect IMAGE_ID for filename**

PDS3 versions of two DTMs (filenames te90s000.img and tg90s000.img) had an 
IMAGE_ID that did not match their filenames and implied an incorrect latitude 
(the opposite pole). The PDS4 versions of these products refer to their 
source identifiers using what we believe the appropriate IMAGE_ID _should 
have been_ -- in other words, one that matches the original filename.

The multispectral DIMs in special/334sp (originally from VO_2010) also had 
IMAGE_IDs that did not match their filenames, implying a longitude value of 
282 as opposed to the value of 78 implied by their filenames, After 
investigating the location of the target, we retained the longitude in the 
filenames as the correct value and propagated it to their source identifiers.

**erroneously written DIMs**

A couple of DIMs (mg25s177 and mi25s177) had data from a different image for
one third of their arrays. These were re-released in the DTM volume (VO_2007)
in an errata folder. We have only included the corrected versions in this
bundle.

**missing source EDRs**

A handful of DIMs (mi80n110, mi80n010, mg80n010, and mg80n110) refer to
EDR source images that do not appear to exist in the EDR corpus. The
referenced EDR IMAGE_IDs are 710B07 and 793B03.


## document collection

**IMPORTANT**: some of the documents in this collection are wholly or
partially deprecated by the ways in which the Viking observational
data has been reformatted or reorganized in this bundle. Specific
notes on these deprecations are contained in this file (as well as
individual product labels). Despite being partially deprecated, these
files have been included as they provide a great deal of useful
information on the contents, history, calibration, reduction, and
general character of this data set.

`edr_volinfo.txt` 
PDS3 volinfo file for the Viking EDR dataset. The function of PDS3
volinfo files was not standardized at this time. This one is an
overview of the mission, data preparation, disk structure, file
organization, and data compression methods in regards to the EDR
files. **WARNING**: It should be considered partially deprecated. Users
should ignore references to file types, storage media, and directory
structure; users should also disregard descriptions of PDS3 label
features except inasmuch as they shed light on what metadata were
generated by the mapmakers. Furthermore, the contents of the
engineering and line header tables have been changed in the PDS4
versions of these products and users are advised to disregard the
references to byte positions and use the data descriptions only in
conjunction with the caveats given in the relevant sections above and
in appendices A and B.

`mdim_dtm_volinfo_1992.txt` 
PDS3 volinfo file for the Viking map projected single-band DIM and DTM
products. This volinfo file contains an overview of the mission, data
preparation, compilation information, as well as file organization and
contents for the original PDS3 volumes VO_2001 - VO_2007
(VO_2001 - VO_2006 contain the low resolution single-band DIM products
while VO_2007 contains the DTM products). **WARNING**: It should be
considered partially deprecated. Users should ignore references to file
types, storage media, and directory structure; users should also
disregard descriptions of PDS3 label features except inasmuch as they
shed light on what metadata were generated by the mapmakers. It
nevertheless provides a great deal of useful information on the
contents, history, calibration, reduction, and general character of
this data set.

`mdim_dtm_volinfo_1998.txt` 
PDS3 volinfo file for the Viking high resolution map projected DIM
(single band and multispectral) and DTM products. This volinfo file
covers much of the material in `mdim_mspec_volinfo_1992.txt` and
`mdim_dtm_volinfo_1992.txt` and includes descriptions of the original
PDS3 volumes  VO_2015 - VO_2022. **WARNING**: It should be considered
partially deprecated. Users should ignore references to file types,
storage media, and directory structure; users should also disregard
descriptions of PDS3 label features except inasmuch as they shed light
on what metadata were generated by the mapmakers.

`mdim_mspec_volinfo_1992.txt` 
PDS3 volinfo file for the Viking map projected multispectral DIM
products. This volinfo file contains an overview of the mission, data
preparation, and  compilation/correction information, as well as file
organization and contents for the original PDS3 volumes VO_2008 -
VO_2014. **WARNING**: It should be considered partially deprecated.
Users should ignore references to file types, storage media, and
directory structure; users should also disregard descriptions of PDS3
label features except inasmuch as they shed light on what metadata were
generated by the mapmakers.

`planetary_image_conversion_task.pdf` 
Postmortem report on the Planetary Image Conversion Task, a 1983-1984
effort, primarily conducted at JPL, to convert JPL's archive of
planetary images to standard formats and write them to more stable
storage media. This project included all Viking Orbiter EDRs. We have
included it to help provide context on the history and provenance of
the data, including possible sources of artifacts, errors, glitches, or
gaps. We copied this document from the NASA Technical Reports Server
and converted it from PDF to PDF/A. The text is unchanged.

`primary_bundle_documentation.md`
The file you are reading right now.

`softinfo.txt` 
Describes the custom Huffman + first-difference compression algorithm
used for the compression of the Viking EDR PDS3 files and the
decompression software included with their original release. These
files have been decompressed as a part of the conversion to PDS4 and
therefore this information is for reference to the prior state of the
PDS3 source files and is deprecated with respect to the PDS4 versions.

`mspec_special_info.txt` 
This document concatenates the various 'imginfo.txt' files provided in
the subdirectories of the 'special' directories on the multispectral
volumes of VO1_VO2-M-VIS-5-DIM-V1.0. These texts explain the contents,
purpose, and provenance of the 'special' multispectral DIMs whose
converted versions may be found in the subdirectories
of /data/mspec/special and /browse/mspec/special in this bundle. Please
note that some elements of this document are deprecated -- for
instance, we did not preserve the browse products, so any notes about
special GIF formatting are now irrelevant. 


## browse collection

*a small caveat:* Because all our browse products are contrast-stretched
 (described in detail below), we caution users against drawing physical
 conclusions from visual comparison of browse images.


### general notes (applicable to all browse products)

Every observational data product in the data collection has an
associated browse product. Each browse product shares a filename stem
with its associated observational product. Similarly, the final portion
of the LID of each browse product is identical to that of its
associated observational product, but with `_browse` appended.


### EDR browse products

EDR browse products consist of four files:
* `{associated_observational_file_stem}_browse.xml`: PDS4 label
* `{associated_observational_file_stem}.png`: filtered browse image
* `{associated_observational_file_stem}_base.png`: unfiltered browse
  image
* `{associated_observational_file_stem}_masked.png`: unfiltered and
  masked browse image

**‘filtered’ browse image** 

The source documentation provides a prose description of a preferred
filtering algorithm for browse products. No implementation of that
algorithm is available, but we wished to provide browse images that
embody what the data providers considered ‘good’ representations of the
EDRs, so we implemented our own version. It works like this:

* Generate a mask array by applying a maximum filter with a 4x4 kernel
  to the image and comparing the output of the filter to the unfiltered
  image. Define all pixels for which the unfiltered image is 0 and the
  maximum-filtered image is not 0 as masked. 
* Apply a 4x4 median filter to the unfiltered image. Do not include
  values that are masked in the median calculation. This effectively
  fills in small 0-valued areas (which are generally artifacts) without
  overwriting contiguous 0-valued areas (which tend to be actually
  representative of the target). 

We then enhance image contrast by clipping the filtered image’s values
at their 0.25th and 99.5th percentiles (excluding 0s). For very ‘dark’
images (images whose 99th percentile is 0) we do not apply this clip.

**‘base’ browse image** 

Because some artifacts are of potential interest, and this filtering
algorithm is not necessarily appropriate for all use cases, we also
provide a non-filtered PNG browse image. We applied the same contrast
enhancement to these images as the filtered images.

**‘masked’ browse image** 

Finally, to help users identify possible artifacts, we provide
a ‘masked’ browse image. This is identical to the ‘base’ browse image,
but all 0 values are masked in cyan.


### DTM and single-band DIM browse products

DTM and single-band DIM browse products consist of three files:
* `{associated_observational_file_stem}_browse.xml`: PDS4 label
* `{associated_observational_file_stem}_browse.png`: unmasked browse
  image
* `{associated_observational_file_stem}_masked.png`: masked browse
  image

**unmasked browse image** 

Contrast-enhanced PNG browse image. Generally, we clip array values at
their 1st and 99th percentiles (zeros excluded). However, if an image
is dark enough(its 99th percentile is 0) or bright enough (its 1st
percentile is 255), we do not apply that half of the clip. 

**masked browse image**

We also provide a ‘masked’ browse image to help users identify missing
data values. These are identical to the unmasked browse images, except
that 0-valued pixels are masked in cyan.


### multispectral DIM browse products

Multispectral DIM browse products consist of 2 files:
* `{associated_observational_file_stem}_browse.xml`: PDS4 label
* `{associated_observational_file_stem}_browse.png`: browse image

To generate a browse image for a multispectral cube, we first assign
each of its bands to an red/green/blue (RGB) color channel. Image bands
taken through the red filter are always assigned to R, and image bands
taken through the violet filter are always assigned to B. If an image
band taken through the green filter is available, it is assigned to G;
if it is not, but a ‘synthetic green’ band is available, that band is
assigned to G. If no appropriate band is available for a given channel,
we set that channel to black. **IMPORTANT**: As ‘real’ green-filter
bands are not available for all cubes, we caution users against
comparing two browse images without first considering which type of
data occupies the green channel. 

Then, we clip the overall values of the multispectral cube (not per-band
values)[^4] at their 0.5th and 99.5th percentiles; if an image is dark
enough (any channel’s 99.5th percentile is 0), we do not clip it.

[^4]: It is intuitively appealing to individually stretch the image
bands. Planetary scientists often call images produced in this
way ‘enhanced color’ images; it is a form of what, in other contexts,
is sometimes referred to as ‘white balancing’. Unfortunately, naive
versions of this process produced unsatisfying results for the
multispectral DIMs, so we have provided only ‘natural color’
contrast-stretched images.


### shaded airbrush relief map browse products

The shaded airbrush relief maps are wide-swath images intended primarily
for ‘cosmetic’ purposes. Little information is given about the creation
of these airbrush products in the source documentation. The original
PDS3 source products are IMG files with attached PVL headers and
embedded histograms. As with all other products in this bundle, we
discarded the histograms (see Appendix C). Because the PVL labels for
these airbrush products lacked sufficient metadata to straightforwardly
convert them to valid PDS4 Product_Observational objects, and they were
basically aesthetic artifacts in the first place, we chose to simply
convert them to browse products. We did not include projection
information in these PDS4 products.

These products are PNG-encoded versions of the shaded airbrush relief
map tiles. They use the following filename convention:

`s{resolution code}{latitude}{latitude direction}{longitude}.png`

* The resolution code expresses the resolution of the image in
  degrees/pixel. Options are:
    * ‘c’ for 1/4
    * ‘e’ for 1/16 
* Latitude is the central latitude of the image, rounded down to the
  nearest whole number 
* Longitude direction is n for north, s for south
* Longitude is the central longitude of the image, rounded down to the
  nearest whole number.


## appendix A: EDR line header table modifications

Two columns present in the line header tables from the PDS3 source
products were dropped from the PDS4 products: FILL_IN and
AVERAGE_PIXEL. FILL_IN was an unused filler column. AVERAGE_PIXEL was
supposed to provide the average pixel value for the pixels in the line,
however the values were out of the range of possible pixel values and
the data type of this column was not set up to actually support valid
values. Additionally, the PDS3 source products allocated 8 bytes to
describe the 7 track segments in the EMBEDDED_SCIENCE_DATA columns. The
final byte was always zero. (This padding byte was described in dataset
documentation, but not the products’ format files.) We omitted it from
the PDS4 products.


## appendix B: EDR engineering table modifications

The engineering tables had most of the columns in them dropped in their
PDS4 versions below are the names of each dropped column and the
rationale for removing them. As the engineering tables underwent less
quality control than the other objects in the PDS3 source files, any
information redundant with the label or line header table was removed
from the engineering tables as they were considered less reliable.

**PHYSICAL_SEQUENCE_NUMBER**: unused filler column

**LOGICAL_SEQUENCE_NUMBER**: unused filler column

**FIRST_ERT**: redundant with label; noted as unreliable in PDS3 source
  documentation

**FIRST_ERT_MINUTE**: redundant with label; noted as unreliable in PDS3
  source documentation

**FIRST_ERT_MILLISECOND**: redundant with label; noted as unreliable in
  PDS3 source documentation

**LAST_ERT**: noted as unreliable in PDS3 source documentation; rarely
  matched a reasonable value relative to the FIRST_ERT in label

**LAST_ERT_MINUTE**: noted as unreliable in PDS3 source documentation;
  rarely matched a reasonable value relative to the FIRST_ERT in label

**LAST_ERT_MILLISECOND**: noted as unreliable in PDS3 source
  documentation; rarely matched a reasonable value relative to the
  FIRST_ERT in label

**FILL_IN**: unused filler column

**TRACK_PRESENCE_MASK**: redundant with line header table

**UNUSED_1**: unused filler column

**UNUSED_2**: unused filler column

**UNUSED_3**: unused filler column

**UNUSED_4**: unused filler column

**UNUSED_5**: unused filler column

**UNUSED_6**: unused filler column

**IMAGE_ID**: redundant with label _NOTE:_ `EDR_ID` in the current table
  refers to EDR Tape ID (details in edr_volinfo.txt) not IMAGE_ID

**TRANSMITTED_CODE_WORD1**: most values redundant with label; data
  quality indicator decoded and retained as text in new column named
  `TRANSMITTED_CODE_WORD_1_DQI`; cathode current flag information has
  been retained as ON/OFF in the PDS4 label under CATHODE_CURRENT

**TRANSMITTED_CODE_WORD2**: most values redundant with label; data
  quality indicator decoded and retained as text in new column named
  `TRANSMITTED_CODE_WORD_2_DQI`

**RECEIVED_CODE_WORD**: most values redundant with label; data quality
  indicator decoded and retained as text in new column named
  `RECEIVED_CODE_WORD_DQI`


## appendix C: discarded image histograms

Almost all the PDS3 source products for this bundle contained
IMAGE_HISTOGRAM objects. The data providers included them for
optimization purposes, so that, e.g., image display applications could
use them to determine appropriate contrast and brightness parameters
for a specific CRT display without loading the entirety of the array
into main memory. However, 1.4 MB is no longer a challenging amount of
memory, so discrete histogram tables would be quaint historical
curiosities at best. We have discarded all IMAGE_HISTOGRAM objects.
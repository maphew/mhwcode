# pdf2jpg

Some windows batch files to convert PDF to images using Ghostscript.

## Requires

`gswin64c` - doing the conversion

`touch` - for setting output JPG to same timestamp as input PDF

`rsync` - not actually used anymore, but setenv script relies on it being present
*(TODO: change to use touch instead.)*

## Setup

Edit *call* statement in `setenv.gs` to point to where Ghostscript is installed.



## Usage

**`setenv`**

**`pdf2jpg`**

 Convert a PDF to JPG using Ghostscript, to the specified page size in inches
 (specify "#" to use internal bounding box)

 Usage: pdf2jpg infile.pdf [width, #] [height, #]


**`pdf2jpg-all`**

 Usage:  pdf2jpg-all [path\to\folder]


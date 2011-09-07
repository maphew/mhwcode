#@+leo-ver=5-thin
#@+node:maphew.20100428145300.1263: * @file extract-pdf-img.py
# Extract jpg's from pdf's. Quick and dirty.
import sys

pdf = file(sys.argv[1], "rb").read()

startmark = "\xff\xd8"
startfix = 0
endmark = "\xff\xd9"
endfix = 2
i = 0

njpg = 0
while True:
    istream = pdf.find("stream", i)
    if istream < 0:
        break
    istart = pdf.find(startmark, istream, istream+20)
    if istart < 0:
        i = istream+20
        continue
    iend = pdf.find("endstream", istart)
    if iend < 0:
        raise Exception("Didn't find end of stream!")
    iend = pdf.find(endmark, iend-20)
    if iend < 0:
        raise Exception("Didn't find end of JPG!")

    istart += startfix
    iend += endfix
    print "JPG %d from %d to %d" % (njpg, istart, iend)
    jpg = pdf[istart:iend]
    jpgfile = file("jpg%d.jpg" % njpg, "wb")
    jpgfile.write(jpg)
    jpgfile.close()

    njpg += 1
    i = iend
#@-leo

import os
from os import listdir
import sys
from sys import argv
from gamera.core import *
init_gamera()

'''
Note: nolabel-check.py currently cannot handle dotted lines! Also presently ignores
letters attached to the figures by any black pixels.
'''

path = "/home/chris/Github/x_eu-images/diag/"
work = sys.argv[-1]

if not os.path.exists(path + work + "/separate_check/"):
  os.makedirs(path + work + "/separate_check/")
if not os.path.exists(path + work + "/separate_fail/"):
  os.makedirs(path + work + "/separate_fail/")

fileList = listdir(path + work + "/selections")

for f in fileList:
  if ".png" not in f and ".tif" not in f:
    pass

  else:
    img = load_image(path + work + "/selections/" + f)

    img = img.to_onebit()
    highlight = img.to_rgb()

    ccs = img.cc_analysis()

    for c in ccs:
      a = (float(c.nrows)/float(img.nrows)) * (float(c.ncols)/float(img.ncols))
      ar = float(c.nrows) / float(c.ncols)

      if ar < 4 and ar > 0.25:
        if a < 0.10:
          highlight.highlight(c, RGBPixel(125,125,125))
          

    if ".tif" in f:
      highlight.save_tiff(path + work + "/separate_check/" + f)
    else:
      highlight.save_PNG(path + work + "/separate_check/" + f)

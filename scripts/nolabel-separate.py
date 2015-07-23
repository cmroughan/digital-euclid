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

if not os.path.exists(path + work + "/separate_alphabetic/"):
  os.makedirs(path + work + "/separate_alphabetic/")
if not os.path.exists(path + work + "/separate_geometric/"):
  os.makedirs(path + work + "/separate_geometric/")

fileList = listdir(path + work + "/separate_check")

for f in fileList:
  if ".png" not in f and ".tif" not in f:
    pass

  else:
    img = load_image(path + work + "/selections/" + f)

    img = img.to_onebit()
    highlight_alpha = img.to_rgb()
    highlight_geo = img.to_rgb()

    ccs = img.cc_analysis()

    for c in ccs:
      a = (float(c.nrows)/float(img.nrows)) * (float(c.ncols)/float(img.ncols))
      ar = float(c.nrows) / float(c.ncols)

      if ar < 4 and ar > 0.25:
        if a < 0.10:
          highlight_geo.highlight(c, RGBPixel(255,255,255))
        else:
          highlight_alpha.highlight(c, RGBPixel(255,255,255))
      else:
        highlight_alpha.highlight(c, RGBPixel(255,255,255))

    if ".tif" in f:
      highlight_alpha.save_tiff(path + work + "/separate_alphabetic/" + f)
      highlight_geo.save_tiff(path + work + "/separate_geometric/" + f)
    else:
      highlight_alpha.save_PNG(path + work + "/separate_alphabetic/" + f)
      highlight_geo.save_PNG(path + work + "/separate_geometric/" + f)

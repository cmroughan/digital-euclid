import os
from os import listdir
import sys
from gamera.core import *
init_gamera()


def hline_training(work):
  hline_height = []
  fileList = listdir("/home/chris/Github/x_eu-images/diag/" + work + "/hline/")
  for f in fileList:
    img = load_image
    if img.data.pixel_type != ONEBIT:
      img = img.to_onebit()
    ccs = img.cc_analysis()

    for c in ccs:
      hline_height.append(c.nrows)

  return hline_height


def vline_training(work):
  vline_width = []
  fileList = listdir("/home/chris/Github/x_eu-images/diag/" + work + "/vline/")
  for f in fileList:
    img = load_image
    if img.data.pixel_type != ONEBIT:
      img = img.to_onebit()
    ccs = img.cc_analysis()

    for c in ccs:
      vline_width.append(c.ncols)

  return vline_width


def character_training(work):
  character_sizes = []
  fileList = listdir("/home/chris/Github/x_eu-images/diag/" + work + "/text/")
  for f in fileList:
    img = load_image
    if img.data.pixel_type != ONEBIT:
      img = img.to_onebit()
    ccs = img.cc_analysis()

    for c in ccs:
      character_sizes.append(c.ncols, c.nrows)

  return character_sizes
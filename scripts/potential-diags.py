import os
from os import listdir
import sys
import numpy as np
from numpy import array
import PIL
from PIL import Image as Im
import pickle
from diagram_toolkit import rm_endpages
from repo_management import load_diagDirectory, status_update

"""
An initial script that runs through the pages and gathers useful information
about the images, typical connected components, and layouts.

Takes input regarding diagram layouts (marginal/inline/top/mixed and always_left/
always_right/alternating/mixed) to make better judgements.

Returns pickled information that can be further filtered down if necessary as well 
as a visual check.
"""

# Request work ID, confirm directory exists, and record path information
path, work, extension = load_diagDirectory()

fileList = sorted(listdir(path + work + "/" + extension))

# Remove endpages and save that info for future runs
skip = rm_endpages(path, work, extension)


# Start Gamera portion of program

from gamera.core import *
init_gamera()
from gamera.plugins import draw
from diagram_toolkit import is_outlier, rect_extend_boundaries, find_margins
from diagram_toolkit import to_rectGeneral, to_rectGamera, filter_areas

# These lists and dictionary will be exported so later scripts can use 
# the normal areas, line widths/heights, and page dimensions and margins

page_max_norm_areas = {}
page_min_norm_areas = {} 
vline_width = []
hline_height = []
page_dimensions = {}
page_margins = {}
possDiags_initial = {}

if not os.path.exists(path + work + "/check/"):
  os.makedirs(path + work + "/check/")

for f in fileList:
  if f in skip:
    pass
  else:
    if ".png" in f:
      name = f[:-4]
    elif ".tiff" in f:
      name = f[:-5]
    elif ".tif" in f:
      name = f[:-4]

    img = load_image(path + work + "/" + extension + "/" + str(f))

    if img.data.pixel_type != ONEBIT:
      print "WARNING: Image " + f + " not yet binarized.\nBinarizing..."
      img = img.to_onebit()

    # Grab page dimensions
    page_dimensions[str(f)] = img.ncols, img.nrows

    # Grab margins and account for margin of error
    leftMargin, rightMargin = find_margins(img)
    if leftMargin > 0.03 * img.ncols:
      leftMargin = leftMargin - int(0.03 * img.ncols)
    else:
      leftMargin = 0
    if rightMargin < 0.97 * img.ncols:
      rightMargin = rightMargin + int(0.03 * img.ncols)
    else:
      rightMargin = img.ncols

    page_margins[str(f)] = leftMargin, rightMargin
      
    highlight = img.to_rgb()

    #img = img.kfill_modified()

    possDiags_initial[str(f)] = []
    possDiags_filtered = []
    notDiags = []
    ccs = img.cc_analysis()

# Determine area outliers and get max/min non-outlier areas

    filtered = filter_areas(ccs)
    max_norm_area = np.amax(filtered)
    min_norm_area = np.amin(filtered)

    page_max_norm_areas[name] = max_norm_area
    page_min_norm_areas[name] = min_norm_area
  
    for c in ccs:
      a = ((float(c.ncols)/float(img.ncols)) * (float(c.nrows)/float(img.nrows)))
      ar = float(c.nrows) / float(c.ncols)
      x_offset = float(c.offset_x) / float(img.ncols)
      y_offset = float(c.offset_y) / float(img.nrows)

# Catches page edges

      if x_offset < 0.03 or x_offset > 0.97:
        highlight.highlight(c, RGBPixel(125,125,125))
        del c
        pass
      elif y_offset < 0.05 or y_offset > 0.95:
        highlight.highlight(c, RGBPixel(125,125,125))
        pass
        del c

# Catches 'definite' lines, based on surpassing a certain aspect ratio
# Note: these are not definite line *diags*
# Quite possible that this picks up page edges, crit app dividers, etc

      elif ar > 10 and a > (0.01 * min_norm_area):
        vline_width.append(c.ncols)
        highlight.highlight(c, RGBPixel(0,255,0))
        possDiags_filtered.append(Rect(c))
        possDiags_initial[str(f)].append(to_rectGeneral(Rect(c)))
      elif ar < 0.1 and a > (0.01 * min_norm_area):
        hline_height.append(c.nrows)
        highlight.highlight(c, RGBPixel(0,255,0))
        possDiags_filtered.append(Rect(c))
        possDiags_initial[str(f)].append(to_rectGeneral(Rect(c)))

# Catches large rois (potential 'quad' diags)

      elif a > (max_norm_area * 3):
        highlight.highlight(c, RGBPixel(255,0,0))
        possDiags_filtered.append(Rect(c))
        possDiags_initial[str(f)].append(to_rectGeneral(Rect(c)))

# Catches potential lines

      elif ar > 4 and a > (0.01 * min_norm_area):
        highlight.highlight(c, RGBPixel(0,0,255))
        possDiags_filtered.append(Rect(c))
        possDiags_initial[str(f)].append(to_rectGeneral(Rect(c)))

      elif ar < 0.25 and a > (0.01 * min_norm_area):
        highlight.highlight(c, RGBPixel(0,0,255))
        possDiags_filtered.append(Rect(c))
        possDiags_initial[str(f)].append(to_rectGeneral(Rect(c)))

# Remainder

      elif a < (max_norm_area * 3):
        pass
        highlight.highlight(c, RGBPixel(125,125,125))
        del c
(
# Tries to suppress false positives within the text

    compare = {}
    for c1 in possDiags_filtered:
      compare[c1] = [c1.ncols * c1.nrows, [], c1.nrows, []]
      for c2 in notDiags:
        if c1.distance_bb(c2) < 100:
          compare[c1][1].append(c2.ncols * c2.nrows)

    for key in compare:
      closeAreas = 0
      for c2area in compare[key][1]:
        if c2area > compare[key][0] * 0.9 and c2area < 1.1 * compare[key][0]:
          closeAreas = closeAreas + 1

      closeHeights = 0
      for c2height in compare[key][3]:
        if c2height > compare[key][2] * 0.45 and c2height < 2.2 * compare[key][2]:
          closeHeights = closeHeights + 1

      if len(compare[key][1]) == 0:
        pass
      elif (closeAreas/len(compare[key][1])) > 0.75:
        possDiags_filtered.remove(key)
        notDiags.append(key)
      elif (closeHeights/len(compare[key][3])) > 0.75:
        possDiags_filtered.remove(key)
        notDiags.append(key)

# Extend cc boundary boxes, find overlap, and export resulting images

    for c in possDiags_filtered:
      c = rect_extend_boundaries(c, (img.ncols, img.nrows), 160)

    x = 0
    for x in range(0,4):
      for n in range(0, len(possDiags_filtered)):
        for m in range(0, len(possDiags_filtered)):
          if n == m:
            pass
          else:
            if possDiags_filtered[n].intersects(possDiags_filtered[m]):
              possDiags_filtered[n].union(possDiags_filtered[m])
      x = x + 1

    possDiags_filtered = set(possDiags_filtered)
    possDiags_filtered = list(possDiags_filtered)

    j = 0
    done = []
    for c in possDiags_filtered:
      j = j + 1
      if c not in done:
        highlight.draw_hollow_rect(c, RGBPixel(0,0,255), 7.0)
        done.append(c)

    highlight.save_PNG(path + work + "/check/" + name + ".png")

    j = 0
    for c in ccs:
      c.to_xml_filename("/home/chris/" + name + str(j) + ".xml")
      j = j + 1

# Create empty corrections directory in case any are necessary

if not os.path.exists(path + work + "/corr/"):
  os.makedirs(path + work + "/corr/")

# Pickle assorted data

max_area_record = open('/home/chris/Github/digital-euclid/intermediate/diag/' + work + '/pickled/page_max_norm_areas.pickle', mode ='wb')
pickle.dump(page_max_norm_areas, max_area_record)
max_area_record.close()

min_area_record = open('/home/chris/Github/digital-euclid/intermediate/diag/' + work + '/pickled/page_min_norm_areas.pickle', mode ='wb')
pickle.dump(page_min_norm_areas, min_area_record)
min_area_record.close()

vline_record = open('/home/chris/Github/digital-euclid/intermediate/diag/' + work + '/pickled/vline_widths.pickle', mode ='wb')
pickle.dump(vline_width, vline_record)
vline_record.close()

hline_record = open('/home/chris/Github/digital-euclid/intermediate/diag/' + work + '/pickled/hline_heights.pickle', mode ='wb')
pickle.dump(hline_height, hline_record)
hline_record.close()

dimension_record = open('/home/chris/Github/digital-euclid/intermediate/diag/' + work + '/pickled/page_dimensions.pickle', mode ='wb')
pickle.dump(page_dimensions, dimension_record)
dimension_record.close()

endpage_record = open('/home/chris/Github/digital-euclid/intermediate/diag/' + work + '/pickled/endpages.pickle', mode ='wb')
pickle.dump(skip, endpage_record)
endpage_record.close()

possDiags_record = open('/home/chris/Github/digital-euclid/intermediate/diag/' + work + '/pickled/possDiags_initial.pickle', mode = 'wb')
pickle.dump(possDiags_initial, possDiags_record)
possDiags_record.close()

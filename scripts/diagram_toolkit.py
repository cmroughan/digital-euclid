#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np #is_outlier
import PIL #rm_endpages
from PIL import Image as Im #rm_endpages
from gamera.core import *  #Gamera CCs
from gamera.plugin import *
init_gamera()
from gamera.plugins import projections, draw
import os #rm_endpages
from os import listdir #rm_endpages
import sys #rm_endpages
import pickle #rm_endpages


def is_outlier(points, thresh=3.5):
  '''
  Returns a boolean array with True if points are outliers and False 
  otherwise.

  Parameters:
  -----------
    points : An numobservations by numdimensions array of observations
    thresh : The modified z-score to use as a threshold. Observations with
      a modified z-score (based on the median absolute deviation) greater
      than this value will be classified as outliers.

  Returns:
  --------
    mask : A numobservations-length boolean array.

  References:
  ----------
    Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
    Handle Outliers", The ASQC Basic References in Quality Control:
    Statistical Techniques, Edward F. Mykytka, Ph.D., Editor. 
  '''
  if len(points.shape) == 1:
    points = points[:,None]
  median = np.median(points, axis=0)
  diff = np.sum((points - median)**2, axis=-1)
  diff = np.sqrt(diff)
  med_abs_deviation = np.median(diff)

  modified_z_score = 0.6745 * diff / med_abs_deviation

  return modified_z_score > thresh


def add_areas(c1_left,c1_right,c1_top,c1_bottom,c2_left,c2_right,c2_top,c2_bottom):
  '''
  Accepts as input the coords for two boxes, then returns the coords of the
  box that contains both of them.

  Parameters:
  -----------
    c1_(left/right/top/bottom) : the pairs of x and y values for the first box
    c2_(left/right/top/bottom) : the pairs of x and y values for the second box

  Returns:
  --------
    A string containing the coords of a box containing both areas
  '''
  if c1_left <= c2_left:
    offset_x = c1_left
  elif c1_left >= c2_left:
    offset_x = c2_left

  if c1_top <= c2_top:
    offset_y = c1_top
  elif c1_top >= c2_top:
    offset_y = c2_top

  if c1_right >= c2_right:
    width = c1_right - offset_x
  elif c1_right <= c2_right:
    width = c2_right - offset_x

  if c1_bottom >= c2_bottom:
    height = c1_bottom - offset_y
  elif c1_bottom <= c2_bottom:
    height = c2_bottom - offset_y

  return str(offset_x) + "," + str(offset_y) + "," + str(width) + "," + str(height)


def area_overlap(c1_left,c1_right,c1_top,c1_bottom,c2_left,c2_right,c2_top,c2_bottom):
  '''
  Accepts as input the coords for two boxes, and returns a boolean regarding
  whether or not the areas overlap.

  Parameters:
  -----------
    c1_(left/right/top/bottom) : the pairs of x and y values for the first box
    c2_(left/right/top/bottom) : the pairs of x and y values for the second box

  Returns:
  --------
    overlap : boolean that is true when overlap occurs; false otherwise
  '''
  overlap = False

  if c1_left >= c2_left and c1_left <= c2_right:
    if c1_top >= c2_top and c1_top <= c2_bottom:
      overlap = True

    elif c1_bottom >= c2_top and c1_bottom <= c2_bottom:
      overlap = True

  elif c1_right >= c2_left and c1_right <= c2_right:
    if c1_top >= c2_top and c1_top <= c2_bottom:
      overlap = True

    elif c1_bottom >= c2_top and c1_bottom <= c2_bottom:
      overlap = True

  return overlap


def rect_extend_boundaries(rect, pageDims, amount):
  '''
  Accepts as input a connected component and an integer amount by which
  to extend its boundaries (in pixels). Requires also a Gamera image or
  image dimensions to confirm boundaries do not extend past the edge of
  the image.

  Parameters:
  -----------
    rect : A Gamera rectangle.
    pageDims : A tuple describing the pixel dimensions of the page in question.
    amount : Pixel amount by which to increase the sides of the rectangle.

  Returns:
  --------
    rect : The resulting larger rectangle.
  '''
  old_offset_x = rect.ul_x
  old_offset_y = rect.ul_y
  old_width = rect.ncols
  old_height = rect.nrows

  if rect.ul_x >= amount:
    rect.ul_x = rect.ul_x - amount
  else:
    rect.ul_x = 0

  if rect.ul_y >= amount:
    rect.ul_y = rect.ul_y - amount
  else:
    rect.ul_y = 0

  if old_offset_x + old_width + amount <= pageDims[0]:
    rect.ncols = old_width + (amount * 2)
  else:
    rect.ncols = img.ncols - rect.ul_x

  if old_offset_y + old_height + amount <= pageDims[1]:
    rect.nrows = old_height + (amount * 2)
  else:
    rect.nrows = img.nrows - rect.ul_y

  return rect


def cc_extend_boundaries(c, pageDims, amount):
  '''
  Accepts as input a connected component and an integer amount by which
  to extend its boundaries (in pixels). Requires also a Gamera image to
  confirm boundaries do not extend past the edge of the image.

  Parameters:
  -----------
    c : A Gamera connected component.
    pageDims : A tuple describing the pixel dimensions of the page in question.
    amount : Pixel amount by which to increase the sides of the rectangle.

  Returns:
  --------
    c : The adjusted Gamera CC
  '''
  old_offset_x = c.offset_x
  old_offset_y = c.offset_y
  old_width = c.ncols
  old_height = c.nrows

  # This changes c.ncols too for an unknown reason
  if c.offset_x >= amount:
    c.offset_x = c.offset_x - amount
  else:
    c.offset_x = 0

  # This changes c.nrows too for an unknown reason
  if c.offset_y >= amount:
    c.offset_y = c.offset_y - amount
  else:
    c.offset_y = 0

  if old_offset_x + old_width + amount <= pageDims[0]:
    c.ncols = old_width + (amount * 2)
  else:
    c.ncols = img.ncols - old_offset_x

  if old_offset_y + old_height + amount <= pageDims[1]:
    c.nrows = old_height + (amount * 2)
  else:
    c.nrows = img.nrows - old_offset_y

  return c


def rm_endpages(path, work, extension):
  '''
  Given a work ID, returns a list that contains all of the endpages to 
  be removed from a filelist that will be iterated over.

  Parameters:
  -----------
    work : a string containing the work ID of the edition in question

  Returns:
  --------
    skip : a list containing the filenames to be skipped
  '''
  skip = []
  # Handle paths better
  if os.path.isfile("/home/chris/Github/digital-euclid/intermediate/diag/" + work + "/pickled/endpages.pickle"):
    pickled = open("/home/chris/Github/digital-euclid/intermediate/diag/" + work + "/pickled/endpages.pickle")
    skip = pickle.load(pickled)
    pickled.close()
  else:
    fileList = sorted(listdir(path + work + "/" + extension))

    for i in range(0, 20):
      im = Im.open(path + work + "/" + extension + "/" + fileList[i])

      # Resize: full size unnecessary
      basewidth = 300
      wpercent = (basewidth/float(im.size[0]))
      hsize = int((float(im.size[1])*float(wpercent)))
      im = im.resize((basewidth,hsize),PIL.Image.ANTIALIAS)
      im.show()

      # Request user input
      endpage = raw_input("Endpage? Y/n: ")
      if "y" in endpage:
        skip.append(fileList[i])
      elif "n" in endpage:
        break

    for i in range(1, 20):
      im = Im.open(path + work + "/" + extension + "/" + fileList[-1 * i])

      # Resize: full size unnecessary
      basewidth = 300
      wpercent = (basewidth/float(im.size[0]))
      hsize = int((float(im.size[1])*float(wpercent)))
      im = im.resize((basewidth,hsize),PIL.Image.ANTIALIAS)
      im.show()

      # Request user input
      endpage = raw_input("Endpage? Y/n: ")
      if "y" in endpage:
        skip.append(fileList[-1 * i])
      elif "n" in endpage:
        break

    # Save pickled results
    print("Saving endpages...")

    if not os.path.exists("/home/chris/Github/digital-euclid/intermediate/diag/" + work + "/pickled/"):
      os.makedirs("/home/chris/Github/digital-euclid/intermediate/diag/" + work + "/pickled/")

    pickled = open("/home/chris/Github/digital-euclid/intermediate/diag/" + work + "/pickled/endpages.pickle", mode ='wb')
    pickle.dump(skip, pickled)
    pickled.close()

  return(skip)


def find_margins(img):
  '''
  '''

  img.remove_border()
  colProjs = img.projection_cols()

  leftMargin = "Left Margin NOT FOUND"
  rightMargin = "Right Margin NOT FOUND"

  # An attempt to avoid problematic edges by focusing only on the center third of the page
  middleMaximum = max(colProjs[int(0.33 * len(colProjs)):int(0.66 * len(colProjs))])

  x = 0
  for proj in colProjs:
    if proj > middleMaximum * 0.25:
      leftMargin = x
      break
    else:
      x = x + 1

  x = img.ncols
  for proj in reversed(colProjs):
    if proj > middleMaximum * 0.25:
      rightMargin = x
      break
    else:
      x = x - 1

  return leftMargin, rightMargin


def to_rectGamera(pointDim_tuple):
  '''
  A quick function to convert between the general tuple ((x,y),(w,h))
  and Rect(Point(x,y),Dim(w,h)) in Gamera.

  Parameters:
  -----------
    pointDim_tuple : A tuple with the form ((x,y),(w,h)).

  Returns:
  --------
    rectGamera : A Gamera rectangle object.
  '''
  rectGamera = Rect(Point(pointDim_tuple[0]),Dim(pointDim_tuple[1]))

  return rectGamera


def to_rectGeneral(Rect):
  '''
  A quick function to convert between Rect(Point(x,y),Dim(w,h)) in
  in Gamera and the general tuple ((x,y),(w,h)).

  Parameters:
  -----------
    Rect : A Gamera rectangle object.

  Returns:
  --------
    pointDim_tuple : A tuple with the form ((x,y),(w,h)).
  '''
  coords_point = Rect.ul.x, Rect.ul.y
  coords_dim = Rect.dim.ncols, Rect.dim.nrows
  pointDim_tuple = coords_point, coords_dim

  return pointDim_tuple


def filter_areas(ccs):
  '''
  Given a list of CCs, filters them so as to remove any with outlier
  areas. Used mainly to obtain data for distinguishing between characters
  and diagrams on the basis of area.

  Parameters:
  -----------
    ccs : A list of Gamera connected components.

  Returns:
  --------
    filtered : An array containing the values of non-outlier areas.

  '''
  area = []
  for c in ccs:
    a = (float(c.nrows)/float(img.nrows)) * (float(c.ncols)/float(img.ncols))
    area.append(a)

  np_area = array( area )
  filtered = np_area[~is_outlier(np_area)]

  return filtered

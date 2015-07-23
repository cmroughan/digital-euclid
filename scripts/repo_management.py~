#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os #load_diagDirectory
from os import listdir #load_diagDirectory
import sys #load_diagDirectory
from sys import argv

def load_diagDirectory():
  '''
  Initial script for all the first-stage diagram extraction scripts.
  Requests a work ID, then confirms that that collection directory exists
  in a useable form.

  Returns:
  --------
    path : a string identifying the base path to page images
    work : the identifying string to be used for identifying the collection
    extension : a string identifying the file extension
  '''
  # Take user input for which collection to strip
  path = "/home/chris/Github/x_eu-images/full/"
  work = sys.argv[-1]

  # Confirm that collection exists and in a Gamera-friendly filetype
  if os.path.isdir(path + work + "/png"):
    extension = "png"
    print("Directory exists. File extension is PNG.")
  elif os.path.isdir(path + work + "/tif"):
    extension = "tif"
    print("Directory exists. File extension is TIFF.")
  else:
    extension = "none"
    print("Internal ID not found.")
    sys.exit

  return(path, work, extension)



def status_update(status_csv,work,value):
  '''
  Updates the status.csv file in the repository

  Parameters:
  -----------
    status_csv : the path to the appropriate status.csv file
    work : the internal ID to locate in the file
    value : the value to update in the csv file

  Returns:
  --------
    None. Saves the updated file.
  '''
  statusFile = open(status_csv)
  statusText = statusFile.read()
  statusFile.close()
  statusLines = statusText.split('\n')

  newStatus = ""
  for line in statusLines:
    line = line.split(',')
    if work in line:
      line[int(value)] = "y"

  for line in statusLines:
    newStatus = newStatus + str(line) + '\n'

  newStatus = newStatus.rstrip('\n')

  outfile = open(status_csv, mode="w")
  outfile.write(newStatus)
  outfile.close()


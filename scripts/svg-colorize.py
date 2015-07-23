import os
from os import listdir
import random
import re

fileList = listdir("/home/chris/Github/x_eu-images/diag/heath_1908_v3_1/rough-autotrace/")

# Open and edit the svg file
for f in fileList:
  if ".svg" in f:
    svgFile = open("/home/chris/Github/x_eu-images/diag/heath_1908_v3_1/rough-autotrace/" + f)
    svgStr = svgFile.read()
    svgFile.close()

    lines = svgStr.split('\n')

    fullPath = lines[2].lstrip('<path style="stroke:#000000; fill:none;" d="').rstrip('"/>')
    brokenPaths = fullPath.split('M')

    newFile = lines[0] + '\n' + lines[1] + '\n'

    for path in brokenPaths:
# Construct the new paths and generate a random color for each
      r = lambda: random.randint(0,255)
      color = '#%02X%02X%02X' % (r(),r(),r())
      newFile = newFile + '<path style="stroke:#000000;fill:none;stroke-width:5" d="M' + path + '"/>\n'
      newFile = newFile + '<path style="stroke:' + color + ';fill:none;stroke-width:4" d="M' + path + '"/>\n'

# add circles at endpoints
      components = re.split(' |C|L',path)
      if len(components) > 1:
        circ_x1 = components[0]
        circ_y1 = components[1]
        circ_x2 = components[-2]
        circ_y2 = components[-1]

        newFile = newFile + '<circle stroke="#000000" fill="none" stroke-width="2" r="15" cx="' + circ_x1 + '" cy="' + circ_y1 + '"/>\n'
        newFile = newFile + '<circle stroke="#000000" fill="none" stroke-width="2" r="15" cx="' + circ_x2 + '" cy="' + circ_y2 + '"/>\n'

# look for and mark corners
      if len(components) >= 6:
        print("At least three points!")

# finish file

    newFile = newFile + '</svg>'
 
    outfile = open("/home/chris/Github/x_eu-images/diag/heath_1908_v3_1/annotated-autotrace/" + f, mode="w")
    outfile.write(newFile)
    outfile.close()

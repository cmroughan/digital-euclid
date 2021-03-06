import pickle
import os
from os import listdir

collection = raw_input("Internal ID: ")
imgType = raw_input("Type? (diag/enun): ")

# Dict refers to a specific image and pixel amounts. A later conversion will handle page image CITE URNs and percent coords.
rawCoords = {}
tsv = "Temp ID\tImage Path\tImage Width\tImage Height\tX Offset\tY Offset\tX Width\tY Height"

fileList = listdir("/home/chris/Github/digital-euclid/intermediate/" + imgType  + "/" + collection + "/imagej/")

for eachFile in fileList:
  if '.txt' in eachFile:
    inFile = open("/home/chris/Github/digital-euclid/intermediate/" + imgType  + "/" + collection + "/imagej/" + eachFile)
    rawText = inFile.read()
    lines = rawText.split('\n')
    inFile.close()

    # Grab tempID

    tempID = eachFile[:-4]

    # Grab name of image file

    fromImg = lines[1].split()[1]

    # Grab image dimensions
 
    imgWidth = int(lines[2].split()[1])
    imgHeight = int(lines[3].split()[1])

    # Pixel coords of ROI
    pixLeft = int(lines[-5].split()[1])
    pixTop = int(lines[-4].split()[1])
    pixWidth = int(lines[-3].split()[1])
    pixHeight = int(lines[-2].split()[1])
    pixRight = pixLeft + pixWidth
    pixBottom = pixTop + pixHeight

    # Add extracted info to the dictionary and tsv file

    rawCoords[tempID] = [fromImg, imgWidth, imgHeight, pixLeft, pixTop, pixWidth, pixHeight]
    tsv = tsv + "\n" + tempID + "\t" + fromImg + "\t" + str(imgWidth) + "\t" + str(imgHeight) + "\t" + str(pixLeft) + "\t" + str(pixTop) + "\t" + str(pixWidth) + "\t" + str(pixHeight)

# Save info

if not os.path.exists("/home/chris/Github/digital-euclid/intermediate/" + imgType + "/" + collection + "/pickled"):
  os.makedirs("/home/chris/Github/digital-euclid/intermediate/" + imgType + "/" + collection + "/pickled")

dict_record = open("/home/chris/Github/digital-euclid/intermediate/" + imgType + "/" + collection + "/pickled/rawCoords.pickle", mode ='wb')
pickle.dump(rawCoords, dict_record)
dict_record.close()

outFile = open("/home/chris/Github/digital-euclid/intermediate/" + imgType + "/" + collection + "/coords/pixelCoords.tsv", mode ='wb')
outFile.write(tsv)
outFile.close()

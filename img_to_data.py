import json
import cv2
import pytesseract
from pytesseract import Output
from config import workdir, number

for i in range(1, number + 1):
    img = cv2.imread(f"{workdir}/src/{str(i).zfill(2)}.png")
    d = pytesseract.image_to_data(img, output_type=Output.DICT, lang="rus")
    # Serializing json
    json_object = json.dumps(d, indent=4)
    # Writing to XX.json
    with open(f"{workdir}/psm3/{str(i).zfill(2)}.json", "w") as outfile:
        outfile.write(json_object)
    print("#", end="")
print()
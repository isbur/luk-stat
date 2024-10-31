import json
import cv2
import pytesseract
from pytesseract import Output

for i in range(1, 29):
    img = cv2.imread(f"./PNGs/{str(i).zfill(2)}.png")
    d = pytesseract.image_to_data(img, output_type=Output.DICT, lang="rus")
    # Serializing json
    json_object = json.dumps(d, indent=4)
    # Writing to XX.json
    with open(f"./JSONs-PSM6/{str(i).zfill(2)}.json", "w") as outfile:
        outfile.write(json_object)
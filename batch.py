import json
import cv2
from PIL import Image
from visual import PSM3


print("Processing images...")
images = []
for i in range(1, 29):
    img = cv2.imread(f"./PNGs/{str(i).zfill(2)}.png")

    with open(f"./JSONs-PSM3/{str(i).zfill(2)}.json", "r") as f:
        d: dict[str, list[int|float|str]] = json.load(f)
    
    PSM3(img, d)

    cv2.imwrite(f"./Temp/{str(i).zfill(2)}.jpg", img)

    images.append(Image.open(f"./Temp/{str(i).zfill(2)}.jpg"))
    
    print("#", end = "")

print()
images[0].save(
    "output.pdf", "PDF", resolution = 100.0, save_all=True, append_images = images[1:]
)

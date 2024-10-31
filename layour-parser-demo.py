import cv2
import layoutparser as lp

fileNumber = 100

img = cv2.imread(f"./PNGs/{str(fileNumber).zfill(2)}.png")
img2 = img[..., ::-1]
# model = lp.Detectron2LayoutModel('lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
#                                  label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"})
model = lp.Detectron2LayoutModel('lp://PrimaLayout/mask_rcnn_R_50_FPN_3x/config',
                                 label_map={1:"TextRegion", 2:"ImageRegion", 3:"TableRegion", 4:"MathsRegion", 5:"SeparatorRegion", 6:"OtherRegion"})
layout = model.detect(img2)
# lp.draw_box(img2, layout, box_width=3)

for elemBlock in layout:
    if elemBlock.type == "ImageRegion":
        b = elemBlock.block
        x1 = int(b.x_1)
        y1 = int(b.y_1)
        x2 = int(b.x_2)
        y2 = int(b.y_2)
        cv2.rectangle(img, (x1,y1), (x2, y2), (0,0,255), 2)

#### Fullscreen by default
cv2.namedWindow('img', cv2.WINDOW_FULLSCREEN)
#### ...
####

cv2.imshow('img',img)
cv2.waitKey(0)
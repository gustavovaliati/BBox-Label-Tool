'''
Reads the Images directory, find label-tool annotations and parse annotations to darknet format in the Labels-darknet

#---
bbox-label-tool format (1 file per frame, 1 line per bbox):
Example:
File: C_BLC03-02/0/18/01/08/16/58/41/00023-capture.txt
2
474 42 497 102 0
510 44 528 101 0
File: C_BLC03-02/0/18/01/08/16/58/41/000106-capture.txt
5
182 54 201 100 0
136 66 164 126 0
116 70 134 115 0
93 81 109 125 0
76 88 93 119 0
File: (...)

'''
import os
import glob
from pathlib import Path
from PIL import Image
from tqdm import tqdm

IMAGES_PATH='./Images'
LABELS_PATH='./Labels/Images'
LABELS_DARKNET_PATH='./Labels-darknet/Images'

if os.path.exists(LABELS_DARKNET_PATH):
    raise Exception('Path already exists', LABELS_DARKNET_PATH)

image_list = glob.glob(os.path.join(IMAGES_PATH, '**/*.jpg'), recursive=True)

def convert(im_w, im_h, bbox):
    '''
    References:
    - https://github.com/Guanghan/darknet/blob/master/scripts/convert.py
    - https://github.com/AlexeyAB/darknet
    '''

    classId = bbox[4]

    xmin = float(bbox[0])
    xmax = float(bbox[2])
    if xmax >= im_w:#handles annotation tool bug which permits annotating out of the image boundaries.
        xmax = im_w -1
    ymin = float(bbox[1])
    ymax = float(bbox[3])
    if ymax >= im_h:#handles annotation tool bug which permits annotating out of the image boundaries.
        ymax = im_h -1

    dw = 1./im_w
    dh = 1./im_h
    x = (xmin + xmax)/2.0
    y = (ymin + ymax)/2.0
    w = xmax - xmin
    h = ymax - ymin
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    # print(x,y,w,h)
    return '{} {} {} {} {}'.format(classId,x,y,w,h)

for image in tqdm(image_list):
    label_tool_annot = image.replace(IMAGES_PATH,LABELS_PATH).replace('.jpg','.txt')
    label_darknet_annot = label_tool_annot.replace(LABELS_PATH, LABELS_DARKNET_PATH)
    darknet_basedir = os.path.dirname(label_darknet_annot)
    if not os.path.exists(label_tool_annot):
        raise Exception('Missing label file:', label_tool_annot)

    os.makedirs(darknet_basedir,exist_ok=True)

    with open(label_tool_annot, 'r') as tool_annot_f:
        annotations = tool_annot_f.readlines()
        if len(annotations) > 1:
            #the first element is the number of bbox.
            expected_bbox_quantity = int(annotations[0])
            real_bbox_quantity = len(annotations[1:])
            if expected_bbox_quantity != real_bbox_quantity:
                raise Exception('The expected number of bboxes in the tool annotations is different from the factual number.')
            img = Image.open(image)
            img_w, img_h = img.size
            del img
            with open(label_darknet_annot, 'w') as dark_annot_f:
                for bbox in annotations[1:]:
                    bbox = list(map(int, bbox.split(' ')))
                    dark_annot_f.write(convert(img_w, img_h, bbox) + '\n')
        else:
            #no bbox for this image. Create an empty darknet annot file.
            Path(label_darknet_annot).touch()

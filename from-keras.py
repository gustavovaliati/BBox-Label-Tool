'''
This scripts gets the annotation file in keras-yolo3 format (https://github.com/gustavovaliati/keras-yolo3)
and converts back to the Labels format for this tool.

#----
keras-yolo3 format (1 file, 1 line per frame):
Example:
File: test_dataset.txt
C_BLC03-02/0/18/01/08/16/58/41/00023-capture.jpg 474,42,497,102,0 510,44,528,101,0
C_BLC03-02/0/18/01/08/16/58/41/00106-capture.jpg 182,54,201,100,0 136,66,164,126,0 116,70,134,115,0 93,81,109,125,0 76,87,93,118,0
(...)

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
import argparse
import datetime
from tqdm import tqdm

ap = argparse.ArgumentParser()

ap.add_argument("-a", "--annotation_file",
                required=True,
                default=None,
                type=str,
                help="keras-yolo3 annotation file.")

ARGS = ap.parse_args()

version = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
output_dir = './from-keras/{}/'.format(version)

with open(ARGS.annotation_file, 'r') as annot_f:
    for annot_line in annot_f:
        splitted = annot_line.split(' ')
        img_path = splitted[0].strip()

        file_name = os.path.basename(img_path)
        base_dir = os.path.dirname(img_path)

        if base_dir.startswith('/'):
            base_dir = base_dir.replace('/','',1)


        new_dir = os.path.join(output_dir, base_dir)
        os.makedirs(new_dir, exist_ok=True)

        with open(os.path.join(new_dir, file_name.replace('.jpg', '.txt')), 'w') as out_f:
            out_f.write('{}\n'.format(len(splitted[1:]))) #write bbox quantity
            for bbox in splitted[1:]:
                    x_min, y_min, x_max, y_max, class_id = list(map(float, bbox.split(',')))
                    x_min, y_min, x_max, y_max, class_id = list(map(int, [x_min, y_min, x_max, y_max, class_id]))
                    out_f.write('{} {} {} {} {}\n'.format(x_min, y_min, x_max, y_max, class_id))

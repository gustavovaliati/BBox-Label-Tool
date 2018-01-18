import sys, os, glob, datetime, shutil
from tqdm import tqdm
from PIL import Image

BBOX_LABELS_PATH = './Labels'
DARKNET_LABELS_PATH = './Labels-darknet'
THEHIVE_LABELS_PATH = './Labels-thehive'
DESTINATION_SUBDIR = './MERGED_{}'.format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

bbox_labels = glob.glob(os.path.join(BBOX_LABELS_PATH, '**/*.txt'), recursive=True)
darknet_labels = glob.glob(os.path.join(DARKNET_LABELS_PATH, '**/*.txt'), recursive=True)
thehive_labels = glob.glob(os.path.join(THEHIVE_LABELS_PATH, '**/*.txt'), recursive=True)

def convert(bbox, im_size):
    '''
    References:
    - https://github.com/Guanghan/darknet/blob/master/scripts/convert.py
    - https://github.com/AlexeyAB/darknet
    '''
    im_w, im_h = im_size

    xmin = float(bbox[0])
    xmax = float(bbox[2])
    ymin = float(bbox[1])
    ymax = float(bbox[3])

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
    return '{} {} {} {}'.format(x,y,w,h)

print('Copying thehive labels and converting to darknet format.')
for thehive_l in tqdm(thehive_labels, total=len(thehive_labels)):
    # print(thehive_l)
    new_f_path_bbox = thehive_l.replace('./Labels-thehive', os.path.join(DESTINATION_SUBDIR, BBOX_LABELS_PATH))
    new_f_path_darknet = thehive_l.replace('./Labels-thehive', os.path.join(DESTINATION_SUBDIR, DARKNET_LABELS_PATH))
    # print(new_f_path_bbox)
    dir_path_bbox = os.path.dirname(new_f_path_bbox)
    dir_path_darknet = os.path.dirname(new_f_path_darknet)
    # print(dir_path_bbox)
    os.makedirs(dir_path_bbox, exist_ok=True)
    os.makedirs(dir_path_darknet, exist_ok=True)
    im_path = thehive_l.replace('/Labels-thehive','').replace('.txt', '.jpg')
    # print(im_path)
    im = Image.open(im_path)
    with open(thehive_l, 'r') as hive_f:
        shutil.copy(thehive_l, new_f_path_bbox)
        with open(new_f_path_darknet, 'w') as f:
            for index, line in enumerate(hive_f):
                if index == 0:
                    continue
                tmp = [int(t.strip()) for t in line.split()]
                f.write('0 ' + convert(bbox=tuple(tmp), im_size=im.size) + '\n')
print('Done.')

missing_images_list = []
missing_images_filepath = os.path.join(DESTINATION_SUBDIR,'missing_images_list.txt')
missing_backup_dir = os.path.join(DESTINATION_SUBDIR,'missing_images_labels_backup')
os.makedirs(missing_backup_dir, exist_ok=True)

print('Copying bbox labels and converting to darknet format.')
with open(missing_images_filepath, 'w') as bkp_f:
    for bbox_l in tqdm(bbox_labels, total=len(bbox_labels)):
        # print(thehive_l)
        new_f_path_bbox = bbox_l.replace('./Labels', os.path.join(DESTINATION_SUBDIR, BBOX_LABELS_PATH))
        new_f_path_darknet = bbox_l.replace('./Labels', os.path.join(DESTINATION_SUBDIR, DARKNET_LABELS_PATH))
        # print(new_f_path_bbox)
        dir_path_bbox = os.path.dirname(new_f_path_bbox)
        dir_path_darknet = os.path.dirname(new_f_path_darknet)
        # print(dir_path_bbox)
        os.makedirs(dir_path_bbox, exist_ok=True)
        os.makedirs(dir_path_darknet, exist_ok=True)
        im_path = bbox_l.replace('/Labels','').replace('.txt', '.jpg')
        # print(im_path)
        if not os.path.exists(im_path):
            missing_images_list.append(im_path)
            bkp_f.write(im_path + "\n")
            full_dir_path = os.path.join(missing_backup_dir, os.path.dirname(bbox_l))
            os.makedirs(full_dir_path, exist_ok=True)
            shutil.move(bbox_l,os.path.join(full_dir_path, os.path.basename(bbox_l)))
            continue
        im = Image.open(im_path)
        with open(bbox_l, 'r') as hive_f:
            shutil.copy(bbox_l, new_f_path_bbox)
            with open(new_f_path_darknet, 'w') as f:
                for index, line in enumerate(hive_f):
                    if index == 0:
                        continue
                    tmp = [int(t.strip()) for t in line.split()]
                    f.write('0 ' + convert(bbox=tuple(tmp), im_size=im.size) + '\n')
print('Done.')

print('Writting the {} missing images paths to {}, and the labels backup to {}.'.format(len(missing_images_list), missing_images_filepath, missing_backup_dir))

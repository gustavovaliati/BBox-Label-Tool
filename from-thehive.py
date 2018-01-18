import csv, json, sys, os, argparse
from PIL import Image


ap = argparse.ArgumentParser()
ap.add_argument("-e", "--export-file",
                required = True,
                default = False,
                help = 'The csv result file from "The Hive" containing all the labels.',
                dest='export_file')
ARGS = vars(ap.parse_args())

if ARGS['export_file'] == '':
    print('Missing the csv result file from "The Hive".')
    sys.exit()

THE_HIVE_LABELS_PATH = './Labels-thehive/Images'
BBOX_LABELS_PATH = './Labels'
DARKNET_LABELS_PATH = './Labels-darknet'


'''
['project_id', 'day', 'task_id', 'created_on', 'csv_upload_id', 'image_url', 'original_filename', 'file_id', 'label_data', 'status', 'task_units', 'base_customer_charge', 'total_customer_charge']
'''
TASK_ID = 2
FILE_NAME = 6
LABEL_DATA = 9

with open(ARGS['export_file'], newline='') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')

    tasks_number = 0
    for index, row in enumerate(csvreader):
        if index == 0:
            continue

        if row[FILE_NAME] == '':
            print("Task ID {}. Task without file name! Continuing to the next one.".format(row[TASK_ID]))
            continue

        if row[LABEL_DATA] == '':
            #no label data.
            continue

        print(row[FILE_NAME])

        #001_C_BLC03-12_0_18_01_08_16_59_57_00151-capture.jpg
        inner_file_path = row[FILE_NAME].replace('001_C_', '001/C?')
        inner_file_path = inner_file_path.replace('_', '/')
        inner_file_path = inner_file_path.replace('001/C?', '001/C_')
        img_inner_file_path = inner_file_path
        inner_file_path = inner_file_path.replace('.jpg', '.txt')
        thehive_file_path = os.path.join(THE_HIVE_LABELS_PATH, inner_file_path)
        dir_path = os.path.dirname(thehive_file_path)
        os.makedirs(dir_path, exist_ok=True)

        json_data = json.loads(row[LABEL_DATA])
        bbox_len = len(json_data)
        # print('bbox_len', bbox_len)
        im = Image.open(os.path.join('./Images',img_inner_file_path))
        width, height = im.size
        inconclusive = False
        with open(thehive_file_path, 'w') as hive_f:

            for index, jd in enumerate(json_data):
                # print('jd', jd)
                if jd == 'NO_BOUNDING_BOX':
                    #labeled as having no bounding boxes.
                    print("Task id {}. NO_BOUNDING_BOX.".format(row[TASK_ID]))
                    hive_f.write('0\n')
                elif jd == 'inconclusive':
                    print("Task id {}. Inconclusive.".format(row[TASK_ID]))
                    inconclusive = True
                else:
                    if float(jd['width'] != 1.0):
                        print("something is wrong with the width")
                        sys.exit()
                    if index == 0:
                        hive_f.write('{}\n'.format(bbox_len))
                    x1 = int(float(jd['p1']['x']) * width)
                    x2 = int(float(jd['p2']['x']) * width)
                    y1 = int(float(jd['p1']['y']) * height)
                    y2 = int(float(jd['p2']['y']) * height)

                    hive_f.write('{} {} {} {}\n'.format(x1, y1, x2, y2))
        if inconclusive:
            os.remove(thehive_file_path)
            
        tasks_number += 1
print('Number of useful tasks: {}.'.format(tasks_number))

import glob
import os
import argparse
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--annotation_dir', help="Annotation directory. For the bbox-label tool it is the Label directory.", type=str, required=True)
parser.add_argument('-d', '--destination_dir', help="Destination directory for the extracted annotations", type=str, required=True)
parser.add_argument('-f', '--first_position', help="First image position. Starts in 1. ", type=int, required=True)
parser.add_argument('-l', '--last_position', help="Last image position. The last image is included.", type=int, required=True)
args = parser.parse_args()

annotation_list = glob.glob(os.path.join(args.annotation_dir, '**/*.txt'), recursive=True)
annotation_list_size = len(annotation_list)

if args.first_position <= 0 or  args.last_position <= 0:
    raise Exception('The positions cannot be less than zero.')

if args.last_position > annotation_list_size or args.first_position > annotation_list_size:
    raise Exception('The last position cannot be greater than the total number of annotation which is: ',annotation_list_size)

if args.last_position < args.first_position:
    raise Exception('The last position cannot be less than the first position.')

print('##################################################################')
print('Be aware: the positions are for the ordered list of annotations.')
print('##################################################################')

abs_destination_dir = os.path.abspath(args.destination_dir)
print('\nExtracting...')
annotation_list.sort()
for annot in annotation_list[args.first_position-1 : args.last_position]:
    annot = os.path.abspath(annot)
    dest_annot = os.path.join(abs_destination_dir, annot.replace('/','',1))
    os.makedirs(os.path.dirname(dest_annot), exist_ok=True)
    shutil.copy(annot, dest_annot)

print('Done.')

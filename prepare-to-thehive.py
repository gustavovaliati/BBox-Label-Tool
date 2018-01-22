import os, glob, sys, shutil

# imagedir = './Images/001'
imagedir = './Images/001/C_BIBT-07'
hivedir = './thehive-images'

if not os.path.exists(imagedir):
    print('Something is wrong with the image dir.')
    sys.exit()

if not os.path.exists(hivedir):
    os.mkdir(hivedir)

imageList = glob.glob(os.path.join(imagedir, '**/*.jpg'), recursive=True)

if len(imageList) == 0:
    print("No images found on dir.")
    sys.exit()

copied = 0
for im_index, im in enumerate(imageList):
    labelpath = './Labels/' + im.replace('.jpg', '.txt')
    if not os.path.exists(labelpath):
        new_path = im.replace('/','_')
        new_path = new_path.replace('._Images_', './thehive-images/')
        shutil.copy(im, new_path)
        copied += 1
print("Copied to thehive image folder {} files.".format(copied))

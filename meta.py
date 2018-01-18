import os, glob, sys

darknetdir = './Labels-darknet'
metadir = './meta'

frame_rate = 2.5 #vary according to the source.

if not os.path.exists(darknetdir):
    print('Something is wrong with the darknet labels dir.')
    sys.exit()

if not os.path.exists(metadir):
    os.mkdir(metadir)


labelsList = glob.glob(os.path.join(darknetdir, '**/*.txt'), recursive=True)

if len(labelsList) == 0:
    print("No labels found on dir.")
    sys.exit()

metaDic = {}
for lfile in labelsList:
    with open(lfile, 'r') as f:
        #count number of lines
        lcount = sum(1 for _ in f)
        if not lcount in metaDic:
            metaDic[lcount] = []
        metaDic[lcount].append(lfile)

totalLabeled = 0
totalBBoxes = 0
for lcount in metaDic:
    labelList = metaDic[lcount]
    if lcount > 0:
        totalLabeled = totalLabeled + len(labelList)
        totalBBoxes = totalBBoxes + (lcount * len(labelList))
    print("{} frames with {} bboxes. Aprox {} seconds of video.".format(len(labelList), lcount, len(labelList) / frame_rate))
    fbboxcountname = "bbox_number_{}.txt".format(lcount)
    fbboxcount = os.path.join(metadir, fbboxcountname)
    with open(fbboxcount, 'w') as f:
        for l in labelList:
            f.write(l + '\n')
print("Total of labeled frames: {}. Aprox {} seconds of video.".format(totalLabeled, totalLabeled / frame_rate))
print("Total of bounding boxes: {}.".format(totalBBoxes))

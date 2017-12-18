import os, glob, sys

darknetdir = './Labels-darknet'
metadir = './meta'

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
    print("{} frames with {} bboxes. ".format(len(labelList), lcount))
    fbboxcountname = "bbox_number_{}.txt".format(lcount)
    fbboxcount = os.path.join(metadir, fbboxcountname)
    with open(fbboxcount, 'w') as f:
        for l in labelList:
            f.write(l + '\n')
print("Total of labeled frames: {}. Ps: Frames with zero bboxes does not count.".format(totalLabeled))
print("Total of bounding boxes: {}.".format(totalBBoxes))

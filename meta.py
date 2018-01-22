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
summary_file_path = 'meta/summary.txt'
with open(summary_file_path, 'w')as summary_f:

    for lcount in metaDic:
        labelList = metaDic[lcount]
        if lcount > 0:
            totalLabeled = totalLabeled + len(labelList)
            totalBBoxes = totalBBoxes + (lcount * len(labelList))
        out = "{} frames with {} bboxes. Aprox {} seconds of video.".format(len(labelList), lcount, len(labelList) / frame_rate)
        summary_f.write(out+'\n')
        print(out)
        fbboxcountname = "bbox_number_{}.txt".format(lcount)
        fbboxcount = os.path.join(metadir, fbboxcountname)
        with open(fbboxcount, 'w') as f:
            for l in labelList:
                f.write(l + '\n')
    out = "Total of labeled frames: {}. Aprox {} seconds of video.".format(totalLabeled, totalLabeled / frame_rate)
    summary_f.write(out+'\n')
    print(out)
    out = "Total of bounding boxes: {}.".format(totalBBoxes)
    summary_f.write(out+'\n')
    print(out)

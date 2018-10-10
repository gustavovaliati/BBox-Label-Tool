#-------------------------------------------------------------------------------
# Name:        Object bounding box label tool
# Purpose:     Label object bboxes for ImageNet Detection data
# Author:      Qiushi
# Created:     06/06/2014

#
#-------------------------------------------------------------------------------
from __future__ import division
# from Tkinter import *
from tkinter import *
from tkinter import messagebox


from PIL import Image, ImageTk
import os, shutil, glob, random, sys

# colors for the bboxes
COLORS = ['red', 'blue', 'pink', 'cyan', 'green', 'yellow', 'black' ]
# image sizes for the examples
# SIZE = 256, 256
CLASSES_FILE_PATH = './classes.txt'

class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("LabelTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = True, height = True)
        self.hivedir = './thehive'
        self.hivecount = 0


        # initialize global state
        self.imageDir = ''
        self.imageList= []
        self.egDir = ''
        self.egList = []
        self.currLayoutRow = -1
        # self.outDir = ''
        # self.darknetOutDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None
        self.orderImageList = BooleanVar()
        self.orderImageList.set(True)
        self.noBboxes = BooleanVar()
        self.hideOtherBboxes = BooleanVar()

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []

        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = Label(self.frame, text = "Image Dir:")
        self.label.grid(row = 0, column = 0, sticky = E)
        self.entry = Entry(self.frame)
        self.entry.grid(row = 0, column = 1, sticky = W+E)
        self.entry.insert(END, '1')
        self.ldBtn = Button(self.frame, text = "Load", command = self.loadDir)
        self.ldBtn.grid(row = self.getNextLayoutRow(), column = 2, sticky = W+E)
        self.checkbutton = Checkbutton(self.frame, text = "Order Image list", variable = self.orderImageList)
        self.checkbutton.grid(row = self.getNextLayoutRow(), column = 2, sticky = W)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.parent.bind("<MouseWheel>", self.mouseWheel) #windows
        self.parent.bind("<Button-4>", self.mouseWheel) #linux
        self.parent.bind("<Button-5>", self.mouseWheel) #linux
        self.parent.bind("<Key>", self.keyPressed)
        self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        self.parent.bind("s", self.cancelBBox)
        self.parent.bind("a", self.prevImage) # press 'a' to go backforward
        self.parent.bind("d", self.nextImage) # press 'd' to go forward
        self.parent.bind("<Left>", self.prevImage)
        self.parent.bind("<Right>", self.nextImage)
        self.parent.bind("z", self.deleteLastBBox) #delete the last bbox from the list
        # self.parent.bind("h", self.sendToTheHive)
        self.parent.bind("v", self.nextBBoxOverlap)
        self.parent.bind("p", self.toggleNoBboxes)
        self.parent.bind("f", self.toggleHideOtherBboxes)
        self.parent.bind("m", self.setManualBBox)
        self.parent.bind("o", self.nextNoBboxImage)
        self.mainPanel.grid(row = 1, column = 1, rowspan = 10, sticky = W+N)

        # showing bbox info & delete bbox
        self.lbCurrClass = Label(self.frame, text = 'New Annot as: None')
        self.lbCurrClass.grid(row = self.getNextLayoutRow(), column = 2,  sticky = W+N)

        self.lb1 = Label(self.frame, text = 'Bounding boxes:')
        self.lb1.grid(row = self.getNextLayoutRow(), column = 2,  sticky = W+N)

        self.checkbuttonNobboxes = Checkbutton(self.frame, text = "No bboxes", variable = self.noBboxes)
        self.checkbuttonNobboxes.grid(row = self.getNextLayoutRow(), column = 2, sticky = W+N)
        self.listbox = Listbox(self.frame, width = 25, height = 12)
        self.listbox.grid(row = self.getNextLayoutRow(), column = 2, sticky = N)
        self.listbox.bind('<<ListboxSelect>>', self.listboxSelected)

        self.btnSetAllBboxClasses = Button(self.frame, text='Update Classes', command = self.setAllBboxClasses)
        self.btnSetAllBboxClasses.grid(row = self.getNextLayoutRow(), column = 2, sticky = W+E+N)


        self.lbClassesList = Label(self.frame, text = 'Class List:')
        self.lbClassesList.grid(row = self.getNextLayoutRow(), column = 2,  sticky = W+N)
        self.listboxClasses = Listbox(self.frame, width = 22, height = 8)
        self.listboxClasses.grid(row = self.getNextLayoutRow(), column = 2, sticky = N)
        self.listboxClasses.bind('<<ListboxSelect>>', self.listboxClassesSelected)

        self.checkbHideOthersBboxes = Checkbutton(self.frame, text = "Hide other bboxes", variable = self.hideOtherBboxes)
        self.checkbHideOthersBboxes.grid(row = self.getNextLayoutRow(), column = 2, sticky = W+N)
        self.setManualBBoxEntry = Entry(self.frame, width = 20)
        self.setManualBBoxEntry.grid(row = self.getNextLayoutRow(), column = 2, sticky = W+N)
        self.btnSetManualBbox = Button(self.frame, text='Manual BBox', command = self.setManualBBox)
        self.btnSetManualBbox.grid(row = self.getNextLayoutRow(), column = 2, sticky = W+E+N)
        self.btnNextNoBBox = Button(self.frame, text='Next No-BBox', command = self.nextNoBboxImage)
        self.btnNextNoBBox.grid(row = self.getNextLayoutRow(), column = 2, sticky = W+E+N)
        self.btnDel = Button(self.frame, text = 'Delete', command = self.delBBox)
        self.btnDel.grid(row = self.getNextLayoutRow(), column = 2, sticky = W+E+N)
        self.btnClear = Button(self.frame, text = 'ClearAll', command = self.clearBBox)
        self.btnClear.grid(row = self.getNextLayoutRow(), column = 2, sticky = W+E+N)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = self.getNextLayoutRow(), column = 1, columnspan = 2, sticky = W+E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width = 10, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)
        self.tmpLabel = Label(self.ctrPanel, text = "Go to Image No.")
        self.tmpLabel.pack(side = LEFT, padx = 5)
        self.idxEntry = Entry(self.ctrPanel, width = 5)
        self.idxEntry.pack(side = LEFT)
        self.goBtn = Button(self.ctrPanel, text = 'Go', command = self.gotoImage)
        self.goBtn.pack(side = LEFT)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = RIGHT)

        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(4, weight = 1)

        self.classes = self.loadClasses(CLASSES_FILE_PATH)
        self.currDefaultBboxClassId = 0
        self.updateMarkingClass(self.currDefaultBboxClassId)

        self.topViewLine = None
        self.smallLine = None

        # self.mainPanel.create_line(15, 25, 200, 25)

    def mouseWheel(self, event):
        if event.num == 5 or event.delta == -120:
            self.prevImage()
        if event.num == 4 or event.delta == 120:
            self.nextImage()

    def getNextLayoutRow(self):
        self.currLayoutRow += 1
        return self.currLayoutRow

    def loadDir(self, dbg = False):
        if not dbg:
            s = self.entry.get()
            self.parent.focus()
            self.category = int(s)
        else:
            s = r'D:\workspace\python\labelGUI'
       # if not os.path.isdir(s):
           # tkMessageBox.showerror("Error!", message = "The specified dir doesn't exist!")
           # return
        # get image list
        self.imageDir = os.path.join(r'./Images', '%03d' %(self.category))
        #self.imageList = glob.glob(os.path.join(self.imageDir, '**/*.jpg'), recursive=True)

        import fnmatch
        self.imageList = []
        for root, dirnames, filenames in os.walk(self.imageDir):
            for filename in fnmatch.filter(filenames, '*.jpg'):
                self.imageList.append(os.path.join(root, filename))


        if len(self.imageList) == 0:
            print('No .jpg images found in the specified dir!')
            return

        if(self.orderImageList.get()):
            self.imageList.sort()

        # print(self.imageList)

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

         # set up output dir
        self.labelsdir = './Labels'
        if not os.path.exists(self.labelsdir):
            os.mkdir(self.labelsdir)
        # self.outDir = os.path.join(self.labelsdir, '%03d' %(self.category))
        # if not os.path.exists(self.outDir):
            # os.mkdir(self.outDir)

        # darknet labels dir
        self.darknetdir = './Labels-darknet'
        if not os.path.exists(self.darknetdir):
            os.mkdir(self.darknetdir)
        # self.darknetOutDir = os.path.join(self.darknetdir, '%03d' %(self.category))
        # if not os.path.exists(self.darknetOutDir):
        #     os.mkdir(self.darknetOutDir)

        # darknet labels dir
        # self.metadir = './meta'
        # if not os.path.exists(self.metadir):
        #     os.mkdir(self.metadir)

        # # load example bboxes
        # self.egDir = os.path.join(r'./Examples', '%03d' %(self.category))
        # if not os.path.exists(self.egDir):
        #     return
        # filelist = glob.glob(os.path.join(self.egDir, '*.jpg'))
        # self.tmp = []
        # self.egList = []
        # random.shuffle(filelist)
        # for (i, f) in enumerate(filelist):
        #     if i == 3:
        #         break
        #     im = Image.open(f)
        #     r = min(SIZE[0] / im.size[0], SIZE[1] / im.size[1])
        #     new_size = int(r * im.size[0]), int(r * im.size[1])
        #     self.tmp.append(im.resize(new_size, Image.ANTIALIAS))
        #     self.egList.append(ImageTk.PhotoImage(self.tmp[-1]))
        #     self.egLabels[i].config(image = self.egList[-1], width = SIZE[0], height = SIZE[1])

        self.loadImage()
        print('%d images loaded from %s' %(self.total, s))

    def toggleNoBboxes(self, event=None):
        self.noBboxes.set( not self.noBboxes.get() )

    def toggleHideOtherBboxes(self, event=None):
        self.saveImage()
        self.hideOtherBboxes.set( not self.hideOtherBboxes.get() )
        self.loadImage()

    def setManualBBox(self, event=None):
        tmp = [int(t.strip()) for t in self.setManualBBoxEntry.get().split()]
        if(len(tmp) == 4):
            self.bboxList.append(tuple(tmp))

            tmpId = self.mainPanel.create_rectangle(tmp[0], tmp[1], \
                                                        tmp[2], tmp[3], \
                                                        width = 1, \
                                                        outline = COLORS[(len(self.bboxList)-1) % len(COLORS)])
            self.bboxIdList.append(tmpId)
            print(len(self.bboxIdList))
            self.listbox.insert(END, '%d:(%d,%d,%d,%d)[%d]' %(len(self.bboxIdList), tmp[0], tmp[1], tmp[2], tmp[3], self.currDefaultBboxClassId+1))
            self.listbox.itemconfig(len(self.bboxList) - 1, fg = COLORS[(len(self.bboxList) - 1) % len(COLORS)])

    def keyPressed(self, event=None):
        key = event.char

        #handle class bindings
        class_keys = [str(x) for x in range(1,11)]
        if key in class_keys:
            self.setClassPressed(class_keys.index(key))

    def listboxSelected(self, event):
        selections = self.listbox.curselection()
        if len(selections) == 1:
            currBboxId = int(selections[0])
            classId = self.bboxList[currBboxId][4]
            self.reloadClassList(classId)
        elif len(selections) > 1:
            raise Exception("We do not support multi-selection")
        else:
            #deselecting
            self.reloadClassList()

    def listboxClassesSelected(self, event):
        selections = self.listboxClasses.curselection()
        if len(selections) == 1:
            self.updateMarkingClass(int(self.listboxClasses.curselection()[0]))
        elif len(selections) > 1:
            raise Exception("We do not support multi-selection")
        else:
            #deselecting
            self.reloadClassList()

    def updateMarkingClass(self, classId):
        self.currDefaultBboxClassId = classId
        # print('Changing current class for annotations to', classId)
        self.lbCurrClass.config(text='New Annot as: {}'.format(self.classes[classId]))

    def setClassPressed(self, classId):
        if classId >= 0 and classId < self.listboxClasses.size() and self.listbox.size() > 0:
            self.updateMarkingClass(classId)
            self.setBBoxClass(classId)

    def reloadClassList(self, class_id=None):
        self.listboxClasses.delete(0,END)
        for id, cl in enumerate(self.classes):
            if id == class_id:
                self.listboxClasses.insert(END, '->[{}]'.format(id+1) + cl)
            else:
                self.listboxClasses.insert(END, '[{}]'.format(id+1) + cl)

    def setBBoxClass(self, classId):
        if classId >= self.listboxClasses.size():
            raise Exception('The class does not exist.')

        if self.listbox.size() == 0:
            return

        selections = self.listbox.curselection()
        if len(selections) == 1:
            bbox_index = int(selections[0])
            bbox = list(self.bboxList[bbox_index])
            self.bboxList.pop(bbox_index)
            bbox[4] = classId
            self.bboxList.insert(bbox_index, tuple(bbox))
            print(self.bboxList)
            self.saveImage()
            self.reloadClassList(classId)
            self.reloadBboxListbox()

    def setAllBboxClasses(self):
        if self.currDefaultBboxClassId >= self.listboxClasses.size():
            raise Exception('The class does not exist.')

        if self.listbox.size() == 0:
            return

        for bbox_index in range(self.listbox.size()):
            bbox = list(self.bboxList[bbox_index])
            self.bboxList.pop(bbox_index)
            bbox[4] = self.currDefaultBboxClassId
            self.bboxList.insert(bbox_index, tuple(bbox))
            # print(self.bboxList)
        self.saveImage()
        self.reloadClassList()
        self.reloadBboxListbox()

    def loadClasses(self, classes_path):
        if not os.path.exists(classes_path):
            message = "Classes file not found."
            print(message)
            messagebox.showerror("Classes", message)
            sys.exit()

        classes = []
        with open(classes_path, 'r') as f:
            for cl in f:
                cl = cl.strip()
                classes.append(cl)
                self.listboxClasses.insert(END,cl)

        if len(classes) == 0:
            message = "Classes file is empty."
            print(message)
            messagebox.showerror("Classes", message)
            sys.exit()

        print('Loaded classes:',classes)
        return classes

    def loadImage(self):
        # load image
        self.imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(self.imagepath)
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))

        # load labels
        self.imagename = os.path.split(self.imagepath)[-1].split('.')[0]
        labelname = self.imagename + '.txt'
        self.dirspath = os.path.split(self.imagepath)[0]
        self.labelfilename = os.path.join(self.labelsdir, self.dirspath, labelname)
        self.darknetfilename = os.path.join(self.darknetdir, self.dirspath, labelname)

        self.reloadClassList()

        topViewLineCoords = (0,379,639,379)
        if not self.topViewLine:
            self.topViewLine = self.mainPanel.create_line(topViewLineCoords, width = 1, dash=(4, 4))
        else:
            self.mainPanel.delete(self.topViewLine)
            self.topViewLine = self.mainPanel.create_line(topViewLineCoords, width = 1, dash=(4, 4))

        smallPedestriansCoords = (0,50,639,50)
        if not self.smallLine:
            self.smallLine = self.mainPanel.create_line(smallPedestriansCoords, width = 1, dash=(4, 4))
        else:
            self.mainPanel.delete(self.smallLine)
            self.smallLine = self.mainPanel.create_line(smallPedestriansCoords, width = 1, dash=(4, 4))



        return self.reloadBboxListbox()

    def reloadBboxListbox(self):
        self.clearBBox()
        bbox_cnt = 0
        if os.path.exists(self.labelfilename):

            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    if i == 0:
                        bbox_cnt = int(line.strip())
                        if bbox_cnt > 0:
                            self.noBboxes.set(False)
                        else:
                            self.noBboxes.set(True)
                        continue
                    tmp = [int(t.strip()) for t in line.split()]
                    if len(tmp) == 4:
                        #Seems like the current label file is in the old format. We need to add the class to it, which the default is 0.
                        defaultClass = 0
                        tmp.append(defaultClass) #adding default class zero as last element.

                    x1, y1, x2, y2, classId = tmp
                    x1 = 0 if x1 < 0 else x1
                    y1 = 0 if y1 < 0 else y1
                    x2 = self.tkimg.width()-1 if x2 >= self.tkimg.width() else x2
                    y2 = self.tkimg.height()-1 if y2 >= self.tkimg.height() else y2
                    self.bboxList.append(tuple([x1,y1,x2,y2,classId]))
                    if not self.hideOtherBboxes.get():
                        tmpId = self.mainPanel.create_rectangle(x1, y1, \
                                                                x2, y2, \
                                                                width = 1, \
                                                                outline = COLORS[(len(self.bboxList)-1) % len(COLORS)])
                        self.mainPanel.create_text(x1+5, y1+5, activefill='#000fff000', fill='#fff', anchor=W, text=str(classId+1))
                        self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, '%d:(%d,%d,%d,%d)[%d]' %(i, x1,y1,x2,y2,classId+1))
                    self.listbox.itemconfig(len(self.bboxList) - 1, fg = COLORS[(len(self.bboxList) - 1) % len(COLORS)])
        else:
            self.noBboxes.set(False)

        return bbox_cnt > 0

    def convert(self, bbox):
        '''
        References:
        - https://github.com/Guanghan/darknet/blob/master/scripts/convert.py
        - https://github.com/AlexeyAB/darknet
        '''
        im_w, im_h = self.img.size

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

    def saveMeta(self):
        #register image by class count
        fileName = "classcount_{}.txt".format(len(self.bboxList))
        classCountFile = os.path.join(self.metadir, fileName)
        with open(classCountFile, 'a') as f:
            f.write("{}\n".format(self.imagepath))

    def prepareFileDirs(self):
        labelsdirpath = os.path.join(self.labelsdir, self.dirspath)
        os.makedirs(labelsdirpath, exist_ok=True)
        darknetdirspath = os.path.join(self.darknetdir, self.dirspath)
        os.makedirs(darknetdirspath, exist_ok=True)

    def saveImage(self):
        if len(self.bboxList) > 0 or self.noBboxes.get():
            self.prepareFileDirs();

            with open(self.labelfilename, 'w') as f:
                f.write('%d\n' % len(self.bboxList))
                for bbox in self.bboxList:
                    f.write(' '.join(map(str, bbox)) + '\n')

            with open(self.darknetfilename, 'w') as f:
                for bbox in self.bboxList:
                    f.write(self.convert(bbox=bbox) + '\n')

            # self.saveMeta()

            print('Image {} label saved. Path: {}'.format(self.cur, self.imagepath))
        else:
            print('Skipping: Image {}. You should draw bboxes or mark as [No BBoxes]. Path: {}.'.format(self.cur, self.imagepath))

            if os.path.exists(self.labelfilename):
                print('Also: Removing the existing label file.')
                os.remove(self.labelfilename)

            if os.path.exists(self.darknetfilename):
                print('Also: Removing the existing darknet label file.')
                os.remove(self.darknetfilename)



    def mouseClick(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            x1 = 0 if x1 < 0 else x1
            y1 = 0 if y1 < 0 else y1
            x2 = self.tkimg.width()-1 if x2 >= self.tkimg.width() else x2
            y2 = self.tkimg.height()-1 if y2 >= self.tkimg.height() else y2

            self.bboxList.append((x1, y1, x2, y2, self.currDefaultBboxClassId))
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, '%d:(%d,%d,%d,%d)[%d]' %(len(self.bboxIdList),x1, y1, x2, y2, self.currDefaultBboxClassId+1))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
        self.STATE['click'] = 1 - self.STATE['click']

    def mouseMove(self, event):
        self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width = 1)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width = 1)
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                            event.x, event.y, \
                                                            width = 1, \
                                                            outline = COLORS[len(self.bboxList) % len(COLORS)])

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def deleteLastBBox(self, event):
        bboxlen = len(self.bboxIdList)
        if bboxlen == 0:
            return
        idx = bboxlen - 1
        self.delBBoxByIndex(idx)

    def delBBoxByIndex(self, idx):
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        self.delBBoxByIndex(idx)

    def nextBBoxOverlap(self, event = None):
        pass

    def sendToTheHive(self, event = None):
        if not os.path.exists(self.hivedir):
            os.mkdir(self.hivedir)

        new_image_name = self.imagepath.replace('./','')
        new_image_name = new_image_name.replace('/','_')
        new_path = os.path.join(self.hivedir, new_image_name)
        shutil.copy(self.imagepath, new_path)
        self.hivecount += 1
        print("{}. Sent {} to {}.".format(self.hivecount, new_path, self.hivedir))


    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []

    def prevImage(self, event = None):
        if self.noBboxes.get() and len(self.bboxList) > 0:
            print('Conflict: Marked as [No BBoxes] but has bboxes in the list.')
            return

        self.saveImage()
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def checkNoBboxConflict(self):
        if self.noBboxes.get() and len(self.bboxList) > 0:
            print('Conflict: Marked as [No BBoxes] but has bboxes in the list.')
            return True
        return False

    def nextImage(self, event = None):
        if self.checkNoBboxConflict():
            return

        self.saveImage()
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

    def nextNoBboxImage(self, event = None):
        self.btnNextNoBBox.config(state="disabled")
        while True:
            self.nextImage()
            if len(self.bboxList) == 0 or self.cur >= self.total or self.checkNoBboxConflict():
                self.btnNextNoBBox.config(state="normal")
                return


    def gotoImage(self):
        if self.noBboxes.get() and len(self.bboxList) > 0:
            print('Conflict: Marked as [No BBoxes] but has bboxes in the list.')
            return

        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            self.cur = idx
            self.loadImage()

##    def setImage(self, self.imagepath = r'test2.jpg'):
##        self.img = Image.open(self.imagepath)
##        self.tkimg = ImageTk.PhotoImage(self.img)
##        self.mainPanel.config(width = self.tkimg.width())
##        self.mainPanel.config(height = self.tkimg.height())
##        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)

if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.resizable(width =  True, height = True)
    root.mainloop()

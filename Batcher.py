#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Program der masse omdøber filnavne via deres dato
#Version 1.12.0.0

License:

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

The GNU Public License is available at
http://www.gnu.org/copyleft/gpl.html
"""


try:
    from tkinter import *
    from tkinter import messagebox
except ImportError:
    raise ImportError("TKinter could not be imported")

                      
try:
    import subprocess
except ImportError:
    raise ImportError("The subprocess module is required to run this program")


try:
    from PIL import Image
    from PIL import ImageStat
    from PIL import ImageOps
    from PIL import ImageEnhance
    from PIL.ExifTags import TAGS
except ImportError:
    raise ImportError("Pillow module is required to run this program")


try:
    from sets import *
except ImportError:
    raise ImportError("sets module is required to run this program")

import os, re, shutil, datetime, glob #dateutil,

RESIZER = 70

class Batcher(Frame):

    # Define settings upon initialization. Here you can specify
    def __init__(self, master=None):
        # parameters that you want to send through the Frame class.
        Frame.__init__(self, master)

        # reference to the master widget, which is the tk window
        self.master = master

        # with that, we want to then run init_window, which doesn't yet exist
        self.init_window()

    # Creation of init_window
    def init_window(self):
        # changing the title of our master widget
        self.master.title("Batcher")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        # creating a menu instance
        menu = Menu(self.master)
        self.master.config(menu=menu)

        # create the file object
        file = Menu(menu)
        file.add_command(label="Quit", command=self.OnExit)
        menu.add_cascade(label="File", menu=file)

        # create the change object
        change = Menu(menu)
        change.add_command(label="Insert name", command=self.OnInsert)
        change.add_command(label="Change EXIF date", command=self.OnChange)
        change.add_command(label="Resize", command=self.OnResize)
        change.add_command(label="Convert -> JPG", command=self.ConvertRAWJPG)
        change.add_command(label="Convert to greyscale", command=self.OnGreyscale)
        change.add_command(label="Rename using EXIF data", command=self.OnRenameEXIF)
        change.add_command(label="Rename using filedate", command=self.OnRenameDATE)
        change.add_command(label="Rename consecutive numbers", command=self.OnConsNUMBER)
        menu.add_cascade(label="Change", menu=change)

        # create the timelapse object
        timelapse = Menu(menu)
        timelapse.add_command(label="Convert to greyscale", command=self.OnGreyscale)
        timelapse.add_command(label="Remove dark photos", command=self.OnRemoveDark)
        timelapse.add_command(label="Rename consecutive numbers", command=self.OnConsNUMBER)
        timelapse.add_command(label="Timelapse", command=self.OnTimelapse)
        timelapse.add_command(label="All in one", command=self.OnAllInOne)
        menu.add_cascade(label="Timelapse", menu=timelapse)

        # create the help object
        help = Menu(menu)
        help.add_command(label="About", command=self.OnAbout)
        menu.add_cascade(label="Help", menu=help)

    #Toolbar ---------------------------------------------------------------    
 #       toolbar = wx.ToolBar(self, -1)
 #       self.tcFilename = wx.TextCtrl(toolbar, -1,size=(100, -1))
 #       self.labelFilename = wx.StaticText(toolbar, wx.ID_ANY, label="Filename", style=wx.ALIGN_CENTER)
 #       self.tcFotograf = wx.TextCtrl(toolbar, -1,size=(100, -1))
 #       self.labelFotograf = wx.StaticText(toolbar, wx.ID_ANY, label="Photographer", style=wx.ALIGN_CENTER)
 #       self.tcSize = wx.TextCtrl(toolbar, -1, size=(35, -1))
 #       self.labelSize = wx.StaticText(toolbar, wx.ID_ANY, label="Size (%)", style=wx.ALIGN_CENTER)
 #       self.tcQuality = wx.TextCtrl(toolbar, -1, size=(35, -1))
 #       self.labelQuality = wx.StaticText(toolbar, wx.ID_ANY, label="Quality (%)", style=wx.ALIGN_CENTER)
 #       toolbar.AddControl(self.labelFilename)
 #       toolbar.AddControl(self.tcFilename)
#        toolbar.AddSeparator()
#        toolbar.AddControl(self.labelFotograf)
#        toolbar.AddControl(self.tcFotograf)
#        toolbar.AddSeparator()
#        toolbar.AddControl(self.labelSize)
#        toolbar.AddControl(self.tcSize)
#        toolbar.AddSeparator()
#        toolbar.AddControl(self.labelQuality)
#        toolbar.AddControl(self.tcQuality)
#        toolbar.Realize()
#        self.SetToolBar(toolbar)
        
    #---------------------------------------------------------------  
    #self.Bind(wx.EVT_BUTTON, self.OnLaunchCommandOk, id=ID_BUTTON)
#        self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_ABOUT)
#        self.Bind(wx.EVT_MENU, self.OnRename, id=ID_RENAME)
#        self.Bind(wx.EVT_MENU, self.OnGreyscale, id=ID_GREYSCALE)
#        self.Bind(wx.EVT_MENU, self.OnRenameDATE, id=ID_RENAMEDATE)
#        self.Bind(wx.EVT_MENU, self.OnRemoveDark, id=ID_REMOVEDARK)
#        self.Bind(wx.EVT_MENU, self.OnConsNUMBER, id=ID_CONSNUMBER)
#        self.Bind(wx.EVT_MENU, self.OnTimelapse, id=ID_TIMELAPSE)
#        self.Bind(wx.EVT_MENU, self.OnAllInOne, id=ID_ALLINONE)
#        self.Bind(wx.EVT_MENU, self.OnInsert, id=ID_INSERT)
#        self.Bind(wx.EVT_MENU, self.OnChange, id=ID_CHANGE)
#        self.Bind(wx.EVT_MENU, self.OnConvertRAWJPG, id=ID_CONVERTRAWJPG)
#        self.Bind(wx.EVT_MENU, self.OnResize, id=ID_RESIZE)
#        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_EXIT)
#        self.Bind(wx.EVT_TIMER, self.OnTimer, id=ID_TIMER)
#        self.Bind(wx.EVT_MENU, self.OnTest, id=ID_TEST)
#
#        self.panel = wx.Panel(self, -1, (0, 0), (1000 , 500))
#        self.panel.SetBackgroundColour('WHITE')
#        self.sizer=wx.BoxSizer(wx.VERTICAL)

    
    #Listcontrol -----------------------------------------------
#        self.lcWindow = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
#        self.lcWindow.InsertColumn(0, 'Before')
#        self.lcWindow.InsertColumn(1, 'After')
#        self.lcWindow.SetColumnWidth(0, 300)
#        self.lcWindow.SetColumnWidth(1, 300)
#        self.sizer.Add(self.lcWindow, 1, wx.EXPAND | wx.ALL, 3)
#        self.SetSizer(self.sizer)

    #Statusbar -------------------------------------------------
#        self.statusbar = self.CreateStatusBar()
#        self.statusbar.SetStatusText('Welcome to Batcher')
#        self.Centre()
#        self.Show(True)

#---------------------------------------------------------------
#---------------------------------------------------------------
        
    def OnExit(self):
        if messagebox.askokcancel("Close", "The application will be closed"):
            exit()

#---------------------------------------------------------------

    def OnAbout(self):
        messagebox.showinfo("About", "Batcher v1.12.0.0\t\nMartin B. Sander-Thomsen\t\n \nProject: www.github.com/Joghur/Batcher")

#---------------------------------------------------------------
#---------------------------------------------------------------
#---------------------------------------------------------------
            
    def OnAllInOne(self):
        dialog = self.get_folder('Pick a directory containing photos.')
        if dialog != None:
            self.RemoveDark(dialog)
            self.ConsNUMBER(dialog)
            self.Timelapse(dialog)

#---------------------------------------------------------------

    def OnChange(self):
        self.Change()

#---------------------------------------------------------------

    def OnConsNUMBER(self):
        self.ConsNUMBER(None) # ConsNUMBER functions needs a string arg or None

#---------------------------------------------------------------

    def OnConvertRAWJPG(self):
        self.ConvertRAWJPG()

#---------------------------------------------------------------
            
    def OnGreyscale(self):
        self.Greyscale()
              
#---------------------------------------------------------------

    def OnInsert(self):
        self.Insert()

#---------------------------------------------------------------           

    def OnRemoveDark(self):
        self.RemoveDark(None) # RemoveDark functions needs a string arg or None

#---------------------------------------------------------------
        
    def OnRename(self):
        self.Rename()
        
#---------------------------------------------------------------

    def OnRenameDATE(self):
        self.RenameDATE

#---------------------------------------------------------------
        
    def OnRenameEXIF(self):
        self.RenameEXIF

#---------------------------------------------------------------
            
    def OnResize(self):
        self.Resize()

#---------------------------------------------------------------
        
    def OnTest(self):
        self.Test()

#---------------------------------------------------------------
            
    def OnTimelapse(self):
        dialog = self.get_folder('Pick a directory containing photos.')
        if dialog != None:
            os.chdir(dialog)
            dirList3 = os.listdir("./")
            dirList3.sort()
            for t in dirList3:
                os.chdir(dialog)
                if os.path.isdir(t)==True:
                    os.chdir(t)
                    print("Using subdirectory: ", os.getcwd())
                    self.Timelapse(os.getcwd())
                    if self.Timelapse!=False:
                        num_items = self.lcWindow.GetItemCount()
                        origin = os.getcwd() + "/" + t + ".avi"
                        shutil.move(origin, dialog)
                        self.lcWindow.InsertStringItem(num_items, "Done. Find the timelapse video here: ")
                        self.lcWindow.SetStringItem(num_items, 1, dialog)
                else:
                    print("Using directory: ", dialog)
                    self.Timelapse(dialog)
                    if self.Timelapse!=False:
                        num_items = self.lcWindow.GetItemCount()
                        self.lcWindow.InsertStringItem(num_items, "Done. Find the timelapse video here: ")
                        self.lcWindow.SetStringItem(num_items, 1, dialog)
        else:
            return

        
        
#---------------------------------------------------------------
            

    #def OnLaunchCommandOk(self, event):
    #    input = self.tcFilename.GetValue()
    #    if input == '/bye':
    #        self.OnExit(self)
    #    elif input == '/about':
    #        self.OnAbout(self)
    #    elif input == '/bell':
    #        wx.Bell()
    #    else:
    #        self.statusbar.SetBackgroundColour('RED')
    #        self.statusbar.SetStatusText('Unknown Command')
    #        self.statusbar.Refresh()
    #        self.timer.Start(50)

    #    self.tcFilename.Clear()

#---------------------------------------------------------------
    
    def OnTimer(self):
        self.blick = self.blick + 1
        if self.blick == 25:
            self.statusbar.SetBackgroundColour('#E0E2EB')
            self.statusbar.Refresh()
            self.timer.Stop()
            self.blick = 0

            
#------------------------------------------------------------------------------------------------------------------------------
#Non event functions
#------------------------------------------------------------------------------------------------------------------------------         

 
#---------------------------------------------------------------
      
    def Change(self):
        messagebox.showinfo('Note', 'Not in yet\t')


#---------------------------------------------------------------

    def ConsNUMBER(self, args):
        if args==None:
            dialog = self.get_folder('Pick a directory containing timelapse photos. Photos need to be in named in consecutive order.')
            if dialog != None:            
                arbejds_dir=dialog
            else:
                return
        else:
            arbejds_dir=args
            
        os.chdir(arbejds_dir)
        taeller = 1
        arbejds_filnavn=self.tcFilename.GetValue()
        print("Filename: ", arbejds_filnavn)
        dirList = os.listdir("./")
        dirList.sort()
        dirlistlen = len(dirList)
        print('Number of items in work folder:', dirlistlen)
        # ToDo. Rucursion
        if dirlistlen > 9:
            if dirlistlen > 99:
                if dirlistlen > 999:
                    if dirlistlen > 9999:
                        if dirlistlen > 99999:
                            if dirlistlen > 999999:
                                padding="{0:07d}"
                            else:
                                padding="{0:06d}"
                        else:
                            padding="{0:05d}"
                    else:
                        padding="{0:04d}"
                else:
                    padding="{0:03d}"
            else:
                padding="{0:02d}"
        else:
            padding="{0:01d}"
            
        for d in dirList:
            os.chdir(arbejds_dir)
            if is_image(d): #Check if file is an image
                print(d, "is an image!")
                extension = os.path.splitext(d)[1]
                temp_file=d
                filnavn = arbejds_filnavn + '_' + padding.format(taeller) + extension
                print(filnavn)
                num_items = self.lcWindow.GetItemCount()
                self.lcWindow.InsertStringItem(num_items, d)
                self.lcWindow.SetStringItem(num_items, 1, filnavn)				
                print("Counter: ", taeller)
                print("---")
                os.rename(d, filnavn)
                taeller += 1
            elif os.path.isdir(d)==True:
                os.chdir(d)
                print(d, " is a subfolder!")
                dirList2 = os.listdir("./")
                dirList2.sort()
                taeller2 = 1
                dirlistlen2 = len(dirList2)
                print('Number of items in work folder:', dirlistlen2)
                # ToDo: Recursion
                if dirlistlen2 > 9:
                    if dirlistlen2 > 99:
                        if dirlistlen2 > 999:
                            if dirlistlen2 > 9999:
                                if dirlistlen2 > 99999:
                                    if dirlistlen2 > 999999:
                                        padding2="{0:07d}"
                                    else:
                                        padding2="{0:06d}"
                                else:
                                    padding2="{0:05d}"
                            else:
                                padding2="{0:04d}"
                        else:
                            padding2="{0:03d}"
                    else:
                        padding2="{0:02d}"
                else:
                    padding2="{0:01d}"
                    
                for d2 in dirList2:
                    print("Subdirectory: ", d)
                    if is_image(d2): #Check if file is an image
                        print(d2, "is an image!")
                        extension2 = os.path.splitext(d2)[1]
                        temp_file=d2
                        filnavn2 = d + '_' + padding2.format(taeller2) + extension2
                        print(filnavn2)
                        num_items = self.lcWindow.GetItemCount()
                        self.lcWindow.InsertStringItem(num_items, d2)
                        self.lcWindow.SetStringItem(num_items, 1, filnavn2)				
                        print("Counter: ", taeller2)
                        print("---")
                        os.rename(d2, filnavn2)
                        taeller2 += 1                    
                    else:
                        print(d2, " is NOT an image!")
                        print("---")
            
            else:
                print(d, " is NOT an image or a folder!")
                print("---")

        print("Done.")
            
#---------------------------------------------------------------

    def ConvertRAWJPG(self):
        dialog = self.get_folder('Pick a directory for converting photos.')
        if dialog != None:            
            arbejds_dir=dialog
            os.chdir(arbejds_dir)
        else:
            return
        dirList = os.listdir("./")
        dirList.sort()
        #for d in dirList:
        print('getcwd:', dirList)
        for d in dirList:
            if os.path.isdir(d) == False:
                if is_image(d): #Check if file is an image
                    print(d, "is an image!")
                    temp_file=d
                    d3 = os.path.splitext(d)[0]
                    arg = d + " " + d3 + ".jpg"
                    print("Arg=", arg)

                    # Command line for linux
                    command = "convert " + arg
                    print(command)
                    print("---")

                    num_items = self.lcWindow.GetItemCount()
                    self.lcWindow.InsertStringItem(num_items, d)
                    self.lcWindow.SetStringItem(num_items, 1, d3 + ".jpg")
                    child = subprocess.Popen(command, shell=True)
                    child.communicate()
                else:
                    print(d, "is NOT an image!")
                    print("---")

#---------------------------------------------------------------

    def get_folder(self, dialog_text):
        if messagebox.askokcancel("Get folder", dialog_text):
            arbejds_dir=dialog.GetPath()
            print("Working folder: ", arbejds_dir)
            return arbejds_dir
        else:
            print('No directory.')
            return None

#---------------------------------------------------------------
            
    def Greyscale(self):
        dialog = self.get_folder('Pick a directory containing photos. Photos will be converted to greyscale.')
        if dialog != None:            
            arbejds_dir=dialog
            os.chdir(arbejds_dir)
        else:
            return

        dirList = os.listdir("./")
        dirList.sort()
        for d in dirList:
            os.chdir(arbejds_dir)
            if is_image(d): #Check if file is an image
                print(d, " is an image!")
                print("Converting ", d, " to greyscale.")
                print("---")
                im = Image.open(d)
                im = ImageOps.grayscale(im)
                im.save(d)
            elif os.path.isdir(d)==True:
                os.chdir(d)
                print(d, " is a folder!")
                dirList2 = os.listdir("./")
                dirList2.sort()
                for d2 in dirList2:
                    print("Subdirectory: ", d)
                    if is_image(d2): #Check if file is an image
                        print(d2, " is an image!")
                        print("Converting ", d2, " to greyscale.")
                        print("---")
                        im2 = Image.open(d2)
                        im2 = ImageOps.grayscale(im2)
                        im2.save(d2)
                    else:
                        print(d2, " is NOT an image!")
                        print("---")
            else:
                print(d, " is NOT an image or folder!")
                print("---")

        print("Done.")
#---------------------------------------------------------------

    def Insert(self):
        messagebox.showinfo('Note', 'Not in yet\t')

 #---------------------------------------------------------------           

    def RemoveDark(self, args):
        if args==None:
            dialog = self.get_folder('Pick a directory containing photos. Dark photos will be removed and brightness will be controlled.')
            if dialog != None:            
                arbejds_dir=dialog
            else:
                return
        else:
            arbejds_dir=args
            
        os.chdir(arbejds_dir)
        dirList = os.listdir("./")
        dirList.sort()
        for d in dirList:
            os.chdir(arbejds_dir)
            if is_image(d): #Check if file is an image
                im = Image.open(d).convert('L')
                stat = ImageStat.Stat(im)
                print("Brightness value for ", d, " (<105 is considered a dark photo): ", stat.rms[0])
                if stat.rms[0] < 105:
                    os.remove(d)
                    print(d, " is too dark. It is removed!")
                    print("---")
                else:
                    #Brigthness nomalization
                    img = Image.open(d)
                    enhancer = ImageEnhance.Brightness(img)
                    factor = 120 /stat.rms[0]
                    img_enhanced = enhancer.enhance(factor)
                    img_enhanced.save(d)
                    print("Picture ", d, " adjusted brightness by factor of ", factor, "!")
                    print("---")
            elif os.path.isdir(d)==True:
                os.chdir(d)
                print(d, " is a folder!")
                dirList2 = os.listdir("./")
                dirList2.sort()                
                for d2 in dirList2:
                    print("Subdirectory: ", d)
                    if is_image(d2): #Check if file is an image
                        im2 = Image.open(d2).convert('L')
                        stat = ImageStat.Stat(im2)
                        print("Brightness value for ", d2, " (<105 is considered a dark photo): ", stat.rms[0])
                        if stat.rms[0] < 105:
                            os.remove(d2)
                            print(d2, " is too dark. It is removed!")
                            print("---")
                        else:
                            #Brigthness nomalization
                            img2 = Image.open(d2)
                            enhancer2 = ImageEnhance.Brightness(img2)
                            factor2 = 120 /stat.rms[0]
                            img_enhanced2 = enhancer2.enhance(factor2)
                            img_enhanced2.save(d2)
                            print("Picture ", d2, " adjusted brightness by factor of ", factor2, "!")
                            print("---")
                    else:
                        print(d2, " is NOT an image!")
                        print("---")
            else:
                print(d, " is NOT an image or folder!")
                print("---")
                
        print("Done.")

 #---------------------------------------------------------------
        
    def Rename(self):
        dialog = self.get_folder( 'Pick a directory for renaming files.')
        if dialog != None:            
            arbejds_dir=dialog
        else:
            return
            
        os.chdir(arbejds_dir)            
        nylig_lavet_folder=False
        sidste_fil=""
        flyt_fil=False
        folder_lavet=False
        taeller = 1
        arbejds_filnavn=self.tcFilename.GetValue()
        fotograf=self.tcFotograf.GetValue()
        if fotograf=="":
            pass
        else:
            fotograf= fotograf + "_"

        dirList = os.listdir("./")
        dirList.sort()
        print('getcwd:', dirList)
        def modification_date(filename):
            t = os.path.getmtime(filename)
            return datetime.datetime.fromtimestamp(t)

        def get_exif(fn):
            ret = {}
            i = Image.open(fn)
            info = i._getexif()
            try:
                for tag, value in info.items():
                    decoded = TAGS.get(tag, tag)
                    # print("Decoded=", decoded)
                    if decoded == "DateTimeOriginal":
                        ret[decoded] = value

                return ret['DateTimeOriginal']
            
            except ImportError:
                raise ImportError("This photo may not have EXIF data present")
        
        for d in dirList:
            #d2 = modification_date(d)
            if os.path.isdir(d) == False:
                if is_image(d): #Check if file is an image
                    print(d, "is an image!")
                    d2 = get_exif(d)
                    exif=2                        
                    temp_file=d
                    if exif==1: #bruger fil dato
                        th = str(d2.hour)
                        if len(th)==1:
                            th="0" + th

                        tm = str(d2.minute)
                        if len(tm)==1:
                            tm="0" + tm

                        ts = str(d2.second)
                        if len(ts)==1:
                            ts='0' + ts

                        ty = str(d2.year)

                        tmo = str(d2.month)
                        if len(tmo)==1:
                            tmo='0' + tmo

                        td = str(d2.day)
                        if len(td)==1:
                            td="0" + td
                        extra='_'
                        if arbejds_filnavn=="":
                            extra=''

                    if exif==2: #bruger exif data
                        #th = str(d2.hour)
                        dt = datetime.datetime.strptime(d2, "%Y:%m:%d %H:%M:%S")
                        th=str(dt.hour)
                        # print "dt", dt
                        if len(th)==1:
                            th="0" + th

                        tm = str(dt.minute)
                        if len(tm)==1:
                            tm="0" + tm

                        ts = str(dt.second)
                        if len(ts)==1:
                            ts='0' + ts

                        ty = str(dt.year)

                        tmo = str(dt.month)
                        if len(tmo)==1:
                            tmo='0' + tmo

                        td = str(dt.day)
                        if len(td)==1:
                            td="0" + td
                        extra='_'
                        if arbejds_filnavn=="":
                            extra=''

                    nytnavn=extra + ty + '-' + tmo + '-' + td + '_' + th + tm + ts
                    print(nytnavn)
                    print("Photographer:", fotograf)
                    filnavn = arbejds_filnavn + nytnavn + '_' + fotograf + d
                    print(filnavn)
                    print("---")
                    num_items = self.lcWindow.GetItemCount()
                    self.lcWindow.InsertStringItem(num_items, d)
                    self.lcWindow.SetStringItem(num_items, 1, filnavn)				
                    os.rename(d, filnavn)
                else:
                    print(d, " is NOT an image!")
                    print("---")

#---------------------------------------------------------------

    def RenameDATE(self):
        messagebox.showinfo('Note', 'Not in yet\t')

#---------------------------------------------------------------

    def RenameEXIF(self):
        messagebox.showinfo('Note', 'Not in yet\t')

#---------------------------------------------------------------
            
    def Resize(self):
        dialog = self.get_folder('Pick a directory for resizing photos.')
        if dialog != None:
            arbejds_dir=dialog
        else:
            return

        os.chdir(arbejds_dir)
        arbejds_filsize=self.tcSize.GetValue()
        arbejds_quality=self.tcQuality.GetValue()
        dirList = os.listdir("./")
        dirList.sort()
        for d in dirList:
            if is_image(d): #Check if file is an image
                print(d, " is an image!")
                arg = " " + "-resize " + arbejds_filsize + " " + "-quality " + arbejds_quality + " "
                # Command line for linux
                command = "mogrify " + d + arg + d
                print(command)
                print("---")
                child = subprocess.Popen(command, shell=True)
                child.communicate()
            else:
                print(d, " is NOT an image!")
                print("---")

#---------------------------------------------------------------

    def Test():
        pass
        return

#---------------------------------------------------------------
    
    def Timelapse(self, masterdir):
        if masterdir==None:
            dialog = self.get_folder('Pick a directory containing timelapse photos. Photos need to be in named in consecutive order.')
            if dialog != None:            
                arbejds_dir=dialog
            else:
                return False
        else:
            arbejds_dir=masterdir

        num_items = self.lcWindow.GetItemCount()
        self.lcWindow.InsertStringItem(num_items, "Working.")
        print('Working.')
        #timelapse_name=self.tcFilename.GetValue()
        files = glob.glob(arbejds_dir + '/*.*')
        for i in range(0,len(files)):
            temp = os.path.basename(files[i])
            suffix = os.path.splitext(temp)[1]
            suffix = suffix.lower()
            if is_image(temp):
                origname = os.path.basename(files[i])
                print(temp, " is an image!")
                suffix = os.path.splitext(temp)[1]
                print("Using ", suffix, " files as base for video")
                break
            else:
                print(temp, " is NOT an image!")
                
        #finding amount of digits in filename
        match = re.search('(\d+)\.\w+$', origname)
        print('Padding:', match.group(1))
        match_beforedigits = re.split(match.group(1), origname)
        print('Name before padding:', match_beforedigits[0])
        dig = len(match.group(1))
        print('How many digits in name:' ,dig)
        print('Photo Folder:', arbejds_dir)
        # Command line for linux. Windows need to have ffmpeg binary in same folder as Batcher or in PATH
        command = "ffmpeg -f image2 -i " + arbejds_dir + "/" + match_beforedigits[0] + "%" + str(dig) + "d" + suffix + " -r 30 " + arbejds_dir + "/" + match_beforedigits[0] + ".avi"
        print(command)
        child = subprocess.Popen(command, shell=false)
        child.communicate()
        print('Done.')
        print("---")
        return True
        

#-------------------------------------------------------------------------------------------------------------  
#MAIN
#-------------------------------------------------------------------------------------------------------------

def is_image(filename):
    temp = os.path.basename(filename)
    suffix = os.path.splitext(temp)[1]
    suffix = suffix.lower()
    if suffix==".jpg" or suffix==".raw" or suffix==".tiff" or suffix==".jpeg" or suffix==".gif" or suffix==".png": #Check if file is an image
        return True
    else:
        return False

#---------------------------------------------------------------


# root window created
root = Tk()

root.geometry("1000x800")

#creation of an instance
app = Batcher(root)

#mainloop
root.mainloop()









            

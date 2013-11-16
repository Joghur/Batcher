#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Program der masse omdøber filnavne via deres dato
#Version 1.11.5.4

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
    import wx #from wxPython.wx import *
except ImportError:
    raise ImportError,"The wxPython module is required to run this program"

try:
    from wxPython.wx import *
except ImportError:
    raise ImportError,"The wxPython module is required to run this program"
    dlg = wx.MessageDialog(self, 'The wxPython module is required to run this program\t', 'Note', wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()


                      
try:
    import subprocess
except ImportError:
    raise ImportError,"The subprocess module is required to run this program"
    dlg = wx.MessageDialog(self, 'The subprocess module is required to run this program\t', 'Note', wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()

try:
    from PIL import Image
    from PIL import ImageStat
    from PIL import ImageOps
    from PIL import ImageEnhance    
    from PIL.ExifTags import TAGS
except ImportError:
    raise ImportError,"The PIL (Python Image Library) module is required to run this program"
    dlg = wx.MessageDialog(self, 'The PIL (Python Image Library) module is required to run this program\t', 'Note', wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()


import os, re, sets, shutil, datetime, subprocess, glob #dateutil, 
from sets import Set



ID_TIMER = 1
ID_EXIT  = 2
ID_ABOUT = 3
ID_BUTTON = 4
ID_RENAME = 5
ID_RESIZE = 6
ID_CONVERTRAWJPG = 7
ID_INSERT = 8
ID_CHANGE = 9
ID_RENAMEDATE = 10
ID_CONSNUMBER = 11
ID_TIMELAPSE = 12
ID_ALLINONE = 13
ID_REMOVEDARK = 14
ID_GREYSCALE = 15
ID_TEST = 16

RESIZER = 70

class Batcher(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(632,500)) # Windows size here

        self.timer = wx.Timer(self, ID_TIMER)
        self.blick = 0
    
    #Menu ---------------------------------------------------------------  
        file = wx.Menu()
        file.Append(ID_EXIT, '&Quit\tCtrl+Q', 'Quit')

        change = wx.Menu()
        change.Append(ID_RENAME, '&Rename using EXIF data\tCtrl+R', 'Rename EXIF')
        change.Append(ID_RENAMEDATE, '&Rename using filedate\tCtrl+D', 'Rename date')
        change.Append(ID_CONSNUMBER, '&Rename with consecutive numbers\tCtrl+N', 'Rename consecutive numbers')       
        change.Append(ID_INSERT, '&Insert name\tCtrl+I', 'Insert')
        change.Append(ID_CHANGE, '&Change EXIF date\tCtrl+E', 'Change EXIF date')
        change.Append(ID_CONVERTRAWJPG, '&Convert -> JPG\tCtrl+C', 'Convert -> JPG')
        change.Append(ID_RESIZE, '&Resize\tCtrl+S', 'Resize')

        timelapse = wx.Menu()
        timelapse.Append(ID_GREYSCALE, '&Convert to greyscale', 'Convert to greyscale')        
        timelapse.Append(ID_REMOVEDARK, '&Remove dark photos', 'Remove dark photos and adjust brightness')        
        timelapse.Append(ID_CONSNUMBER, '&Rename with consecutive numbers\tCtrl+N', 'Rename consecutive numbers')
        timelapse.Append(ID_TIMELAPSE, '&Timelapse\tCtrl+T', 'Timelapse')
        timelapse.Append(ID_ALLINONE, '&All in one', 'Renaming and Timelapse')        

        test = wx.Menu()
        test.Append(ID_TEST, '&Test', 'Test')
        
        help = wx.Menu()
        help.Append(ID_ABOUT, '&About', 'About')

        menubar = wx.MenuBar()
        menubar.Append(file, '&File')
        menubar.Append(change, '&Change')
        menubar.Append(timelapse, '&Timelapse')
        menubar.Append(test, '&Test')    
        menubar.Append(help, '&Help')
        self.SetMenuBar(menubar)

    
    #Toolbar ---------------------------------------------------------------    
        toolbar = wx.ToolBar(self, -1)
        self.tc = wx.TextCtrl(toolbar, -1,size=(100, -1))
        self.labeltc = wx.StaticText(toolbar, wx.ID_ANY, label="Filename", style=wx.ALIGN_CENTER)
        self.tn = wx.TextCtrl(toolbar, -1,size=(100, -1))
        self.labeltn = wx.StaticText(toolbar, wx.ID_ANY, label="Photographer", style=wx.ALIGN_CENTER)
        #btn = wx.Button(toolbar, ID_BUTTON, 'Ok', size=(40, 28))
        self.tr = wx.TextCtrl(toolbar, -1, size=(100, -1))
        self.labeltr = wx.StaticText(toolbar, wx.ID_ANY, label="Size in %", style=wx.ALIGN_CENTER)
        self.ts = wx.TextCtrl(toolbar, -1, size=(100, -1))
        self.labelts = wx.StaticText(toolbar, wx.ID_ANY, label="Quality", style=wx.ALIGN_CENTER)
        toolbar.AddControl(self.labeltc)
        toolbar.AddControl(self.tc)
        toolbar.AddSeparator()
        toolbar.AddControl(self.labeltn)
        toolbar.AddControl(self.tn)
        toolbar.AddSeparator()
        toolbar.AddControl(self.labeltr)
        toolbar.AddControl(self.tr)
        toolbar.AddSeparator()
        toolbar.AddControl(self.labelts)
        toolbar.AddControl(self.ts)
        #toolbar.AddControl(btn)
        toolbar.Realize()
        self.SetToolBar(toolbar)
        
    #---------------------------------------------------------------  
    #self.Bind(wx.EVT_BUTTON, self.OnLaunchCommandOk, id=ID_BUTTON)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnRename, id=ID_RENAME)
        self.Bind(wx.EVT_MENU, self.OnGreyscale, id=ID_GREYSCALE)
        self.Bind(wx.EVT_MENU, self.OnRenameDATE, id=ID_RENAMEDATE)
        self.Bind(wx.EVT_MENU, self.OnRemoveDark, id=ID_REMOVEDARK)
        self.Bind(wx.EVT_MENU, self.OnConsNUMBER, id=ID_CONSNUMBER)
        self.Bind(wx.EVT_MENU, self.OnTimelapse, id=ID_TIMELAPSE)
        self.Bind(wx.EVT_MENU, self.OnAllInOne, id=ID_ALLINONE)                          
        self.Bind(wx.EVT_MENU, self.OnInsert, id=ID_INSERT)
        self.Bind(wx.EVT_MENU, self.OnChange, id=ID_CHANGE)
        self.Bind(wx.EVT_MENU, self.OnConvertRAWJPG, id=ID_CONVERTRAWJPG)
        self.Bind(wx.EVT_MENU, self.OnResize, id=ID_RESIZE)
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_EXIT)   
        self.Bind(wx.EVT_TIMER, self.OnTimer, id=ID_TIMER)
        self.Bind(wx.EVT_MENU, self.OnTest, id=ID_TEST)        

        self.panel = wx.Panel(self, -1, (0, 0), (1000 , 500))
        self.panel.SetBackgroundColour('WHITE')
        self.sizer=wx.BoxSizer(wx.VERTICAL)
        #self.sizer.Add(self.panel, 1, wx.EXPAND)

    
    #Listcontrol -----------------------------------------------
        self.lc = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.lc.InsertColumn(0, 'Before')
        self.lc.InsertColumn(1, 'After')
        self.lc.SetColumnWidth(0, 300)
        self.lc.SetColumnWidth(1, 300)
        self.sizer.Add(self.lc, 1, wx.EXPAND | wx.ALL, 3)
        self.SetSizer(self.sizer)

    #Statusbar -------------------------------------------------
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText('Welcome to Batcher')
        self.Centre()
        self.Show(True)

#---------------------------------------------------------------
#---------------------------------------------------------------
        
    def OnExit(self, event):
        dlg = wx.MessageDialog(self, 'Are you sure to quit Batcher?', 'Please Confirm', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.Close(True)

#---------------------------------------------------------------

    def OnAbout(self, event):
        dlg = wx.MessageDialog(self, 'Batcher\t\n' 'v1.11.5.4\t\n' '\t\n' 'Martin B. Sander-Thomsen\t\n' 'Project: www.github.com/Joghur/Batcher\t', 'About', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

#---------------------------------------------------------------
#---------------------------------------------------------------
#---------------------------------------------------------------
            
    def OnAllInOne(self, event):
        #self.AllInOne()
        self.RemoveDark()
        self.ConsNUMBER()
        self.Timelapse()

#---------------------------------------------------------------

    def OnChange(self, event):
        self.Change()

#---------------------------------------------------------------

    def OnConsNUMBER(self, event):
        self.ConsNUMBER()

#---------------------------------------------------------------

    def OnConvertRAWJPG(self, event):
        self.ConvertRAWJPG()

#---------------------------------------------------------------
            
    def OnGreyscale(self, event):
        self.Greyscale()
              
#---------------------------------------------------------------

    def OnInsert(self, event):
        self.Insert()

#---------------------------------------------------------------           

    def OnRemoveDark(self, event):
        self.RemoveDark()

#---------------------------------------------------------------
        
    def OnRename(self, event):
        self.Rename()
        
#---------------------------------------------------------------

    def OnRenameDATE(self, event):
        self.RenameDATE

#---------------------------------------------------------------
        
    def OnRenameEXIF(self, event):
        self.RenameEXIF

#---------------------------------------------------------------
            
    def OnResize(self, event):
        self.Resize()

#---------------------------------------------------------------
        
    def OnTest(self, event):
        self.Test()

#---------------------------------------------------------------
            
    def OnTimelapse(self, event):
        self.Timelapse()
        
#---------------------------------------------------------------
            

    #def OnLaunchCommandOk(self, event):
    #    input = self.tc.GetValue()
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

    #    self.tc.Clear()

#---------------------------------------------------------------
    
    def OnTimer(self, event):
        self.blick = self.blick + 1
        if self.blick == 25:
            self.statusbar.SetBackgroundColour('#E0E2EB')
            self.statusbar.Refresh()
            self.timer.Stop()
            self.blick = 0

            
#---------------------------------------------------------------
#Non event functions
#---------------------------------------------------------------            

#---------------------------------------------------------------
            
    def AllInOne(self):
        homefolder=os.getcwd()
        dialog = wxDirDialog ( None, message = 'Pick a directory.' )
        if dialog.ShowModal() == wxID_OK:
            print 'Directory:', dialog.GetPath()
            nylig_lavet_folder=False
            sidste_fil=""
            flyt_fil=False
            folder_lavet=False

            taeller = 1


            arbejds_dir=dialog.GetPath()
            arbejds_filnavn=self.tc.GetValue()

            os.chdir(arbejds_dir)

            print 'Work Folder:', os.getcwd()
            dirList = os.listdir("./")
            dirList.sort()
            print 'getcwd:', dirList
            dirlistlen = len(dirList)
            print 'Number of items in work folder:', dirlistlen
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
                if os.path.isdir(d) == False:
                    suffix = os.path.splitext(d)[1]
                    suffix = suffix.lower()
                    if suffix==".jpg" or suffix==".raw" or suffix==".tiff" or suffix==".jpeg" or suffix==".gif" or suffix==".png": #Check if file is an image
                        print d, " is an image!"
                        extension = os.path.splitext(d)[1]
                        temp_file=d

                        filnavn = arbejds_filnavn + '_' + padding.format(taeller) + extension
                        print filnavn

                        #wx.StaticText(self.panel, -1, filnavn, (1, taeller), style=wx.ALIGN_LEFT)
                        num_items = self.lc.GetItemCount()
                        self.lc.InsertStringItem(num_items, d)
                        self.lc.SetStringItem(num_items, 1, filnavn)				

                        #wx.ListCtrl(self, -1, style=wx.LC_REPORT)
                        #taeller += 1
                        print "Counter: ", taeller

                        os.rename(d, filnavn)
                        taeller += 1
                    else:
                        print d, " is NOT an image!"

        else: #dialog.ShowModal() == wxID_OK:
            print 'No directory.'
            dialog.Destroy()
   
        os.chdir(homefolder)                         
        num_items = self.lc.GetItemCount()
        self.lc.InsertStringItem(num_items, "Working.")
        print 'Working.'
        timelapse_name=self.tc.GetValue()
        files = glob.glob(arbejds_dir + '/*.*')
        for i in range(0,len(files)):
            temp = os.path.basename(files[i])
            suffix = os.path.splitext(temp)[1]
            suffix = suffix.lower()
            print "Temp: ", temp
            print "suffix: ", suffix
            if suffix==".jpg" or suffix==".raw" or suffix==".tiff" or suffix==".jpeg" or suffix==".gif" or suffix==".png": #Check if file is an image
                origname = os.path.basename(files[i])
                print "Origname:", origname
                suffix = os.path.splitext(temp)[1]
                break
            else:
                print "Temp (", temp, ") is not an image!"
        #finding a mount of digits in filename
        match = re.search('(\d+)\.\w+$', origname)
        print 'Padding:', match.group(1)
        match_beforedigits = re.split(match.group(1), origname)
        print 'Name before padding:', match_beforedigits[0]

        dig = len(match.group(1))
        print 'How many digits in name:' ,dig
        
        suffix= os.path.splitext(files[0])[1]
        print "Suffix:", suffix
        #os.chdir(arbejds_dir)
        print 'Work Folder:', homefolder
        print 'Photo Folder:', arbejds_dir
        # Command line for linux. Windows need to have ffmpeg binary in same folder as Batcher or in Path
        command = "ffmpeg -f image2 -i " + arbejds_dir + "/" + match_beforedigits[0] + "%" + str(dig) + "d" + suffix + " -r 30 " + arbejds_dir + "/" + timelapse_name + ".mp4"
        print command
        args = command.split()
        child = subprocess.Popen(args, shell=True)
        child.communicate()
        num_items = self.lc.GetItemCount()
        self.lc.InsertStringItem(num_items, "Done. Find the timelapse video here: ")
        self.lc.SetStringItem(num_items, 1, arbejds_dir)
        print 'Done.'

#---------------------------------------------------------------
        
    def Change(self):
        dlg = wx.MessageDialog(self, 'Not in yet\t', 'Note', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()    

#---------------------------------------------------------------

    def ConsNUMBER(self):
        dlg = wx.MessageDialog(self, "Have you made a backup? There\'s almost no error correction in Batcher.\nRemember to type in the generic filename you want added to the files.",'Please Confirm', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            dialog = wxDirDialog ( None, message = 'Pick a directory for renaming files.' )
            if dialog.ShowModal() == wxID_OK:
                print 'Directory:', dialog.GetPath()
                nylig_lavet_folder=False
                sidste_fil=""
                flyt_fil=False
                folder_lavet=False
                #dirList = os.listdir("./")
                #dirList.sort()
                #dirList = str(dirList)
                #u = unicode( dirList, "utf-8" )
                taeller = 1

                #print u, taeller

                arbejds_dir=dialog.GetPath() #raw_input('Indtast foldernavn--> ')
                arbejds_filnavn=self.tc.GetValue() #raw_input('Indtast ønsket filnavn--> ')

                os.chdir(arbejds_dir)

                print 'Work Folder:', os.getcwd()
                dirList = os.listdir("./")
                dirList.sort()
                print 'getcwd:', dirList
                dirlistlen = len(dirList)
                print 'Number of items in work folder:', dirlistlen
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
                    if os.path.isdir(d) == False: #Check if "file" is not a folder
                        suffix = os.path.splitext(d)[1]
                        suffix = suffix.lower()
                        if suffix==".jpg" or suffix==".raw" or suffix==".tiff" or suffix==".jpeg" or suffix==".gif" or suffix==".png": #Check if file is an image
                            print d, " is an image!"
                            extension = os.path.splitext(d)[1]
                            temp_file=d

                            filnavn = arbejds_filnavn + '_' + padding.format(taeller) + extension
                            print filnavn

                            #wx.StaticText(self.panel, -1, filnavn, (1, taeller), style=wx.ALIGN_LEFT)
                            num_items = self.lc.GetItemCount()
                            self.lc.InsertStringItem(num_items, d)
                            self.lc.SetStringItem(num_items, 1, filnavn)				

                            #wx.ListCtrl(self, -1, style=wx.LC_REPORT)
                            #taeller += 1
                            print "Counter: ", taeller

                            os.rename(d, filnavn)
                            taeller += 1
                        else:
                            print d, " is NOT an image!"

            else: #dialog.ShowModal() == wxID_OK:
                print 'No directory.'
                dialog.Destroy()

        else: #dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()
            
#---------------------------------------------------------------

    def ConvertRAWJPG(self):
        dialog = wxDirDialog ( None, message = 'Pick a directory for converting photos.' )
        if dialog.ShowModal() == wxID_OK:
            arbejds_dir=dialog.GetPath()
            arbejds_filsize=self.tr.GetValue()
            os.chdir(arbejds_dir)
            print 'Work Folder:', os.getcwd()
            dirList = os.listdir("./")
            dirList.sort()
            #for d in dirList:
            print 'getcwd:', dirList
            for d in dirList:
                if os.path.isdir(d) == False:
                    temp_file=d
                    d3 = os.path.splitext(d)[0]
                    arg = d + " " + d3 + ".jpg"
                    print "Arg=", arg
                    print 'Work Folder:', os.getcwd()

                    # Command line for linux
                    command = "convert " + arg
                    print command

                    num_items = self.lc.GetItemCount()
                    self.lc.InsertStringItem(num_items, d)
                    self.lc.SetStringItem(num_items, 1, d3 + ".jpg")
                    child = subprocess.Popen(command, shell=True)
                    child.communicate()						
        else: #dialog.ShowModal() == wxID_OK:
            print 'No directory.'

#---------------------------------------------------------------
            
    def Greyscale(self):
        dialog = wxDirDialog ( None, message = 'Pick a directory containing photos. Photos will be converted to greyscale.' )
        if dialog.ShowModal() == wxID_OK:
            arbejds_dir=dialog.GetPath()
            os.chdir(arbejds_dir)
            dirList2 = os.listdir("./")
            dirList2.sort()
            print 'Work Folder:', os.getcwd()
            for d in dirList2:
                suffix = os.path.splitext(d)[1]
                suffix = suffix.lower()
                if isa_image(d): #Check if file is an image
                    print d, " is an image!"
                    origname = os.path.splitext(d)[0]
                    suffix= os.path.splitext(d)[1]
                    print "Original filename:", origname
                    print "Suffix:", suffix
                    im = Image.open(d) #convert('LA')
                    im = ImageOps.grayscale(im)
                    im.save(d)
                    
                else:
                    print d, " is NOT an image!"
                
        else: #dialog.ShowModal() == wxID_OK:
            print 'No directory.'

#---------------------------------------------------------------

    def Insert(self):
        dlg = wx.MessageDialog(self, 'Not in yet\t', 'Note', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()

 #---------------------------------------------------------------           

    def RemoveDark(self):
        
            dialog = wxDirDialog ( None, message = 'Pick a directory containing photos. Dark photos will be removed and brightness will be controlled.' )
            if dialog.ShowModal() == wxID_OK:
                arbejds_dir=dialog.GetPath()
                os.chdir(arbejds_dir)
                dirList2 = os.listdir("./")
                dirList2.sort()
                print 'Work Folder:', os.getcwd()
                for d in dirList2:
                    suffix = os.path.splitext(d)[1]
                    suffix = suffix.lower()
                    if isa_image(d): #Check if file is an image
                        origname = os.path.basename(d)
                        print "Origname:", origname
                        print "Suffix:", suffix
                        im = Image.open(d).convert('L')
                        stat = ImageStat.Stat(im)
                        print "Brightness value (<90 is a dark photo)", stat.rms[0]
                        if stat.rms[0] < 90:
                            os.remove(d)
                            print d, " is too dark. It is removed"
                        else:
                            #Brigthness nomalization
                            img = Image.open(d)
                            enhancer = ImageEnhance.Brightness(img)
                            factor = 120 /stat.rms[0]
                            img_enhanced = enhancer.enhance(factor)
                            img_enhanced.save(d)
                            print "Picture ", d, " now has a brightness factor of ", factor
                    else:
                        print d, " is not an image!"

            else: #dialog.ShowModal() == wxID_OK:
                print 'No directory.'

 #---------------------------------------------------------------
        
    def Rename(self):
        dlg = wx.MessageDialog(self, "Have you made a backup? There\'s almost no error correction in Batcher.\nRemember to type in the generic filename you want added to the files.",'Please Confirm', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            dialog = wxDirDialog ( None, message = 'Pick a directory for renaming files.' )
            if dialog.ShowModal() == wxID_OK:
                print 'Directory:', dialog.GetPath()
                nylig_lavet_folder=False
                sidste_fil=""
                flyt_fil=False
                folder_lavet=False
                #dirList = os.listdir("./")
                #dirList.sort()
                #dirList = str(dirList)
                #u = unicode( dirList, "utf-8" )
                taeller = 1

                #print u, taeller

                arbejds_dir=dialog.GetPath() #raw_input('Indtast foldernavn--> ')
                arbejds_filnavn=self.tc.GetValue() #raw_input('Indtast ønsket filnavn--> ')
                fotograf=self.tn.GetValue()
                if fotograf=="":
                    pass
                else:
                    fotograf= fotograf + "_"

                os.chdir(arbejds_dir)

                print 'Work Folder:', os.getcwd()
                dirList = os.listdir("./")
                dirList.sort()
                print 'getcwd:', dirList
                def modification_date(filename):
                    t = os.path.getmtime(filename)
                    return datetime.datetime.fromtimestamp(t)

                def get_exif(fn):
                    ret = {}
                    i = Image.open(fn)
                    info = i._getexif()
                    for tag, value in info.items():
                        decoded = TAGS.get(tag, tag)
                        #print "Decoded=", decoded
                        if decoded == "DateTimeOriginal":
                            ret[decoded] = value
 
                    return ret['DateTimeOriginal']
           
                for d in dirList:
                    d2 = get_exif(d)
                    #d2 = modification_date(d)
                    if os.path.isdir(d) == False:
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
                            #print "dt", dt
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
                        print nytnavn
                        print "Photographer:", fotograf
                        filnavn = arbejds_filnavn + nytnavn + '_' + fotograf + d
                        print filnavn

                        #wx.StaticText(self.panel, -1, filnavn, (1, taeller), style=wx.ALIGN_LEFT)
                        num_items = self.lc.GetItemCount()
                        self.lc.InsertStringItem(num_items, d)
                        self.lc.SetStringItem(num_items, 1, filnavn)				

                        #wx.ListCtrl(self, -1, style=wx.LC_REPORT)
                        #taeller += 1
                        #print "Tæller: ", taeller


                        os.rename(d, filnavn)

            else: #dialog.ShowModal() == wxID_OK:
                print 'No directory.'
                dialog.Destroy()

        else: #dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()

#---------------------------------------------------------------

    def RenameDATE(self):
        dlg = wx.MessageDialog(self, 'Not in yet\t', 'Note', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()

#---------------------------------------------------------------

    def RenameEXIF(self):
        dlg = wx.MessageDialog(self, 'Not in yet\t', 'Note', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()            

#---------------------------------------------------------------
            
    def Resize(self):
        dialog = wxDirDialog ( None, message = 'Pick a directory for resizing photos.' )
        if dialog.ShowModal() == wxID_OK:
            arbejds_dir=dialog.GetPath()
            arbejds_filsize=self.tr.GetValue()
            arbejds_quality=self.ts.GetValue()
            os.chdir(arbejds_dir)
            dirList2 = os.listdir("./")
            dirList2.sort()
            for d in dirList2:
                suffix = os.path.splitext(d)[1]
                suffix = suffix.lower()
                if isa_image(d): #Check if file is an image
                    print d, " is an image!"
                    origname = os.path.splitext(d)[0]
                    suffix= os.path.splitext(d)[1]
                    print "Original filename:", origname
                    print "Suffix:", suffix
                    arg = " " + "-resize " + arbejds_filsize + " " + "-quality " + arbejds_quality + " "
                    print 'Work Folder:', os.getcwd()
                    # Command line for linux
                    command = "convert " + d + arg + d
                    print command
                    child = subprocess.Popen(command, shell=True)
                    child.communicate()

        else: #dialog.ShowModal() == wxID_OK:
            print 'No directory.'              

#---------------------------------------------------------------

     
    def Test():
        pass
        return

#---------------------------------------------------------------
    
    def Timelapse(self):
        dialog = wxDirDialog ( None, message = 'Pick a directory containing timelapse photos. Photos need to be in named in consecutive order' )
        if dialog.ShowModal() == wxID_OK:
            num_items = self.lc.GetItemCount()
            self.lc.InsertStringItem(num_items, "Working.")
            print 'Working.'
            timelapse_name=self.tc.GetValue()             
            arbejds_dir=dialog.GetPath()
            files = glob.glob(arbejds_dir + '/*.*')
            for i in range(0,len(files)):
                temp = os.path.basename(files[i])
                
                suffix = os.path.splitext(temp)[1]
                suffix = suffix.lower()
                print "Temp: ", temp
                print "Suffix: ", suffix
                if isa_image(temp):
                    origname = os.path.basename(files[i])
                    print temp, " is an image!"
                    suffix = os.path.splitext(temp)[1]
                    break
                else:
                    print temp, " is NOT an image!"
            #finding amount of digits in filename
            match = re.search('(\d+)\.\w+$', origname)
            print 'Padding:', match.group(1)
            match_beforedigits = re.split(match.group(1), origname)
            print 'Name before padding:', match_beforedigits[0]

            dig = len(match.group(1))
            print 'How many digits in name:' ,dig
            
            #suffix= os.path.splitext(files[0])
            print "Suffix:", suffix
            #os.chdir(arbejds_dir)
            #print 'Work Folder:', os.getcwd()
            print 'Photo Folder:', arbejds_dir
            # Command line for linux. Windows need to have ffmpeg binary in same folder as Batcher or in Path
            command = "ffmpeg -f image2 -i " + arbejds_dir + "/" + match_beforedigits[0] + "%" + str(dig) + "d" + suffix + " -r 30 " + arbejds_dir + "/" + timelapse_name + ".mp4"
            print command
            child = subprocess.Popen(command, shell=false)
            child.communicate()
            num_items = self.lc.GetItemCount()
            self.lc.InsertStringItem(num_items, "Done. Find the timelapse video here: ")
            self.lc.SetStringItem(num_items, 1, arbejds_dir)
            print 'Done.'

        else: #dialog.ShowModal() == wxID_OK:
            print 'No directory.'
        

#-------------------------------------------------------------------------------------------------------------  
#MAIN
#-------------------------------------------------------------------------------------------------------------    

def isa_image(filename):
    temp = os.path.basename(filename)
    suffix = os.path.splitext(temp)[1]
    suffix = suffix.lower()
    if suffix==".jpg" or suffix==".raw" or suffix==".tiff" or suffix==".jpeg" or suffix==".gif" or suffix==".png": #Check if file is an image
        return True
    else:
        return False

#---------------------------------------------------------------
    
app = wx.App()
Batcher(None, -1, 'Batcher')
app.MainLoop()













            

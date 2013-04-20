#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Program der masse omdøber filnavne via deres dato
#Version 1.08

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
    import wx
except ImportError:
    raise ImportError,"The wxPython module is required to run this program"

from wxPython.wx import *
import os, re, sets, shutil, datetime, dateutil, subprocess
from sets import Set
from PIL import Image
from PIL.ExifTags import TAGS


ID_TIMER = 1
ID_EXIT  = 2
ID_ABOUT = 3
ID_BUTTON = 4
ID_RENAME = 5
ID_RESIZE = 6
ID_CONVERTRAWJPG = 7
ID_INSERT = 8
ID_CHANGE = 9
RESIZER = 70


class Batch_Renamer(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)

        self.timer = wx.Timer(self, ID_TIMER)
        self.blick = 0
	
	#Menu 
        file = wx.Menu()
        file.Append(ID_EXIT, '&Quit\tCtrl+Q', 'Quit')

        change = wx.Menu()
        change.Append(ID_RENAME, '&Rename\tCtrl+R', 'Rename')
        change.Append(ID_INSERT, '&Insert name\tCtrl+I', 'Insert')
        change.Append(ID_CHANGE, '&Change EXIF date\tCtrl+D', 'Change EXIF date')
        change.Append(ID_CONVERTRAWJPG, '&Convert -> JPG\tCtrl+E', 'Convert -> JPG')
        change.Append(ID_RESIZE, '&Resize\tCtrl+T', 'Resize')

        help = wx.Menu()
        help.Append(ID_ABOUT, '&About', 'About')

        menubar = wx.MenuBar()
        menubar.Append(file, '&File')
        menubar.Append(change, '&Change')
        menubar.Append(help, '&Help')
        self.SetMenuBar(menubar)

	
	#Toolbar       
        toolbar = wx.ToolBar(self, -1)
        self.tc = wx.TextCtrl(toolbar, -1,size=(100, -1))
        self.labeltc = wx.StaticText(toolbar, wx.ID_ANY, label="Generic filename", style=wx.ALIGN_CENTER)
        self.tn = wx.TextCtrl(toolbar, -1,size=(100, -1))
        self.labeltn = wx.StaticText(toolbar, wx.ID_ANY, label="Photographer", style=wx.ALIGN_CENTER)
        #btn = wx.Button(toolbar, ID_BUTTON, 'Ok', size=(40, 28))
        self.tr = wx.TextCtrl(toolbar, -1, size=(100, -1))
        self.labeltr = wx.StaticText(toolbar, wx.ID_ANY, label="Size in %", style=wx.ALIGN_CENTER)	
        toolbar.AddControl(self.labeltc)
        toolbar.AddControl(self.tc)
        toolbar.AddSeparator()
        toolbar.AddControl(self.labeltn)
        toolbar.AddControl(self.tn)
        toolbar.AddSeparator()
        toolbar.AddControl(self.labeltr)
        toolbar.AddControl(self.tr)
        #toolbar.AddControl(btn)
        toolbar.Realize()
        self.SetToolBar(toolbar)
       
	#self.Bind(wx.EVT_BUTTON, self.OnLaunchCommandOk, id=ID_BUTTON)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnRename, id=ID_RENAME)
        self.Bind(wx.EVT_MENU, self.OnInsert, id=ID_INSERT)
        self.Bind(wx.EVT_MENU, self.OnChange, id=ID_CHANGE)
        self.Bind(wx.EVT_MENU, self.OnConvertRAWJPG, id=ID_CONVERTRAWJPG)
        self.Bind(wx.EVT_MENU, self.OnResize, id=ID_RESIZE)
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_EXIT)
        self.Bind(wx.EVT_TIMER, self.OnTimer, id=ID_TIMER)

        self.panel = wx.Panel(self, -1, (0, 0), (1000 , 500))
        self.panel.SetBackgroundColour('WHITE')
        self.sizer=wx.BoxSizer(wx.VERTICAL)
        #self.sizer.Add(self.panel, 1, wx.EXPAND)

	
	#Listcontrol
	self.lc = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.lc.InsertColumn(0, 'Before')
        self.lc.InsertColumn(1, 'After')
        self.lc.SetColumnWidth(0, 300)
        self.lc.SetColumnWidth(1, 300)
        self.sizer.Add(self.lc, 1, wx.EXPAND | wx.ALL, 3)
        self.SetSizer(self.sizer)

	#Statusbar
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText('Welcome to Batcher (Batch Renamer)')
        self.Centre()
        self.Show(True)

    def OnExit(self, event):
        dlg = wx.MessageDialog(self, 'Are you sure to quit Batch Renamer?', 
		'Please Confirm', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
		    self.Close(True)


    def OnAbout(self, event):

        dlg = wx.MessageDialog(self, 'Batcher (Batch Renamer)\t\n' 'v1.08\t\n' 'Martin Bøgh Sander-Thomsen\t', 'About', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
	
    def OnRename(self, event):
        dlg = wx.MessageDialog(self, "Have you made a backup? There\'s almost no error correction in Batch Renamer.\nRemember to type in the generic filename you want added to the files.",'Please Confirm', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
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
                #for d in dirList:
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
                        temp_file=d
                        exif=2
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
                        filnavn = arbejds_filnavn + nytnavn + '_' + d
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
	
    def OnResize(self, event):
	
        dlg = wx.MessageDialog(self, 'Have you made a backup? There\'s almost no error correction in Batch Renamer.\nRemember to type in the size in % you want photos to be resized to.', 
            'Please Confirm', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:

		dialog = wxDirDialog ( None, message = 'Pick a directory for resizing photos.' )
		if dialog.ShowModal() == wxID_OK:

			arbejds_dir=dialog.GetPath()
			arbejds_filsize=self.tr.GetValue()
			os.chdir(arbejds_dir)

			arg = " " + "-resize " + arbejds_filsize + " "
			print 'Work Folder:', os.getcwd()
			# Command line for linux
			command = "mogrify " + arg + "*"
			print command
			# Command line for windows, alter path if needed
			# command = "c:\\programs\\ImageMagick\\mogrify.exe " + arg + "*"

			# Invoke mogrify.
			child = subprocess.Popen(command, shell=True)
			child.communicate() 
		else: #dialog.ShowModal() == wxID_OK:

			print 'No directory.'
	else: #dlg.ShowModal() == wx.ID_YES:
		dlg.Destroy()


    def OnInsert(self, event):
        pass



    def OnChange(self, event):
        pass



    def OnConvertRAWJPG(self, event):
        dlg = wx.MessageDialog(self, 'Have you made a backup? There\'s almost no error correction in Batch Renamer.','Please Confirm', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
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

                        # Invoke mogrify.
                        child = subprocess.Popen(command, shell=True)
                        child.communicate()

            else: #dialog.ShowModal() == wxID_OK:
                print 'No directory.'

        else: #dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()


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

    def OnTimer(self, event):
        self.blick = self.blick + 1
        if self.blick == 25:
            self.statusbar.SetBackgroundColour('#E0E2EB')
            self.statusbar.Refresh()
            self.timer.Stop()
            self.blick = 0

app = wx.App()
Batch_Renamer(None, -1, 'Batcher (Batch Renamer)')
app.MainLoop()













            

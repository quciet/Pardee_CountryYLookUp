## Essential Module
import wx
import os
import wx.grid as gridlib
import pandas as pd
import numpy as np
import re
## Converting Algorithms for IFs DataBase
import ConvertingAlgo as Algo

File_set="Data files (*.csv;*.xlsx;*.xls)|*.csv;*.xlsx;*.xls"

class ConvertConcordBut(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent=parent)
        self.Sizer_butbegin=wx.BoxSizer(wx.HORIZONTAL)
        self.But_view=wx.Button(self, label="View Base")
        self.But_begin=wx.Button(self, label="Begin")
        self.Sizer_butbegin.Add(self.But_view,0,wx.RIGHT, 20)
        self.Sizer_butbegin.Add(self.But_begin,0,wx.LEFT, 20)
        self.SetSizer(self.Sizer_butbegin)

class TextWithButton_Ver(wx.Panel):
    def __init__(self,parent,txtTitle,listChoice=[]):
        wx.Panel.__init__(self,parent=parent)
        self.Sizer_TxtBut=wx.BoxSizer(wx.VERTICAL)
        self.Sizer_TxtBut_sub=wx.BoxSizer(wx.HORIZONTAL)
        # 
        self.Txt_title= wx.StaticText(self,label=txtTitle)
        self.list_Choice= listChoice
        self.Txt_Entry = wx.ComboBox(self,choices = self.list_Choice,\
        style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER)

        self.But_Entry= wx.Button(self, label="Clear")
        self.Txt_result= wx.StaticText(self,label='Selected:')
        #
        self.Sizer_TxtBut_sub.Add(self.Txt_Entry,proportion=2,flag=0,border=0)
        self.Sizer_TxtBut_sub.Add(self.But_Entry,proportion=0.5,flag=0,border=0)
        self.Sizer_TxtBut.Add(self.Txt_title,0,wx.EXPAND | wx.BOTTOM, 5)
        self.Sizer_TxtBut.Add(self.Sizer_TxtBut_sub,0,wx.EXPAND | wx.BOTTOM, 5)
        self.Sizer_TxtBut.Add(self.Txt_result,0,wx.EXPAND | wx.BOTTOM| 5)
        self.SetSizer(self.Sizer_TxtBut)
        #
        self.Txt_Entry.Bind(wx.EVT_TEXT, self.TextChanged) 
        self.IgnoreTxtChange = False
        self.Txt_Entry.Bind(wx.EVT_TEXT_ENTER, self.ShowList)
        self.Txt_Entry.Bind(wx.EVT_COMBOBOX, self.ConfirmSelected)
        self.But_Entry.Bind(wx.EVT_BUTTON, self.ResetSelected)
        
    def ConfirmSelected(self, event):
        if self.Txt_Entry.GetValue() in self.list_Choice:
            self.Txt_result.SetLabel(f'Selected: {self.Txt_Entry.GetValue()}')
        else:
            self.Txt_result.SetLabel('Selected:')

    def TextChanged(self,event):
        self.Txt_Entry.Dismiss()
        if self.IgnoreTxtChange:
            self.IgnoreTxtChange = False
            return
        if self.Txt_Entry.IsTextEmpty():
            self.Txt_Entry.SetItems(self.list_Choice)
            return
        Txt_current=event.GetString()
        item_list=[]
        for i in self.list_Choice:
            if Txt_current.lower() in i.lower():
                item_list.append(i)
        self.Txt_Entry.SetItems(item_list)
        self.IgnoreTxtChange = True
        self.Txt_Entry.SetValue(Txt_current)
        self.Txt_Entry.SetInsertionPoint(len(Txt_current))

    def ShowList(self,event):
        self.Txt_Entry.Popup()

    def ResetSelected(self,event):
        self.Txt_Entry.Clear()
        self.Txt_Entry.SetItems(self.list_Choice)
        self.Txt_result.SetLabel('Selected:')
 
class ConfirmOptionBut(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent=parent)
        self.Sizer_butbox=wx.BoxSizer(wx.VERTICAL)
        self.But_summary=wx.Button(self, label="View Summary")
        self.But_confirm=wx.Button(self, label="Confirm")
        self.But_baseupdate=wx.Button(self, label="Update Base")
        self.Sizer_butbox.Add(self.But_summary,0,wx.ALIGN_CENTER  | wx.TOP, 40)
        self.Sizer_butbox.Add(self.But_confirm,0,wx.ALIGN_CENTER | wx.TOP, 20)
        self.Sizer_butbox.Add(self.But_baseupdate,0,wx.ALIGN_CENTER | wx.TOP, 20)
        self.SetSizer(self.Sizer_butbox)

class RBotOptionPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent=parent)
        self.Box_opt=wx.StaticBox(self,wx.ID_ANY,'Options')
        self.Sizer_opt=wx.StaticBoxSizer(self.Box_opt,wx.VERTICAL)
        # Data Row/Column with Country Names
        self.Entry_C=TextWithButton_Ver(self,txtTitle='Row/Column-Countries:')
        self.Entry_Y=TextWithButton_Ver(self,txtTitle='Row/Column-Years:')
        self.Knowledge_Base=TextWithButton_Ver(self,txtTitle='Knowledge Base:',\
        listChoice=['IFs Essential (186 Country/Region)'])
        self.BeginConvert=ConvertConcordBut(self)
        # Layour Sizer
        self.Sizer_opt.Add(self.Entry_C,0,wx.EXPAND | wx.TOP, 5)
        self.Sizer_opt.Add(self.Entry_Y,0,wx.EXPAND | wx.TOP, 5)
        self.Sizer_opt.Add(self.Knowledge_Base,0,wx.EXPAND | wx.TOP, 5)
        self.Sizer_opt.Add(self.BeginConvert,0,wx.EXPAND | wx.TOP|wx.ALIGN_BOTTOM, 25)
        self.SetSizer(self.Sizer_opt)

class GridBoxPanel(wx.Panel):
    def __init__(self,parent,title):
        wx.Panel.__init__(self,parent=parent)
        # Data PreView Table
        self.Box_dataview=wx.StaticBox(self,wx.ID_ANY,label=title)
        self.Sizer_dataview=wx.StaticBoxSizer(self.Box_dataview,wx.VERTICAL)
        # Table using Grid
        self.Grid_dataview = gridlib.Grid(self)
        self.Grid_dataview.CreateGrid(0,0)
        # actions
        self.Grid_dataview.Bind(gridlib.EVT_GRID_LABEL_RIGHT_CLICK,self.showOptionMenu)
        # Layour Sizer
        self.Sizer_dataview.Add(self.Grid_dataview,1,wx.EXPAND,0)
        self.SetSizer(self.Sizer_dataview)

    def showOptionMenu(self, event):
        self.label_selected=self.Grid_dataview.GetColLabelValue(event.GetCol())
        if self.label_selected=="Match":
            self.MenuPosition=event.GetPosition()
            self.PopupMenu(self.menu_match,self.MenuPosition)
        if self.label_selected=="IFs":
            self.MenuPosition=event.GetPosition()
            self.PopupMenu(self.menu_ifs,self.MenuPosition)

    def toggle_menuitem(self, event):
        if self.label_selected=="IFs":
            self.PopupMenu(self.menu_ifs,self.MenuPosition)
        if self.label_selected=="Match":
            self.PopupMenu(self.menu_match,self.MenuPosition)


class RBotResultPanel(wx.Panel):
    def __init__(self,parent,title):
        wx.Panel.__init__(self,parent=parent)
        self.Box_result=wx.StaticBox(self,wx.ID_ANY,label=title)
        self.Sizer_result=wx.StaticBoxSizer(self.Box_result,wx.HORIZONTAL)
        # Add Results & Confirmation Options
        self.ResultPanel=GridBoxPanel(self,'Result Table')
        self.ConfirmPanel=ConfirmOptionBut(self)
        # Layour Sizer
        self.Sizer_result.Add(self.ResultPanel,4,wx.EXPAND|wx.FIXED_MINSIZE,0)
        self.Sizer_result.Add(self.ConfirmPanel,1,wx.EXPAND|wx.FIXED_MINSIZE,0)
        self.SetSizer(self.Sizer_result)

class RBotPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent=parent)
        # Country Concordance Viewer
        self.Box_country=wx.StaticBox(self,wx.ID_ANY,'Country Concordance')
        self.Sizer_country=wx.StaticBoxSizer(self.Box_country,wx.HORIZONTAL)
        # Add Panels for Option and Results
        self.OptPanel=RBotOptionPanel(self)
        self.OutPutPanel=RBotResultPanel(self,'Mapping')

        # self.ResultPanel=GridBoxPanel(self,'Mapping Results')
        # Layout Sizer
        self.Sizer_country.Add(self.OptPanel,1,wx.EXPAND|wx.FIXED_MINSIZE,0)
        self.Sizer_country.Add(self.OutPutPanel,3,wx.EXPAND|wx.FIXED_MINSIZE,0)
        self.SetSizer(self.Sizer_country)

class LeftPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent=parent)
        # Creating the Sizer
        self.Sizer_left = wx.BoxSizer(wx.HORIZONTAL)
        # File Browswer
        self.Directory_column=wx.GenericDirCtrl(self,dir=os.environ['USERPROFILE'],filter=File_set,\
        style=wx.DIRCTRL_EDIT_LABELS|wx.DIRCTRL_SHOW_FILTERS)
        self.Directory_column.ShowHidden(show=False)
        # Set Sizer
        self.Sizer_left.Add(self.Directory_column, 1, wx.EXPAND,0)
        self.SetSizer(self.Sizer_left)

class MainWindow(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, parent= None , title=title,size=wx.Size(1200,600))
        # Split into Right & Left Windows, Left as File Browser
        Splitter=wx.SplitterWindow(self,style=wx.SP_NOBORDER)
        rSplitter=wx.SplitterWindow(Splitter)
        # Split right panel into Top & Bot
        self.rTop_Panel=GridBoxPanel(parent=rSplitter,title='Data PreView')
        self.rBot_Panel=RBotPanel(rSplitter)
        rSplitter.SplitHorizontally(self.rTop_Panel,self.rBot_Panel,200)
        self.Left_Panel=LeftPanel(Splitter)
        Splitter.SplitVertically(self.Left_Panel,rSplitter,300)
        # Fixed Relative Size
        rSplitter.SetSashGravity(0.5)
        Splitter.SetSashGravity(0.5)

        # Setting up the menu
        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets
        Mainmenu= wx.Menu()
        menuAbout=Mainmenu.Append(101, "&About","Information about this program")
        Mainmenu.AppendSeparator()
        menuExit=Mainmenu.Append(102,"&Exit","Terminate the program")
        Filemenu=wx.Menu()
        menuOpen=Filemenu.Append(wx.ID_OPEN, "&Open","Open a new file")
        # Filemenu.AppendSeparator()
        # menuSave=Filemenu.Append(wx.ID_SAVE,"&Save\tCtrl+S","Save the file")
        # Creating the menubar
        menuBar = wx.MenuBar()
        menuBar.Append(Mainmenu,"&App") # Adding the "filemenu" to the MenuBar
        menuBar.Append(Filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        # Creating the Status bar
        self.statusBarBot=self.CreateStatusBar(1)
        self.statusBarBot.SetStatusText('YLookUp V0.1 beta')
        #
        self.FilePath=None

        # Setting up events.
        # For menu selection
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        '''self.Bind(wx.EVT_MENU, self.OnSave, menuSave)'''
        # For File Browswer Selection
        self.Bind(wx.EVT_DIRCTRL_SELECTIONCHANGED, self.OnBrowserSelect, \
        self.Left_Panel.Directory_column)
        self.Bind(wx.EVT_DIRCTRL_FILEACTIVATED, self.OnBrowserDoubleClick, \
        self.Left_Panel.Directory_column)
        self.Bind(wx.EVT_BUTTON,self.OnBeginConvert,\
        self.rBot_Panel.OptPanel.BeginConvert.But_begin)

    def OnAbout(self,event):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog(self, "A simple country concordance tool.\nContact:\nYutang.Xiong@du.edu\nPardee Center", "Information")
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,event):
        self.Close(True)  # Close the frame.

    def OnBrowserSelect(self,event):
        CurrentPath=self.Left_Panel.Directory_column.GetFilePath()
        if '.xlsx' in CurrentPath or '.xls' in CurrentPath or '.csv' in CurrentPath:
            self.statusBarBot.SetStatusText(f'Current Working File:{CurrentPath}')
            return CurrentPath
        else:
            self.statusBarBot.SetStatusText('YLookUp V0.1 beta')
            return None

    def OnBrowserDoubleClick(self,event):
        CurrentPath=self.OnBrowserSelect(wx.EVT_DIRCTRL_SELECTIONCHANGED)
        if CurrentPath:
            if '.xlsx' in CurrentPath or '.xls' in CurrentPath or '.csv' in CurrentPath:
                FileName=re.findall(r'([^/]+\.[a-zA-Z]+)',CurrentPath)[0]
                dlg = wx.MessageDialog(parent=self,message=f"Load the File: {FileName}?",\
                style=wx.OK|wx.CANCEL)
                if dlg.ShowModal()==wx.ID_OK:
                    self.PreviewData(CurrentPath)

    def OnOpen(self,event):
        self.dirname = ''
        dlg = wx.FileDialog(parent=self,message="Choose a Data file",\
        defaultDir=self.dirname,wildcard=File_set,style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            OpenPath=os.path.join(self.dirname, self.filename)
            dlg.Destroy()
        self.PreviewData(OpenPath)

    def PreviewData(self,OpenPath):
        # Use data to create grid for preview
        if '.csv' in OpenPath:
            LoadedPreviewDT=pd.read_csv(OpenPath,nrows=20)
        if '.xlsx' in OpenPath or '.xls' in OpenPath:
            LoadedPreviewDT=pd.read_excel(OpenPath,nrows=20)
        DTdim=LoadedPreviewDT.shape
        MissDT=LoadedPreviewDT.isna()
        Current_Col_Number=self.rTop_Panel.Grid_dataview.GetNumberCols()
        Current_Row_Number=self.rTop_Panel.Grid_dataview.GetNumberRows()
        LoadedDataColumns=list(LoadedPreviewDT.columns)
        # Update Grid table
        if Current_Row_Number<DTdim[0]:
            self.rTop_Panel.Grid_dataview.AppendRows(numRows=DTdim[0]-Current_Row_Number)
        if DTdim[1]>Current_Col_Number:
            self.rTop_Panel.Grid_dataview.AppendCols(numCols=DTdim[1]-Current_Col_Number)
        elif DTdim[1]<Current_Col_Number:
            self.rTop_Panel.Grid_dataview.DeleteCols(pos=0,numCols=Current_Col_Number-DTdim[1])
        for i in range(DTdim[0]):
            for j in range(DTdim[1]):
                if MissDT.iloc[i,j]==False:
                    self.rTop_Panel.Grid_dataview.SetCellValue(i, j, str(LoadedPreviewDT.iloc[i,j]))
                else:
                    self.rTop_Panel.Grid_dataview.SetCellValue(i, j, '')
        for i in range(DTdim[1]):
            self.rTop_Panel.Grid_dataview.SetColLabelValue(col=i,value=LoadedDataColumns[i])
        self.rBot_Panel.OptPanel.Entry_C.list_Choice=LoadedDataColumns
        self.rBot_Panel.OptPanel.Entry_C.Txt_Entry.SetItems(LoadedDataColumns)
        self.rBot_Panel.OptPanel.Entry_Y.list_Choice=LoadedDataColumns
        self.rBot_Panel.OptPanel.Entry_Y.Txt_Entry.SetItems(LoadedDataColumns)
        self.FilePath=OpenPath

    def OnBeginConvert(self,event):
        if self.rBot_Panel.OptPanel.Knowledge_Base.Txt_result.GetLabel()==\
        'Selected: IFs Essential (186 Country/Region)':
            if self.rBot_Panel.OptPanel.Entry_C.Txt_result.GetLabel()!='Selected:':
                Country_Column_Load=re.sub(r'Selected: ','',\
                self.rBot_Panel.OptPanel.Entry_C.Txt_result.GetLabel())
                mapping=Algo.IFs_map()
                if '.xlsx' in self.FilePath or '.xls' in self.FilePath:
                    dt=pd.read_excel(self.FilePath)
                elif '.csv' in self.FilePath:
                    dt=pd.read_csv(self.FilePath)
                Data_Dict=Algo.CountryColumn(dt,Country_Column_Load,mapping)
                ###
                DTmapper=pd.DataFrame(Data_Dict)
                DTmapper.sort_values(by=['Country','IFs'],inplace=True)
                DTmapper.reset_index(inplace=True,drop=True)
                MissDT=DTmapper.isna()
                DTdim=DTmapper.shape
                LoadedDataColumns=list(DTmapper.columns)
                self.rBot_Panel.OutPutPanel.ResultPanel.Grid_dataview.ClearGrid()
                Current_Col_Number=self.rBot_Panel.OutPutPanel.ResultPanel.Grid_dataview.GetNumberCols()
                Current_Row_Number=self.rBot_Panel.OutPutPanel.ResultPanel.Grid_dataview.GetNumberRows()
                # Update Grid table
                if Current_Row_Number<DTdim[0]:
                    self.rBot_Panel.OutPutPanel.ResultPanel.Grid_dataview.AppendRows(numRows=DTdim[0]-Current_Row_Number)
                if DTdim[1]>Current_Col_Number:
                    self.rBot_Panel.OutPutPanel.ResultPanel.Grid_dataview.AppendCols(numCols=DTdim[1]-Current_Col_Number)
                elif DTdim[1]<Current_Col_Number:
                    self.rBot_Panel.OutPutPanel.ResultPanel.Grid_dataview.DeleteCols(pos=0,numCols=Current_Col_Number-DTdim[1])
                for i in range(DTdim[0]):
                    for j in range(DTdim[1]):
                        if MissDT.iloc[i,j]==False:
                            self.rBot_Panel.OutPutPanel.ResultPanel.Grid_dataview.SetCellValue(i, j, str(DTmapper.iloc[i,j]))
                        else:
                            self.rBot_Panel.OutPutPanel.ResultPanel.Grid_dataview.SetCellValue(i, j, '')
                for i in range(DTdim[1]):
                    self.rBot_Panel.OutPutPanel.ResultPanel.Grid_dataview.SetColLabelValue(col=i,value=LoadedDataColumns[i])
                # After Table updates, update the header options
                self.rBot_Panel.OutPutPanel.ResultPanel.menu_ifs=wx.Menu()
                self.rBot_Panel.OutPutPanel.ResultPanel.menu_match=wx.Menu()
                for i in ["IFs","Match"]:
                    items_filter=list(set(Data_Dict[i]))
                    items_filter.sort()
                    if i=="IFs":
                        menu_edit=self.rBot_Panel.OutPutPanel.ResultPanel.menu_ifs
                    else:
                        menu_edit=self.rBot_Panel.OutPutPanel.ResultPanel.menu_match
                    for j in range(1002,1002+len(items_filter)):
                        menu_edit.AppendCheckItem(j, items_filter[j-1002])
                        menu_edit.Bind(wx.EVT_MENU, self.rBot_Panel.OutPutPanel.ResultPanel.toggle_menuitem, id=j)
                    menu_edit.AppendSeparator()
                    menu_edit.Append(203, "Apply Filter")
                    menu_edit.Append(204, "Clear Filter")



if __name__=="__main__":
    app = wx.App()
    frame = MainWindow("YLookUp")
    frame.Show()
    app.MainLoop()

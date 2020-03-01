# Dialog for create a new window
# -*- coding: utf-8 -*-
import io
import os 
import wx
import numpy as np
import json
#from scenario_generator import *
 
class generate_Dialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "New scenario", size=(280, 240))
 
        self.InitUI() #绘制Dialog的界面
 
    def InitUI(self):
        panel = wx.Panel(self)
 
        Label1 = wx.StaticText(panel, -1, 'Demand rate', pos=(20, 25))
        Label1.SetForegroundColour('#0a74f7')
 
        self.demand_input = wx.SpinCtrl(panel, -1, "", min = 1, max = 100000, initial = 2000, pos=(150, 25), size = [80,-1])
 
        Label2 = wx.StaticText(panel, -1, 'Working hours', pos=(20, 50))
        Label2.SetForegroundColour('#0a74f7')
 
        self.workhour_input = wx.SpinCtrl(panel, -1, "", min = 1, max = 50, initial = 1, pos=(150, 50), size = [80,-1])
        
        Label3 = wx.StaticText(panel, -1, 'Rhythm', pos=(20, 75))
        Label3.SetForegroundColour('#0a74f7')
 
        self.rhythm_input = wx.SpinCtrl(panel, -1, "", min = 1, max = 10, initial = 2, pos=(150, 75), size = [80,-1])

        Label4 = wx.StaticText(panel, -1, 'Platoon length', pos=(20, 100))
        Label4.SetForegroundColour('#0a74f7')
 
        self.platoon_input = wx.SpinCtrl(panel, -1, "", min = 1, max = 50, initial = 1, pos=(150, 100), size = [80,-1])
        

        sureButton = wx.Button(panel, -1, 'Generate', pos=(20, 140), size=(80, 40))
        sureButton.SetForegroundColour('white')
        sureButton.SetBackgroundColour('#0a74f7')
        self.Bind(wx.EVT_BUTTON, self.sureEvent, sureButton)
        sureButton.Enabled = False
 
        cancleButton = wx.Button(panel, -1, 'Cancel', pos=(140, 140), size=(80, 40))
        cancleButton.SetBackgroundColour('black')
        cancleButton.SetForegroundColour('#ffffff')
        self.Bind(wx.EVT_BUTTON, self.cancleEvent, cancleButton)
 
    def sureEvent(self, event):
        de = self.demand_input.GetValue()
        wh = self.workhour_input.GetValue()
        rhy = self.rhythm_input.GetValue()
        pla = self.platoon_input.GetValue()
        #scenario_generator(de,wh,rhy,pla)
        self.Destroy() 
 
    def cancleEvent(self, event):
        self.Destroy() 


class testframe(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        dlg = InputDialog(0)
        dlg.ShowModal()
        dlg.Destroy()

if __name__ == "__init__":
    app = wx.App()
    frame = testframe()
    frame.Show()
    app.MainLoop()

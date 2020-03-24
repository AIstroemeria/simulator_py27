# Dialog for create a new window
# -*- coding: utf-8 -*-
### py2 ###
from __future__ import division
######
import io
import os 
import wx
import numpy as np
import json
import time
from scenario_generator import *
import threading as td
from multiprocessing import Queue
from pubsub import pub
 
class generate_Dialog(wx.Dialog):
    def __init__(self, m, n, noj):
        wx.Dialog.__init__(self, None, -1, "New scenario", size=(260, 280))
        self.m = m
        self.n = n
        self.noj = noj
        self.InitUI() #绘制Dialog的界面
        self.result = None
 
    def InitUI(self):
        panel = wx.Panel(self)
 
        Label1 = wx.StaticText(panel, -1, 'Demand rate', pos=(20, 25))
        Label1.SetForegroundColour('#0a74f7')
 
        self.demand_input = wx.SpinCtrl(panel, -1, "", min = 1, max = 100000, initial = 2000, pos=(150, 25), size = [80,-1])
 
        Label2 = wx.StaticText(panel, -1, 'Working minute', pos=(20, 50))
        Label2.SetForegroundColour('#0a74f7')
 
        self.workhour_input = wx.SpinCtrl(panel, -1, "", min = 1, max = 60, initial = 10, pos=(150, 50), size = [80,-1])
        
        Label3 = wx.StaticText(panel, -1, 'Rhythm', pos=(20, 75))
        Label3.SetForegroundColour('#0a74f7')
 
        self.rhythm_input = wx.SpinCtrl(panel, -1, "", min = 1, max = 10, initial = 2, pos=(150, 75), size = [80,-1])

        Label4 = wx.StaticText(panel, -1, 'Platoon length', pos=(20, 100))
        Label4.SetForegroundColour('#0a74f7')
 
        self.platoon_input = wx.SpinCtrl(panel, -1, "", min = 1, max = 50, initial = 1, pos=(150, 100), size = [80,-1])
        

        self.sureButton = wx.Button(panel, -1, 'Generate', pos=(20, 140), size=(80, 40))
        self.sureButton.SetForegroundColour('white')
        self.sureButton.SetBackgroundColour('#0a74f7')
        self.Bind(wx.EVT_BUTTON, self.sureEvent, self.sureButton)
 
        self.cancleButton = wx.Button(panel, -1, 'Cancel', pos=(140, 140), size=(80, 40))
        self.cancleButton.SetBackgroundColour('black')
        self.cancleButton.SetForegroundColour('#ffffff')
        self.Bind(wx.EVT_BUTTON, self.cancleEvent, self.cancleButton)
        
        self.gauge = wx.Gauge(panel, -1, 100, pos = (30,200))
        self.gauge.SetBezelFace(3)
        self.gauge.SetShadowWidth(3)
        pub.subscribe(self.set_gauge, "change_guage_generating")
 
    def sureEvent(self, event):
        de = self.demand_input.GetValue()
        wh = self.workhour_input.GetValue()
        rhy = self.rhythm_input.GetValue()
        pla = self.platoon_input.GetValue()
        q = Queue()
        td1 = td.Thread(target = scenario_generator, args = (q, self.m, self.n, self.noj, de, wh, rhy, pla))
        td1.start()
        td2 = td.Thread(target = self.receiving, args = (q,))
        td2.start()
        self.sureButton.Enabled = False
        self.cancleButton.Enabled = False
 
    def receiving(self, q):
        self.result = q.get()
        self.Destroy() 

    def cancleEvent(self, event):
        self.Destroy() 
    
    def set_gauge(self, v):
        self.gauge.SetValue(v)


class testframe(wx.Frame):
    def __init__(self, *args, **kw):
        super(testframe, self).__init__(*args, **kw)
        dlg = InputDialog(0)
        dlg.ShowModal()
        dlg.Destroy()

if __name__ == "__init__":
    app = wx.App()
    frame = testframe()
    frame.Show()
    app.MainLoop()

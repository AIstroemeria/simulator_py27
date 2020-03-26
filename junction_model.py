# -*- coding: utf-8 -*-
### py2 ###
from __future__ import division
######
import wx
import wx.lib.agw.shapedbutton as SB
import numpy as np
import copy
from pubsub import pub

class junction_btn(SB.SBitmapButton):
    def __init__(self, parent, id, bitmap, pos=wx.DefaultPosition, size=wx.DefaultSize, order = [0,0]):
        super(junction_btn, self).__init__(parent, id, bitmap, pos=pos, size=size)

        self.order = order
        self.bmp = bitmap
        self.titleFont = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.num1 = 15
        self.num2 = 8
        self.capacity_1 = 100
        self.capacity_2 = 50

        self.InitBuffer()

        self.Bind(wx.EVT_PAINT, self.Onpaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)
    
    def InitBuffer(self):
        size = self.GetClientSize()
        #3 创建一个缓存的设备上下文
        self.buffer = wx.Bitmap(size.width, size.height)
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackgroundMode(wx.PENSTYLE_TRANSPARENT)
        #4 使用设备上下文
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.Draw_all(dc)
        self.reInitBuffer = False
    
    def OnSize(self, event):
        self.reInitBuffer = True #11 处理一个resize事件
    
    def OnIdle(self, event):#12 空闲时的处理
        if self.reInitBuffer:
            self.InitBuffer()
            self.Refresh(False)
    
    def Onpaint(self, event):
        dc = wx.BufferedPaintDC(self, self.buffer)
    

    def Draw_all(self, dc):
        dc.SetPen(wx.Pen("Black",style = wx.PENSTYLE_TRANSPARENT))
        dc.SetBrush(wx.Brush("White"))
        dc.DrawRectangle (0, 0, *dc.GetSize())
        dc.DrawBitmap(self.bmp,0,0)
        str1 = str(self.num1)
        str2 = str(self.num2)
        dc.SetFont(self.titleFont)
        dc.SetBrush(wx.Brush("Green"))
        self.draw_stat(dc, str1, [1/4,1/2], self.num1, self.capacity_1)
        dc.SetBrush(wx.Brush("Red"))
        self.draw_stat(dc, str2, [3/4,1/2], self.num2, self.capacity_2)
    
    def draw_stat(self, dc, s, pos, numb, capa):
        dw, dh = dc.GetSize()
        tw, th = dc.GetTextExtent(s)
        r = th
        if numb <= capa and numb > 0:
            ang1 = 90 - 360*numb/capa
            ang2 = 90
            dc.SetPen(wx.Pen("Black",style = wx.PENSTYLE_TRANSPARENT))
            dc.DrawEllipticArc (dw*pos[0]-r, dh*pos[1]-r, 2*r, 2*r, ang1, ang2)
            r = r*0.9
            dc.SetBrush(wx.Brush("White"))
            dc.DrawCircle(dw*pos[0],dh*pos[1],r)
        dc.SetPen(wx.Pen("Black"))
        dc.DrawText(s, dw*pos[0]-tw/2, dh*pos[1]-th/2)
    
    def get_order(self):
        return self.order
    
    def Getnum1Data(self):
        return self.num1

    def Setnum1Data(self, new_num):
        self.num1 = new_num
        self.InitBuffer()
    
    def Changenum1Data(self, new_num):
        self.num1 = self.num1 + new_num
        self.InitBuffer()
    
    def Getnum2Data(self):
        return self.num2

    def Setnum2Data(self, new_num):
        self.num2 = new_num
        self.InitBuffer()
    
    def Changenum2Data(self, new_num):
        self.num2 = self.num2 + new_num
        self.InitBuffer()

    def Change_data(self, data):
        self.num1 = data[0][self.order[0]][self.order[1]]
        self.num2 = data[1][self.order[0]][self.order[1]]
        self.InitBuffer()
        pub.sendMessage("refresh_main")
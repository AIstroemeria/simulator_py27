
# -*- coding: utf-8 -*-
### py2 ###
from __future__ import division
######
import wx
import wx.lib.agw.shapedbutton as SB
import numpy as np
import copy
from pubsub import pub
import os

class entrance_btn(SB.SBitmapButton):
    def __init__(self, parent, id, bitmap, pos=wx.DefaultPosition, size=wx.DefaultSize, order = [0,0]):
        super(entrance_btn, self).__init__(parent, id, bitmap, pos=pos, size=size)

        self.size = size
        self.order = order
        self.bmp = bitmap
        self.titleFont = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.num1 = 0
        self.num2 = 10

        self.scale = 1
        img1 = self.bmp.ConvertToImage()
        if order[0] == 0 and np.mod(order[1],2) == 0:
            img2 = img1.Scale(size[0]*self.scale,size[1]*self.scale/1.8)
        elif order[0] == 0 and np.mod(order[1],2) == 1:
            img2 = img1.Scale(size[0]*self.scale,size[1]*self.scale/1.8)
            #img2 = img2.Rotate180()
        elif order[0] == 1 and np.mod(order[1],2) == 0:
            #img2 = img1.Rotate90() 
            img2 = img1.Scale(size[0]*self.scale/1.8,size[1]*self.scale)
        elif order[0] == 1 and np.mod(order[1],2) == 1:
            #img2 = img1.Rotate90() 
            img2 = img1.Scale(size[0]*self.scale/1.8,size[1]*self.scale)
            #img2 = img2.Rotate180()
        self.bmp = wx.Bitmap(img2)

        name = os.getcwd() + os.sep + "mate" + os.sep + 'goods.png'
        img1 = wx.Image(name=name, type = wx.BITMAP_TYPE_PNG)
        img2 = img1.Scale(min(self.size)*0.2,min(self.size)*0.2)
        self.goodbmp = wx.Bitmap(img2)

        name = os.getcwd() + os.sep + "mate" + os.sep + 'drone.png'
        img1 = wx.Image(name=name, type = wx.BITMAP_TYPE_PNG)
        img2 = img1.Scale(min(self.size)*0.2,min(self.size)*0.2)
        self.agvbmp = wx.Bitmap(img2)

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
        offset = 0.3
        if self.order[0] == 0 and np.mod(self.order[1],2) == 0:
            dc.DrawBitmap(self.bmp,0,offset/(1+2*offset) * self.size[1])
        elif self.order[0] == 0 and np.mod(self.order[1],2) == 1:
            dc.DrawBitmap(self.bmp,0,offset/(1+2*offset) * self.size[1])
        elif self.order[0] == 1 and np.mod(self.order[1],2) == 0:
            dc.DrawBitmap(self.bmp,offset/(1+2*offset) * self.size[0],0)
        elif self.order[0] == 1 and np.mod(self.order[1],2) == 1:
            dc.DrawBitmap(self.bmp,offset/(1+2*offset) * self.size[0],0)
        str1 = str(self.num1)
        str2 = str(self.num2)
        dc.SetFont(self.titleFont)
        rate1 = []
        rate2 = []
        rate3 = []
        rate4 = []
        if self.order[0] == 0 and np.mod(self.order[1],2) == 0:
            rate1 = [1/2,offset/(1+2*offset)]
            rate2 = [1/2,(1+offset)/(1+2*offset)]
            rate3 = [1/4,offset/(1+2*offset)]
            rate4 = [1/4,(1+offset)/(1+2*offset)]
        elif self.order[0] == 0 and np.mod(self.order[1],2) == 1:
            rate1 = [1/2,offset/(1+2*offset)]
            rate2 = [1/2,(1+offset)/(1+2*offset)]
            rate3 = [1/4,offset/(1+2*offset)]
            rate4 = [1/4,(1+offset)/(1+2*offset)]
        elif self.order[0] == 1 and np.mod(self.order[1],2) == 0:
            rate1 = [offset/(1+2*offset),1/2]
            rate2 = [(1+offset)/(1+2*offset),1/2]
            rate3 = [offset/(1+2*offset),1/4]
            rate4 = [(1+offset)/(1+2*offset),1/4]
        elif self.order[0] == 1 and np.mod(self.order[1],2) == 1:
            rate1 = [offset/(1+2*offset),1/2]
            rate2 = [(1+offset)/(1+2*offset),1/2] 
            rate3 = [offset/(1+2*offset),1/4]
            rate4 = [(1+offset)/(1+2*offset),1/4]

        dc.DrawBitmap(self.goodbmp,rate3[0]*self.size[0]-self.goodbmp.GetWidth()/2,rate3[1]*self.size[1]-self.goodbmp.GetHeight()/2)
        dc.SetBrush(wx.Brush("Green"))
        self.draw_stat(dc, str1, rate1, self.num1)

        dc.DrawBitmap(self.agvbmp,rate4[0]*self.size[0]-self.agvbmp.GetWidth()/2,rate4[1]*self.size[1]-self.agvbmp.GetHeight()/2)
        dc.SetBrush(wx.Brush("Red"))
        self.draw_stat(dc, str2, rate2, self.num2)
    
    def draw_stat(self, dc, s, pos, numb):
        dw, dh = dc.GetSize()
        tw, th = dc.GetTextExtent(s)
        r = th
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
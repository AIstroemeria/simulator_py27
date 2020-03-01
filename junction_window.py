# under working!
# junction window of simulator
import wx
import wx.lib.agw.shapedbutton as SB
import copy
import numpy as np

# junction map 控件
class junc_map_window(wx.Window):
    def __init__(self,parent,size,juncs,order,range,zoom_scale):
        #super(the_map, self).__init__(parent,size=size,style=wx.TRANSPARENT_WINDOW | wx.NO_BORDER)
        super(the_map_window, self).__init__(parent,size=size,style=wx.NO_BORDER)
        self.SetBackgroundColour("White")

        # Attributes
        self.size = size
        self.m = 2
        self.n = 2
        self.juncs = juncs
        self.blocksize = (self.size[0]/1.5,self.size[1]/1.5)
        self.roadwidth = self.blocksize[0]/10
        self.points = []
        self.nums = []

        self.order = order
        self.range = range
        self.zoom_scale = zoom_scale
        
        self.InitBuffer()

        # Event Handlers
        self.Bind(wx.EVT_LEFT_DOWN, self.Onleftdown)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
        self.Bind(wx.EVT_PAINT, self.Onpaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

    def InitBuffer(self):
        size = self.GetClientSize()
        #3 创建一个缓存的设备上下文
        self.buffer = wx.Bitmap(size.width, size.height)
        dc = wx.BufferedDC(None, self.buffer)
        #4 使用设备上下文
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.Draw_all(dc)
        self.reInitBuffer = False
    
    def GetpointsData(self):
        return self.points[:]

    def SetpointsData(self, points):
        self.points = points[:]
        self.InitBuffer()
        self.Refresh()
    
    def GetnumsData(self):
        return self.nums[:]

    def SetnumsData(self, nums):
        self.nums = nums[:]
        self.InitBuffer()
        self.Refresh()
    
    def OnSize(self, event):
        self.reInitBuffer = True #11 处理一个resize事件

    def OnIdle(self, event):#12 空闲时的处理
        if self.reInitBuffer:
            self.InitBuffer()
            self.Refresh(False)

    def Onleftdown(self, event):
        print("press on map")
        position = event.GetPosition()
        for item in self.points:
            if (item[0]-position[0])^2 + (item[1]-position[1])^2 < 25:
                break

    def OnErase(self, event):
    # Do nothing, reduces flicker by removing
    # unneeded background erasures and redraws
        pass

    def Draw_all(self, dc):
        ori = (0,0)

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush('WHITE'))
        dc.DrawRectangle(0,0,self.size[0],self.size[1])

        # draw horizontal and vertical roads
        pos = copy.copy(ori)
        dc.SetBrush(wx.Brush('GREY'))
        for i in range(self.m):
            dc.DrawRectangle(pos[0],pos[1]+(i+1)*self.blocksize[1]-self.roadwidth/2,self.blocksize[0]*(self.n+1),self.roadwidth)
        for j in range(self.n):
            dc.DrawRectangle((j+1)*self.blocksize[0]-self.roadwidth/2+pos[0],pos[1],self.roadwidth,self.blocksize[1]*(self.m+1))
        
        # draw turnings
        pen = wx.Pen('GREY', 2*self.roadwidth, wx.PENSTYLE_SOLID)
        pen.SetCap(wx.CAP_ROUND)
        dc.SetPen(pen)
        for i in range(self.m):
            for j in range(self.n):
                pos = [ori[0]+(j+1)*self.blocksize[0], ori[1]+(i+1)*self.blocksize[1]]
                if np.mod((i+j),2) == 0:
                    dc.DrawLine(pos[0]-self.blocksize[0]/4,pos[1]-self.roadwidth/2,pos[0]-self.roadwidth,pos[1]-self.roadwidth/2)
                    dc.DrawLine(pos[0]-self.roadwidth/2,pos[1]-self.blocksize[1]/4,pos[0]-self.roadwidth/2,pos[1]-self.roadwidth)
                    dc.DrawLine(pos[0]+self.blocksize[0]/4,pos[1]+self.roadwidth/2,pos[0]+self.roadwidth,pos[1]+self.roadwidth/2)
                    dc.DrawLine(pos[0]+self.roadwidth/2,pos[1]+self.blocksize[1]/4,pos[0]+self.roadwidth/2,pos[1]+self.roadwidth)
                else:
                    dc.DrawLine(pos[0]+self.blocksize[0]/4,pos[1]-self.roadwidth/2,pos[0]+self.roadwidth,pos[1]-self.roadwidth/2)
                    dc.DrawLine(pos[0]+self.roadwidth/2,pos[1]-self.blocksize[1]/4,pos[0]+self.roadwidth/2,pos[1]-self.roadwidth)
                    dc.DrawLine(pos[0]-self.blocksize[0]/4,pos[1]+self.roadwidth/2,pos[0]-self.roadwidth,pos[1]+self.roadwidth/2)
                    dc.DrawLine(pos[0]-self.roadwidth/2,pos[1]+self.blocksize[1]/4,pos[0]-self.roadwidth/2,pos[1]+self.roadwidth)  

        point_scale = 3.5*self.zoom_scale
        for item in self.points:
            if item[3][0] > self.range[0] and item[3][0] < self.range[1] and item[3][1] > self.range[2] and item[3][1] < self.range[4]:
                x = (item[3][0] - self.range[0])*self.zoom_scale
                y = (item[3][1] - self.range[1])*self.zoom_scale
                dc.SetPen(wx.Pen("Black", 1))
                dc.SetBrush(wx.Brush('RED'))
                dc.DrawCircle(x,y,point_scale)
                if item[5] != 0:
                    dc.SetPen(wx.Pen("Black", style = wx.PENSTYLE_TRANSPARENT))
                    dc.SetBrush(wx.Brush('Green'))
                    dc.DrawCircle(x,y,point_scale*0.8)

    def Onpaint(self, event):
        dc = wx.BufferedPaintDC(self, self.buffer)

if __name__ == '__main__':
    points = []
    nums = []
    juncs = []
    for j in range(6):
        for i in range(5):
            juncs.append([i+0.5, j])
    for i in range(6):
        for j in range(5):
            juncs.append([i, j+0.5])

    app = wx.App()
    frame = wx.Frame(None)
    ske = the_map_window(frame,[800,800],6,6,juncs)
    frame.Show(True)
    app.MainLoop()
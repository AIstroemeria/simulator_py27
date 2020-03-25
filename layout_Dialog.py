# Dialog for create a new window
# -*- coding: utf-8 -*-
### py2 ###
from __future__ import division

######
import os 
import io
import wx
import numpy as np
import json
from path_generator import *
 
class InputDialog(wx.Dialog):
    def __init__(self, func_callBack):
        wx.Dialog.__init__(self, None, -1, "network layout", size=(320, 300))
        self.func_callBack = func_callBack
        self.InitUI() #绘制Dialog的界面 

    def InitUI(self):
        panel = wx.Panel(self)
 
        accountLabel = wx.StaticText(panel, -1, 'pairs of rows', pos=(20, 25))
        accountLabel.SetForegroundColour('#0a74f7')
 
        self.m_input = wx.SpinCtrl(panel, -1, "", min = 1, max = 50, initial = 3, pos=(150, 25), size = [40,-1])
 
        passwordLabel = wx.StaticText(panel, -1, 'pairs of columns', pos=(20, 70))
        passwordLabel.SetForegroundColour('#0a74f7')
 
        self.n_input = wx.SpinCtrl(panel, -1, "", min = 1, max = 50, initial = 3, pos=(150, 70), size = [40,-1])

        sureButton = wx.Button(panel, -1, 'Initial network', pos=(20, 130), size=(120, 40))
        sureButton.SetForegroundColour('white')
        sureButton.SetBackgroundColour('#0a74f7')
        self.Bind(wx.EVT_BUTTON, self.sureEvent, sureButton)
 
        cancleButton = wx.Button(panel, -1, 'Cancel', pos=(160, 130), size=(120, 40))
        cancleButton.SetBackgroundColour('black')
        cancleButton.SetForegroundColour('#ffffff')
        self.Bind(wx.EVT_BUTTON, self.cancleEvent, cancleButton)

        loadButton = wx.Button(panel, -1, 'Load from ...', pos=(20, 190), size=(260, 40))
        loadButton.SetBackgroundColour('blue')
        loadButton.SetForegroundColour('#ffffff')
        self.Bind(wx.EVT_BUTTON, self.loadEvent, loadButton)
 
    def sureEvent(self, event):
        m = self.m_input.GetValue()*2
        n = self.n_input.GetValue()*2
        self.initial_network(m,n)
        self.Destroy() 
 
    def cancleEvent(self, event):
        self.Destroy() 

    def loadEvent(self, event):
        self.func_callBack(0,"")
        self.Destroy() 

    def initial_network(self,m,n):
        juncs = []
        #[x,y]
        for j in range(m):
            for i in range(n-1):
                juncs.append([i+0.5, j])
        for i in range(n):
            for j in range(m-1):
                juncs.append([i, j+0.5])
        noj = m*(n-1) + n*(m-1)

        l1 = 1.5        # intersection to junc/entrance/exit
        l2 = 1.5
        l3 = 1.5
        l4 = 3        # intersection to intersection
        l5 = 6         # turning
        lor = np.ones([2*m+2*n+noj+4*m*n,2*m+2*n+noj+4*m*n])
        lor = lor * 10000
        #entrance 2 intersection
        for i in range(m):
            if np.mod(i,2) == 0:
                lor[i,2*m+2*n+noj+4*i*n] = l1
            else:
                lor[i,2*m+2*n+noj+4*(i+1)*n-4] = l1
        for i in range(n):
            if np.mod(i,2) == 0:
                lor[m+i,2*m+2*n+noj+4*(m-1)*n+4*i+1] = l1
            else:
                lor[m+i,2*m+2*n+noj+4*i+1] = l1
        #intersection 2 exit
        for i in range(m):
            if np.mod(i,2) == 0:
                lor[2*m+2*n+noj+4*(i+1)*n-2,m+n+i] = l2
            else:
                lor[2*m+2*n+noj+4*i*n+2,m+n+i] = l2
        for i in range(n):
            if np.mod(i,2) == 0:
                lor[2*m+2*n+noj+4*i+3,m+n+m+i] = l2
            else:
                lor[2*m+2*n+noj+4*(m-1)*n+4*i+3,m+n+m+i] = l2
        #junction 2 intersection and inverse
        for i in range(noj):
            pos = juncs[i]
            if np.mod(pos[0]*2,2) == 1:         # junction in row
                intersec1 = [pos[1],int(pos[0]-0.5)]
                intersec2 = [pos[1],int(pos[0]+0.5)]
                if np.mod(pos[1], 2) == 0:      # odd row
                    lor[2*m+2*n+noj+intersec1[0]*4*n+intersec1[1]*4+2, 2*m+2*n+i] = l3
                    lor[2*m+2*n+i, 2*m+2*n+noj+intersec2[0]*4*n+intersec2[1]*4] = l3 
                else:
                    lor[2*m+2*n+noj+intersec2[0]*4*n+intersec2[1]*4+2, 2*m+2*n+i] = l3
                    lor[2*m+2*n+i, 2*m+2*n+noj+intersec1[0]*4*n+intersec1[1]*4] = l3 
            else:
                intersec1 = [int(pos[1]-0.5),pos[0]]
                intersec2 = [int(pos[1]+0.5),pos[0]]
                if np.mod(pos[0], 2) == 0:      # odd column
                    lor[2*m+2*n+noj+intersec2[0]*4*n+intersec1[1]*4+3, 2*m+2*n+i] = l3
                    lor[2*m+2*n+i, 2*m+2*n+noj+intersec1[0]*4*n+intersec1[1]*4+1] = l3
                else:
                    lor[2*m+2*n+noj+intersec1[0]*4*n+intersec1[1]*4+3, 2*m+2*n+i] = l3
                    lor[2*m+2*n+i, 2*m+2*n+noj+intersec2[0]*4*n+intersec2[1]*4+1] = l3
        #intersection to intersection
        for i in range(m):
            for j in range(n):
                intersec = 2*m+2*n+noj+i*4*n+j*4
                lor[intersec,intersec+3] = l5
                lor[intersec+1,intersec+2] = l5
                lor[intersec,intersec+2] = l4
                lor[intersec+1,intersec+3] = l4

        #0
        num_of_nodes = len(lor)
        for i in range(num_of_nodes):
            for j in range(num_of_nodes):
                if i==j:
                    lor[i,j] = 0

        #recording edges
        edges = [[] for _ in range(num_of_nodes)]
        for i in range(num_of_nodes):
            for j in range(num_of_nodes):
                if lor[i][j] < 10000:
                    edges[i].append((j,lor[i][j]))
        
        pre_matrix,dis_matrix = generate_path_rhythm(num_of_nodes, edges)
        data = {"pre":pre_matrix.tolist(), "dis":dis_matrix.tolist(),"m":m, "n":n, "edges":edges}
        temp = 0
        filename = "./layout"+str(temp)+".json"
        while True:
            if os.path.exists(filename):
                temp = temp + 1
                filename = "./layout"+str(temp)+".json"
            else:
                break    

        with io.open(filename,'w',encoding='utf-8') as json_file:
            json_file.write(unicode(json.dumps(data, ensure_ascii=False)))
        
        self.func_callBack(1,"layout"+str(temp)+".json") 

class testframe(wx.Frame):
    def __init__(self, *args, **kw):
        super(testframe,self).__init__(*args, **kw)
        dlg = InputDialog(0)
        dlg.ShowModal()
        dlg.Destroy()

if __name__ == "__init__":
    app = wx.App()
    frame = testframe()
    frame.Show()
    app.MainLoop()

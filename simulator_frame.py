# -*- coding: utf-8 -*-
### py2 ###
from __future__ import division
######
import wx
import wx.lib.agw.shapedbutton as SB
import os
import io
import numpy as np
import copy
import json
import sys, os, time
import random
import threading as td
import multiprocessing as mp
import matplotlib.pyplot as plt
from pubsub import pub
from junction_model import junction_btn
from entrance_model import entrance_btn
from main_window import the_map_window
from layout_Dialog import InputDialog
from generating_Dialog import generate_Dialog
from simulating import simulating
# from PyPubSub import pub as Publisher

class MDIFrame(wx.MDIParentFrame):
    def __init__(self):
        wx.MDIParentFrame.__init__(self, None, -1, "Simulation_v0.1", size = (800,800))
        self.filepath = ""
        self.filename = ""
        menu = wx.Menu()
        menu.Append(5000, "&New Window")
        menu.Append(5001, "&Exit")
        menubar = wx.MenuBar()
        menubar.Append(menu, "&File")

        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.OnNewWindow, id = 5000)
        self.Bind(wx.EVT_MENU, self.OnExit, id = 5001)

    def OnExit(self, evt):
        self.Close(True)  

    def OnNewWindow(self, evt):
        dlg = InputDialog(self.loading_layout)
        dlg.Show()
    
    def loading_layout(self,status,thefile):
        if status == 0:
            wildcard = "Json files(*.json)|*.json"
            dlg = wx.FileDialog(None,"select",os.getcwd(),"",wildcard=wildcard,style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) 
            result = dlg.ShowModal()
            if result == wx.ID_OK:
                self.filename = dlg.GetFilename()
                self.filepath = dlg.GetPath()
            dlg.Destroy()
        else:
            self.filename = ehefile
            self.filepath = "./" + thefile

        with io.open(self.filepath,'r',encoding='utf-8') as json_file: 
            data=json.load(json_file)
        m = data['m']
        n = data['n']
        win = Simulator_frame(self, m, n, id=-1, title = self.filename, layout_filepath = self.filepath)
        win.Show(True)
        

class Simulator_frame(wx.MDIChildFrame):
    def __init__(self, parent, m=6, n=6, id=wx.ID_ANY, title="",
                layout_filepath = "",
                pos=wx.DefaultPosition, size=wx.DefaultSize,
                style=wx.DEFAULT_FRAME_STYLE,                 
                name="Simulator_frame"):  
        
        super(Simulator_frame, self).__init__(parent, id, title,
                                     pos, size, style, name)

        # Attributes        
        with io.open(layout_filepath,'r',encoding='utf-8') as json_file: 
            data=json.load(json_file)
        self.pre_matrix = data['pre']
        self.dis_matrix = data['dis']

        self.m = m #num of horizontal lines
        self.n = n #num of vertival lines
        self.noj = 2*m*n - m - n
        self.rhythm = 2
        self.simulation_res = None
        self.blockinfo_res = None

        self.is_start = False
        self.t_start = None
        self.pausing_time = 0
        self.next_flag = False
        self.next_t_start = None
        self.counting = -1
        self.accelarate_r = 5
        self.num_of_wave = 1
        self.current_running_t = 0
        self.new_period = 0
        self.time_duration = 0.1 # duration between different simulation frames
        self.completemission = 0
        self.counting_frames = 0

        block_scale = 100
        road_scale = 1/12
        self.size = ((n+2)*block_scale,(m+2)*block_scale)
        self.blocksize = (block_scale, block_scale)
        self.roadwidth =  block_scale*road_scale

        self.juncs = []
        #[x,y]
        for j in range(m):
            for i in range(n-1):
                self.juncs.append([i+0.5, j])
        for i in range(n):
            for j in range(m-1):
                self.juncs.append([i, j+0.5])
        self.locations = self.get_locations(self.m,self.n,self.noj)
        

        # junction2block
        self.junc2block = {}
        blocknum0 = m-1
        blocknum1 = n-1
        for i in range(blocknum0):
            for j in range(blocknum1):
                decision = [0,0,0,0]
                if i == (blocknum0-1)/2 and j == (blocknum1-1)/2:
                    decision = [1,1,1,1]
                elif i == (blocknum0-1)/2 and j < (blocknum1-1)/2:
                    decision = [1,1,1,0]
                elif i == (blocknum0-1)/2 and j > (blocknum1-1)/2:
                    decision = [1,1,0,1]
                elif i < (blocknum0-1)/2 and j == (blocknum1-1)/2:
                    decision = [1,0,1,1] 
                elif i > (blocknum0-1)/2 and j == (blocknum1-1)/2:             
                    decision = [0,1,1,1] 
                elif i < (blocknum0-1)/2 and j < (blocknum1-1)/2:
                    decision = [1,0,1,0]      
                elif i > (blocknum0-1)/2 and j < (blocknum1-1)/2:
                    decision = [0,1,1,0]    
                elif i > (blocknum0-1)/2 and j > (blocknum1-1)/2:
                    decision = [0,1,0,1]  
                elif i < (blocknum0-1)/2 and j > (blocknum1-1)/2:
                    decision = [1,0,0,1]    

                if decision[0] == 1:
                    self.junc2block[i*(n-1)+j] = [i,j]                   #down
                if decision[1] == 1:
                    self.junc2block[(i+1)*(n-1)+j] = [i,j]               #up
                if decision[2] == 1:
                    self.junc2block[m*(n-1) + j*(m-1)+i] = [i,j]         #left
                if decision[3] == 1:
                    self.junc2block[m*(n-1) + (j+1)*(m-1)+i] = [i,j]     #right
        

        # Controls
        self.map = the_map_window(self,self.size, self.m, self.n, self.juncs)

        self.panel = wx.Panel(self)


        self.btn1 = wx.Button(self.panel, -1, label = 'load')
        self.btn2 = wx.Button(self.panel, -1, label = 'play')
        self.btn2.Enabled = False
        self.btn3 = wx.Button(self.panel, -1, label = 'pause')
        self.btn3.Enabled = False
        self.btn4 = wx.Button(self.panel, -1, label = 'resume')
        self.btn4.Enabled = False       
        self.btn5 = wx.Button(self.panel, -1, label = 'next rhythm')
        self.btn5.Enabled = False
        self.btn6 = wx.Button(self.panel, -1, label = 'generate')
        self.btn6.Enabled = True

        self.rate_label = wx.StaticText(self.panel, -1, "time rate: ",size = [70,-1])
        self.blank_label = wx.StaticText(self.panel, -1, " ",size = [100,-1])
        self.rate_sc = wx.SpinCtrl(self.panel, -1, "", min = 1, max = 50, initial = self.accelarate_r, size = [30,-1])
        self.rate_slider = wx.Slider(self.panel, -1, self.accelarate_r, 1, 50, size=(100, -1),
            style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_MIN_MAX_LABELS)
        self.rate_slider.SetTickFreq(5)

        self.gauge = wx.Gauge(self, -1, 100)
        self.gauge.SetBezelFace(3)
        self.gauge.SetShadowWidth(3)

        self.fps_label = wx.StaticText(self.map, -1, "", pos = [20,20])

        # junction buttons
        img1 = wx.Image(name="mate\junc.png", type = wx.BITMAP_TYPE_PNG)
        self.junction_blocks = []
        self.junction_block_info = []
        change1 = 1-3*road_scale
        change2 = 0.5 + (1-change1)/2
        img2 = img1.Scale(int(change1*self.blocksize[0]),int(change1*self.blocksize[1]))
        self.junc_appe = wx.Bitmap(img2)
        self.junction_block_info.append(np.zeros((2,self.m-1,self.n-1)))
        for i in range(self.m-1):
            self.junction_blocks.append([])
            for j in range(self.n-1):
                b = junction_btn(self.map, -1, bitmap = self.junc_appe, pos = ((1+change2+j)*self.blocksize[0],(self.m-i-1+change2)*self.blocksize[1]), 
                    size = (change1*self.blocksize[0],change1*self.blocksize[1]), order = [i,j])
                b.SetUseFocusIndicator(False)
                b.Setnum1Data(40)
                b.Setnum2Data(5)
                self.Bind(wx.EVT_BUTTON, self.watching_junction, b)
                self.junction_blocks[i].append(b)
                self.junction_block_info[0][0][i][j] = 40
                self.junction_block_info[0][1][i][j] = 5 
                pub.subscribe(b.Change_data, "update_junction")

        # entrance buttons
        self.entrance2block = {}
        self.entr_appe = wx.Bitmap(name="mate\entrance.png", type = wx.BITMAP_TYPE_PNG)
        self.entrance_blocks = []
        self.entrance_block_info = []
        i = 0
        self.entrance_blocks.append([])
        self.entrance_block_info.append(np.zeros((2,2,max(self.m,self.n))))
        for j in range(self.m):
            if np.mod(j,2) == 0:
                b = entrance_btn(self.map, -1, bitmap = self.entr_appe, pos = (0,(self.m-0.9-j)*self.blocksize[1]), 
                    size = (self.blocksize[0],1.8*self.blocksize[1]), order = [i,j])
                self.entrance2block[j] = [i,j]
                self.entrance2block[j+1+self.m+self.n] = [i,j]
            else:
                b = entrance_btn(self.map, -1, bitmap = self.entr_appe, pos = ((self.n+1)*self.blocksize[0],(self.m+0.1-j)*self.blocksize[1]), 
                    size = (self.blocksize[0],1.8*self.blocksize[1]), order = [i,j])
                self.entrance2block[j] = [i,j]
                self.entrance2block[j-1+self.m+self.n] = [i,j]
            b.SetUseFocusIndicator(False)
            b.Setnum1Data(0)
            b.Setnum2Data(40)
            self.Bind(wx.EVT_BUTTON, self.watching_entrance, b)
            self.entrance_blocks[i].append(b)
            self.entrance_block_info[0][0][i][j] = 0
            self.entrance_block_info[0][1][i][j] = 40 
            pub.subscribe(b.Change_data, "update_entrance")
        i = 1
        self.entrance_blocks.append([])
        for j in range(self.n):    
            if np.mod(j,2) == 0:
                b = entrance_btn(self.map, -1, bitmap = self.entr_appe, pos = ((1.1+j)*self.blocksize[0],0), 
                    size = (1.8*self.blocksize[0],self.blocksize[1]), order = [i,j])
                self.entrance2block[self.m + j] = [i,j]
                self.entrance2block[j+1+2*self.m+self.n] = [i,j]
            else:
                b = entrance_btn(self.map, -1, bitmap = self.entr_appe, pos = ((0.1+j)*self.blocksize[0],(self.m+1)*self.blocksize[1]), 
                    size = (1.8*self.blocksize[0],self.blocksize[1]), order = [i,j])
                self.entrance2block[self.m + j] = [i,j]
                self.entrance2block[j-1+2*self.m+self.n] = [i,j]
            b.SetUseFocusIndicator(False)
            b.Setnum1Data(0)
            b.Setnum2Data(40)
            self.Bind(wx.EVT_BUTTON, self.watching_entrance, b)
            self.entrance_blocks[i].append(b)
            self.entrance_block_info[0][0][i][j] = 0
            self.entrance_block_info[0][1][i][j] = 40 
            pub.subscribe(b.Change_data, "update_entrance")
        

        # layout
        time_rate_box = wx.BoxSizer(wx.HORIZONTAL)
        time_rate_box.Add(self.rate_label,1, wx.EXPAND)
        time_rate_box.Add(self.rate_sc,1, wx.EXPAND)

        toolarea = wx.BoxSizer(wx.VERTICAL)
        toolarea.Add(self.btn6, 0, wx.EXPAND)
        toolarea.Add(self.btn1, 0, wx.EXPAND)
        toolarea.Add(self.btn2, 0, wx.EXPAND)
        toolarea.Add(self.btn3, 0, wx.EXPAND)
        toolarea.Add(self.btn4, 0, wx.EXPAND)
        toolarea.Add(self.btn5, 0, wx.EXPAND)
        toolarea.Add(self.blank_label, 0, wx.EXPAND)
        toolarea.Add(time_rate_box, 0, wx.EXPAND)
        toolarea.Add(self.rate_slider, 0, wx.EXPAND)
        
        self.panel.SetSizer(toolarea)   
        toolarea.Fit(self.panel)

        working_area = wx.BoxSizer(wx.VERTICAL)
        working_area.Add(self.map, 0, wx.EXPAND)
        working_area.Add(self.gauge, 1, wx.EXPAND)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.panel, 0, wx.EXPAND)
        box.Add(working_area, 0, wx.EXPAND)
        self.SetSizer(box)
        # box.Fit(self)
        print(self.GetSize())
        
        self.initStatusBar()

        # Event Handlers 
        self.Bind(wx.EVT_BUTTON, self.loading, self.btn1)
        self.Bind(wx.EVT_BUTTON, self.playing, self.btn2)
        self.Bind(wx.EVT_BUTTON, self.pausing, self.btn3)
        self.Bind(wx.EVT_BUTTON, self.resuming, self.btn4)
        self.Bind(wx.EVT_BUTTON, self.go_next_rhy, self.btn5)
        self.Bind(wx.EVT_BUTTON, self.generate, self.btn6)
        self.Bind(wx.EVT_SCROLL_CHANGED, self.Change_rate_slider, self.rate_slider)
        self.Bind(wx.EVT_SPINCTRL, self.Change_rate_sc, self.rate_sc)

        thread_mt = td.Thread(target=self.Mainthread)
        thread_mt.setDaemon(True)
        thread_mt.start()

        thread_uu = td.Thread(target=self.updating_GUI)
        thread_uu.start()
    
    def initStatusBar(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(3)
        self.statusbar.SetStatusWidths([-1, -2, -3])
        self.statusbar.SetStatusText("No data" , 0)

    def Change_rate_slider(self, event): 
        r = self.rate_slider.GetValue()
        self.rate_sc.SetValue(r)
        self.accelarate_r = r
    
    def Change_rate_sc(self, event): 
        r = self.rate_sc.GetValue()
        self.rate_slider.SetValue(r)
        self.accelarate_r = r

    #get the location of each node
    def get_locations(self,m,n,noj):
        num = 2*m + 2*n + noj + 4*m*n
        locs = []
        for i in range(m):
            if np.mod(i,2) == 0:
                locs.append([self.blocksize[0],self.size[1] - (i+1.5)*self.blocksize[1]])
            else:
                locs.append([self.size[0] - self.blocksize[0],self.size[1] - (i+1.5)*self.blocksize[1]])
        for i in range(n):
            if np.mod(i,2) == 0:
                locs.append([(i+1.5)*self.blocksize[0],self.blocksize[1]])
            else:
                locs.append([(i+1.5)*self.blocksize[0],self.size[1] - self.blocksize[1]])
        for i in range(m):
            if np.mod(i,2) == 1:
                locs.append([self.blocksize[0]/2,self.size[1] - (i+1.5)*self.blocksize[1]])
            else:
                locs.append([self.size[0] - self.blocksize[0]/2,self.size[1] - (i+1.5)*self.blocksize[1]])
        for i in range(n):
            if np.mod(i,2) == 1:
                locs.append([(i+1.5)*self.blocksize[0],self.blocksize[1]/2])
            else:
                locs.append([(i+1.5)*self.blocksize[0],self.size[1] - self.blocksize[1]/2])
        for i in range(noj):
            junc_loc = self.juncs[i]
            locs.append([(1.5+junc_loc[0])*self.blocksize[0],self.size[1] - (1.5+junc_loc[1])*self.blocksize[1]])
        
        offset0 = [(-0.25,0),(0,0.25),(0.25,0),(0,-0.25)]
        offset1 = [(-0.25,0),(0,-0.25),(0.25,0),(0,0.25)]
        offset2 = [(0.25,0),(0,0.25),(-0.25,0),(0,-0.25)]
        offset3 = [(0.25,0),(0,-0.25),(-0.25,0),(0,0.25)] 
        for i in range(4*m*n):
            turning = np.floor(i/4)
            order = np.mod(i,4)
            turn_loc = [np.floor(turning/n),np.mod(turning,n)]
            if np.mod(turn_loc[0],2) == 0 and np.mod(turn_loc[1],2) == 0:
                locs.append([(1.5+turn_loc[1]+offset0[order][0])*self.blocksize[0],self.size[1] - (1.5+turn_loc[0]+offset0[order][1])*self.blocksize[1]])
            elif np.mod(turn_loc[0],2) == 0 and np.mod(turn_loc[1],2) == 1:
                locs.append([(1.5+turn_loc[1]+offset1[order][0])*self.blocksize[0],self.size[1] - (1.5+turn_loc[0]+offset1[order][1])*self.blocksize[1]])
            elif np.mod(turn_loc[0],2) == 1 and np.mod(turn_loc[1],2) == 0:
                locs.append([(1.5+turn_loc[1]+offset2[order][0])*self.blocksize[0],self.size[1] - (1.5+turn_loc[0]+offset2[order][1])*self.blocksize[1]])
            elif np.mod(turn_loc[0],2) == 1 and np.mod(turn_loc[1],2) == 1:
                locs.append([(1.5+turn_loc[1]+offset3[order][0])*self.blocksize[0],self.size[1] - (1.5+turn_loc[0]+offset3[order][1])*self.blocksize[1]])
        return locs

    def get_simulation_res(self, q_frame):
        while True:
            temp_res = q_frame.get()
            if temp_res is None:
                break
            self.simulation_res.append(temp_res[0])
            self.junction_block_info.append(copy.copy(self.junction_block_info[-1]))
            self.entrance_block_info.append(copy.copy(self.entrance_block_info[-1]))
            for item in temp_res[1]:
                if item[2] == 0:
                    if item[1] >= 2*(self.m+self.n):
                        order = self.junc2block[item[1] - 2*self.m - 2*self.n]
                        self.junction_block_info[-1][0][order[0]][order[1]] += 0
                        self.junction_block_info[-1][1][order[0]][order[1]] += item[3]
                        self.completemission += item[3]
                        
                    elif item[1] >= (self.m+self.n):
                        order = self.entrance2block[item[1]]
                        self.entrance_block_info[-1][0][order[0]][order[1]] += 0
                        self.entrance_block_info[-1][0][order[0]][order[1]] += item[3] 
                        self.completemission += item[3]

                elif item[2] == 1:
                    if item[1] >= 2*(self.m+self.n):
                        order = self.junc2block[item[1] - 2*self.m - 2*self.n]
                        self.junction_block_info[-1][0][order[0]][order[1]] += item[3]
                        self.junction_block_info[-1][1][order[0]][order[1]] += item[3]
                        self.completemission += item[3]

                    elif item[1] >= (self.m+self.n):
                        order = self.entrance2block[item[1]]
                        self.entrance_block_info[-1][0][order[0]][order[1]] += item[3]
                        self.entrance_block_info[-1][0][order[0]][order[1]] += item[3] 
                        self.completemission += item[3]

    # load simulation result
    def loading(self, event):
        print("press btn1")
        self.simulation_res = []
        self.blockinfo_res = []

        wildcard = "Json files(*.json)|*.json"
        dlg = wx.FileDialog(None,"select a result file",os.getcwd(),"",wildcard=wildcard,style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) 
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            filepath = dlg.GetPath()
            with io.open(filepath,'r',encoding='utf-8') as json_file: 
                self.res=json.load(json_file)
                self.num_of_wave = len(self.res)

            self.btn2.Enabled = True
            wx.MessageBox('Done!')
            self.statusbar.SetStatusText("Loading success" , 0)
        dlg.Destroy()

        q_frame = mp.Queue()
        td_simulate = td.Thread(target = simulating, args = (self.time_duration, q_frame, self.res, self.rhythm, self.m, self.n, self.noj, 
            self.blocksize, self.dis_matrix, self.pre_matrix, self.locations, self.junc2block,))
        td_simulate.start()
        td_collect = td.Thread(target = self.get_simulation_res, args = (q_frame,))
        td_collect.start()
        
    # play simulation 
    def playing(self, event):
        print("press btn2")

        self.completemission = 0
        self.counting_frames = 0
        self.pausing_time = 0
        self.current_running_t = 0
        self.is_start = True
        self.reload = True
        self.t_start= time.time()
        self.pretime = self.t_start
        self.newtime = self.t_start

        self.btn3.Enabled = True
        self.btn4.Enabled = False
        self.btn5.Enabled = False
        self.statusbar.SetStatusText("Playing" , 0)
        self.statusbar.SetStatusText("Complete mission: %d" % self.completemission, 2)
    
    # pause and resume
    def pausing(self, event):
        print("press btn3")

        self.is_start = False
        self.statusbar.SetStatusText("Pausing" , 0)

        self.btn3.Enabled = False
        self.btn4.Enabled = True
        self.btn5.Enabled = True

    # resume
    def resuming(self, event):
        print("press btn4")
        self.pretime = time.time()
        self.is_start = True
        self.statusbar.SetStatusText("Playing" , 0)

        self.btn3.Enabled = True
        self.btn4.Enabled = False
        self.btn5.Enabled = False

    # go to next rhythm, able when paused
    def go_next_rhy(self, event):
        print("press btn5")

        self.is_start = True
        self.next_flag = True
        self.statusbar.SetStatusText("Next rhythm" , 0)

    def generate(self, event):
        print("press btn6")

        dlg = generate_Dialog()
        dlg.Show()

    # press at junctions
    def watching_junction(self, event):
        theid = event.GetId()
        item = self.FindWindowById(theid)
        m,n = item.get_order()
        print("press at junction (%d,%d)" % (m,n))
        infos = np.array(self.junction_block_info[m][n])
        infos = infos.transpose()
        plt.close()
        fig=plt.figure("Junction (%d,%d)" % (m,n),(10,5),frameon=False)
        ax1=plt.subplot(1,2,1)
        plt.plot(infos[0],infos[1],'g-')
        plt.ylabel("Goods")
        ax1=plt.subplot(1,2,2)
        plt.plot(infos[0],infos[2],'r-')
        plt.ylabel("AGVs")
        plt.show()
    
    # press at entrances
    def watching_entrance(self, event):
        theid = event.GetId()
        item = self.FindWindowById(theid)
        m,n = item.get_order()
        print("press at entrance (%d,%d)" % (m,n))
        infos = np.array(self.entrance_block_info[m][n])
        infos = infos.transpose()
        plt.close()
        fig=plt.figure("Entrance (%d,%d)" % (m,n),(10,5),frameon=False)
        ax1=plt.subplot(1,2,1)
        plt.plot(infos[0],infos[1],'g-')
        plt.ylabel("Goods")
        ax1=plt.subplot(1,2,2)
        plt.plot(infos[0],infos[2],'r-')
        plt.ylabel("AGVs")
        plt.show()

    # simulation player
    def Mainthread(self):
        '''仿真线程函数'''
        while True:
            if self.is_start:
                if self.reload:
                    wave  = 0
                    self.reload = False

                if not self.next_flag:
                    self.newtime = time.time()
                    self.new_period = self.accelarate_r * (self.newtime - self.pretime) # scaling simulation time
                    if self.new_period == 0:
                        continue
                    self.current_running_t = self.current_running_t + self.new_period # scaling simulation time
                    self.pretime = self.newtime
                else:
                    self.pretime = time.time()
                    self.current_running_t = self.current_running_t - np.mod(self.current_running_t,self.rhythm) + self.rhythm
                    self.is_start = False
                    self.next_flag = False
                
                self.counting_frames = np.floor(self.current_running_t / self.time_duration)
                self.counting_frames = int(self.counting_frames)
                wave = int(np.floor(self.counting *self.time_duration / self.rhythm))

                if len(self.simulation_res) <= self.counting_frames:
                    time.sleep(0.1)
                    self.pretime = time.time()
                    continue
                
                time.sleep(0.01)
            else:
                time.sleep(0.03)
    
    def updating_GUI(self):
        pretime = time.time()
        while True:
            curtime = time.time()
            if self.is_start == False or curtime - pretime < self.time_duration:
                time.sleep(0.01)
            else:
                wx.CallAfter(self.statusbar.SetStatusText, "Operating time: %d sec %d min %d hour" %(np.mod(self.current_running_t,60),
                 np.floor(np.mod(self.current_running_t,3600)/60), np.floor(self.current_running_t/3600)) , 1)
                wx.CallAfter(self.set_gauge, self.current_running_t/(self.rhythm * self.num_of_wave)*100)
                if self.new_period != 0: 
                    wx.CallAfter(self.fps_label.SetLabel, "fps %.1f" % (1/self.new_period))
                else:
                    wx.CallAfter(self.fps_label.SetLabel, "fps 999")

                wx.CallAfter(self.statusbar.SetStatusText, "Complete mission: %d" % self.completemission, 2)
                pub.sendMessage("update_junction", data = self.junction_block_info[self.counting_frames])
                pub.sendMessage("update_entrance", data = self.entrance_block_info[self.counting_frames])
                wx.CallAfter(self.map.SetpointsData, self.simulation_res[self.counting_frames])
                pretime = curtime

    '''
    def updating_infos_in_juncbtn(self,num1,num2,order,time):
        self.junction_blocks[order[0]][order[1]].Changenum1Data(num1)
        self.junction_blocks[order[0]][order[1]].Changenum2Data(num2)
        self.junction_blocks[order[0]][order[1]].Refresh()
        self.Update()
    
    def updating_infos_in_entrbtn(self,num1,num2,order,time):
        self.entrance_blocks[order[0]][order[1]].Changenum1Data(num1)
        self.entrance_blocks[order[0]][order[1]].Changenum2Data(num2)
        self.entrance_blocks[order[0]][order[1]].Refresh()
        self.Update()
    '''


    def set_gauge(self, v):
        self.gauge.SetValue(v)


if __name__ == "__main__":
    app = wx.App()
    frame = MDIFrame()
    frame.Show()
    app.MainLoop()
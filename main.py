# -*- coding: utf-8 -*-
### py2 ###
from __future__ import division
######

import simulator_frame
import wx

if __name__ == "__main__":
    app = wx.App()
    frame = simulator_frame.MDIFrame()
    frame.Show()
    app.MainLoop()
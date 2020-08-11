#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import sys
import io
import os
import struct
import time
import base64
from PyQt5.QtWidgets import QApplication,QWidget,QTabWidget
from PyQt5.QtGui import QIcon

from SimpleUpdata import SimpleUpdata
from aithinker_png import aithinker_png as logo

from TBXX_Flash_Tool import TB_Tools
from FW_Combin_Tool import FW_Tools
from FW_Market import FW_Market
from SP_Tools import SP_Tools
from Dev_Document import Dev_Document

__version__ = "V1.5.0"

class MainForm(QTabWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setWindowTitle("Anxinke TB module debugging tool " + __version__)

        if not os.path.exists("combine/") : os.makedirs("combine/")

        if not os.path.exists('combine/aithinker.png'):
            tmp = open('combine/aithinker.png', 'wb+')
            tmp.write(base64.b64decode(logo))
            tmp.close()

        self.setWindowIcon(QIcon("combine/aithinker.png"))
        self.resize(600,370)

        self.tab_TB_Tools=TB_Tools()
        self.tab_SP_Tools=SP_Tools()
        self.tab_FW_Market=FW_Market()
        self.tab_Dev_Doc=Dev_Document()
        self.tab_FW_Tools=FW_Tools()

        self.addTab(self.tab_TB_Tools, "Burn firmware")
        self.addTab(self.tab_SP_Tools, "Serial debugging")
        self.addTab(self.tab_FW_Market,"Firmware market")
        self.addTab(self.tab_Dev_Doc,  "Development materials")
        self.addTab(self.tab_FW_Tools, "Merge firmware")

        self.currentChanged['int'].connect(self.tabfun)
    
    def tabfun(self,index):
        if (index == 2):
            self.tab_FW_Market.get_fw_list()
        elif (index == 3):
            self.tab_Dev_Doc.get_doc_list()

if __name__=="__main__":
    app=QApplication(sys.argv)
    win=MainForm()
    win.show()

    su = SimpleUpdata()
    su.check_updata('https://ai-thinker.oss-cn-shenzhen.aliyuncs.com/TB_Tool/updata.json')
    sys.exit(app.exec_())
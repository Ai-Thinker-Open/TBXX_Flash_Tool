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

__version__ = "V1.3.1 dev"

class MainForm(QTabWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setWindowTitle("安信可TB模块调试工具 " + __version__)

        if not os.path.exists('aithinker.png'):
            tmp = open('aithinker.png', 'wb+')
            tmp.write(base64.b64decode(logo))
            tmp.close()

        self.setWindowIcon(QIcon("aithinker.png"))
        self.resize(500,300)

        self.tab1=TB_Tools()
        self.tab2=FW_Tools()
        self.tab3=QWidget()
        self.tab4=QWidget()

        self.addTab(self.tab1, "烧录固件")
        self.addTab(self.tab2, "合并固件")
        self.addTab(self.tab3, "串口调试")
        self.addTab(self.tab4, "固件市场")

if __name__=="__main__":
    app=QApplication(sys.argv)
    win=MainForm()
    win.show()

    su = SimpleUpdata()
    su.check_updata('https://ai-thinker.oss-cn-shenzhen.aliyuncs.com/TB_Tool/updata.json')
    sys.exit(app.exec_())
import requests
import json
import argparse
import sys
import io
import os
import struct
import time
import base64
import hashlib
from PyQt5.QtWidgets import QApplication,QWidget,QTabWidget,QTextEdit,QVBoxLayout,QLabel,QHBoxLayout,QPushButton
from PyQt5.QtCore import Qt,QThread,pyqtSignal
from PyQt5.QtGui import QIcon

from aithinker_png import aithinker_png as logo

from TBXX_Flash_Tool import TB_Tools
from FW_Combin_Tool import FW_Tools

CMD_SHOW_FORM  = 0x00
CMD_CLOSE_FORM = 0x01
CMD_UPDATA_OK  = 0x02

new_file_url = ''

class UpdataThread(QThread):
    formSignal = pyqtSignal(int)
    textSignal = pyqtSignal(str)
    def __init__(self,action, args):
        super(UpdataThread, self).__init__()

        self.action = action
        self.args = args
        
    def run(self):
        global new_file_url
        if self.action == "check":#检查是否需要更新
            r = requests.get(self.args)

            data = r.json()

            if(self.get_file_md5(sys.argv[0]).upper() != data["MD5"].upper()): #对比本地文件与线上文件的MD5
                desc = "版本号:" + "\r\n更新内容:\r\n" + data["desc"] + "\r\nMD5:" + self.get_file_md5(sys.argv[0])

                new_file_url = data["url"]
                self.textSignal.emit(desc)
                self.formSignal.emit(CMD_SHOW_FORM)
            else:
                self.formSignal.emit(CMD_CLOSE_FORM)

        elif self.action == "updata":#下载新文件，执行更新
            r = requests.get(new_file_url)
            with open("tmp.exe", "wb") as new_file:
                new_file.write(r.content)
            self.formSignal.emit(CMD_UPDATA_OK)


    def get_file_md5(self, file_name):
        with open(file_name, 'rb') as fp:
            data = fp.read()
        return hashlib.md5(data).hexdigest()


class SimpleUpdata(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle("发现新版本")

        if not os.path.exists('aithinker.png'):
            tmp = open('aithinker.png', 'wb+')
            tmp.write(base64.b64decode(logo))
            tmp.close()

        self.setWindowIcon(QIcon("aithinker.png"))
        self.resize(300,80)

        self.lable=QLabel()

        line_btn=QHBoxLayout()
        btn_updata =QPushButton("立即更新")
        btn_ignore =QPushButton("忽略该版本")
        btn_next   =QPushButton("下次提醒我")

        btn_updata.clicked.connect(self.updata)
        btn_ignore.clicked.connect(self.ignore)
        btn_next.clicked.connect(self.next_time)

        line_btn.addWidget(btn_updata)
        line_btn.addWidget(btn_ignore)
        line_btn.addWidget(btn_next)

        self.layout=QVBoxLayout()
        self.layout.addWidget(self.lable)
        self.layout.addLayout(line_btn)

        self.setLayout(self.layout)

    def check_updata(self,url):
        self.mThread = UpdataThread(action="check", args=url)
        self.mThread.formSignal.connect(self.show_form)
        self.mThread.textSignal.connect(self.set_desc_text)
        self.mThread.start()

    def show_form(self,cmd):#显示或关闭检查更新窗口
        if(cmd == CMD_SHOW_FORM):
            self.show()
        elif(cmd ==  CMD_CLOSE_FORM):
            self.close()
        elif(cmd == CMD_UPDATA_OK):#新文件下载成功
            with open("tmp.bat", "w+") as new_file:
                new_file.write('del Main.exe\r\n')
                new_file.write('mv tmp.exe Main.exe\r\n')
                new_file.write('Main.exe\r\n')
                new_file.write('exit\r\n')
            os.system('start /b tmp.bat >> tmp.txt') #执行外部进程删除旧文件，将下载的文件重命名为原文件
            sys.exit()
    
    def set_desc_text(self,txt):#设置更新说明文字
        self.lable.setText(txt)

    def updata(self):#执行更新
        self.mThread = UpdataThread(action="updata", args=0)
        self.mThread.formSignal.connect(self.show_form)
        self.mThread.textSignal.connect(self.set_desc_text)
        self.mThread.start()

    def ignore(self):#忽略该版本
        self.close()

    def next_time(self):#下次提醒
        self.close()
import requests
import json
import argparse
import sys
import io
import os
import struct
import time
import base64
from contextlib import closing
import hashlib
from PyQt5.QtWidgets import QApplication,QWidget,QTabWidget,QTextEdit,QVBoxLayout,QLabel,QHBoxLayout,QPushButton,QProgressBar,QMessageBox
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
    presSignal = pyqtSignal(int)
    def __init__(self,action, args):
        super(UpdataThread, self).__init__()

        self.action = action
        self.args = args
        
    def run(self):
        global new_file_url
        if self.action == "check":#检查是否需要更新
            try:
                r = requests.get(self.args, timeout=5)
            except Exception as e:
                self.formSignal.emit(CMD_CLOSE_FORM) 

            if r.status_code == 200:
                data = r.json()

                if(self.get_file_md5(sys.argv[0]).upper() != data["MD5"].upper()): #对比本地文件与线上文件的MD5
                    desc = data["desc"]

                    new_file_url = data["url"]
                    self.textSignal.emit(desc)
                    self.formSignal.emit(CMD_SHOW_FORM)
                else:
                    self.formSignal.emit(CMD_CLOSE_FORM)

        elif self.action == "updata":#下载新文件，执行更新

            headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}
            with closing(requests.get(new_file_url, headers=headers,stream=True)) as response:
                chunkSize = 1024
                contentSize = int(response.headers['content-length'])
                dateCount = 0
                with open("combine/tmp.exe","wb") as file:
                    for data in response.iter_content(chunk_size=chunkSize):
                        file.write(data)
                        dateCount = dateCount + len(data)
                        nowJd = (dateCount / contentSize) * 100

                        self.presSignal.emit(nowJd)

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

        self.pbar = QProgressBar(self)

        self.pbar.setVisible(False)

        self.layout=QVBoxLayout()
        self.layout.addWidget(self.lable)
        self.layout.addWidget(self.pbar)
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

            reply = QMessageBox.information(self, '升级成功', '请重新打开软件！！！')

            with open("combine/tmp.bat", "w+") as new_file:
                new_file.write('del ' + sys.argv[0] + '\r\n')
                new_file.write('mv combine\\tmp.exe ' + sys.argv[0] + '\r\n')
                new_file.write('exit\r\n')
            os.system('start /b combine\\tmp.bat >> combine\\tmp.txt') #执行外部进程删除旧文件，将下载的文件重命名为原文件
            sys.exit()
    
    def set_desc_text(self,txt):#设置更新说明文字
        self.lable.setText(txt)
    
    def pressBar_refresh(self, a):#刷新进度条
        self.pbar.setValue(a)

    def updata(self):#执行更新
        self.pbar.setVisible(True)
        self.mThread = UpdataThread(action="updata", args=0)
        self.mThread.formSignal.connect(self.show_form)
        self.mThread.textSignal.connect(self.set_desc_text)
        self.mThread.presSignal.connect(self.pressBar_refresh)
        self.mThread.start()

    def ignore(self):#忽略该版本
        self.close()

    def next_time(self):#下次提醒
        self.close()
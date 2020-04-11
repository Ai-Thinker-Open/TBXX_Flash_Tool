#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import sys
import io
import os
import struct
import time
import zlib
import hashlib
from PyQt5.QtWidgets import QPushButton,QLineEdit,QWidget,QTextEdit,QVBoxLayout,QHBoxLayout,QFileDialog,QLabel

class FW_Tools(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.layout=QVBoxLayout()

        self.tbox_log=QTextEdit()

        line_1=QHBoxLayout()

        self.tbox_boot_file = QLineEdit()
        label_boot=QLabel("Boot:")
        btn_open_boot_file =QPushButton("···")

        btn_open_boot_file.clicked.connect(lambda:self.open_file_fn('boot'))

        line_1.addWidget(label_boot)
        line_1.addWidget(self.tbox_boot_file)
        line_1.addWidget(btn_open_boot_file)

        line_1.setContentsMargins(0, 0, 0, 0)

        line_2=QHBoxLayout()
        
        self.tbox_app_file = QLineEdit()
        label_app=QLabel("App: ")
        btn_open_app_file =QPushButton("···")

        btn_open_app_file.clicked.connect(lambda:self.open_file_fn('app'))

        line_2.addWidget(label_app)
        line_2.addWidget(self.tbox_app_file)
        line_2.addWidget(btn_open_app_file)

        line_2.setContentsMargins(0, 0, 0, 0)

        line_3=QHBoxLayout()

        btn_burn_triad=QPushButton("合并固件")
        btn_burn_triad.clicked.connect(self.combin_fn)
        line_3.addWidget(btn_burn_triad)

        line_3.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(self.tbox_log)
        self.layout.addLayout(line_1)
        self.layout.addLayout(line_2)
        self.layout.addLayout(line_3)

        self.setLayout(self.layout)

    def open_file_fn(self,action): #选择固件
        directory = QFileDialog.getOpenFileName(self, "选择要烧录的固件",'',"固件 (*.bin)") 
        
        if len(str(directory[0])) > 5 :
            if action == "boot":
                self.tbox_boot_file.setText(str(directory[0]))
                self.tbox_boot_file.setStyleSheet("background-color:LightGreen;")
            else:
                self.tbox_app_file.setText(str(directory[0]))
                self.tbox_app_file.setStyleSheet("background-color:LightGreen;")
    
    def combin_fn(self):#合并固件

        if not os.path.exists(self.tbox_boot_file.text()) or os.path.getsize(self.tbox_boot_file.text()) > 0x4000:
            self.tbox_boot_file.setStyleSheet("background-color:red;")
            self.log_string("Boot固件不存在或大小错误")
            return

        if not os.path.exists(self.tbox_app_file.text()) or os.path.getsize(self.tbox_app_file.text()) > 0x2C000:
            self.tbox_app_file.setStyleSheet("background-color:red;")
            self.log_string("APP固件不存在或大小错误")
            return

        if not os.path.exists("combine/") : os.makedirs("combine/")

        boot = open(self.tbox_boot_file.text(), "rb")
        app = open(self.tbox_app_file.text(), "rb")
        boot_app_file_name= self.tbox_app_file.text().replace('.bin','_with_boot.bin')
        boot_app = open(boot_app_file_name, "w+b")

        boot_app.write(boot.read()) # 将Boot固件放在合并后固件的前16K
        boot.close()

        boot_app.seek(0x4000,0)
        app.seek(0x4000,0)

        boot_app.write(app.read()) # APP 固件的 16K 之后的部分 位置不变

        boot_app.seek(0x2c000,0)
        app.seek(0x00000,0)

        boot_app.write(app.read(0x4000)) # 将APP固件的前16K放在合并后固件的0x2C000的位置
        app.close()

        boot_app.seek(0, 0)
        file_content = boot_app.read()
        crc32_result = zlib.crc32(file_content) & 0xffffffff # 计算整个文件的CRC

        boot_app.seek(176 * 1024 - 4, 0)
        boot_app.write(struct.pack('>I', crc32_result)) #RAM Code 前4个字节也放置CRC校验

        boot_app.seek(0, 2)
        boot_app.write(struct.pack('>I', crc32_result)) #文件的最末尾处，放置CRC校验

        boot_app.seek(0, 0)
        file_content = boot_app.read()
        md5_result = hashlib.md5(file_content).hexdigest()

        boot_app.close()

        self.log_string("Combine OK!\r\nFirmware CRC32: " + hex(crc32_result) +"\r\nFirmware MD5: " + md5_result + "\r\n合并好的固件为:" + boot_app_file_name)
        
    def log_string(self, s): #Log窗口日志输出
        self.tbox_log.append(s)
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import sys
import io
import os
import struct
import time
import base64
from PyQt5.QtWidgets import QPushButton,QApplication,QLineEdit,QWidget,QTextEdit,QVBoxLayout,QHBoxLayout,QComboBox,QFileDialog,QProgressBar
from PyQt5.QtCore import Qt,QThread,pyqtSignal
from PyQt5.QtGui import QIcon
from Telink_Tools import get_port_list,tl_open_port,connect_chip,change_baud,telink_flash_write,telink_flash_erase


from aithinker_png import aithinker_png as logo

__version__ = "V1.2"

class TelinkThread(QThread):
    pressbarSignal = pyqtSignal(int)
    textSignal = pyqtSignal(str)
    def __init__(self, _port_name, action, args):
        super(TelinkThread, self).__init__()

        self._port_name = _port_name
        self.action = action
        self.args = args
        
    def run(self):

        try:
            _port = tl_open_port(self._port_name)
        except Exception:
            self.textSignal.emit("串口 " + self._port_name + " 打开失败，请检查串口是否被占用！！！")
            self.pressbarSignal.emit(200)
            return

        self.pressbarSignal.emit(1000)
        self.textSignal.emit("打开串口成功！！！")

        if self.action == "reset":#复位模组，进入运行模式
            _port.setRTS(True)
            _port.setDTR(False)

            time.sleep(0.1)

            _port.setRTS(False)

            self.textSignal.emit("模组已复位！！！")
            self.pressbarSignal.emit(100)
            _port.close()
            return

        if not connect_chip(_port): #连接芯片，进入烧录模式
            self.textSignal.emit("连接芯片失败！！！")
            self.pressbarSignal.emit(200)
            _port.close()
            return
        self.textSignal.emit("连接芯片成功！")
        

        if self.action == "burn": #烧录固件

            self.textSignal.emit("尝试提高波特率...")

            if change_baud(_port):
                self.textSignal.emit("提高波特率成功！！！")

            self.textSignal.emit("擦除固件 ... ... ")

            if not telink_flash_erase(_port, 0x4000, 44):
                self.textSignal.emit("擦除固件失败！！！")
                self.pressbarSignal.emit(200)
                _port.close()
                return
            self.textSignal.emit("擦除固件成功！")

            self.textSignal.emit("烧录固件 :"  + self.args.file_name)

            fo = open(self.args.file_name, "rb")
            firmware_addr = 0
            firmware_size = os.path.getsize(self.args.file_name)
            percent=0

            if(firmware_size >= 192 * 1024): # 固件大于192KB，说明是合并好的固件，要跳过Boot
                fo.seek(16 * 1024, 0)
                firmware_addr = 16 * 1024

            while True:
                data = fo.read(256)
                if len(data) < 1: break

                if not telink_flash_write(_port, firmware_addr, data):
                    self.textSignal.emit("烧录固件失败！！！")
                    self.pressbarSignal.emit(200)
                    break

                firmware_addr += len(data)

                percent = (int)(firmware_addr *100 / firmware_size)
                self.pressbarSignal.emit(percent)  # 跟新进度条

            if percent == 100 : self.textSignal.emit("烧录固件完成！")
            fo.close()

        elif self.action == "burn_triad": #烧录三元组

            self.textSignal.emit("擦除三元组 ... ... ")

            if not telink_flash_erase(_port, 0x78000, 1):
                self.textSignal.emit("擦除三元组失败！！！")
                self.pressbarSignal.emit(200)
                _port.close()
                return
            self.textSignal.emit("擦除三元组成功！")

            self.textSignal.emit("烧录三元组 :" + str(self.args.triad))

            if telink_flash_write(_port, 0x78000, self.args.triad):
                self.textSignal.emit("烧录三元组成功！")
                self.pressbarSignal.emit(100)
            else:
                self.textSignal.emit("烧录三元组失败！！！")
                self.pressbarSignal.emit(200)

        elif self.action == "erase":#擦除Flash

            self.textSignal.emit("擦除Flash: 从 " + hex(self.args.addr) + " 擦除 " + str(self.args.len_t) + " 扇区... ... ")

            if telink_flash_erase(_port, self.args.addr, self.args.len_t):
                self.textSignal.emit("擦除成功！")
                self.pressbarSignal.emit(100)
            else:
                self.textSignal.emit("擦除失败！！！")
                self.pressbarSignal.emit(200)

        _port.close()

class TB_Tools(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setWindowTitle("安信可TB模块烧录工具 " + __version__)

        # if not os.path.exists('aithinker.png'):
        #     tmp = open('aithinker.png', 'wb+')
        #     tmp.write(base64.b64decode(logo))
        #     tmp.close()

        self.setWindowIcon(QIcon("aithinker.png"))
        #self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(500,300)
        self.layout=QVBoxLayout()

        self.tbox_log=QTextEdit()


        line_1=QHBoxLayout()

        self.serial_cb=QComboBox()

        btn_refresh_p=QPushButton("刷新串口")
        btn_erase_fw =QPushButton("擦除固件")
        btn_erase_key=QPushButton("擦除Mesh Key")
        btn_erase_all=QPushButton("整片擦除")
        btn_rst_chip =QPushButton("复位芯片")
        btn_clean_scn=QPushButton("清空窗口")

        btn_refresh_p.clicked.connect(self.refresh_p_fn)
        btn_erase_fw.clicked.connect (lambda:self.erase_fn("fw"))
        btn_erase_key.clicked.connect(lambda:self.erase_fn("key"))
        btn_erase_all.clicked.connect(lambda:self.erase_fn("all"))

        btn_rst_chip.clicked.connect(self.rst_chip_fn)
        btn_clean_scn.clicked.connect(self.clean_screen_fn)

        line_1.addWidget(self.serial_cb)
        line_1.addWidget(btn_refresh_p)
        line_1.addWidget(btn_erase_fw)
        line_1.addWidget(btn_erase_key)
        line_1.addWidget(btn_erase_all)
        line_1.addWidget(btn_rst_chip)
        line_1.addWidget(btn_clean_scn)

        line_1.setContentsMargins(0, 0, 0, 0)

        line_2=QHBoxLayout()
        
        self.tbox_file = QLineEdit()
        btn_open_file =QPushButton("···")
        btn_burn=QPushButton("烧录固件")

        btn_open_file.clicked.connect(self.open_file_fn)
        btn_burn.clicked.connect(self.burn_fn)

        line_2.addWidget(self.tbox_file)
        line_2.addWidget(btn_open_file)
        line_2.addWidget(btn_burn)

        line_2.setContentsMargins(0, 0, 0, 0)

        line_3=QHBoxLayout()

        self.tbox_ali_pID = QLineEdit()
        self.tbox_ali_Mac = QLineEdit()
        self.tbox_ali_Sct = QLineEdit()

        self.tbox_ali_pID.setPlaceholderText("Product ID")
        self.tbox_ali_Mac.setPlaceholderText("MAC地址")
        self.tbox_ali_Sct.setPlaceholderText("Device Secret")


        btn_burn_triad=QPushButton("烧录三元组")
        btn_burn_triad.clicked.connect(self.burn_triad_fn)

        line_3.addWidget(self.tbox_ali_pID)
        line_3.addWidget(self.tbox_ali_Sct)
        line_3.addWidget(self.tbox_ali_Mac)
        line_3.addWidget(btn_burn_triad)

        line_3.setContentsMargins(0, 0, 0, 0)

        line_3.setStretch(0, 2)
        line_3.setStretch(1, 5)
        line_3.setStretch(2, 2)
        line_3.setStretch(3, 1)


        self.layout.addWidget(self.tbox_log)
        self.layout.addLayout(line_1)
        self.layout.addLayout(line_2)
        self.layout.addLayout(line_3)

        self.pbar = QProgressBar(self)
        self.layout.addWidget(self.pbar)

        self.setLayout(self.layout)
        self.refresh_p_fn()


    def refresh_p_fn(self): #刷新串口号
        self.serial_cb.clear()
        plist = get_port_list()
        for i in range(0, len(plist)):
            plist_0 = list(plist[i])
            self.serial_cb.addItem(str(plist_0[0]))

    def clean_screen_fn(self):
        self.tbox_log.clear()
        self.tbox_log.setStyleSheet("background-color:white;")

    def erase_fn(self, action):#擦除Flash
        if not len(self.serial_cb.currentText()) > 0 :
            self.log_string("请选择串口号！！！")
            return

        args = argparse.Namespace()

        if action == "fw":
            args.addr = 0x4000
            args.len_t = 44

        elif action == "key":
            args.addr = 0x30000
            args.len_t = 16

        elif action == "all":
            args.addr = 0x4000
            args.len_t = 124
        
        self.mThread = TelinkThread(_port_name=self.serial_cb.currentText(), action="erase", args=args)

        self.mThread.pressbarSignal.connect(self.pressBar_refresh)
        self.mThread.textSignal.connect(self.log_string)
        self.mThread.start()

    def rst_chip_fn(self):#复位新片
        if not len(self.serial_cb.currentText()) > 0 :
            self.log_string("请选择串口号！！！")
            return

        args = argparse.Namespace()
        
        self.mThread = TelinkThread(_port_name=self.serial_cb.currentText(), action="reset", args=args)

        self.mThread.pressbarSignal.connect(self.pressBar_refresh)
        self.mThread.textSignal.connect(self.log_string)
        self.mThread.start()

    def open_file_fn(self): #选择固件
        directory = QFileDialog.getOpenFileName(self, "选择要烧录的固件",'',"固件 (*.bin)") 
        
        if len(str(directory[0])) > 5 :
            self.tbox_file.setText(str(directory[0]))
            self.tbox_file.setStyleSheet("background-color:LightGreen;")

    def burn_fn(self):#烧录固件
        if not len(self.tbox_file.text()) > 5 :
            self.log_string("请选择要烧录的固件！！！")
            self.tbox_file.setStyleSheet("background-color:red;")
            return

        if not len(self.serial_cb.currentText()) > 0 :
            self.log_string("请选择串口号！！！")
            return

        args = argparse.Namespace()
        args.file_name = self.tbox_file.text()
        
        self.mThread = TelinkThread(_port_name=self.serial_cb.currentText(), action="burn", args=args)

        self.mThread.pressbarSignal.connect(self.pressBar_refresh)
        self.mThread.textSignal.connect(self.log_string)
        self.mThread.start()
    
    def burn_triad_fn(self):#烧录三元组
        try:
            data = struct.pack('<I', int(self.tbox_ali_pID.text())) + bytearray.fromhex(self.tbox_ali_Mac.text()) + bytearray.fromhex(self.tbox_ali_Sct.text())
        except Exception:
            self.log_string("三元组格式错误！！！")
            return

        if(len(data) != 26):
            self.log_string("三元组长度不对！！！")
            return

        if not len(self.serial_cb.currentText()) > 0 :
            self.log_string("请选择串口号！！！")
            return

        args = argparse.Namespace()
        args.triad = data
        
        self.mThread = TelinkThread(_port_name=self.serial_cb.currentText(), action="burn_triad", args=args)

        self.mThread.pressbarSignal.connect(self.pressBar_refresh)
        self.mThread.textSignal.connect(self.log_string)
        self.mThread.start()

    def log_string(self, s): #Log窗口日志输出
        self.tbox_log.append(s)

    def pressBar_refresh(self, a):#刷新进度条及Log串口颜色
        if a < 101 :
            self.pbar.setValue(a)

        if(a == 100):
            self.tbox_log.setStyleSheet("background-color:LawnGreen;")

        if(a == 200):
            self.tbox_log.setStyleSheet("background-color:red;")

        if(a == 1000):
            self.tbox_log.setStyleSheet("background-color:white;")
            self.pbar.setValue(0)


if __name__=="__main__":
    app=QApplication(sys.argv)
    win=TB_Tools()
    win.show()
    sys.exit(app.exec_())
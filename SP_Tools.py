#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import sys
import io
import os
import struct
import time
import base64
from PyQt5.QtWidgets import QPushButton,QApplication,QLineEdit,QWidget,QTextEdit,QVBoxLayout,QHBoxLayout,QComboBox,QFileDialog,QProgressBar,QGridLayout,QCheckBox
from PyQt5.QtCore import Qt,QThread,pyqtSignal
from PyQt5.QtGui import QIcon,QFont,QTextCursor
from Telink_Tools import get_port_list,tl_open_port,connect_chip,telink_flash_write,uart_read


class SP_Thread(QThread):
    stateSignal = pyqtSignal(int)
    textSignal = pyqtSignal(str)
    def __init__(self, _port_name, baudRate):
        super(SP_Thread, self).__init__()

        self._port_name = _port_name
        self._baudRate = baudRate
        self._stop = False

    def my_stop(self):
        self._stop = True

    def send(self, data):
        if (self._port != None):
            self._port.write(data)
        else:
            self.textSignal.emit("请先打开串口！")
        
    def run(self):

        try:
            self._port = tl_open_port(self._port_name)
            self._port.baudrate = int(self._baudRate)
        except Exception:
            self.textSignal.emit("串口 " + self._port_name + " 打开失败，请检查串口是否被占用！！！")
            self.stateSignal.emit(1)
            return

        self.stateSignal.emit(0)
        self.textSignal.emit("打开串口成功！！！")

        self._port.setRTS(False)
        self._port.setDTR(False)

        while(True):
            if self._stop :
                break

            result = uart_read(self._port)
            if(len(result) > 1): 
                self.textSignal.emit(result)
            time.sleep(0.1)

        self._port.close()
        self._port = None

        self.stateSignal.emit(1)

class SP_Tools(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.mThread = None

        self.layout=QVBoxLayout()

        # 最上层的文本框

        self.tbox_log=QTextEdit()
        self.tbox_log.setFontPointSize(10)
        # 按钮及下拉框
        line_1=QHBoxLayout()

        self.serial_cb=QComboBox()

        self.baudRate_cb=QComboBox()
        self.baudRate_cb.addItem("9600")
        self.baudRate_cb.addItem("115200")
        self.baudRate_cb.addItem("500000")
        self.baudRate_cb.addItem("921600")

        btn_refresh_p=QPushButton("刷新串口")
        btn_recv_cnt=QPushButton("收")
        btn_send_cnt=QPushButton("发")
        btn_clean_scn =QPushButton("清除窗口")
        self.btn_Open=QPushButton("打开串口")

        btn_refresh_p.clicked.connect(self.refresh_p_fn)
        btn_clean_scn.clicked.connect(self.clean_screen_fn)
        self.btn_Open.clicked.connect(self.OpenSerial)


        line_1.addWidget(self.serial_cb)
        line_1.addWidget(btn_refresh_p)
        line_1.addWidget(self.baudRate_cb)
        line_1.addWidget(self.btn_Open)
        line_1.addWidget(btn_recv_cnt)
        line_1.addWidget(btn_send_cnt)
        line_1.addWidget(btn_clean_scn)

        line_1.setContentsMargins(0, 0, 0, 0)

        # 发送文本框及发送按钮
        line_2=QHBoxLayout()

        self.cbox_sendData=QComboBox()
        self.cbox_sendData.setEditable(True)

        self.checkBox_Hex = QCheckBox("HEX发送")
        self.checkBox_Hex.setEnabled(False)

        self.checkBox_CF = QCheckBox("加回车换行")
        self.checkBox_CF.setChecked(True)

        btn_Send=QPushButton("发送数据")

        btn_Send.clicked.connect(lambda:self.send_btn_fn())

        line_2.addWidget(self.cbox_sendData)
        line_2.addWidget(self.checkBox_Hex)
        line_2.addWidget(self.checkBox_CF)
        line_2.addWidget(btn_Send)

        line_2.setStretch(0, 42)
        line_2.setStretch(1, 10)
        line_2.setStretch(2, 10)
        line_2.setStretch(3, 10)

        # 预定义的AT指令按键矩阵
        line_3=QGridLayout()

        names = ['AT', 'AT+GMR', 'AT+RST', 'AT+SLEEP','AT+RESTORE', 'AT+SCAN', 'AT+DISCONNECT',
                'AT+NAME?', 'AT+BAUD?', 'AT+MAC?', 'AT+ADDR?','AT+MODE?','AT+STATE?','AT+MESHNAME?']

        positions = [(i, j) for i in range(2) for j in range(7)]

        for name, position in zip(names, positions):

            if name == ' ':
                continue
            button = QPushButton(name)
            button.clicked.connect(lambda:self.grid_btn_fn())
            line_3.addWidget(button, *position)

        self.layout.addWidget(self.tbox_log)
        self.layout.addLayout(line_1)
        self.layout.addLayout(line_2)
        self.layout.addLayout(line_3)

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

    def log_string(self, s): #Log窗口日志输出
        self.tbox_log.append(s)
        cursor =  self.tbox_log.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.tbox_log.setTextCursor(cursor)

    def set_sp_state(self, state): # 设置串口打开关闭状态
        if(state == 0): #串口已打开
            self.btn_Open.setText("关闭串口")
        elif(state == 1): #串口已关闭
            self.btn_Open.setText("打开串口")

    def OpenSerial(self):
        if(self.btn_Open.text() == '打开串口'):   
            self.mThread = SP_Thread(_port_name=self.serial_cb.currentText(), baudRate=self.baudRate_cb.currentText())
            self.mThread.textSignal.connect(self.log_string)
            self.mThread.stateSignal.connect(self.set_sp_state)
            self.mThread.start()
        else:
            self.mThread.my_stop()

    def grid_btn_fn(self):
        if self.mThread != None:
            sender = self.sender()
            self.mThread.send((sender.text() + '\r\n').encode('utf-8'))
        else:
            self.log_string("请先打开串口！")


    def send_btn_fn(self):
        if self.mThread != None:
            if self.checkBox_CF.isChecked():
                self.mThread.send((self.cbox_sendData.currentText() + '\r\n').encode('utf-8'))
            else:
                self.mThread.send((self.cbox_sendData.currentText()).encode('utf-8'))
        else:
            self.log_string("请先打开串口！")
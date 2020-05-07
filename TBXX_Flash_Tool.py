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
            self.textSignal.emit("Serial port " + self._port_name + " Open failed, please check whether the serial port is occupied!")
            self.pressbarSignal.emit(200)
            return

        self.pressbarSignal.emit(1000)
        self.textSignal.emit("Successfully opened the serial port!")

        if self.action == "reset":#Reset the module and enter the operating mode
            _port.setRTS(True)
            _port.setDTR(False)

            time.sleep(0.1)

            _port.setRTS(False)

            self.textSignal.emit("Module has been reset!")
            self.pressbarSignal.emit(100)
            _port.close()
            return

        if not connect_chip(_port): #Connect the chip and enter the burning mode
            self.textSignal.emit("Failed to connect the chip!")
            self.pressbarSignal.emit(200)
            _port.close()
            return
        self.textSignal.emit("Connect the chip successfully!")
        

        if self.action == "burn": #Burn firmware

            self.textSignal.emit("Try to increase the baud rate ...")

            if change_baud(_port):
                self.textSignal.emit("Success in increasing baud rate! ! !")

            self.textSignal.emit("Erase the firmware ...")

            if not telink_flash_erase(_port, 0x4000, 44):
                self.textSignal.emit("Failed to erase firmware! ! !")
                self.pressbarSignal.emit(200)
                _port.close()
                return
            self.textSignal.emit("Successfully erased the firmware!")

            self.textSignal.emit("Burn firmware :"  + self.args.file_name)

            fo = open(self.args.file_name, "rb")
            firmware_addr = 0
            firmware_size = os.path.getsize(self.args.file_name)
            percent=0

            if(firmware_size >= 192 * 1024): # The firmware is greater than 192KB, indicating that it is a merged firmware, you must skip Boot
                fo.seek(16 * 1024, 0)
                firmware_addr = 16 * 1024

            while True:
                data = fo.read(256)
                if len(data) < 1: break

                if not telink_flash_write(_port, firmware_addr, data):
                    self.textSignal.emit("Failed to burn firmware! ! !")
                    self.pressbarSignal.emit(200)
                    break

                firmware_addr += len(data)

                percent = (int)(firmware_addr *100 / firmware_size)
                self.pressbarSignal.emit(percent)  # Follow the new progress bar

            if percent == 100 : self.textSignal.emit("The firmware is burned!")
            fo.close()

        elif self.action == "burn_triad": #Burn triplet  ProductID,MAC,Secert

            self.textSignal.emit("Erase triplet ...")

            if not telink_flash_erase(_port, 0x78000, 1):
                self.textSignal.emit("Failed to erase triplet! ! !")
                self.pressbarSignal.emit(200)
                _port.close()
                return
            self.textSignal.emit("Successfully erased the triplet!")

            self.textSignal.emit("Burn triplet :" + str(self.args.triad))

            if telink_flash_write(_port, 0x78000, self.args.triad):
                self.textSignal.emit("Successfully burned the triplet！")
                self.pressbarSignal.emit(100)
            else:
                self.textSignal.emit("Failed to burn the triplet! ! !")
                self.pressbarSignal.emit(200)

        elif self.action == "erase":#Erase Flash

            self.textSignal.emit("Erase Flash: From " + hex(self.args.addr) + " Erase " + str(self.args.len_t) + " Sector ... ... ")

            if telink_flash_erase(_port, self.args.addr, self.args.len_t):
                self.textSignal.emit("Successfully erased!")
                self.pressbarSignal.emit(100)
            else:
                self.textSignal.emit("Erase failed! ! !")
                self.pressbarSignal.emit(200)

        _port.close()

class TB_Tools(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setWindowTitle("Anxinke TB module burning tool " + __version__)

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

        btn_refresh_p=QPushButton("Refresh the serial port")
        btn_erase_fw =QPushButton("Erase firmware")
        btn_erase_key=QPushButton("Erase Mesh Key")
        btn_erase_all=QPushButton("Chip erase")
        btn_rst_chip =QPushButton("Reset chip")
        btn_clean_scn=QPushButton("Clear window")

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
        btn_burn=QPushButton("Burn firmware")

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
        self.tbox_ali_Mac.setPlaceholderText("MAC address")
        self.tbox_ali_Sct.setPlaceholderText("Device Secret")


        btn_burn_triad=QPushButton("Burn triplet")
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


    def refresh_p_fn(self): #Refresh the serial number
        self.serial_cb.clear()
        plist = get_port_list()
        for i in range(0, len(plist)):
            plist_0 = list(plist[i])
            self.serial_cb.addItem(str(plist_0[0]))

    def clean_screen_fn(self):
        self.tbox_log.clear()
        self.tbox_log.setStyleSheet("background-color:white;")

    def erase_fn(self, action):#Erase Flash
        if not len(self.serial_cb.currentText()) > 0 :
            self.log_string("Please select the serial port number!")
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

    def rst_chip_fn(self):#Reset new movie
        if not len(self.serial_cb.currentText()) > 0 :
            self.log_string("Please select the serial port number!")
            return

        args = argparse.Namespace()
        
        self.mThread = TelinkThread(_port_name=self.serial_cb.currentText(), action="reset", args=args)

        self.mThread.pressbarSignal.connect(self.pressBar_refresh)
        self.mThread.textSignal.connect(self.log_string)
        self.mThread.start()

    def open_file_fn(self): #Select firmware
        directory = QFileDialog.getOpenFileName(self, "Choose the firmware to burn",'',"firmware (*.bin)") 
        
        if len(str(directory[0])) > 5 :
            self.tbox_file.setText(str(directory[0]))
            self.tbox_file.setStyleSheet("background-color:LightGreen;")

    def burn_fn(self):#Burn firmware
        if not len(self.tbox_file.text()) > 5 :
            self.log_string("Please select the firmware to burn.")
            self.tbox_file.setStyleSheet("background-color:red;")
            return

        if not len(self.serial_cb.currentText()) > 0 :
            self.log_string("Please select a serial number! ! !")
            return

        args = argparse.Namespace()
        args.file_name = self.tbox_file.text()
        
        self.mThread = TelinkThread(_port_name=self.serial_cb.currentText(), action="burn", args=args)

        self.mThread.pressbarSignal.connect(self.pressBar_refresh)
        self.mThread.textSignal.connect(self.log_string)
        self.mThread.start()
    
    def burn_triad_fn(self):#Burn triplet
        try:
            data = struct.pack('<I', int(self.tbox_ali_pID.text())) + bytearray.fromhex(self.tbox_ali_Mac.text()) + bytearray.fromhex(self.tbox_ali_Sct.text())
        except Exception:
            self.log_string("Incorrect triplet format! ! !")
            return

        if(len(data) != 26):
            self.log_string("The length of the triple is wrong! ! !")
            return

        if not len(self.serial_cb.currentText()) > 0 :
            self.log_string("Please select a serial number! ! !")
            return

        args = argparse.Namespace()
        args.triad = data
        
        self.mThread = TelinkThread(_port_name=self.serial_cb.currentText(), action="burn_triad", args=args)

        self.mThread.pressbarSignal.connect(self.pressBar_refresh)
        self.mThread.textSignal.connect(self.log_string)
        self.mThread.start()

    def log_string(self, s): #LogWindow log output
        self.tbox_log.append(s)

    def pressBar_refresh(self, a):#Refresh progress bar and Log serial port color
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
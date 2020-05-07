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
import requests
from contextlib import closing
from lxml import etree
import re
import markdown2
from mdx_math import MathExtension
from PyQt5.QtWidgets import QPushButton,QLineEdit,QWidget,QTextEdit,QVBoxLayout,QHBoxLayout,QFileDialog,QLabel
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem,QAbstractItemView,QFrame,QHeaderView,QMessageBox
from PyQt5.QtCore import Qt,QThread,pyqtSignal
from PyQt5.QtGui import QIcon,QPalette,QColor,QFont

CMD_SHOW_FORM  = 0x00
CMD_CLOSE_FORM = 0x01
CMD_UPDATA_OK  = 0x02
CMD_DOWNLOAD_OK = 0x03

class DocThread(QThread):
    formSignal = pyqtSignal(int)
    textSignal = pyqtSignal(str)
    presSignal = pyqtSignal(int)
    def __init__(self, action, url, fileName=''):
        super(DocThread, self).__init__()

        self.action = action
        self.url = url
        self.fileName = fileName

        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
        print(action + " : " + url)
        
    def run(self):

        if self.action == "down_doc":#下载Bin文件

            with closing(requests.get(self.url, headers=self.headers,stream=True)) as response:
                chunkSize = 1024
                dateCount = 0
                with open(self.fileName,"wb") as file:
                    for data in response.iter_content(chunk_size=chunkSize):
                        file.write(data)
                        dateCount = dateCount + len(data)
            self.formSignal.emit(CMD_DOWNLOAD_OK) 
            return
        
        elif self.action == "get_doc_list":#获取gitee上固件文件列表

            r = None
            try:
                r = requests.get(self.url, timeout=10, headers=self.headers)
                r.encoding = 'utf-8'#r.apparent_encoding
            except Exception as e:
                self.formSignal.emit(CMD_CLOSE_FORM) 

            if r == None:
                self.formSignal.emit(CMD_CLOSE_FORM) 
                return 

            if r.status_code == 200:
                tbodys = re.findall('<div class=\'grid list selection([\w\W]+?)<div class=\'ui tree_progress\'>',r.text)

                if tbodys == None:
                    self.formSignal.emit(CMD_CLOSE_FORM) 
                    return

                tbody = '<div class=\'grid list selection' + tbodys[0]

                self.textSignal.emit(tbody)


class Dev_Document(QWidget):

    def __init__(self,parent=None):
        super().__init__(parent)

        self.layout=QVBoxLayout(self)

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(192,253,123,100))

        self.waitPage=QLabel(self)

        self.waitPage.setGeometry(0, 0, 600, 350)
        self.waitPage.setAlignment(Qt.AlignVCenter)
        self.waitPage.setText("<center><font color='red' size='6' line-height='50px';><red>Getting list of documents......</font></center>")
        self.waitPage.setAutoFillBackground(True)
        self.waitPage.setPalette(palette)

        self.is_First_Show = True

    def get_doc_list(self):

        if not self.is_First_Show: return

        self.mThread = DocThread(action="get_doc_list", url='https://gitee.com/Ai-Thinker-Open/TB_Dev_Document')
        self.mThread.textSignal.connect(self.show_doc_list)
        self.mThread.formSignal.connect(self.waitPag_State)
        self.mThread.start()

        self.is_First_Show = False


    def show_doc_list(self, tbody):

        selector = etree.HTML(tbody)        # 转换为lxml解析的对象

        contents = selector.xpath('//div/div[@data-type="file"]/div[@data-type="file"]/a/text()')    # 这里返回的是一个列表
        messages = selector.xpath('//div/div[@data-type="file"]/div/div[@class="commit-details"]/a/text()')    # 这里返回的是一个列表

        print(contents)
        print(messages)

        self.TableWidget=QTableWidget()
        self.TableWidget.setColumnCount(3) # 表格共有四列
        self.TableWidget.verticalHeader().setVisible(False)  # 隐藏垂直表头
        self.TableWidget.horizontalHeader().setVisible(True)  # 显示水平表头

        font = QFont('Arial', 10)
        font.setBold(True)  #设置字体加粗
        self.TableWidget.horizontalHeader().setFont(font) #设置表头字体

        # self.TableWidget.setFrameShape(QFrame.NoFrame)  ##设置无表格的外框
        self.TableWidget.horizontalHeader().setFixedHeight(25) ##设置表头高度

        self.TableWidget.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)#设置第一列宽度自动调整，充满屏幕
        # self.TableWidget.horizontalHeader().setStretchLastSection(True) ##设置最后一列拉伸至最大

        self.TableWidget.setHorizontalHeaderLabels(['file name','Document introduction','operating']) #Set header content
        self.TableWidget.horizontalHeader().setSectionsClickable(False)
        self.TableWidget.horizontalHeader().setStyleSheet('QHeaderView::section{background:green}')#设置表头的背景色为绿色

        self.TableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers) # 不可编辑
        self.TableWidget.setSelectionBehavior(QAbstractItemView.SelectRows) #只能选择整行

        self.TableWidget.setColumnWidth(1,230)
        self.TableWidget.setColumnWidth(2,80)

        rows = self.TableWidget.rowCount()
        rows_index = 0

        for content, message in zip(contents, messages):
            content = content.strip()        # 去掉字符左右的空格
            message = message.strip()
            self.TableWidget.setRowCount(rows_index + 1)
            self.TableWidget.setItem(rows_index, 0, QTableWidgetItem(content))
            self.TableWidget.setItem(rows_index, 1, QTableWidgetItem(message))
            self.TableWidget.setCellWidget(rows_index, 2, self.buttonForRow(rows_index))
            rows_index += 1

        self.TableWidget.setGeometry(15, 10,300,300)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.TableWidget)

        return 0


    def buttonForRow(self,id):
        widget=QWidget()
        # 修改
        downloadBtn = QPushButton('download')
        downloadBtn.setStyleSheet(''' text-align : center;
        background-color : NavajoWhite;
        height : 30px;
        border-style: outset;
        font : 13px  ''')

        downloadBtn.clicked.connect(lambda:self.download(id))

        hLayout = QHBoxLayout()
        hLayout.addWidget(downloadBtn)
        hLayout.setContentsMargins(5,2,5,2)
        widget.setLayout(hLayout)
        return widget

    def download(self, id):

        fileName, ok = QFileDialog.getSaveFileName(self, "Save file", "./combine/" + self.TableWidget.item(id, 0).text(), "All Files (*);;Bin Files (*.pdf)")
        if ok:
            print(fileName)

            self.mThread = DocThread(action="down_doc", url="https://gitee.com/Ai-Thinker-Open/TB_Dev_Document/raw/master/" + self.TableWidget.item(id, 0).text(), fileName = fileName)
            self.mThread.formSignal.connect(self.waitPag_State)
            self.mThread.start()

            self.waitPage.setText("<center><font color='red' size='6' line-height='50px';><red>Downloading document......</font></center>")
            self.waitPage.show()
            self.waitPage.raise_()

    def waitPag_State(self, state):
        if state == CMD_CLOSE_FORM:
            self.waitPage.hide()
        elif state == CMD_DOWNLOAD_OK:
            self.waitPage.hide()
            QMessageBox.information(self,"Warning","download successful!")

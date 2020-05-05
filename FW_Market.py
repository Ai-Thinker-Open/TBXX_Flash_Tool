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
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem,QAbstractItemView,QFrame,QHeaderView
from PyQt5.QtCore import Qt,QThread,pyqtSignal
from PyQt5.QtGui import QIcon,QPalette,QColor,QFont

from Markdown_CSS import html_head
from Markdown_CSS import html_tail
from Markdown_CSS import html_test

CMD_SHOW_FORM  = 0x00
CMD_CLOSE_FORM = 0x01
CMD_UPDATA_OK  = 0x02

class FwThread(QThread):
    formSignal = pyqtSignal(int)
    textSignal = pyqtSignal(str)
    presSignal = pyqtSignal(int)
    def __init__(self, action, url, fileName=''):
        super(FwThread, self).__init__()

        self.action = action
        self.url = url
        self.fileName = fileName

        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
        print(action + " : " + url)
        
    def run(self):

        if self.action == "down_bin":#下载Bin文件

            with closing(requests.get(self.url, headers=self.headers,stream=True)) as response:
                chunkSize = 1024
                dateCount = 0
                with open(self.fileName,"wb") as file:
                    for data in response.iter_content(chunk_size=chunkSize):
                        file.write(data)
                        dateCount = dateCount + len(data)
            return

        r = None
        try:
            r = requests.get(self.url, timeout=10, headers=self.headers)
            r.encoding = 'utf-8'#r.apparent_encoding
        except Exception as e:
            self.formSignal.emit(CMD_CLOSE_FORM) 

        if r == None:
            self.formSignal.emit(CMD_CLOSE_FORM) 
            return 

        if self.action == "get_fw_list":#获取gitee上固件文件列表

            if r.status_code == 200:
                tbodys = re.findall('<div class=\'grid list selection([\w\W]+?)<div class=\'ui tree_progress\'>',r.text)
                tbody = '<div class=\'grid list selection' + tbodys[0]

                self.textSignal.emit(tbody)

        elif self.action == "get_bin_url":#获取Bin文件的下载地址

            if r.status_code == 200:
                tbodys = re.findall('<div class=\'grid list selection([\w\W]+?)<div class=\'ui tree_progress\'>',r.text)
                tbody = '<div class=\'grid list selection' + tbodys[0]

                selector = etree.HTML(tbody)        # 转换为lxml解析的对象
                titles = selector.xpath('//div/div[@data-type="file"]/div[@data-type="file"]/a/@href')    # 这里返回的是一个列表

                for each in titles:
                    title = each.strip()        # 去掉字符左右的空格
                    if title.find('.bin') > 0:
                        self.textSignal.emit(title)
                        break

                self.formSignal.emit(CMD_CLOSE_FORM) # 获取下载地址失败

        elif self.action == "get_readme":#获取说明文档
            if r.status_code == 200:
                self.textSignal.emit(r.text)

class Doc_From(QWidget): # 用来显示文档的窗口
    def __init__(self,parent=None):
        super().__init__(parent)

        if os.path.exists('combine/aithinker.png'): self.setWindowIcon(QIcon("combine/aithinker.png"))

        self.docPage=QTextEdit(self)
        self.docPage.setGeometry(5, 5, 600, 350)
        self.docPage.setReadOnly(True)
        self.docPage.setStyleSheet("background:transparent;border-width:0;border-style:outset")
        

    def set_readme(self,readme):
        exts = extras = ['code-friendly', 'fenced-code-blocks', 'footnotes','tables','code-color','pyshell','nofollow','cuddled-lists','header ids','nofollow']
        self.docPage.setHtml(html_head + markdown2.markdown(readme, extras=exts) + html_tail)
        # self.docPage.setHtml(markdown2.markdown(readme, extras=exts))
        # self.docPage.setText(html_test)
    
    def set_title(self, title):
        self.setWindowTitle(title)


class FW_Market(QWidget):

    def __init__(self,parent=None):
        super().__init__(parent)

        self.layout=QVBoxLayout(self)

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(192,253,123,100))

        self.waitPage=QLabel(self)

        self.waitPage.setGeometry(0, 0, 600, 350)
        self.waitPage.setAlignment(Qt.AlignVCenter)
        self.waitPage.setText("<center><font color='red' size='6' line-height='50px';><red>正在获取固件列表......</font></center>")
        self.waitPage.setAutoFillBackground(True)
        self.waitPage.setPalette(palette)

        self.is_First_Show = True

    def get_fw_list(self):

        if not self.is_First_Show: return

        self.mThread = FwThread(action="get_fw_list", url='https://gitee.com/Ai-Thinker-Open/TB_FW_Market')
        self.mThread.textSignal.connect(self.show_bin_list)
        self.mThread.formSignal.connect(self.waitPag_State)
        self.mThread.start()

        self.is_First_Show = False


    def show_bin_list(self, tbody):

        selector = etree.HTML(tbody)        # 转换为lxml解析的对象

        contents = selector.xpath('//div/div[@data-type="folder"]/div[@data-type="folder"]/a/text()')    # 这里返回的是一个列表
        messages = selector.xpath('//div/div[@data-type="folder"]/div/div[@class="commit-details"]/a/text()')    # 这里返回的是一个列表
        timeagos = selector.xpath('//div/div[@data-type="folder"]/div/span[@class="timeago"]/@datetime')    # 这里返回的是一个列表

        print(contents)
        print(messages)
        print(timeagos)

        self.TableWidget=QTableWidget()
        self.TableWidget.setColumnCount(4) # 表格共有四列
        self.TableWidget.verticalHeader().setVisible(False)  # 隐藏垂直表头
        self.TableWidget.horizontalHeader().setVisible(True)  # 显示水平表头

        font = QFont('微软雅黑', 10)
        font.setBold(True)  #设置字体加粗
        self.TableWidget.horizontalHeader().setFont(font) #设置表头字体

        # self.TableWidget.setFrameShape(QFrame.NoFrame)  ##设置无表格的外框
        self.TableWidget.horizontalHeader().setFixedHeight(25) ##设置表头高度

        self.TableWidget.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)#设置第一列宽度自动调整，充满屏幕
        # self.TableWidget.horizontalHeader().setStretchLastSection(True) ##设置最后一列拉伸至最大

        self.TableWidget.setHorizontalHeaderLabels(['固件名称','固件版本','更新日期','操作']) #设置表头内容
        self.TableWidget.horizontalHeader().setSectionsClickable(False)
        self.TableWidget.horizontalHeader().setStyleSheet('QHeaderView::section{background:green}')#设置表头的背景色为绿色

        self.TableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers) # 不可编辑
        self.TableWidget.setSelectionBehavior(QAbstractItemView.SelectRows) #只能选择整行

        self.TableWidget.setColumnWidth(1,100)
        self.TableWidget.setColumnWidth(2,130)
        self.TableWidget.setColumnWidth(3,100)

        rows = self.TableWidget.rowCount()
        rows_index = 0

        for content, message, timeago in zip(contents, messages, timeagos):
            content = content.strip()        # 去掉字符左右的空格
            if content.find('@') > 0:
                message = message.strip()
                timeago = timeago.strip()
                self.TableWidget.setRowCount(rows_index + 1)
                self.TableWidget.setItem(rows_index, 0, QTableWidgetItem(content))
                self.TableWidget.setItem(rows_index, 1, QTableWidgetItem(message))
                self.TableWidget.setItem(rows_index, 2, QTableWidgetItem(timeago))
                self.TableWidget.setCellWidget(rows_index, 3, self.buttonForRow(rows_index))
                rows_index += 1

        self.TableWidget.setGeometry(15, 10,300,300)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.TableWidget)

        return 0


    def buttonForRow(self,id):
        widget=QWidget()
        # 修改
        downloadBtn = QPushButton('下载')
        downloadBtn.setStyleSheet(''' text-align : center;
        background-color : NavajoWhite;
        height : 30px;
        border-style: outset;
        font : 13px  ''')

        downloadBtn.clicked.connect(lambda:self.download(id))

        # 查看
        docBtn = QPushButton('文档')
        docBtn.setStyleSheet(''' text-align : center;
        background-color : DarkSeaGreen;
        height : 30px;
        border-style: outset;
        font : 13px; ''')

        docBtn.clicked.connect(lambda: self.document(id))

        hLayout = QHBoxLayout()
        hLayout.addWidget(downloadBtn)
        hLayout.addWidget(docBtn)
        hLayout.setContentsMargins(5,2,5,2)
        widget.setLayout(hLayout)
        return widget

    def download(self, id):
        self.mThread = FwThread(action="get_bin_url", url='https://gitee.com/Ai-Thinker-Open/TB_FW_Market/tree/master/' + self.TableWidget.item(id, 0).text())
        self.mThread.textSignal.connect(self.save_File)
        self.mThread.formSignal.connect(self.waitPag_State)
        self.mThread.start()

        self.waitPage.setText("<center><font color='red' size='6' line-height='50px';><red>正在解析下载地址......</font></center>")
        self.waitPage.show()
        self.waitPage.raise_()

    def save_File(self, fileUrl):

        tmp = re.findall('master/([\w\W]+?).bin', fileUrl)
        tmp = tmp[0].strip() + '.bin'
        tmp = re.findall('/([\w\W]+?).bin', tmp)
        raw_fileName = tmp[0].strip() + '.bin'

        fileName, ok = QFileDialog.getSaveFileName(self, "文件保存", "./combine/" + raw_fileName, "All Files (*);;Bin Files (*.bin)")
        fileUrl = fileUrl.replace('/blob/','/raw/')
        if ok:
            print(fileName)

            self.mThread = FwThread(action="down_bin", url="https://gitee.com" + fileUrl, fileName = fileName)
            self.mThread.start()

        self.waitPage.hide()

    def document(self, id):
        self.mThread = FwThread(action="get_readme", url="https://gitee.com/Ai-Thinker-Open/TB_FW_Market/raw/master/" + self.TableWidget.item(id, 0).text() + "/README.md")
        self.mThread.textSignal.connect(self.show_document)
        self.mThread.formSignal.connect(self.waitPag_State)
        self.mThread.start()
        self.waitPage.setText("<center><font color='red' size='6' line-height='50px';><red>正在获取文档......</font></center>")
        self.waitPage.show()
        self.waitPage.raise_()

        self.docPage_Title = self.TableWidget.item(id, 0).text() + " 固件使用说明"

    def show_document(self, readme):
        self.waitPage.hide()
        self.win = Doc_From()
        self.win.set_readme(readme)
        self.win.set_title(self.docPage_Title)
        self.win.show()

    def waitPag_State(self, state):
        if state == CMD_CLOSE_FORM:
            self.waitPage.hide()


if __name__ == '__main__':
    app=QApplication(sys.argv)
    win=FW_Market()
    win.show()
    sys.exit(app.exec_())
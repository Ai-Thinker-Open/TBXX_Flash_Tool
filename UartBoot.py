#coding=utf-8
#!/usr/bin/env python

### ComSwireWriter.py ###
###    Autor: pvvx    ###
###    Edited: Aaron Christophel ATCnetz.de    ###
###    Edit : Pila    ###

import sys
import signal
import struct
import serial
import platform
import time
import argparse
import os
import io
import serial.tools.list_ports
import base64

boot_bin = base64.b64decode(b"""
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
ENCgBGYWlsDQoAAE9LXzAyDQoAT0tfMDMNCgA=
""")

def sws_encode_blk(blk):
	pkt=[]
	d = bytearray([0xe8,0xef,0xef,0xef,0xef])
	for el in blk:
		if (el & 0x80) != 0:
			d[0] &= 0x0f
		if (el & 0x40) != 0:
			d[1] &= 0xe8
		if (el & 0x20) != 0:
			d[1] &= 0x0f
		if (el & 0x10) != 0:
			d[2] &= 0xe8
		if (el & 0x08) != 0:
			d[2] &= 0x0f
		if (el & 0x04) != 0:
			d[3] &= 0xe8
		if (el & 0x02) != 0:
			d[3] &= 0x0f
		if (el & 0x01) != 0:
			d[4] &= 0xe8
		pkt += d 
		d = bytearray([0xef,0xef,0xef,0xef,0xef])
	return pkt

# encode command stop into 10-bit swire words
def sws_code_end():
	return sws_encode_blk([0xff])
# encode the command for writing data into 10-bit swire words
def sws_wr_addr(addr, data):
	return sws_encode_blk(bytearray([0x5a, (addr>>16)&0xff, (addr>>8)&0xff, addr & 0xff, 0x00]) + bytearray(data)) + sws_encode_blk([0xff])
# send block to USB-COM
def wr_usbcom_blk(serialPort, blk):
	return serialPort.write(blk)
# send and receive block to USB-COM
def	rd_wr_usbcom_blk(serialPort, blk):
	i = wr_usbcom_blk(serialPort, blk)
	return i == len(serialPort.read(i))
# send swire command write to USB-COM
def sws_wr_addr_usbcom(serialPort, addr, data):
	return wr_usbcom_blk(serialPort, sws_wr_addr(addr, data))
# send and receive swire command write to USB-COM


def activate(serialPort, tact_ms):

	serialPort.setDTR(True)
	serialPort.setRTS(True)
	time.sleep(0.05)
	serialPort.setDTR(False)
	serialPort.setRTS(False)
	# Stop CPU|: [0x0602]=5
	sws_wr_addr_usbcom(serialPort, 0x06f, bytearray([0x20])) # soft reset mcu
	blk = sws_wr_addr(0x0602, bytearray([0x05]))
	if tact_ms > 0:
		tact = tact_ms/1000.0
		t1 = time.time()
		while time.time()-t1 < tact:
			for i in range(5):
				wr_usbcom_blk(serialPort, blk)
			serialPort.reset_input_buffer()
	#--------------------------------
	# Duplication with syncronization
	time.sleep(0.01)
	serialPort.reset_input_buffer()
	rd_wr_usbcom_blk(serialPort, sws_code_end())
	rd_wr_usbcom_blk(serialPort, blk)
	time.sleep(0.01)
	serialPort.reset_input_buffer()

def load_ram(_port):
	size = len(boot_bin)
	addr = 0x40000
	bin_addr = 0
	while size > 0:
		data = boot_bin[bin_addr:bin_addr+0x100]
		if not len(data) > 0: # end of stream
			break
		_port.write(sws_wr_addr(addr, data))
		_port.reset_input_buffer()
		bin_addr += len(data)
		addr += len(data)
		size -= len(data)

	# print('\rBin bytes writen:', bin_addr)		
	# print('CPU go Start...')
	_port.write(sws_wr_addr(0x0602, b'\x88')) # cpu go Start
	time.sleep(0.07)
	_port.flushInput()
	_port.flushOutput()
	_port.reset_input_buffer()
	_port.reset_output_buffer()
	time.sleep(0.07)
	return True

def uart_boot(serialPort):
	activate(serialPort, 80)
	return load_ram(serialPort)

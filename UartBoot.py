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

COMPORT_MIN_BAUD_RATE=340000
COMPORT_DEF_BAUD_RATE=921600
USBCOMPORT_BAD_BAUD_RATE=460800

debug = False
bit8mask = 0x20


boot_bin = base64.b64decode(b"""
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
""")

# encode data (blk) into 10-bit swire words
def sws_encode_blk(blk):
	pkt=[]
	d = bytearray(10) # word swire 10 bits
	d[0] = 0x80 # start bit byte cmd swire = 1
	for el in blk:
		m = 0x80 # mask bit
		idx = 1
		while m != 0:
			if (el & m) != 0:
				d[idx] = 0x80
			else:
				d[idx] = 0xfe
			idx += 1
			m >>= 1
		d[9] = 0xfe # stop bit swire = 0
		pkt += d
		d[0] = 0xfe # start bit next byte swire = 0
	return pkt
# decode 9 bit swire response to byte (blk)
def sws_decode_blk(blk):
	if (len(blk) == 9) and ((blk[8] & 0xfe) == 0xfe):
		bitmask = bit8mask
		data = 0;
		for el in range(8):
			data <<= 1
			if (blk[el] & bitmask) == 0:
				data |= 1
			bitmask = 0x10
		#print('0x%02x' % data)
		return data
	#print('Error blk:', blk)
	return None
# encode a part of the read-by-address command (before the data read start bit) into 10-bit swire words
def sws_rd_addr(addr):
	return sws_encode_blk(bytearray([0x5a, (addr>>16)&0xff, (addr>>8)&0xff, addr & 0xff, 0x80]))
# encode command stop into 10-bit swire words
def sws_code_end():
	return sws_encode_blk([0xff])
# encode the command for writing data into 10-bit swire words
def sws_wr_addr(addr, data):
	return sws_encode_blk(bytearray([0x5a, (addr>>16)&0xff, (addr>>8)&0xff, addr & 0xff, 0x00]) + bytearray(data)) + sws_encode_blk([0xff])
# send block to USB-COM
def wr_usbcom_blk(serialPort, blk):
	# USB-COM chips throttle the stream into blocks at high speed!
	# Swire is transmitted by 10 bytes of UART.
	# The packet must be a multiple of these 10 bytes.
	# Max block USB2.0 64 bytes -> the packet will be 60 bytes.
	if serialPort.baudrate > USBCOMPORT_BAD_BAUD_RATE:
		i = 0
		s = 60
		l = len(blk)
		while i < l:
			if l - i < s:
				s = l - i
			i += serialPort.write(blk[i:i+s])
			serialPort.flush()
		return i
	return serialPort.write(blk)
# send and receive block to USB-COM
def	rd_wr_usbcom_blk(serialPort, blk):
	i = wr_usbcom_blk(serialPort, blk)
	return i == len(serialPort.read(i))
# send swire command write to USB-COM
def sws_wr_addr_usbcom(serialPort, addr, data):
	return wr_usbcom_blk(serialPort, sws_wr_addr(addr, data))
# send and receive swire command write to USB-COM
def rd_sws_wr_addr_usbcom(serialPort, addr, data):
	i = wr_usbcom_blk(serialPort, sws_wr_addr(addr, data))
	return i == len(serialPort.read(i))
# send swire data in fifo mode
def rd_sws_fifo_wr_usbcom(serialPort, addr, data):
	rd_sws_wr_addr_usbcom(serialPort, 0x00b3, bytearray([0x80])) # [0xb3]=0x80 ext.SWS into fifo mode
	rd_sws_wr_addr_usbcom(serialPort, addr, data) # send all data to one register (no increment address - fifo mode)
	rd_sws_wr_addr_usbcom(serialPort, 0x00b3, bytearray([0x00])) # [0xb3]=0x00 ext.SWS into normal(ram) mode
# send and receive swire command read to USB-COM
def sws_read_data(serialPort, addr, size = 1):
	time.sleep(0.05)
	serialPort.reset_input_buffer()
	# send addr and flag read
	rd_wr_usbcom_blk(serialPort, sws_rd_addr(addr))
	out = []
	# read size bytes
	for i in range(size):
		# send bit start read byte
		serialPort.write([0xfe])
		# read 9 bits swire, decode read byte
		blk = serialPort.read(9)
		# Added retry reading for Prolific PL-2303HX and ...
		if len(blk) < 9:
			blk += serialPort.read(10-len(blk))
		x = sws_decode_blk(blk)
		if x != None:
			out += [x]
		else:
			if debug:
				print('\r\nDebug: read swire byte:')
				hex_dump(addr+i, blk)
			# send stop read
			rd_wr_usbcom_blk(serialPort, sws_code_end())
			out = None
			break
	# send stop read
	rd_wr_usbcom_blk(serialPort, sws_code_end())
	return out
# set sws speed according to clk frequency and serialPort baud
def set_sws_speed(serialPort, clk):
	#--------------------------------
	# Set register[0x00b2]
	print('SWire speed for CLK %.1f MHz... ' % (clk/1000000), end='')
	swsdiv = int(round(clk*2/serialPort.baudrate))
	if swsdiv > 0x7f:
		print('Low UART baud rate!')
		return False
	byteSent = sws_wr_addr_usbcom(serialPort, 0x00b2, [swsdiv])
	# print('Test SWM/SWS %d/%d baud...' % (int(serialPort.baudrate/5),int(clk/5/swsbaud)))
	read = serialPort.read(byteSent)
	if len(read) != byteSent:
		if serialPort.baudrate > USBCOMPORT_BAD_BAUD_RATE and byteSent > 64 and len(read) >= 64 and len(read) < byteSent:
			print('\n\r!!!!!!!!!!!!!!!!!!!BAD USB-UART Chip!!!!!!!!!!!!!!!!!!!')
			print('UART Output:')
			hex_dump(0,sws_wr_addr(0x00b2, [swsdiv]))
			print('UART Input:')
			hex_dump(0,read)
			print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
			return False
		print('\n\rError: Wrong RX-TX connection!')
		return False
	#--------------------------------
	# Test read register[0x00b2]
	x = sws_read_data(serialPort, 0x00b2)
	#print(x)
	if x != None and x[0] == swsdiv:
		print('ok.')
		if debug:
			print('Debug: UART-SWS %d baud. SW-CLK ~%.1f MHz' % (int(serialPort.baudrate/10), serialPort.baudrate*swsdiv/2000000))
			print('Debug: swdiv = 0x%02x' % (swsdiv))
		return True
	#--------------------------------
	# Set default register[0x00b2]
	rd_sws_wr_addr_usbcom(serialPort, 0x00b2, 0x05)
	print('no')
	return False

def activate(serialPort, tact_ms):
	#--------------------------------
	# issue reset-to-bootloader:
	# RTS = either RESET (active low = chip in reset)
	# DTR = active low
	print('Reset module (RTS low)...')
	serialPort.setDTR(True)
	serialPort.setRTS(True)
	time.sleep(0.05)
	serialPort.setDTR(False)
	serialPort.setRTS(False)
	#--------------------------------
	# Stop CPU|: [0x0602]=5
	print('Activate (%d ms)...' % tact_ms)
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

	print('\rBin bytes writen:', bin_addr)		
	print('CPU go Start...')
	_port.write(sws_wr_addr(0x0602, b'\x88')) # cpu go Start
	time.sleep(0.07)
	_port.flushInput()
	_port.flushOutput()
	_port.reset_input_buffer()
	_port.reset_output_buffer()
	time.sleep(0.07)
	return True

def uart_boot(serialPort):

	if(serialPort.baudrate < COMPORT_MIN_BAUD_RATE):
		print ('The minimum speed of the COM port is %d baud!' % COMPORT_MIN_BAUD_RATE)
		return False

	activate(serialPort, 80)

	if not set_sws_speed(serialPort, 24000000):
		print('Chip sleep? -> Use reset chip (RTS-RST): see option --tact')
		return False

	print('Download uart_boot.bin')
	return load_ram(serialPort)

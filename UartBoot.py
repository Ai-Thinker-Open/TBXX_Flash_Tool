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
		return True
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

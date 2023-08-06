# gnoduino - Python Arduino IDE implementation
# Copyright (C) 2010-2012  Lucian Langa
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
import gettext
_ = gettext.gettext
import misc
import sys
import time

import board
import config
import programmer
import misc
import prefs
import serialio

avr = [
	"avrdude",
#	"-Chardware/tools/avrdude.conf",
	"-v",
	"-v",
	"-v",
	"-F",	#force write to ignore signature check
	"-D"
]

avr_bl = [
	"avrdude",
#	"-Chardware/tools/avrdude.conf",
#	"-v",
]


def burnBootloader(serial, output, notify, id):
	p = prefs.preferences()
	misc.clearConsole(output)
	context = notify.get_context_id("main")
	notify.pop(context)
	notify.push(context, _("Burning bootloader..."))
	b = board.Board()
	compline=[i for i in avr_bl]
	pgm = programmer.Programmer()
	if pgm.getCommunication(id) == 'serial':
        	port = serial.getConfigSerialPort(notify, output)
	        if port != -1:
        	        serial.resetBoard()
        	"""De-fuse and erase board"""

		port = serial.getConfigSerialPort(notify, output)
		if port == -1:
			notify.pop(context)
			notify.push(context, _("Flashing error."))
			return
		compline.append("-P" + port)
		if pgm.getSpeed(id) != 0:
			compline.append("-b" + pgm.getSpeed(id))
	elif pgm.getCommunication(id) == 'usb':
		compline.append("-Pusb")
	compline.append("-c" + pgm.getProtocol(id))
	compline.append("-p" + b.getBoardMCU(b.getBoard()))
	compline.append("-e")
	if pgm.getForce(id) == 'true':
		compline.append("-F")
	compline.append("-Ulock:w:" + b.getFuseUnlock(b.getBoard()) + ":m")
	if b.getBoardMCU(b.getBoard()) != 'atmega8':
		compline.append("-Uefuse:w:" + b.getFuseExtended(b.getBoard()) + ":m")
	compline.append("-Uhfuse:w:" + b.getFuseHigh(b.getBoard()) + ":m")
	compline.append("-Ulfuse:w:" + b.getFuseLow(b.getBoard()) + ":m")
	try:
		if p.getBoolValue("upload.verbose"):
			sys.stderr.write(' '.join(compline)+"\n")
			misc.printMessageLn(output, ' '.join(compline))
		(run, sout) = misc.runProg(compline)
		misc.printMessageLn(output, sout, p.getBoolValue("upload.verbose"), 'false')
		if p.getBoolValue("upload.verbose"): sys.stderr.write(sout+"\n")
		if run == False: raise
	except:
		misc.printErrorLn(notify, output, _("Burn Error"), _("Burn ERROR."))
		return
	"""Burn and fuse board"""
	compline=[i for i in avr_bl]
	compline.append("-c" + pgm.getProtocol(id))
	if pgm.getCommunication(id) == 'serial':
		port = serial.getConfigSerialPort(notify, output)
		if port == -1:
			notify.pop(context)
			notify.push(context, _("Flashing error."))
			return
		compline.append("-P" + port)
		if pgm.getSpeed(id) != 0:
			compline.append("-b" + pgm.getSpeed(id))
	elif pgm.getCommunication(id) == 'usb':
		compline.append("-Pusb")
	compline.append("-p" + b.getBoardMCU(b.getBoard()))
	compline.append("-e")
	if pgm.getForce(id) == 'true':
		compline.append("-F")
	compline.append("-Uflash:w:" + findBootLoader() + ":i")
	compline.append("-Ulock:w:" + b.getFuseLock(b.getBoard()) + ":m")
	try:
		if p.getBoolValue("upload.verbose"):
			sys.stderr.write(' '.join(compline)+"\n")
			misc.printMessageLn(output, ' '.join(compline))
		(run, sout) = misc.runProg(compline)
		misc.printMessageLn(output, sout, p.getBoolValue("upload.verbose"), 'false')
		if p.getBoolValue("upload.verbose"): sys.stderr.write(sout+"\n")
		if run == False: raise
	except:
		misc.printErrorLn(notify, output, _("Burn Error"), _("Burn ERROR."))
		return
	notify.pop(context)
	notify.push(context, _("Burn complete."))
	misc.printMessageLn(output, \
		"Burn OK.");

def upload(obj, serial, output, notify, force_protocol):
	p = prefs.preferences()
	pgm = programmer.Programmer()
	context = notify.get_context_id("main")
	notify.pop(context)
	notify.push(context, _("Flashing..."))
	b = board.Board()
	compline=[i for i in avr]
	protocol = b.getPGM(b.getBoard())
	# avrdude wants "stk500v1" to distinguish it from stk500v2
	if protocol == "stk500": protocol = "stk500v1"
	# if we do not get any protocol back probably means board doesn't
	# enforce any particular programmer
	if protocol == "" or force_protocol is True:
		#try selected programmer (via menu)
		protocol =  pgm.getProtocol(pgm.getProgrammer())
		try:
			comm = pgm.getCommunication(pgm.getProgrammer())
			if comm:
				if comm == "serial":
					port = serial.getConfigSerialPort(notify, output)
					if port == -1:
						notify.pop(context)
						notify.push(context, _("Flashing error."))
						return
					serial.resetBoard()
					compline.append("-P" + port)
				else: compline.append("-P" + comm)
				try:
					compline.append("-b" + pgm.getSpeed(pgm.getProgrammer()))
				except: pass
		except: pass
	else:
		if protocol != "usbtiny":	#usbtiny works via spi, need to do some device parsing here
			port = serial.getConfigSerialPort(notify, output)
			if port == -1:
				notify.pop(context)
				notify.push(context, _("Flashing error."))
				return
			compline.append("-P" + port)
			serial.resetBoard(b.getPath(b.getBoard()))
	compline.append("-c" + protocol)
	try:
		compline.append("-b" + b.getPGMSpeed(b.getBoard()))
	except: pass
	compline.append("-p" + b.getBoardMCU(b.getBoard()))
	compline.append("-Uflash:w:"+obj+".hex:i")
	try:
		if p.getBoolValue("upload.verbose"):
			sys.stderr.write(' '.join(compline)+"\n")
			misc.printMessageLn(output, ' '.join(compline))
		(run, sout) = misc.runProg(compline)
		misc.printMessageLn(output, sout, p.getBoolValue("upload.verbose"), 'false')
		if p.getBoolValue("upload.verbose"): sys.stderr.write(sout+"\n")
		if run == False: raise
	except:
		misc.printErrorLn(notify, output, _("Flashing Error"), _("Flash ERROR.\n"))
		return
	notify.pop(context)
	notify.push(context, _("Flashing complete."))
	misc.printMessageLn(output, \
		"Flash OK.");

def findBootLoader():
	b = board.Board()
	boot = b.getBootloader(b.getBoard())
	if boot.endswith(".hex"): None
	else: boot = boot + ".hex"
	return os.path.join(misc.getArduinoBootPath(), b.getPath(b.getBoard()), boot)


#!/usr/bin/env python3

from collections import namedtuple

intSize = 4

PoI = namedtuple('PoI', ['offset', 'value'])

PoIs = []

def readBinFile(filename):
	fh = open(filename, "rb")
	contents = fh.read()
	fh.close()
	return contents[:]

def writeBinFile(filename, data):
	newFilename = os.path.splitext(filename)[0] + '.txt'
	if os.path.exists(newFilename):
		print(f"{newFilename} already exists")
		num = 0
	else:
		print(f"Creating {newFilename}")
		fh = open(newFilename, "wb")
		num = fh.write(data)
		fh.close()
	return num

def getBytes(data, offset, size):
	return data[offset:offset+size]

def getInt(data, offset, size=intSize):
	# Return a 32-bit int
	return int.from_bytes(data[offset:offset+size], byteorder='little', signed=False)

def main(args):
	filename = args.filename
	
	content = readBinFile(filename)
	filesize = len(content)
	
	if content[:2] != b"VA":
		print(f"{filename} isn't a spi file")
	
	# Offset  Size   Value
	#    0      4    56 41 00 02
	#    4      4    Offset to (12 bytes before) user programs
	#                Metadata
	#                    Each item begins with 01 00 00 00
	#                    Label and values begin with 02 00 00 00
	#                    Size of the data follows: XX XX 00 00
	#                    Data
	#                End of metadata: 03 00 00 00
	#                PLC programs 
	#                    Name starts with 01 00 00 00
	#                    Size of the name follows: XX XX 00 00
	#                    Data starts with 01 00 00 00
	#                    Data ends with 03 00 00 00 (size not specified)
	#                Global variables(?)
	#                    Each item begins with 01 00 00 00
	#                    ???
	#   *4      4    Offset to end of data
	#   *4+4    4    Size of user programs?
	#   *4+8    4    Size of user global variable or settings?
	#                Axis Settings
	#                Global Settings
	#                USDA(?) binary data
	#
	
	# Location of offset to user programs (12 bytes before)
	offset = 4
	
	programOffset = getInt(content, offset, intSize)
	
	dataEndOffset = getInt(content, programOffset, intSize)
	
	# TODO: understand the meaning of the 8 bytes that are being skipped
	offset = programOffset + 12
	
	data = getBytes(content, offset, dataEndOffset - offset)
	
	# Find USDA(?) offset (doesn't exist in older firmware backups)
	for i in range(len(data)):
		binStr = getBytes(data, i, 4)
		if binStr == b"USDA":
			break
	
	actualData = data[:i]
	#!print(actualData)
	
	num = writeBinFile(filename, actualData)
	print(f"Bytes written: {num}")
	
	### 2nd attempt: searching through the file for unprintable ascii delimiters to see if they are meaningful
	## Ignore the start of the file for now
	#offset = 8
	#
	#size = None
	#lastOffset = 0
	#
	#for off in range(offset, filesize - intSize):
	#	value = getInt(content, off, intSize);
	#	if value == 1:
	#		#!print(f"0x{off:x}: Start of Heading")
	#		PoIs.append(PoI(off, value))
	#	elif value == 2:
	#		#!print(f"0x{off:x}: Start of Text")
	#		PoIs.append(PoI(off, value))
	#	elif value == 3:
	#		#!print(f"0x{off:x}: End of Text")
	#		PoIs.append(PoI(off, value))
	#	
	#
	#for idx, poi in enumerate(PoIs):
	#	if poi.value == 2:
	#		print(f"0x{poi.offset:x}: [2] Start of Text")
	#	if poi.value == 3:
	#		print(f"0x{poi.offset:x}: [3] End of Text\n")
	#	if poi.value == 1:
	#		print(f"0x{poi.offset:x}: [1] Start of Heading")
	#		
	#		if idx < len(PoIs[:-1]):
	#			if PoIs[idx].offset + 4 == PoIs[idx+1].offset:
	#				print("The next value is a PoI!\n")
	#				continue
	#			# Look at the next value
	#			nextValue = getInt(content, PoIs[idx].offset+4, intSize)
	#			print(f"  Next value = {nextValue}")
	#			nextPoI = PoIs[idx+1].offset - (PoIs[idx].offset+4)
	#			print(f"  Distance until to next PoI = {nextPoI}")
			
	### 1st attempt: trying to parse data based on unprintable ascii delimiters
	#while offset < filesize:
	#	# Store the last offset
	#	lastOffset = offset
	#	#
	#	value = getInt(content, offset, intSize)
	#	if value == 2:
	#		print(f"Start of Text: 0x{offset:x}")
	#		offset += 4
	#	elif value == 1:
	#		print(f"Start of Heading: 0x{offset:x}")
	#		offset += 4
	#		
	#		#
	#		size = getInt(content, offset, intSize)
	#		
	#		print(f"Size of Heading: {size}")
	#		offset += 4
	#		
	#		#
	#		data = getBytes(content, offset, size)
	#		print(f"Data: {data}\n")
	#		offset += size
	#		
	#	elif value == 3:
	#		print(f"End of Text: 0x{offset}\n\n")
	#		offset += 4
	#		
	#	else:
	#		print(f"value = {value}")
	#		
	#		# Should 4 be subtracted from the offset because the previous size=0 read was actually part of the data
	#		
	#		if size == 0:
	#			# This is likely an unspecified data block. Continue until hitting the 3.
	#			print("I need to do something")
	#			
	#			extra = 0
	#			while True:
	#				#print(extra)
	#				value = getInt(content, offset+extra, intSize)
	#				if value == 3:
	#					break
	#				else:
	#					extra += 1
	#			
	#			print(f"Size of variable data: {extra+4}")
	#			data = getBytes(content, offset-4, extra+4)
	#			print(f"Data: {data}")
	#			offset = offset + extra
	#			
	#		else:
	#			print(size)





if __name__ == '__main__':
	import argparse as ap
	import sys
	import os
	
	parser = ap.ArgumentParser("spi-extractor.py")
	
	parser.add_argument("filename", action="store", default=None, help="ACS backup file name")
	
	args = parser.parse_args(sys.argv[1:])
	
	
	#!print(args)
	
	if (os.path.isfile(args.filename)):
		main(args)
	else:
		print("Error: {} does not exist".format(args.filename))

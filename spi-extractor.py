#!/usr/bin/env python3

intSize = 4

def readBinFile(filename):
	fh = open(filename, "rb")
	contents = fh.read()
	fh.close()
	return contents[:]

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
	
	# Ignore the start of the file for now
	offset = 8
	
	size = None
	lastOffset = 0
	
	while offset < filesize:
		# Store the last offset
		lastOffset = offset
		#
		value = getInt(content, offset, intSize)
		if value == 2:
			print(f"Start of Text: 0x{offset:x}")
			offset += 4
		elif value == 1:
			print(f"Start of Heading: 0x{offset:x}")
			offset += 4
			
			#
			size = getInt(content, offset, intSize)
			
			print(f"Size of Heading: {size}")
			offset += 4
			
			#
			data = getBytes(content, offset, size)
			print(f"Data: {data}\n")
			offset += size
			
		elif value == 3:
			print(f"End of Text: 0x{offset}\n\n")
			offset += 4
			
		else:
			print(f"value = {value}")
			
			# Should 4 be subtracted from the offset because the previous size=0 read was actually part of the data
			
			if size == 0:
				# This is likely an unspecified data block. Continue until hitting the 3.
				print("I need to do something")
				
				extra = 0
				while True:
					#print(extra)
					value = getInt(content, offset+extra, intSize)
					if value == 3:
						break
					else:
						extra += 1
				
				print(f"Size of variable data: {extra+4}")
				data = getBytes(content, offset-4, extra+4)
				print(f"Data: {data}")
				offset = offset + extra
				
			else:
				print(size)





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

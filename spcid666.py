import struct
import sys

subChunkTypes = {
	#[data, description]. type is: 0 string, 1 integer, 2 data.
	0x01: [0, "Song Name"],
	0x02: [0, "Game Name"],
	0x03: [0, "Artist's Name"],
	0x04: [0, "Dumper's Name"],
	0x05: [1, "Date Song was Dumped (stored as YYYYMMDD)"],
	0x06: [2, "Emulator Used"],
	0x07: [0, "Comments"],
	0x10: [0, "Official Soundtrack Title"],
	0x11: [2, "OST Disc"],
	0x12: [2, "OST Track (upper byte is the number 0-99], lower byte is an optional ASCII character)"],
	0x13: [0, "Publisher's Name"],
	0x14: [2, "Copyright Year"],
	0x30: [1, "Introduction Length (lengths are stored in 1/64000th seconds)"],
	0x31: [1, "Loop Length"],
	0x32: [1, "End Length"],
	0x33: [1, "Fade Length"],
	0x34: [2, "Muted Voices (a bit is set for each voice that's muted)"],
	0x35: [2, "Number of Times to Loop"],
	0x36: [2, "Mixing (Preamp) Level"]
}

def readFromBuffer(bfr, size):
	mod = size % 4 #32 bits alignment
	paddingLength = 0
	if mod:
		paddingLength = 4 - mod
		
	retval = bfr[:size + paddingLength]
	del bfr[:size + paddingLength]
	return retval

def printValue(header, data):
	if header['dataType'] == 0: #string
		print "String or data value:", data
	elif header['dataType'] == 1: #integer
		print "Integer value:", struct.unpack_from("i", data)[0]
	elif header['dataType'] == 2: #data
		dataToPrint = data if header['hasData'] else header['valueBytes']
		print "Data type value as bytes:", ':'.join("0x%02X" % byte for byte in dataToPrint)
		printInterpretedValue(header, data)

def printInterpretedValue(header, data):
	if header['id'] == 0x12:
		print "Interpreted value:", data >> 8, chr(data & 0x00FF)
	else:
		print "Interpreted value:", data

def parseHeader(headerData):
	return {
		'id': headerData[0],
		'description': subChunkTypes[headerData[0]][1],
		'dataType': subChunkTypes[headerData[0]][0],
		'hasData': headerData[1] != 0,
		'value':  struct.unpack_from("h", headerData[2:])[0],
		'valueBytes': headerData[2:]
	}

if len(sys.argv) != 2:
	print "Usage: id666reader.py spcfile.spc"
else:
	with open(sys.argv[1], "rb") as f:
		f.seek(0x10200) #ID666 extended offset
		riffId = f.read(4) # always "xid6"
		riffChunkSize = struct.unpack("i", f.read(4))[0]
		riffBuffer = bytearray(f.read(riffChunkSize))

		while riffBuffer:
			subChunkHeader = readFromBuffer(riffBuffer, 4)
			header = parseHeader(subChunkHeader);
			
			print "Subchunk ID", "0x%X" % header['id'], ":", header['description']
			print "Value is in header:", not header['hasData']
			if header['hasData']:
				subchunkData = readFromBuffer(riffBuffer, header['value'])
				printValue(header, subchunkData)
			else:
				printValue(header, header['value'])

			print

import struct
import sys
import collections
import string

_DEBUG = False #Print debug information on stdout
_PREFER_BIN = False #Default to binary format, if type is indeterminable

###############################
class ExtendedTag:
	def __init__(self):
		self.reset();

	def get_items(self):
		stringProperties = [
			[0x01, self.title],
			[0x02, self.game],
			[0x03, self.artist],
			[0x04, self.dumper],
			[0x07, self.comments],
			[0x10, self.officiel_title]
		]
		for stringProperty in stringProperties:
			yield XID6_Item(header, data, stringProperty[1])

	def get_total_size(self):
		xid6Items = self.get_items()
		#additionner tous les tags not None Integer (4 bytes chaque)
		#additionner tous les strings. doivent finir avec 00 donc +1
		#additionnner tous les data.
		#toujours aligner sur 4 octets.
		return 0

	def reset(self):
		self.title = None
		self.game = None
		self.artist = None
		self.dumper = None
		self.date = None
		self.emulator = None
		self.comments = None
		self.official_title = None
		self.disc = None
		self.track = None
		self.publisher = None
		self.copyright = None
		self.muted_channels = None
		self.nb_loops = None
		self.mixing_level = None
		self.unknown_items = []
		self.intro_length = None
		self.loop_length = None
		self.end_length = None
		self.fade_length = None

###############################
class BaseTag:
	binary_offsets = [[0x2E, 32], [0x4E, 32], [0x6E, 16], [0x7E, 32], [0x9E, 4], [0xA9, 3], [0xAC, 4], [0xB0, 32], [0xD0, 1], [0xD1, 1]]
	text_offsets = [[0x2E, 32], [0x4E, 32], [0x6E, 16], [0x7E, 32], [0x9E, 11], [0xA9, 3], [0xAC, 5], [0xB1, 32], [0xD1, 1], [0xD2, 1]]

	def __init__(self):
		self.is_binary = False
		self.title = ''
		self.game = ''
		self.dumper = ''
		self.comments = ''
		self.date = None
		self.artist = ''
		self.muted_channels = 0
		self.emulator = Emulator()
		self.length_before_fadeout = 0
		self.fadeout_length = 0


###############################
class XID6_Item:
	def __init__(self, header = None, data = None, interpreted_value = None, id = None):
		if header != None:
			self.header = header
			self.data = data
			self.interpreted_value = interpreted_value
		else: #this will be used for writing. unfinished and untested.
			self.header = XID6_ItemHeader(id) 
			if self.header.dataType == 0: #string
				self.header.hasData = True
				self.header.valueBytes = len(interpreted_value) + 1
				self.data = bytearray(interpreted_value).append(0x00)
			elif self.header.dataType == 1: #integer
				self.header.hasData = False
				self.header.valueBytes = len(interpreted_value) + 1
			else: #data (not sure about the values here.)
				self.header.hasData = True
				self.header.valueBytes = len(data)
				self.data = data


###############################
class XID6_ItemHeader:
	ids = {
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
	
	def __init__(self, id, dataType = None, hasData = None, valueBytes = None, description = None, value = None):
		self.id = id
		self.value = value
		self.valueBytes = valueBytes
		self.hasData = hasData
		
		if dataType != None or id not in XID6_ItemHeader.ids:
			self.dataType = dataType
			self.description = description
		else:
			self.dataType = XID6_ItemHeader.ids[id][0]
			self.description = XID6_ItemHeader.ids[id][1]

###############################
class Emulator:
	names = ["unknown", "ZSNES", "Snes9x", "ZST2SPC", "ETC", "SNEShout", "ZSNESW"]
	
	def __init__(self, emulatorString = ''):
		if emulatorString == '':
			self.code = '0'
			self.name = Emulator.names[0]
			self.is_other = False
		elif emulatorString in string.digits[0:len(Emulator.names)]:
			self.code = emulatorString
			self.name = Emulator.names[int(emulatorString)]
			self.is_other = False
		else:
			self.code = emulatorString
			self.name = "other"
			self.is_other = True

###############################
class Tag:
	def __init__(self, base, extended):
		self.base = base
		self.extended = extended

###############################
class _TagReader:
	def _read_from_buffer(self, bfr, size, offset = 0):
		mod = size % 4 #32 bits alignment
		paddingLength = 0
		if mod:
			paddingLength = 4 - mod

		retval = bfr[:size + paddingLength]
		del bfr[:size + paddingLength]
		return retval

	def _interpret_data_for_item_id(self, itemId, data):
		if itemId == 0x12: #ost track
			optionalChar = data & 0x00FF
			return data >> 8, chr(optionalChar) if 0x20 <= optionalChar <= 0x7f else None
		else:
			return data

	def _parse_header(self, headerData):
		return XID6_ItemHeader(
			id = headerData[0],
			description = XID6_ItemHeader.ids[headerData[0]][1] if headerData[0] in XID6_ItemHeader.ids.keys() else "Unknown",
			dataType = XID6_ItemHeader.ids[headerData[0]][0] if headerData[0] in XID6_ItemHeader.ids.keys() else None,
			hasData = headerData[1] != 0,
			value =  struct.unpack_from("h", headerData[2:])[0],
			valueBytes = headerData[2:]
		)

	def _read_file(self, f, offset_size):
		f.seek(offset_size[0])
		return bytearray(f.read(offset_size[1]));

	def _bytes_to_string(self, bts):
		retval = str(bts).rstrip(' \t\r\n\0')
		return self._decode_string(retval)

	def _get_type(self, fieldBytes):
		if all(b == 0 for b in fieldBytes):
			return None; #empty string or 0
		elif all((b >= 0x30 and b <= 0x39 or b == '/' or b == 0) for b in fieldBytes):
			return 'text'
		else:
			return 'binary'

	def _base_tag_is_binary(self, f):
		# This method is highly based on SNESAmp
		# http://www.alpha-ii.com/
		
		dateBytes = self._read_file(f, [0x9E, 11])
		dateType = self._get_type(dateBytes)
		songType = self._get_type(self._read_file(f, [0xA9, 3]))
		fadeType = self._get_type(self._read_file(f, [0xAC, 5]))

		channelDisable = self._read_file(f, [0xd1, 1])
		emulator = self._read_file(f, [0xd2, 1])
		isBinary = True

		if songType == None and fadeType == None and dateType == None:	#If no times or date, use default
			if channelDisable == 1 and emulator == 0:											#Was the file dumped with ZSNES?
				isBinary = True
			else:
				isBinary = _PREFER_BIN
				if _DEBUG:
					print "Unknown base tag type, prefered binary:", _PREFER_BIN
		elif songType != 'binary' and fadeType != 'binary':							#If no time, or time is text
			if dateType == 'text':
				isBinary = False
			elif dateType == None:
				isBinary = _PREFER_BIN																			#Times could still be binary (ex. 56 bin = '8' txt)
				if _DEBUG:
					print "Unknown base tag type, prefered binary:", _PREFER_BIN
			elif dateType == 'binary':																		#Date contains invalid characters
				if all(b == 0 for b in dateBytes[4:7]):											#If bytes 4-7 are 0's, it's probably a ZSNES dump
					isBinary = True
				else:
					isBinary = False																					#Otherwise date may contain alpha characters
		else:
			isBinary = True																								#If time is not text, tag is binary

		return isBinary

	def _decode_string(self, string):
		for encoding in ['ascii', 'UTF8', 'latin-1']:
			try:
				return string.decode(encoding)
			except:
				pass
		return 'INVALID ENCODING'

	def parse_base_tag(self, f):
		tagIsBinary = self._base_tag_is_binary(f)
		if _DEBUG:
			print "Base tag is binary:", tagIsBinary
		
		if tagIsBinary:
			offsets = BaseTag.binary_offsets
		else:
			offsets = BaseTag.text_offsets

		retval = BaseTag()
		retval.is_binary = tagIsBinary
		retval.title = self._bytes_to_string(self._read_file(f, offsets[0]))
		retval.game = self._bytes_to_string(self._read_file(f, offsets[1]))
		retval.dumper = self._bytes_to_string(self._read_file(f, offsets[2]))
		retval.comments = self._bytes_to_string(self._read_file(f, offsets[3]))
		retval.date = self._bytes_to_string(self._read_file(f, offsets[4]))
		retval.artist = self._bytes_to_string(self._read_file(f, offsets[7]))
		retval.muted_channels = self._read_file(f, offsets[8])[0] #always binary
		
		lengthBytes = self._read_file(f, offsets[5])
		fadeoutBytes = self._read_file(f, offsets[6])
		emulatorBytes = self._read_file(f, offsets[9])
		
		if tagIsBinary:
			lengthBytes.append(0x00)
			retval.length_before_fadeout = struct.unpack_from("i", lengthBytes)[0]
			retval.fadeout_length = struct.unpack_from("i", fadeoutBytes)[0]
			retval.emulator = Emulator(str(struct.unpack_from("b", emulatorBytes)[0]))
		else:
			lengthString = self._bytes_to_string(lengthBytes)
			fadeoutString = self._bytes_to_string(fadeoutBytes)
			retval.length_before_fadeout = int(lengthString) if lengthString != '' else 0
			retval.fadeout_length = int(fadeoutString) if fadeoutString != '' else 0
			retval.emulator = Emulator(self._bytes_to_string(emulatorBytes))

		return retval

	def _parse_interpreted_value(self, header, data):
		if header.dataType == 0: #string
			return self._bytes_to_string(data)
		elif header.dataType == 1: #integer
			if header.hasData:
				return struct.unpack_from("i", data)[0]
			else:
				return data
		elif header.dataType == 2: #data
			return self._interpret_data_for_item_id(header.id, data)

	def _apply_corruption_workarounds(self, header, riffBuffer):
		if header.id == 0x13: #publisher name sometimes declares one byte too many
			newLength = header.value
			while newLength > 0 and (len(riffBuffer) - newLength) % 4 > 0 and riffBuffer[newLength-1] != 0:
				newLength = newLength - 1
			if newLength > 0:
				header.value = newLength

	def parse_extended_tag(self, f):
		f.seek(0x10200) #ID666 extended offset
		riffId = f.read(4) # always "xid6"
		
		if riffId == '':
			return None
		else:
			riffChunkSize = struct.unpack("i", f.read(4))[0]
			riffBuffer = bytearray(f.read(riffChunkSize))

			items = []
			while riffBuffer:
				subChunkHeader = self._read_from_buffer(riffBuffer, 4)
				header = self._parse_header(subChunkHeader);

				if _DEBUG:
					print "Subchunk ID", "0x%X" % header.id, ":", header.description

				if header.hasData:
					self._apply_corruption_workarounds(header, riffBuffer)
					subchunkData = self._read_from_buffer(riffBuffer, header.value)
					items.append(XID6_Item(header, subchunkData, self._parse_interpreted_value(header, subchunkData)))
				else:
					items.append(XID6_Item(header, None, self._parse_interpreted_value(header, header.value)))

			return self._create_extended_tag(items)
		
	def _create_extended_tag(self, items):
		retval = ExtendedTag()
		retval.title = self._pop_item_value_or_default(items, 0x1)
		retval.game = self._pop_item_value_or_default(items, 0x2)
		retval.artist = self._pop_item_value_or_default(items, 0x3)
		retval.dumper = self._pop_item_value_or_default(items, 0x4)
		retval.date = self._pop_item_value_or_default(items, 0x5)
		retval.emulator = self._pop_item_value_or_default(items, 0x6)
		retval.comments = self._pop_item_value_or_default(items, 0x7)
		retval.official_title = self._pop_item_value_or_default(items, 0x10)
		retval.disc = self._pop_item_value_or_default(items, 0x11)
		retval.track = self._pop_item_value_or_default(items, 0x12)
		retval.publisher = self._pop_item_value_or_default(items, 0x13)
		retval.copyright = self._pop_item_value_or_default(items, 0x14)
		retval.intro_length = self._pop_item_value_or_default(items, 0x30)
		retval.loop_length = self._pop_item_value_or_default(items, 0x31)
		retval.end_length = self._pop_item_value_or_default(items, 0x32)
		retval.fade_length = self._pop_item_value_or_default(items, 0x33)
		retval.muted_channels = self._pop_item_value_or_default(items, 0x34)
		retval.nb_loops = self._pop_item_value_or_default(items, 0x35)
		retval.mixing_level = self._pop_item_value_or_default(items, 0x36)
		retval.unknown_items = items
		return retval


	def _pop_item_value_or_default(self, items, itemId):
		item = next((item for item in items if item.header.id == itemId), None)
		if item != None:
			items.remove(item)
			return item.interpreted_value
		else:
			return None;

###############################
class _TagWriter:
	def __init__(self, f, tag):
		self.f = f
		self.tag = tag
		if tag.base.is_binary:
			self.offsets = BaseTag.binary_offsets
		else:
			self.offsets = BaseTag.text_offsets

	def _write_file(self, offset, data, forceText):
		size = offset[1]
		
		if not forceText and isinstance(data, int):
			data = bytearray(struct.unpack("4B", struct.pack("I", data))[:size])
		elif forceText and (isinstance(data, int) or isinstance(data, float)):
			data = str(int(data))[:size]
			data = data + ('\x00' * (size - len(data))) #padding
		else:
			data = str(data)[:size]
			data = data + ('\x00' * (size - len(data))) #padding

		self.f.seek(offset[0])
		self.f.write(data)
		

	def write_base_tag(self):
		tag = self.tag.base
		self._write_file(self.offsets[0], tag.title, False)
		self._write_file(self.offsets[1], tag.game, False)
		self._write_file(self.offsets[2], tag.dumper, False)
		self._write_file(self.offsets[3], tag.comments, False)
		self._write_file(self.offsets[4], tag.date, not tag.is_binary)
		self._write_file(self.offsets[7], tag.artist, False)
		self._write_file(self.offsets[8], tag.muted_channels, False)
		self._write_file(self.offsets[5], tag.length_before_fadeout, not tag.is_binary)
		self._write_file(self.offsets[6], tag.fadeout_length, not tag.is_binary)
		self._write_file(self.offsets[9], tag.emulator.code, not tag.is_binary)

	def write_extended_tag(self):
		xid6Size = self.tag.extended.get_total_size()
		if xid6Size > 0:
			#pad with \x00 until we reach 0x10200
			f.seek(0x10200) #ID666 extended offset
			f.write('xid6')
			#write xid6Size in 4 bytes
			#write each xid6 item.

###############################
def parse(filename):
	reader = _TagReader()
	with open(filename, "rb") as f:
		return Tag(
			base = reader.parse_base_tag(f),
			extended = reader.parse_extended_tag(f)
		)

def save(tag, filename):
	dataUntilXid6 = None
	with open(filename, 'r+b') as f:
		writer = _TagWriter(f, tag)
		writer.write_base_tag()

		#xid6 not supported yet, will be stripped.
		f.seek(0)
		dataUntilXid6 = f.read(0x10200)
		
	with open(filename, 'w+b') as f:
		f.write(dataUntilXid6)
		writer = _TagWriter(f, tag)
		writer.write_extended_tag()

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: spcid666.py spcfile.spc"
	else:
		print parse(sys.argv[1])

import struct
import sys
import collections
import string

_DEBUG = False #Print debug information on stdout
_PREFER_BIN = False #Default to binary format, if type is indeterminable

_extended_tag = collections.namedtuple('ExtendedTag', [
	'title',
	'game',
	'artist',
	'dumper',
	'date',
	'emulator',
	'comments',
	'official_title',
	'disc',
	'track',
	'publisher',
	'copyright',
	'intro_length',
	'loop_length',
	'end_length',
	'fade_length',
	'muted_channels',
	'nb_loops',
	'mixing_level',
	'unknown_items'
])

_xid6_item = collections.namedtuple('XID6_Item', [
	'header',
	'data',
	'interpreted_value'
])

_base_tag = collections.namedtuple('BaseTag', [
	'isBinary',
	'title',
	'game',
	'dumper',
	'comments',
	'date',
	'length_before_fadeout',
	'fadeout_length',
	'artist',
	'muted_channels',
	'emulator'
])

_tag = collections.namedtuple('ID666Tag', [
	'base',
	'extended'
])

_emulator = collections.namedtuple('Emulator', [
	'code',
	'name',
	'is_other'
])

_extended_ids = {
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

def _read_from_buffer(bfr, size, offset = 0):
	mod = size % 4 #32 bits alignment
	paddingLength = 0
	if mod:
		paddingLength = 4 - mod
		
	retval = bfr[:size + paddingLength]
	del bfr[:size + paddingLength]
	return retval

def _interpret_data_for_item_id(itemId, data):
	if itemId == 0x12: #ost track
		return data >> 8, chr(data & 0x00FF)
	else:
		return data

def _parse_header(headerData):
	return {
		'id': headerData[0],
		'description': _extended_ids[headerData[0]][1],
		'dataType': _extended_ids[headerData[0]][0],
		'hasData': headerData[1] != 0,
		'value':  struct.unpack_from("h", headerData[2:])[0],
		'valueBytes': headerData[2:]
	}

def _read_file(f, offset_size):
	f.seek(offset_size[0])
	return bytearray(f.read(offset_size[1]));

def _bytes_to_string(bts):
	return str(bts).rstrip(' \t\r\n\0')

def _get_type(fieldBytes):
	if all(b == 0 for b in fieldBytes):
		return None; #empty string or 0
	elif all((b >= 0x30 or b <= 0x39 or b == '/' or b == 0) for b in fieldBytes):
		return 'text'
	else:
		return 'binary'

def _base_tag_is_binary(f):
	dateBytes = _read_file(f, [0x9E, 11])
	dateType = _get_type(dateBytes)
	songType = _get_type(_read_file(f, [0xA9, 3]))
	fadeType = _get_type(_read_file(f, [0xAC, 5]))

	channelDisable = _read_file(f, [0xd1, 1])
	emulator = _read_file(f, [0xd2, 1])

	isBinary = True
	
	if songType == None and fadeType == None and dateType == None:	#If no times or date, use default
		if channelDisable == 1 and emulator == 0:											#Was the file dumped with ZSNES?
			isBinary = True
		else:
			isBinary = _PREFER_BIN
	elif songType != 'binary' and fadeType != 'binary':							#If no time, or time is text
		if dateType == 'text':
			isBinary = False
		elif dateType == None:
			isBinary = _PREFER_BIN																			#Times could still be binary (ex. 56 bin = '8' txt)
		elif dateType == 'binary':																		#Date contains invalid characters
			if all(b == 0 for b in dateBytes[4:7]):											#If bytes 4-7 are 0's, it's probably a ZSNES dump
				isBinary = True
			else:
				isBinary = False																					#Otherwise date may contain alpha characters
	else:
		isBinary = True																								#If time is not text, tag is binary

	return isBinary


def _parse_base_tag(f):
	tagIsBinary = _base_tag_is_binary(f)
	if tagIsBinary:
		offsets = [[0x2E, 32], [0x4E, 32], [0x6E, 16], [0x7E, 32], [0x9E, 11], [0xA9, 3], [0xAC, 5], [0xB0, 32], [0xD0, 1], [0xD1, 1]]
	else:
		offsets = [[0x2E, 32], [0x4E, 32], [0x6E, 16], [0x7E, 32], [0x9E, 4], [0xA9, 3], [0xAC, 4], [0xB1, 32], [0xD1, 1], [0xD2, 1]]

	return _base_tag(
		isBinary= tagIsBinary,
		title = _bytes_to_string(_read_file(f, offsets[0])),
		game = _bytes_to_string(_read_file(f, offsets[1])),
		dumper = _bytes_to_string(_read_file(f, offsets[2])),
		comments = _bytes_to_string(_read_file(f, offsets[3])),
		date = _bytes_to_string(_read_file(f, offsets[4])),
		length_before_fadeout = _bytes_to_string(_read_file(f, offsets[5])),
		fadeout_length = _bytes_to_string(_read_file(f, offsets[6])),
		artist = _bytes_to_string(_read_file(f, offsets[7])),
		muted_channels = _read_file(f, offsets[8])[0], #always binary
		emulator = _parse_emulator(_bytes_to_string(_read_file(f, offsets[9])))
	)

def _parse_emulator(emulatorString):
	names = ["unknown", "ZSNES", "Snes9x", "ZST2SPC", "ETC", "SNEShout", "ZSNESW"]
	if emulatorString == '':
		return _emulator(code = '0', name = names[0], is_other = False)
	elif emulatorString in string.digits[0:len(names)]:
		return _emulator(code = emulatorString, name = names[int(emulatorString)], is_other = False)
	else:
		return _emulator(code = emulatorString, name = "other", is_other = True)

def _parse_interpreted_value(header, data):
	if header['dataType'] == 0: #string
		return _bytes_to_string(data)
	elif header['dataType'] == 1: #integer
		return struct.unpack_from("i", data)[0]
	elif header['dataType'] == 2: #data
		return _interpret_data_for_item_id(header['id'], data)

def _parse_extended_tag(f):
	f.seek(0x10200) #ID666 extended offset
	riffId = f.read(4) # always "xid6"
	riffChunkSize = struct.unpack("i", f.read(4))[0]
	riffBuffer = bytearray(f.read(riffChunkSize))

	items = []
	while riffBuffer:
		subChunkHeader = _read_from_buffer(riffBuffer, 4)
		header = _parse_header(subChunkHeader);

		if _DEBUG:
			print "Subchunk ID", "0x%X" % header['id'], ":", header['description']

		if header['hasData']:
			subchunkData = _read_from_buffer(riffBuffer, header['value'])
			items.append(_xid6_item(header, subchunkData, _parse_interpreted_value(header, subchunkData)))
		else:
			items.append(_xid6_item(header, None, _parse_interpreted_value(header, header['value'])))

	return _extended_tag(
		title = pop_item_or_default(items, 0x1),
		game = pop_item_or_default(items, 0x2),
		artist = pop_item_or_default(items, 0x3),
		dumper = pop_item_or_default(items, 0x4),
		date = pop_item_or_default(items, 0x5),
		emulator = pop_item_or_default(items, 0x6),
		comments = pop_item_or_default(items, 0x7),
		official_title = pop_item_or_default(items, 0x10),
		disc = pop_item_or_default(items, 0x11),
		track = pop_item_or_default(items, 0x12),
		publisher = pop_item_or_default(items, 0x13),
		copyright = pop_item_or_default(items, 0x14),
		intro_length = pop_item_or_default(items, 0x30),
		loop_length = pop_item_or_default(items, 0x31),
		end_length = pop_item_or_default(items, 0x32),
		fade_length = pop_item_or_default(items, 0x33),
		muted_channels = pop_item_or_default(items, 0x34),
		nb_loops = pop_item_or_default(items, 0x35),
		mixing_level = pop_item_or_default(items, 0x36),
		unknown_items = items
	)

def pop_item_or_default(items, itemId):
	item = next((item for item in items if item.header['id'] == itemId), None)
	if item != None:
		items.remove(item)

	return item;

def parse(filename):
	with open(filename, "rb") as f:
		return _tag(
			base = _parse_base_tag(f),
			extended = _parse_extended_tag(f)
		)

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: id666reader.py spcfile.spc"
	else:
		print parse(sys.argv[1])

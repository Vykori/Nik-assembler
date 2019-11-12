import os
import binascii

assembly = open("testing.nik", "r") #get file as read-only
binary = open("output.bin","w+b") #make new file for output

emptylines = False

def emptyLinesError():
	if emptylines == False:
		print("Warning: You have at least 1 empty line in this file. Please ensure you\'re not jumping to incorrect addresses.")
	return

#run through each line of input file
valid = True
for count, line in enumerate(assembly, 1):
	line = line.replace('\n', '')
	line = line.replace('\t', ' ')

	words = line.split(" ") #never gives an empty list

	#clear any leading spaces, empty lines, comments, etc
	if len(words) == 1:
		if words[0] == "":
			emptyLinesError()
			emptylines = True
			continue
	lineisempty = False #temporary variable just for double-breaking
	while True:
		if len(words[0]) == 0:
			words = words.pop(0)
			if len(words) == 0:
				emptylines = True
				emptyLinesError()
				lineisempty = True
				break
		else:
			break
	if lineisempty == True:
		continue
	if words[0][0] == ";":
		emptyLinesError()
		emptylines = True
		continue
	for x in range(len(words)):
		if words[x][0] == ";":
			words = words[:x]
			break;

	#initialization
	print ("Line {}: ".format(count), end = '')
	for word in words:
		print(word, end = ' ')
	print()
	operation = 0
	unimplimented = False

	#go through all operation types
	words[0] = words[0].lower()
	if words[0] == "hault":
		operation = 0
		if len(words) > 1:
			print("Warning: \"hault\" takes no arguments. They will be ignored.".format(count))

	elif words[0] == "reset":
		operation = 64512
		if len(words) > 1:
			print("Warning: \"reset\" takes no arguments. They will be ignored.".format(count))
	elif words[0] == "nothing":
		operation = 7168
		if len(words) > 1:
			print("Warning: \"nothing\" takes no arguments. They will be ignored.".format(count))
	elif words[0] == "copy":
		unimplimented = True
	elif words[0] == "copyzero":
		unimplimented = True
	elif words[0] == "copyoverflow":
		unimplimented = True
	elif words[0] == "mode":
		operation = 32768
		if words[1] == "add":
			unimplimented = True
		elif words[1] == "subtract":
			unimplimented = True
		elif words[1] == "and":
			unimplimented = True
		elif words[1] == "xor":
			unimplimented = True
		else:
			print("Error: \"mode\" needs a single argument specifying \"add\", \"subtract\", \"and\", or \"xor\". Stopping.")
			valid = False
			break
		if len(words) > 2:
			print("Warning: \"mode\" only takes 1 argument. The rest will be ignored.".format(count))
	elif words[0] == "or":
		unimplimented = True
	elif words[0][0] == "0":
		if len(words[0]) != 2:
			print(words[0], "is an unknown operation. stopping.")
			valid = False
			break
		elif words[0][1] == "d":
			if len(words) > 2:
				print("Warning: \"0d\" only takes 1 argument. The others will be ignored.".format(count))
			elif len(words) < 2:
				print("Error: \"0d\" needs a decimal number as an argument. Stopping.")
				valid = False
				break
			operation = int(words[1])
		elif words[0][1] == "x":
			if len(words) > 2:
				print("Warning: \"0x\" only takes 1 argument. The others will be ignored.".format(count))
			elif len(words) < 2:
				print("Error: \"0x\" needs a hexadecimal number as an argument. Stopping.")
				valid = False
				break
			operation = int("{0:>04}".format(words[1]), 16)
			# https://docs.python.org/3/library/functions.html#int
		elif words[0][1] == "b":
			if len(words) > 2:
				print("Warning: \"0b\" only takes 1 argument. The others will be ignored.".format(count))
			elif len(words) < 2:
				print("Error: \"0b\" needs a binary number as an argument. Stopping.")
				valid = False
				break
			operation = int("{0:>016}".format(words[1]), 2)
			# https://docs.python.org/3/library/functions.html#int
		else:
			print(words[0], "is an unknown operation. stopping.")
			valid = False
			break
	else:
		print("\"{0}\" is an unknown operation. stopping.".format(words[0]))
		valid = False
		break

	if unimplimented == True:
		print("Error: \"{1}\" is an unimplimented operation for now. stopping.".format(count, words[0]))
		valid = False
		break
	else:
		opcode = operation.to_bytes(2, byteorder='big', signed=False)
		# converting opcode int into bytearray that I will later write to output file

		testing = "{:02X}{:02X}".format(opcode[0],opcode[1])

		binarystring = '{:016b}'.format(operation)
		# '016' means 16 chars wide and fill leading space with zeros, b means binary
		# https://docs.python.org/3/library/string.html#format-specification-mini-language

		print(binarystring, "or in hex:", testing)
		
		binary.write(opcode)


if valid == False:
	binary.close()
	os.remove("output.bin")
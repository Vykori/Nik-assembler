import os
import binascii

assembly = open("testing.nik", "r") #get input file as read-only
outputFile = open("output.bin","w+b") #make new output file as read-write, create-if-needed, binary

#at the end, if this variable is true, print a warning to console that there are empty lines in the input file
emptylines = False

#run through each line of input file
valid = True
for count, line in enumerate(assembly, 1):
	line = line.replace('\n', '') #remove that pesky newline that exists at the end of each line (except the last line)
	line = line.replace('\t', ' ') #easiest way to support tab and space indenting is convert them to the same thing

	words = line.split(" ") #never gives an empty list

	#clear any leading spaces, comments, convert to lowercase, detect blank lines, etc.
	if len(words) == 1:
		if words[0] == "":
			emptylines = True
			continue
	lineisempty = False #temporary variable just for double-breaking
	while True:
		if len(words[0]) == 0:
			words = words.pop(0)
			if len(words) == 0:
				emptylines = True
				lineisempty = True #double break
				break
		else:
			break
	if lineisempty == True:
		continue
	if words[0][0] == ";":
		emptylines = True
		continue
	for x in range(len(words)):
		if words[x][0] == ";":
			words = words[:x]
			break;
		words[x] = words[x].lower()
		if words[x][len(words[x]) - 1] == "," or words[x][len(words[x]) - 1] == ";":
			words[x] = words[x][:len(words[x]) - 1]

	#print the input code that's currently being interpreted
	print ("Line {}: ".format(count), end = '')
	for word in words:
		print(word, end = ' ')
	print()
	

	#go through all operation types
	operation = 0 #this variable will be the output data for this line of assembly. it will be converted to binary data at the end
	if words[0] == "halt":
		operation = int("0000000000000000", 2)
		if len(words) > 1:
			print("Warning: \"halt\" takes no arguments. They will be ignored.".format(count))

	elif words[0] == "reset":
		operation = int("1111110000000000", 2)
		if len(words) > 1:
			print("Warning: \"reset\" takes no arguments. They will be ignored.".format(count))

	elif words[0] == "nothing":
		operation = int("0001110000000000", 2)
		if len(words) > 1:
			print("Warning: \"nothing\" takes no arguments. They will be ignored.".format(count))

	elif words[0] == "copy" or words[0] == "copyzero" or words[0] == "copyoverflow":
		if words[0] == "copy":
			operation = int("1000000000000000", 2)
		elif words[0] == "copyzero":
			operation = int("1000010000000000", 2)
		elif words[0] == "copyoverflow":
			operation = int("1000100000000000", 2)

		if len(words) > 5:
			print("Warning: \"copy\" only takes 4 argument. Extras will be ignored.".format(count))
		elif len(words) < 5:
			print("Error: \"mode\" needs an argument specified. Stopping.")
			valid = False
			break

		#copy mode
		if words[1] == "direct":
			operation = operation + int("0000000000000000", 2)
		elif words[1] == "memory":
			operation = operation + int("0000000000010000", 2)
		elif words[1] == "proxy":
			operation = operation + int("0000000000011000", 2)
		else:
			print("Erorr. \"{0}\" is an unknown argument. Read mode must be \"direct\", \"memory\", or \"proxy\".".format(words[1]))

		#copy location
		if words[2] == "a":
			operation = operation + int("0000000000000000", 2)
		elif words[2] == "b":
			operation = operation + int("0000000000000001", 2)
		elif words[2] == "counter":
			operation = operation + int("0000000000000010", 2)
		elif words[2] == "output":
			operation = operation + int("0000000000000011", 2)
		elif words[2] == "operand":
			operation = operation + int("0000000000000100", 2)
		elif words[2] == "nowhere":
			operation = operation + int("0000000000000101", 2)
		elif words[2] == "alu":
			operation = operation + int("0000000000000110", 2)
		elif words[2] == "input":
			operation = operation + int("0000000000000111", 2)
		else:
			print("Erorr. \"{0}\" is an unknown argument. Read location must be \"A\", \"B\", \"Counter\", \"Output\", \"Operand\", \"Nowhere\", \"ALU\", or \"Input\".".format(words[2]))

		#write mode
		if words[3] == "direct":
			operation = operation + int("0000000000000000", 2)
		elif words[3] == "memory":
			operation = operation + int("0000001000000000", 2)
		elif words[3] == "proxy":
			operation = operation + int("0000001100000000", 2)
		else:
			print("Erorr. \"{0}\" is an unknown argument. Write mode must be \"direct\", \"memory\", or \"proxy\".".format(words[3]))

		#write location
		if words[4] == "a":
			operation = operation + int("0000000000000000", 2)
		elif words[4] == "b":
			operation = operation + int("0000000000100000", 2)
		elif words[4] == "counter":
			operation = operation + int("0000000001000000", 2)
		elif words[4] == "output":
			operation = operation + int("0000000001100000", 2)
		elif words[4] == "operand":
			operation = operation + int("0000000010000000", 2)
		elif words[4] == "nowhere":
			operation = operation + int("0000000010100000", 2)
		else:
			print("Erorr. \"{0}\" is an unknown argument. Write location must be \"A\", \"B\", \"Counter\", \"Output\", \"Operand\", or \"Nowhere\".".format(words[4]))

	elif words[0] == "mode":
		operation = int("0100000000000000", 2)
		if len(words) > 2:
				print("Warning: \"mode\" only takes 1 argument. Extras will be ignored.".format(count))
		elif len(words) < 2:
			print("Error: \"mode\" needs an argument specified. Stopping.")
			valid = False
			break
		if words[1] == "add":
			pass
		elif words[1] == "subtract":
			operation = operation + int("0000010000000000", 2)
		elif words[1] == "and":
			operation = operation + int("0000100000000000", 2)
		elif words[1] == "xor":
			operation = operation + int("0000110000000000", 2)
		else:
			print("Error: \"mode\" needs a single argument specifying \"add\", \"subtract\", \"and\", or \"xor\". Stopping.")
			valid = False
			break
		if len(words) > 2:
			print("Warning: \"mode\" only takes 1 argument. Extras will be ignored.".format(count))

	elif words[0] == "or":
		operation = int("1100000000000000")

		#write mode
		if words[1] == "direct":
			operation = operation + int("0000000000000000", 2)
		elif words[1] == "memory":
			operation = operation + int("0000001000000000", 2)
		elif words[1] == "proxy":
			operation = operation + int("0000001100000000", 2)
		else:
			print("Erorr. \"{0}\" is an unknown argument. Write mode must be \"direct\", \"memory\", or \"proxy\".".format(words[1]))

		#write location
		if words[2] == "a":
			operation = operation + int("0000000000000000", 2)
		elif words[2] == "b":
			operation = operation + int("0000000000100000", 2)
		elif words[2] == "counter":
			operation = operation + int("0000000001000000", 2)
		elif words[2] == "output":
			operation = operation + int("0000000001100000", 2)
		elif words[2] == "operand":
			operation = operation + int("0000000010000000", 2)
		elif words[2] == "nowhere":
			operation = operation + int("0000000010100000", 2)
		else:
			print("Erorr. \"{0}\" is an unknown argument. Write location must be \"A\", \"B\", \"Counter\", \"Output\", \"Operand\", or \"Nowhere\".".format(words[2]))
	
	elif words[0][0] == "0":
		if len(words[0]) != 2:
			print(words[0], "is an unknown operation. stopping.")
			valid = False
			break

		elif words[0][1] == "d": #d stands for decimal in this case
			if len(words) > 2:
				print("Warning: \"0d\" only takes 1 argument. The others will be ignored.".format(count))
			elif len(words) < 2:
				print("Error: \"0d\" needs a decimal number as an argument. Stopping.")
				valid = False
				break
			operation = int(words[1])

		elif words[0][1] == "x": #hexadecimal
			if len(words) > 2:
				print("Warning: \"0x\" only takes 1 argument. The others will be ignored.".format(count))
			elif len(words) < 2:
				print("Error: \"0x\" needs a hexadecimal number as an argument. Stopping.")
				valid = False
				break
			operation = int("{0:>04}".format(words[1]), 16)
			# https://docs.python.org/3/library/functions.html#int

		elif words[0][1] == "b": #binary
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

	# converting opcode int into bytearray that I will later write to output file
	opcode = operation.to_bytes(2, byteorder='big', signed=False)

	hexopcode = '{:04X}'.format(operation)

	binaryopcode = '{:016b}'.format(operation)
	# https://docs.python.org/3/library/string.html#format-specification-mini-language

	print(binaryopcode, "or hex", hexopcode)
	
	outputFile.write(opcode)

if valid == False:
	outputFile.close()
	os.remove("output.bin")
elif emptylines == True:
	print("Warning: You have at least 1 empty line in this file. Please ensure you're not jumping to incorrect addresses.")

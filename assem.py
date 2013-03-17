"""
Casey Collins
CS240 LAB8
Assembler
Fall 2012

Supported Error Checking: WORD does not support character strings,
Indexed addressing not supported with Immeadiate or Indirect Addressing,
Bad symbols not supported, returns error if neither base nor pc relative
addressing work, returns error if there is an attempt to use BR without a
BASE directive having been declared, only arguments in range for SVC, SHIFTL,
and SHIFTR are supported, invalid registers not supported for format 2
instructions, also checks invalid mnemnoics and duplicate labels.

Added 12/15: RESB and RESW now support hex arguments. RESW, RESB, and all
hex literals now check for invalid hex characters.
"""

import sys

NOARG = ['RSUB','HIO','TIO','SIO']

Nbit = 32
Ibit = 16
Xbit = 8
Bbit = 4
Pbit = 2
Ebit = 1

BASE = ''
ISBASE = False

RegisterNumbers = {'A' : 0,
             'X' : 1,
             'L' : 2,
             'B' : 3,
             'S' : 4,
             'T' : 5,
             'PC' : 8,
             'SW' : 9}

MNEMONICS = {
    'START' : ['D'],
    'RESB'  : ['D'],
    'RESW'  : ['D'],
    'WORD'  : ['D'],
    'BYTE'  : ['D'],
    'BASE'  : ['D'],
    'END'   : ['D'],
    'NOBASE' : ['D'],
'ADD'   : ['I',3,0X18,['m']],
'ADDF'   : ['I',3,0X58,['m']],
'ADDR'   : ['I',2,0X90,['r1','r2']],
'AND'   : ['I',3,0X40,['m']],
'CLEAR'   : ['I',2,0XB4,['r1']],
'COMP'   : ['I',3,0X28,['m']],
'COMPF'   : ['I',3,0X88,['m']],
'COMPR'   : ['I',2,0XA0,['r1','r2']],
'DIV'   : ['I',3,0X24,['m']],
'DIVF'   : ['I',3,0X64,['m']],
'DIVR'   : ['I',2,0X9C,['r1','r2']],
'J'   : ['I',3,0X3C,['m']],
'JEQ'   : ['I',3,0X30,['m']],
'JGT'   : ['I',3,0X34,['m']],
'JLT'   : ['I',3,0X38,['m']],
'JSUB'   : ['I',3,0X48,['m']],
'LDA'   : ['I',3,0X00,['m']],
'LDB'   : ['I',3,0X68,['m']],
'LDCH'   : ['I',3,0X50,['m']],
'LDF'   : ['I',3,0X70,['m']],
'LDL'   : ['I',3,0X08,['m']],
'LDS'   : ['I',3,0X6C,['m']],
'LDT'   : ['I',3,0X74,['m']],
'LDX'   : ['I',3,0X04,['m']],
'LPS'   : ['I',3,0XD0,['m']],
'MUL'   : ['I',3,0X20,['m']],
'MULF'   : ['I',3,0X60,['m']],
'MULR'   : ['I',2,0X98,['r1','r2']],
'OR'   : ['I',3,0X44,['m']],
'RD'   : ['I',3,0XD8,['m']],
'RMO'   : ['I',2,0XAC,['r1','r2']],
'RSUB'   : ['I',3,0X4C,['n']],
'SHIFTL'   : ['I',2,0XA4,['r1','n']],
'SHIFTR'   : ['I',2,0XA8,['r1','n']],
'SSK'   : ['I',3,0XEC,['m']],
'STA'   : ['I',3,0X0C,['m']],
'STB'   : ['I',3,0X78,['m']],
'STCH'   : ['I',3,0X54,['m']],
'STF'   : ['I',3,0X80,['m']],
'STI'   : ['I',3,0XD4,['m']],
'STL'   : ['I',3,0X14,['m']],
'STS'   : ['I',3,0X7C,['m']],
'STSW'   : ['I',3,0XE8,['m']],
'STT'   : ['I',3,0X84,['m']],
'STX'   : ['I',3,0X10,['m']],
'SUB'   : ['I',3,0X1C,['m']],
'SUBF'   : ['I',3,0X5C,['m']],
'SUBR'   : ['I',2,0X94,['r1','r2']],
'SVC'   : ['I',2,0XB0,['n']],
'TD'   : ['I',3,0XE0,['m']],
'TIX'   : ['I',3,0X2C,['m']],
'TIXR'   : ['I',2,0XB8,['r1']],
'WD'   : ['I',3,0XDC,['m']],
'HIO'  :  ['I',1,0XF4],
'TIO'  :  ['I',1,0XF8],
'SIO'  :  ['I',1,0XF0]}

SYMTAB = {}

def makeInstruction(mnemonic,operands,pc):
    lineInfo = MNEMONICS[baseMnemonic(mnemonic)]
    zStr = ""
    global BASE
    global ISBASE
    if lineInfo[0] == 'D':
        if mnemonic == 'BYTE' or mnemonic == 'WORD':
            if operands[0] == 'X' or operands [0] == 'C':
                if operands[0] == 'C' and mnemonic == 'WORD':
                    return error('WORD does to support character strings')
                return makeLiteral(operands)
            else:
                if mnemonic == 'WORD':
                    str = bitStr2Hex(toBitString(int(operands),8))
                    return padZero(str,6 - len(str)) #last change
                return bitStr2Hex(toBitString(int(operands),8))
        elif mnemonic == 'RESB' or mnemonic == 'RESW':
            i = 0
            return ""
        elif mnemonic == 'BASE':
            ISBASE = True
            if isSymbol(baseMnemonic(operands)):
                BASE = SYMTAB[baseMnemonic(operands)]
            else:
                BASE = pc
            return ""
        elif mnemonic == 'NOBASE':
            ISBASE = False
            return ''
        else:
            return ""

    length = assembledLength(mnemonic,operands)
    instrBits = toBitString(MNEMONICS[baseMnemonic(mnemonic)][2],8)
    if length==1:
        pass
    elif length==2:
        instrBits = instrBits + handle2(mnemonic,operands)
        
        
    elif length==3:
        instrBits = instrBits[0:6]
        flags = 0
        instrBits = handle34(instrBits,flags,mnemonic,operands,pc,12)
        
    else:
        instrBits = instrBits[0:6]
        flags = 0
        instrBits = handle34(instrBits,flags,mnemonic,operands,pc,20)

    return bitStr2Hex(instrBits).title()

def checkSym(s):
    """Check if s is a number or an invalid symbol"""
    try:
        int(s)
        return True
    except ValueError:
        error('Symbol ' + ' was not found in table. Invalid Symbol.')
    

def handle34(instrBits,flags,mnemonic,operands,pc,addreLen):
    """ """
    global BASE
    index = False
    noIndex = True
    if mnemonic == 'RSUB' or mnemonic == '+RSUB':
        if addreLen == 12:
            return instrBits + "110000000000000000"
        else:
            return instrBits + "11000100000000000000000000"
    
    if operands[0] =='#':
        flags += Ibit
        
    elif operands[0] =='@':
        flags += Nbit
    else:
        flags += Nbit + Ibit
        noIndex = False
    if isExtended(mnemonic):
        flags += Ebit
    if operands[-1] == 'X':
        if noIndex:
            error('Indexed addressing not supported with active I or N bits')
        flags += Xbit
        index = True
        operands = operands[0:-2]

    if not isSymbol(baseMnemonic(operands)):
        checkSym(baseMnemonic(operands))
        
    if addreLen==12: # if it is a length 3 instruction
        if operands[0] == '@' or index:
            symbol = operands.split(',')
            address = SYMTAB[baseMnemonic(symbol[0])]
            pci = False
            if((address-pc) > -2048 and  (address-pc) < 2047 ):
                flags += Pbit
                pci = True
                displ = address - pc

            elif not ISBASE:
                error('No BASE derective declared')
            elif address - BASE < 4095 and not pci:
                flags += Bbit
                displ = address - BASE
        
            else:
                error("Neither Base nor PC relative addressing was allowed " +
                "error with format 3 instruction")
        else:
            npb = False
            pci = False
            temp = False
            if isSymbol(baseMnemonic(operands)):
                address = SYMTAB[baseMnemonic(operands)]
                npb = True
            else:
                address = pc
            if npb:
                if (address-pc) > -2048 or (address- pc) > 2047:
                    flags += Pbit
                    pci = True

                elif not ISBASE:
                    error('No BASE derective declared')
            
                elif address - BASE < 4095 and not pci:
                    flags += Bbit
                    displ = address - BASE
                    temp = True
                else:
                    error("Neither Base nor PC relative addressing" +
                    "was allowed error with format 3 instruction")
            if not temp:
                if isSymbol(baseMnemonic(operands)):
                    displ = SYMTAB[baseMnemonic(operands)] - pc
                else:
                    displ = baseMnemonic(operands)
    
        return instrBits + toBitString(flags,6) + toBitString(displ,12)
        
    else: # if it is a length 4 instruction
        if isSymbol(baseMnemonic(operands)):
            displ = SYMTAB[baseMnemonic(operands)]
        else:
            displ = baseMnemonic(operands)
        return instrBits + toBitString(flags,6) + toBitString(displ,20)

def isSymbol(string):
    """ return True iff string is a key in Symtab """
    return string in SYMTAB.keys()

def isMnemonic(string):
    """return True if string is a key in MNEMONICS"""
    return string in MNEMONICS.keys()

def handle2(mnemonic,operands):
    opType = MNEMONICS[baseMnemonic(mnemonic)][3]
    rest1 = '0000'
    rest2 = '0000'
    if mnemonic == 'SVC':
        if operands > 15 or operands < 0:
            error('argument out of range for ' + mnemonic + '.')
        r1 = toBitString(makeLiteral(operands))
        r2 = '0000'
    if opType == ['r1','r2']:
        r1,r2 = operands.split(',')
        if not isRegister(r1):
            error('Invalid Register: ' + r1)
        if not isRegister(r2):
            error('Invalid Register: ' + r2)
        rest1 = toBitString(RegisterNumbers[r1],4)
        rest2 = toBitString(RegisterNumbers[r2],4)
    elif opType == ['r1','n']:
        r1,r2 = operands.split(',')
        if not isRegister(r1):
            error('Invalid Register: ' + r1)
        if mnemonic == 'SHIFTL' or mnemonic == 'SHIFTR':
            if int(r2) > 16 or int(r2) < 0:
                error('argument out of range for ' + mnemonic)
        rest1 = toBitString(RegisterNumbers[r1],4)
        
        rest2 = toBitString(int(r2) - 1,4)
    else:
        r1 = operands
        if not isRegister(r1):
            error('Invalid Register: ' + r1)
        rest1 = toBitString(RegisterNumbers[r1],4)
        rest2 = "0000"
    return (rest1 + rest2)

def isRegister(s):
    """Checks if register is a valid register"""
    return s in RegisterNumbers.keys()

def error(msg):
    """ print msg and abort the program """
    print msg
    sys.exit(-1)

def padHexEven(string):
    """ string is hexadecimal.  Prepend with '0' if its length is odd. """
    string = str(string)
    string = string[2:].title()
    if (len(string)%2):
        return '0'+string
    return string.title()


def isspace(c):
    """returns true if the char is a space """
    return c== ' ' or c=='\t' or c=='\n'

def isExtended(mnemonic):
    """return true iff this mnemonic begins with a '+'"""
    return mnemonic[0] == '+' or mnemonic[0] == '#' or mnemonic[0] == '@'

def baseMnemonic(mnemonic):
    """return the mnemonic with any leading + stripped off"""
    if isExtended(mnemonic):
        return mnemonic[1:]
    return mnemonic

def isCommentLine(line):
    return line[0] == '.'

def powSixteen(num, pow):
    """Multiplies an integer num by 16 to a given power """
    return (16 ** pow) * num

def oppositeBit(b):
    """b is a single char, 0 or 1. return the other."""
    if b == "1":
        return "0"
    return "1"

def checkHex(s):
    hexStr = "0123456789ABCDEF"
    for char in s:
        i = 0
        while char != hexStr[i] and i < len(hexStr):
            i += 1
            if i >= len(hexStr):
                error('Invalid Hex Character: ' + char)
    return

def resHex(digList):
    hexStr = "0123456789ABCDEF"
    print digList
    j = 0
    pow = len(digList) - 1
    baseTen = 0
    
    while j < len(digList):
        i = 0
        while hexStr[i] != str(digList[j]):
            i += 1
        hexVal = powSixteen(i,pow)
        baseTen += hexVal
        j += 1
        pow -= 1
    return baseTen


def makeLiteral(string):
    """Takes a string of chars or a hex str and returns hex representation"""

    chars = string.split("'")
    hexStr = "0123456789ABCDEF"
    
    if chars[0] == 'C':
        hexStr = ""
        value = 0
        for c in chars[1]:
            hexStr = hexStr + bitStr2Hex(toBitString(ord(c),2))
        return hexStr
    
    elif chars[0] == 'X':
        checkHex(chars[1])
        j = 0
        pow = len(chars[1]) - 1
        baseTen = 0
    
        while j < len(chars[1]):
            i = 0
            while hexStr[i] != chars[1][j]:
                i += 1
            hexVal = powSixteen(i,pow)
            baseTen += hexVal
            j += 1
            pow -= 1    
        return padHexEven(hex(baseTen).upper())
    return padHexEven(hex(int(string))).upper()

def padZero(s,num):
    """Places zeros on the front of a string."""
    zero = '0' * num
    return (zero + s)

def bitStr2Comp(bitstring):
    """Compute and return the 2's complement of bitstring"""
    bitList = []
    for bit in bitstring:
        bitList.append(oppositeBit(bit))
    bitstring = ""
    done = False
    for bit in bitList[::-1]:
        if bit == '0' and done == False:
            bitstring = '1' + bitstring
            done = True
        elif bit == '1' and done == False:
            bitstring = '0' + bitstring
        else:
            bitstring = bit + bitstring
    
    return bitstring

def toBitString(val,length):
    """My bit string function """
    bitString = ''
    val = int(val)
    i = length - 1
    neg = False
    if val < 0:
        val *= -1
        neg = True
    if val == '0':
        return padZero(bitString,length)
    while val > 0:
        bitString = str(val%2) + bitString
        val >>= 1
    bitString = padZero(bitString,(length - len(bitString)))
    if neg:
        bitString = bitStr2Comp(bitString)
    return bitString

    
def bitStr2Hex(bitstring):
    """return a hex representation of a bit string """
    number = 0
    for i,bit in enumerate(bitstring[::-1]):
        number += int(bit) * (2 ** i)
    return padHexEven(hex(number))

def hasNoArg(s):
    """Checks if given mnemonic takes an argument """
    for word in NOARG:
        if word == s:
            return True
    return False

def parseLine(line):

    if line[0] == '.':
        return ('','','')

    lineWords = line.split()

    label,mnemonic,arguments = ["","",""]
    if hasNoArg(baseMnemonic(lineWords[0])):
        return ("",lineWords[0],"")

    if not isspace(line[0]):
        if hasNoArg(baseMnemonic(lineWords[1])):
            label = lineWords[0]
            mnemonic = lineWords[1]
            arguments == ''
        else:
            label = lineWords[0]
            mnemonic = lineWords[1]
            arguments = lineWords[2]

    elif len(lineWords) == 1:
        return (lineWords[0], arguments, arguments)
    else:
        mnemonic = lineWords[0]
        arguments = lineWords[1]

    return (label,mnemonic,arguments)

def findDigs(operands):
    """Returns a list of the hex characters in the argument. Adapted from
    Professor Campbell's orginal makeLiteral. Only used for Hex arguments in
    RESB and RESW"""
    chars = operands.split("'")
    hdigs = chars[1]
    checkHex(hdigs)
    if len(hdigs)%2==1:    # if odd number of nibbles, 
        hdigs = '0'+hdigs     # add a leading zero.
    if len(hdigs) == 2:
        return eval("0x"+hdigs[0]+hdigs[1])
    return [eval("0x"+hdigs[i]+hdigs[i+1]) for i in range(0,len(chars),2)]

def handleDirective(mnemonic,operands):
    """Reserves the correct amount of space for a given directive """
    one = 1
    multiplier = 1
    if mnemonic == "RESW" or mnemonic == "WORD":
        multiplier = 3
    if mnemonic == 'RESW' or mnemonic == 'RESB':
        if operands[0] == 'X':
            test = findDigs(operands)
            if len(str(test)) == 1:
                operands = test
            else:
                operands = resHex(test)
            return operands * multiplier
    if mnemonic == "BYTE" or mnemonic == "WORD":
        if operands[0] == 'C':
            string = operands.split("'")
            return len(string[1])
        return multiplier
    return int(operands)* multiplier

def assembledLength(mnemonic,operands):
    offset = 0
    if not isMnemonic(baseMnemonic(mnemonic)):
        error('Invalid Mnemonic: ' + mnemonic)
    dictInfo = MNEMONICS[baseMnemonic(mnemonic)]    # Look up mnemonic in dict

    if dictInfo[0] == "D":
        if (mnemonic == "WORD" or mnemonic == "RESB" or
            mnemonic == "BYTE" or mnemonic == "RESW"):
            return handleDirective(mnemonic,operands)
        return offset
    else:
        offset = dictInfo[1]
        if isExtended(mnemonic):
            offset += 1

    return int(offset)

def main():
    file = open('hwtest.asm')
    lines = file.readlines()
    offset = 0
    lineData = []
    for i,line in enumerate(lines):
        if isCommentLine(line):
            continue
        
        label,mnemonic,arguments = parseLine(line) #Get individual line pieces

        if label != "": # Record symbols
            if isSymbol(label):
                error('Duplicate Label: ' + label)
            SYMTAB[label] = offset


        offset += assembledLength(mnemonic,arguments)
        
    for item in SYMTAB:
        key = SYMTAB[item]
        print "%s:\t%05X"%(item,key)

    curloc = 0
    pc = 0
    for line in lines:
        if isCommentLine(line):
            print line[:-1]
            continue
        label,mnemonic,arguments = parseLine(line) #Get individual line pieces
            
        pc += assembledLength(mnemonic,arguments)
        instr = makeInstruction(mnemonic,arguments,pc).upper()
        
        print "%05X\t%s\t%s\t%s\t%08s"%(curloc,label,mnemonic,arguments,instr)
        curloc += assembledLength(mnemonic,arguments)
main()


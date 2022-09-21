import re
def _parse_macros(self):
    self._open = []
    self._if_count = 0
    self._if_list = []
    self._loop_count = 0
    self._loop_list = []
    self._iter_lines(self._parse_loop_if)
    self._iter_lines(self._parse_macro)


def _parse_loop_if(self, line, p, o):
    mLOOP = re.search("^\$LOOP\((@\w+)\)$", line)
    mIF = re.search("^\$IF\((@\w+)\)$", line)
    
    check = (mIF == None, line != '{', line != '}', mLOOP == None)
    if all(check):
        return line
    
    if mLOOP:
        condition = mLOOP.group(1)
        self._loop_list.append(self._loop_count)
        self._open.append("LOOP")
        return f"(LOOP_START{self._loop_count})\n{condition}\nD=M\n@LOOP_END{self._loop_count}\nD;JEQ"
    if mIF:
        condition = mIF.group(1)
        self._if_list.append(self._if_count)
        self._open.append("IF")
        return f"{condition}\nD=M\n@IF_END{self._if_count}\nD;JNE"
    
    if line == '{':
        if len(self._open) == 0:
            self._flag = False
            self._line = o
            self._errm = "Syntax error"
        if self._open[-1] == "LOOP":
            self._loop_count += 1
        elif self._open[-1] == "IF":
            self._if_count += 1
        return ""
    
    if line == '}':
        if len(self._open) == 0:
            self._flag = False
            self._line = o
            self._errm = "Syntax error"
        if self._open[-1] == "LOOP":
            n = self._loop_list.pop()
            self._open.pop()
            return f"@LOOP_START{n}\n0;JMP\n(LOOP_END{n})"
        elif self._open[-1] == "IF":
            n = self._if_list.pop()
            self._open.pop()
            return f"(IF_END{self._if_count})"
        
    
def _parse_macro(self, line, p, o):
    if line[0] != "$":
        return line
    else:
        mLD = re.search("^\$LD\(@?(\w+),@?(\w+)\)$", line)
        mADD = re.search("^\$ADD\(@?(\w+),(\d+|@\w+|[ADM]),(\d+|@\w+|[ADM])\)$", line)
        mSUB = re.search("^\$SUB\(@?(\w+),(\d+|@\w+|[ADM]),(\d+|@\w+|[ADM])\)$", line)
        mSWAP = re.search("^\$SWAP\(@?(\w+),@?(\w+)\)$", line)
        mAND = re.search("^\$AND\(@?(\w+),(\d+|@\w+|[ADM]),(\d+|@\w+|[ADM])\)$", line)
        mOR = re.search("^\$OR\(@?(\w+),(\d+|@\w+|[ADM]),(\d+|@\w+|[ADM])\)$", line)
        mXOR = re.search("^\$XOR\(@?(\w+),(\d+|@\w+|[ADM]),(\d+|@\w+|[ADM])\)$", line)
        mNOT = re.search("^\$NOT\(@?(\w+),(\d+|@\w+|[ADM])\)$", line)
        if mLD:
            return f"@{mLD.group(2)}\nD=M\n@{mLD.group(1)}\nM=D"
        elif mADD:
            if mADD.group(2).isnumeric():
                if mADD.group(3).isnumeric():
                    return f"@{mADD.group(2)}\nD=A\n@{mADD.group(3)}\nD=D+A\n@{mADD.group(1)}\nM=D"
                elif re.match('@\w+', mADD.group(3)):
                    return f"@{mADD.group(2)}\nD=A\n{mADD.group(3)}\nD=D+M\n@{mADD.group(1)}\nM=D"
                else:
                    return f"D={mADD.group(3)}\n@{mADD.group(2)}\nD=D+A\n@{mADD.group(1)}\nM=D"
            elif mADD.group(3).isnumeric():
                if re.match('@\w+', mADD.group(2)):
                    return f"@{mADD.group(3)}\nD=A\n{mADD.group(2)}\nD=D+M\n@{mADD.group(1)}\nM=D"
                else:
                    return f"D={mADD.group(2)}\n@{mADD.group(3)}\nD=D+A\n@{mADD.group(1)}\nM=D"
            elif re.match('@\w+', mADD.group(2)):
                if re.match('@\w+', mADD.group(3)):
                    return f"{mADD.group(2)}\nD=M\n{mADD.group(3)}\nD=D+M\n@{mADD.group(1)}\nM=D"
                else:
                    return f"D={mADD.group(3)}\n{mADD.group(2)}\nD=D+M\n@{mADD.group(1)}\nM=D"
            elif re.match('@\w+', mADD.group(3)):
                return f"D={mADD.group(2)}\n{mADD.group(3)}\nD=D+M\n@{mADD.group(1)}\nM=D"
            elif mADD.group(3) == 'D':
                if mADD.group(2) == 'D':
                    return f"@{mADD.group(1)}\nM=D\nM=M+D"
                else:
                    return f"D=D+{mADD.group(2)}\n@{mADD.group(1)}\nM=D"
            else:
                return f"D={mADD.group(2)}\nD=D+{mADD.group(3)}\n@{mADD.group(1)}\nM=D"
        elif mSUB:
            if mSUB.group(3) == mSUB.group(2):
                return f"@{mSUB.group(1)}\nM=0"
            if mSUB.group(2).isnumeric():
                if mSUB.group(3).isnumeric():
                    return f"@{mSUB.group(2)}\nD=A\n@{mSUB.group(3)}\nD=D-A\n@{mSUB.group(1)}\nM=D"
                elif re.match('@\w+', mSUB.group(3)):
                    return f"@{mSUB.group(2)}\nD=A\n{mSUB.group(3)}\nD=D-M\n@{mSUB.group(1)}\nM=D"
                else:
                    return f"@{mSUB.group(2)}\nD=A\n@subVar\nM=D\nD={mSUB.group(3)}\nM=M-D\nD=M@{mSUB.group(1)}\nM=D"
            elif mSUB.group(3).isnumeric():
                if re.match('@\w+', mSUB.group(2)):
                    return f"{mSUB.group(2)}\nD=M\n@{mSUB.group(3)}\nD=D-A\n@{mSUB.group(1)}\nM=D"
                else:
                    return f"D={mSUB.group(2)}\n@{mSUB.group(3)}\nD=D-A\n@{mSUB.group(1)}\nM=D"
            elif re.match('@\w+', mSUB.group(2)):
                if re.match('@\w+', mSUB.group(3)):
                    return f"{mSUB.group(2)}\nD=M\n{mSUB.group(3)}\nD=D-M\n@{mSUB.group(1)}\nM=D"
                else:
                    return f"D={mSUB.group(3)}\n@subVar\nM=D\n{mSUB.group(2)}\nD=M\n@subVar\nM=D-M\nD=M\n@{mSUB.group(1)}\nM=D"
            elif re.match('@\w+', mSUB.group(3)):
                return f"D={mSUB.group(2)}\n{mSUB.group(3)}\nD=D-M\n@{mSUB.group(1)}\nM=D"
            elif mSUB.group(3) == 'D':
                return f"D={mSUB.group(2)}-D\n@{mSUB.group(1)}\nM=D"
            else:
                return f"D={mSUB.group(2)}\nD=D-{mSUB.group(3)}\n@{mSUB.group(1)}\nM=D"
        elif mSWAP:
            return f"@{mSWAP.group(1)}\nD=M\n@swap\nM=D\n@{mSWAP.group(2)}\nD=M\n@{mSWAP.group(1)}\nM=D\n@swap\nD=M\n@{mSWAP.group(2)}\nM=D"
        elif mAND:
            if mAND.group(2).isnumeric():
                if mAND.group(3).isnumeric():
                    return f"@{mAND.group(2)}\nD=A\n@{mAND.group(3)}\nD=D&A\n@{mAND.group(1)}\nM=D"
                elif re.match('@\w+', mAND.group(3)):
                    return f"@{mAND.group(2)}\nD=A\n{mAND.group(3)}\nD=D&M\n@{mAND.group(1)}\nM=D"
                else:
                    return f"D={mAND.group(3)}\n@{mAND.group(2)}\nD=D&A\n@{mAND.group(1)}\nM=D"
            elif mAND.group(3).isnumeric():
                if re.match('@\w+', mAND.group(2)):
                    return f"@{mAND.group(3)}\nD=A\n{mAND.group(2)}\nD=D&M\n@{mAND.group(1)}\nM=D"
                else:
                    return f"D={mAND.group(2)}\n@{mAND.group(3)}\nD=D&A\n@{mAND.group(1)}\nM=D"
            elif re.match('@\w+', mAND.group(2)):
                if re.match('@\w+', mAND.group(3)):
                    return f"{mAND.group(2)}\nD=M\n{mAND.group(3)}\nD=D&M\n@{mAND.group(1)}\nM=D"
                else:
                    return f"D={mAND.group(3)}\n{mAND.group(2)}\nD=D&M\n@{mAND.group(1)}\nM=D"
            elif re.match('@\w+', mAND.group(3)):
                return f"D={mAND.group(2)}\n{mAND.group(3)}\nD=D&M\n@{mAND.group(1)}\nM=D"
            elif mAND.group(3) == 'D':
                if mAND.group(2) == 'D':
                    return f"@{mAND.group(1)}\nM=D\nM=M&D"
                else:
                    return f"D=D&{mAND.group(2)}\n@{mAND.group(1)}\nM=D"
            else:
                return f"D={mAND.group(2)}\nD=D&{mAND.group(3)}\n@{mAND.group(1)}\nM=D"
        elif mOR:
            if mOR.group(2).isnumeric():
                if mOR.group(3).isnumeric():
                    return f"@{mOR.group(2)}\nD=A\n@{mOR.group(3)}\nD=D|A\n@{mOR.group(1)}\nM=D"
                elif re.match('@\w+', mOR.group(3)):
                    return f"@{mOR.group(2)}\nD=A\n{mOR.group(3)}\nD=D|M\n@{mOR.group(1)}\nM=D"
                else:
                    return f"D={mOR.group(3)}\n@{mOR.group(2)}\nD=D|A\n@{mOR.group(1)}\nM=D"
            elif mOR.group(3).isnumeric():
                if re.match('@\w+', mOR.group(2)):
                    return f"@{mOR.group(3)}\nD=A\n{mOR.group(2)}\nD=D|M\n@{mOR.group(1)}\nM=D"
                else:
                    return f"D={mOR.group(2)}\n@{mOR.group(3)}\nD=D|A\n@{mOR.group(1)}\nM=D"
            elif re.match('@\w+', mOR.group(2)):
                if re.match('@\w+', mOR.group(3)):
                    return f"{mOR.group(2)}\nD=M\n{mOR.group(3)}\nD=D|M\n@{mOR.group(1)}\nM=D"
                else:
                    return f"D={mOR.group(3)}\n{mOR.group(2)}\nD=D|M\n@{mOR.group(1)}\nM=D"
            elif re.match('@\w+', mOR.group(3)):
                return f"D={mOR.group(2)}\n{mOR.group(3)}\nD=D|M\n@{mOR.group(1)}\nM=D"
            elif mOR.group(3) == 'D':
                if mOR.group(2) == 'D':
                    return f"@{mOR.group(1)}\nM=D\nM=M|D"
                else:
                    return f"D=D|{mOR.group(2)}\n@{mOR.group(1)}\nM=D"
            else:
                return f"D={mOR.group(2)}\nD=D|{mOR.group(3)}\n@{mOR.group(1)}\nM=D"
        elif mXOR:   # A XOR B = (A OR B) AND (A NAND B)
            if mXOR.group(3) == mXOR.group(2):
                return f"@{mXOR.group(1)}\nM=0"
            if mXOR.group(2).isnumeric():
                if mXOR.group(3).isnumeric():
                    return f"@{mXOR.group(2)}\nD=A\n@{mXOR.group(3)}\nD=A|D\n@{mXOR.group(1)}\nM=D\n@{mXOR.group(2)}\nD=A\n@{mXOR.group(3)}\nD=A&D\nD=!D\n@{mXOR.group(1)}\nM=M&D"    
                elif re.match('@\w+', mXOR.group(3)):
                    return f"@{mXOR.group(2)}\nD=A\n{mXOR.group(3)}\nD=M|D\n@{mXOR.group(1)}\nM=D\n@{mXOR.group(2)}\nD=A\n{mXOR.group(3)}\nD=M&D\nD=!D\n@{mXOR.group(1)}\nM=M&D"
                else:
                    return f"D={mXOR.group(3)}\n@xor\nM=D\n@{mXOR.group(2)}\nD=D|A\n@{mXOR.group(1)}\nM=D\n@xor\nD=M\n@{mXOR.group(2)}\nD=D&A\nD=!D\n@{mXOR.group(1)}\nM=M&D"
            elif mXOR.group(3).isnumeric():
                if re.match('@\w+', mXOR.group(2)):
                    return f"@{mXOR.group(3)}\nD=A\n{mXOR.group(2)}\nD=M|D\n@{mXOR.group(1)}\nM=D\n@{mXOR.group(3)}\nD=A\n{mXOR.group(2)}\nD=M&D\nD=!D\n@{mXOR.group(1)}\nM=M&D"
                else:
                    return f"D={mXOR.group(2)}\n@xor\nM=D\n@{mXOR.group(3)}\nD=D|A\n@{mXOR.group(1)}\nM=D\n@xor\nD=M\n@{mXOR.group(3)}\nD=D&A\nD=!D\n@{mXOR.group(1)}\nM=M&D"
            elif re.match('@\w+', mXOR.group(2)):
                if re.match('@\w+', mXOR.group(3)):
                    return f"{mXOR.group(2)}\nD=M\n{mXOR.group(3)}\nD=M|D\n@{mXOR.group(1)}\nM=D\n{mXOR.group(2)}\nD=M\n{mXOR.group(3)}\nD=M&D\nD=!D\n@{mXOR.group(1)}\nM=M&D"
                else:
                    return f"D={mXOR.group(3)}\n@xor\nM=D\n{mXOR.group(2)}\nD=D|M\n@{mXOR.group(1)}\nM=D\n@xor\nD=M\n{mXOR.group(2)}\nD=D&M\nD=!D\n@{mXOR.group(1)}\nM=M&D"
            elif re.match('@\w+', mXOR.group(3)):
                return f"D={mXOR.group(2)}\n@xor\nM=D\n{mXOR.group(3)}\nD=D|M\n@{mXOR.group(1)}\nM=D\n@xor\nD=M\n{mXOR.group(3)}\nD=D&M\nD=!D\n@{mXOR.group(1)}\nM=M&D"
        elif mNOT:
            if mNOT.group(2).isnumeric():
                return f"@{mNOT.group(2)}\nD=!A\n@{mNOT.group(1)}\nM=D"
            elif re.match('@\w+', mNOT.group(2)):
                return f"{mNOT.group(2)}\nD=!M\n@{mNOT.group(1)}\nM=D"
            else:
                return f"D=!{mNOT.group(2)}\n@{mNOT.group(1)}\nM=D"
        else:
            self._flag = False
            self._line = o
            self._errm = "Macro non-existent"
            return ""


















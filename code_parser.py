
import re
import math

bracket_pairs = {}
bracket_pairs["("] = ")"
bracket_pairs["["] = "]"
bracket_pairs["{"] = "}"
bracket_pairs[")"] = "("
bracket_pairs["]"] = "["
bracket_pairs["}"] = "{"


class CodeParser:


    def __init__(self, filepath, create_maps=False):
        self.create_maps = create_maps
        self.brackets_stack = []
        self.skip_stack = []
        self.filepath = filepath
        self.binary_operators = ["and", "or", ">=", "<=", "==", "<", ">", "!=", "<>"]
        self.sensitivity_list = ["'", '"', '"""', "#", "\n", "\t", "{", "}", "(", ")", "[", "]"]
        with open(filepath, "r") as file_handle:
            self.file_text = file_handle.readlines()

    def skippable(self):
        pass

    def recursive_split(self, line, length, char = " "):
        if (len(line) < length):
            return line
        else:
            split_point = line[0:length].rfind(char)
            print(split_point)
            if (split_point == -1):
                split_point = length
            print(split_point)
            print("".join(line[0:split_point]))
            return "".join(line[0:split_point]) + "$-$" + "".join(self.recursive_split(line[split_point+1:], length))

    def create_skip_map(self):
        self.skip_map = []
        for line in self.file_text:
            line_skip_map = []
            multiline_counter = 0
            for (idx, char) in enumerate(line):
                if (char in ["'", '"', "#"] and self.skip_stack == []):
                    if (line.find('"""') == idx and char == '"'):
                        self.skip_stack.append('"""')
                        multiline_counter = 3
                    else:
                        self.skip_stack.append(char)
                elif (char in ["'", '"', "\n"] and self.skip_stack != []):
                    if (line.find('"""') == idx and char == '"' and '"""' in self.skip_stack):
                        line_skip_map.append("M")
                        continue
                    elif (line.find('"""') == idx - 1 and char == '"' and '"""' in self.skip_stack):
                        line_skip_map.append("M")
                        continue
                    elif (line.find('"""') == idx - 2 and char == '"' and '"""' in self.skip_stack and multiline_counter == 0):
                        self.skip_stack = []
                        line_skip_map.append("M")
                        continue
                    elif (char in self.skip_stack):
                        self.skip_stack = []
                        line_skip_map.append(char)
                        continue
                    elif (char == "\n" and "#" in self.skip_stack):
                        self.skip_stack = []
                        line_skip_map.append("T")
                        continue
                if (multiline_counter > 0):
                    multiline_counter -= 1
                if ('"""' in self.skip_stack):
                    line_skip_map.append("M")
                elif (self.skip_stack != []):
                    line_skip_map.append(self.skip_stack[0])
                elif (self.skip_stack == []):
                    line_skip_map.append("T")
            self.skip_map.append(line_skip_map)
    
    def create_brackets_map(self):
        self.bracket_map = []
        for line, skip_line in zip(self.file_text, self.skip_map):
            line_bracket_map = []
            for (idx, char) in enumerate(line):
                if (char in ["(", '[', "{"] and skip_line[idx]):
                    self.brackets_stack.append(char)
                elif (char in [")", ']', "}"] and skip_line[idx]):
                    if (self.brackets_stack[-1] == bracket_pairs[char]):
                        del self.brackets_stack[-1]
                        line_bracket_map.append(False)
                        continue
                if (self.brackets_stack != []):
                    line_bracket_map.append(False)
                elif (self.brackets_stack == []):
                    line_bracket_map.append(True)
            self.bracket_map.append(line_bracket_map)

    def test_skip_map(self):
        c = 0
        file_handle = open(self.filepath.replace(".py", "_test_skip_map.txt"), "w")
        for line1, line2 in zip(self.skip_map, self.file_text):
            c += 1
            if len(line1) != len(line2):
                print("Error in skip map, line:", c)
            else:
                print("OK", c)
        tt = []
        for i, l in enumerate(self.skip_map, 1):
            print(i, l, len(l))
            t = []
            for c in l:
                if(c):
                    t.append(c)
                else:
                    t.append(c)
            t.append("\n")
            tt.append("".join(t))
        file_handle.writelines(tt)
        file_handle.close()

    def test_bracket_map(self):
        c = 0
        file_handle = open(self.filepath.replace(".py", "_test_bracket_map.txt"), "w")
        for line1, line2 in zip(self.bracket_map, self.file_text):
            c += 1
            if len(line1) != len(line2):
                print("Error in skip map, line:", c)
            else:
                print("OK", c)
        tt = []
        for i, l in enumerate(self.bracket_map, 1):
            print(i, l, len(l))
            t = []
            for c in l:
                if (c):
                    t.append("T")
                else:
                    t.append("F")
            t.append("\n")
            tt.append("".join(t))
        file_handle.writelines(tt)
        file_handle.close()
    
    def parse_import(self):
        ft = []
        c = 0
        for idx, (skip, bracket, line) in enumerate(zip(self.skip_map, self.bracket_map, self.file_text)):
            if (re.search("#imp_skip", line) != None):
                ft.append(line)
            elif (re.search("^( )*from.*import.*as.*", line) != None and skip[line.find("from")] == "T"):
                n = line.count(",")/2
                new_lines = []
                if (n > 0):
                    slice_0 = line.find("from ") + 4
                    slice_1 = line.find(" import ") + 8
                    slice_2 = line.find(" as ") + 4
                    for s1,s2 in zip("".join(line[slice_1:slice_2-4]).split(","), "".join(line[slice_2:-1]).split(",")):
                        new_lines.append("from " + "".join(line[slice_0:slice_1-8]).replace(" ", "") + " import " + s1.replace(" ", "") + " as " + s2.replace(" ", "") + "\n")
                else:
                    new_lines.append(line)
                print(new_lines)
                if(idx >= c):
                    for l in new_lines:
                        ft.insert(c, re.sub("^( )*", "", l))
                        c += 1
                else:
                    for l in new_lines:
                        ft.append(re.sub("^( )*", "", l))
                        c += 1
            elif (re.search("^( )*import.*as.*", line) != None and skip[line.find("from")] == "T"):
                n = line.count(",")/2
                new_lines = []
                if (n > 0):
                    slice_1 = line.find("import ") + 7
                    slice_2 = line.find(" as ") + 3
                    for s1,s2 in zip("".join(line[slice_1:slice_2-3]).split(","), "".join(line[slice_2:-1]).split(",")):
                        new_lines.append("import " + s1.replace(" ", "") + " as " + s2.replace(" ", "") + "\n")
                else:
                    new_lines.append(line)
                print(new_lines)
                if(idx >= c):
                    for l in new_lines:
                        ft.insert(c, re.sub("^( )*", "", l))
                        c += 1
                else:
                    for l in new_lines:
                        ft.append(re.sub("^( )*", "", l))
                        c += 1            
            elif (re.search("^( )*import", line) != None and skip[line.find("import")] == "T"):
                if(idx > c):
                    ft.insert(c, re.sub("^( )*", "", line))
                else:
                    ft.append(re.sub("^( )*", "", line))
                c += 1
            elif (re.search("^( )*from.*import.*", line) != None and skip[line.find("from")] == "T"):
                n = line.count(",")
                new_lines = []
                if (n > 0):
                    slice_1 = line.find("import ") + 7
                    for s in "".join(line[slice_1:]).split(","):
                        new_lines.append("import" + s.replace(" ", "" + "\n"))
                else:
                    new_lines.append(line)
                if(idx >= c):
                    for l in new_lines:
                        ft.insert(c, re.sub("^( )*", "", l))
                        c += 1
                else:
                    for l in new_lines:
                        ft.append(re.sub("^( )*", "", l))
                        c += 1  
            else:
                ft.append(line)
        self.file_text = ft

    def parse_whitespace(self):
        ft = []
        for idx, (skip, bracket, line) in enumerate(zip(self.skip_map, self.bracket_map, self.file_text)):
            line2list = list(line)
            new_line = []
            skip_next = False
            for i,(char, char_next) in enumerate(zip(line2list[:-1], line2list[1:])):
                if (skip_next):
                    skip_next = False
                    continue
                if ("".join(char+char_next) == "+=" and skip[i] == "T" and bracket[i] == True):
                    if(line2list[i-1] != " "):
                        new_line.append(" ")
                    new_line.append(char)
                    new_line.append(char_next)
                    if(line2list[i+2] != " "):
                        new_line.append(" ")
                    skip_next = True                    
                elif (char == "=" and skip[i] == "T" and bracket[i] == True):                    
                    if(line2list[i-1] != " "):
                        new_line.append(" ")
                    new_line.append(char)
                    if(line2list[i+1] != " "):
                        new_line.append(" ")
                elif (char == "=" and skip[i] == "T" and bracket[i] == False):                    
                    if(new_line[-1] == " "):
                        del new_line[-1]
                    new_line.append(char)
                    if(line2list[i+1] == " "):
                        skip_next = True
                elif (char == "+" and skip[i] == "T" and bracket[i] == True):
                    if(line2list[i-1] != " "):
                        new_line.append(" ")
                    new_line.append(char)
                    if(line2list[i+1] != " "):
                        new_line.append(" ")
                elif (char == "," and skip[i] == "T" and bracket[i] == False):
                    if(new_line[-1] == " "):
                        del new_line[-1]
                    new_line.append(char)
                    if(line2list[i+1] != " "):
                        new_line.append(" ")
                elif (char == "," and skip[i] == "T" and bracket[i] == True and re.search("^(import)", line)):
                    pass
                elif (char == "#" and skip[i] == "T" and bracket[i] == True):
                    new_line.append(char)
                    if(line2list[i+1] != " "):
                        new_line.append(" ")
                else:
                    new_line.append(char)
            ft.append("".join(new_line+["\n"]))
        self.file_text = ft

    def parse_newline(self):
        ft = []
        skip_next = 0
        for idx, (skip, bracket, line) in enumerate(zip(self.skip_map, self.bracket_map, self.file_text)):
            if (skip_next > 0):
                skip_next -= 1
            if (re.search("^( )*def (.)+\(.*\):", line)  != None and skip_next == 0):
                if (re.search("^( )*\n", self.file_text[idx-1]) == None):
                    ft.append("\n")
                ft.append(line)
                if (re.search("^( )*\n", self.file_text[idx+1]) == None):
                    ft.append("\n")
                skip_next = 1
            elif (re.search("^( )*class (.)+\(?.*\)?:", line)  != None and skip_next == 0):
                if (re.search("^( )*\n", self.file_text[idx-2]) == None):
                    ft.append("\n")
                if (re.search("^( )*\n", self.file_text[idx-1]) == None):
                    ft.append("\n")
                ft.append(line)
                if (re.search("^( )*\n", self.file_text[idx+1]) == None):
                    ft.append("\n")
                if (re.search("^( )*\n", self.file_text[idx+2]) == None):
                    ft.append("\n")
                skip_next = 2
            elif (re.search("^( )*\n", line)  != None and re.search("^( )*\n", self.file_text[idx-1]) != None and skip_next == 0):
                if (re.search("^( )*class (.)+\(?.*\)?:", self.file_text[idx+1]) != None):
                    ft.append(line)
            else:
                ft.append(line)
        self.file_text = ft
    
    def parse_max_length(self):
        ft = []
        for idx, (skip, bracket, line) in enumerate(zip(self.skip_map, self.bracket_map, self.file_text)):
            if (len(line) >= 72 and re.search("^#", line)):
                for l in self.recursive_split(line[1:-1], 72).split("$-$"):
                    ft.append("# " + l + "\n")
            elif (len(line) > 72 and skip[72] == "M"):
                for l in self.recursive_split(line[0:-1], 72).split("$-$"):
                    ft.append(l + "\n")
            elif (len(line) > 79 and (skip[79] == "T" or skip[79] == '"') and bracket.count(False) > 40):
                start = bracket.index(False)
                # Ovdje bi stvarno bilo korisno da postoji način za očitati unutar koje zagrade se nalazi
                # Nije problem reworkat dio koji radi bracket_map ali onda je potrebno i dosta drugih koji ovise o bracket_map
                # Za proof of koncept samo se linija prelama unutar ()
                # Naravno da mogu copy pasteat ovaj elif blok i malo prilagoditi kod za svaku zagradu ali bi bilo bolje rješiti korijen problema
                if (not all(bracket[start:-1])):
                    size = len(line[start:-1].split(","))                  
                    for (i,l) in enumerate(line[start:-1].split(","), 1):
                        if (i == 1):
                            ft.append(line[:start] + l + ",\n")
                        elif (i == size):
                            ft.append(" "*start + l + "\n")
                        else:
                            ft.append(" "*start + l + ",\n")
            elif (len(line) > 79 and (skip[79] == "T" or skip[79] == '"')):
                lines = self.recursive_split(line[0:-1], 79).split("$-$")
                for (i,l) in enumerate(lines, 1):
                    if (i == 1):
                        ft.append(l + "\\\n")
                        start = len(l)
                    elif (i == len(lines)):
                        ft.append(" "*start + l + "\n")
                    else:
                        ft.append(" "*start + l + "\\\n")
            else:
                ft.append(line)
        self.file_text = ft

    def parse_tab(self):
        ft = []
        for skip, _, line in zip(self.skip_map, self.bracket_map, self.file_text):
            indices = [i for i, x in enumerate(line) if x == "\t"]
            for i in indices:
                if (re.search("^( )*\t", line) != None and skip[i] == "T"):
                    line = re.sub("\t", "    ", line, 1)
            ft.append(line)
        self.file_text = ft

    def parse_all(self):
        self.create_skip_map()
        self.create_brackets_map()

        self.parse_tab()
        self.create_skip_map()
        self.create_brackets_map()

        self.parse_import()
        self.create_skip_map()
        self.create_brackets_map()

        self.parse_max_length()
        self.create_skip_map()
        self.create_brackets_map()

        self.parse_newline()
        self.create_skip_map()
        self.create_brackets_map()

        self.parse_whitespace()
        self.create_skip_map()
        self.create_brackets_map()

        self.file_save()
        if(self.create_maps):
            self.test_skip_map()
            self.test_bracket_map()

    def file_save(self):
        fh = open(self.filepath.replace(".py", "_PEP8.txt"), "w")
        fh.writelines(self.file_text)
        fh.close()

# cp = CodeParser("D:/PythonProjects/PEP8CodeReview/test_folder/test2.py")
# cp.create_skip_map()
# cp.create_brackets_map()

# cp.parse_tab()
# cp.create_skip_map()
# cp.create_brackets_map()

# cp.parse_import()
# cp.create_skip_map()
# cp.create_brackets_map()

# cp.parse_max_length()
# cp.create_skip_map()
# cp.create_brackets_map()

# cp.parse_newline()
# cp.create_skip_map()
# cp.create_brackets_map()

# cp.parse_whitespace()
# cp.create_skip_map()
# cp.create_brackets_map()

# cp.file_save()
# cp.test_skip_map()
# cp.test_bracket_map()

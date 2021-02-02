
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
    
    def __init__(self, filepath):
        self.is_inside_line_comment = False
        self.is_inside_multiline_comment = False
        self.is_inside_string1 = False
        self.is_inside_string2 = False
        self.brackets_stack = []
        self.skip_stack = []
        self.filepath = filepath
        self.binary_operators = ["and", "or", ">=", "<=", "==", "<", ">", "!=", "<>"]
        self.sensitivity_list = ["'", '"', '"""', "#", "\n", "\t", "{", "}", "(", ")", "[", "]"]
        with open(filepath, "r") as file_handle:
            self.file_text = file_handle.readlines()

    def skippable(self):
        return any([self.is_inside_line_comment, self.is_inside_multiline_comment, self.is_inside_string1, self.is_inside_string2])

    def recursive_split(self, line, length):
        if (len(line) < length):
            return line
        else:
            split_point = line[0:length].rfind(" ")
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
            if (re.search("^import", line) != None and skip[line.find("import")] == "T"):
                if(idx > c):
                    ft.insert(c, line)
                else:
                    ft.append(line)
                c += 1
            elif (re.search("^( )*import", line) != None and skip[line.find("import")] == "T"):
                if(idx > c):
                    ft.insert(c, re.sub("^( )*", "", line))
                else:
                    ft.append(re.sub("^( )*", "", line))
                c += 1
            elif (re.search("^from.*import.*", line) != None and skip[line.find("from")] == "T"):
                if(idx > c):
                    ft.insert(c, line)
                else:
                    ft.append(line)
                c += 1
            elif (re.search("^( )*from.*import.*", line) != None and skip[line.find("from")] == "T"):
                if(idx > c):
                    ft.insert(c, re.sub("^( )*", "", line))
                else:
                    ft.append(re.sub("^( )*", "", line))
                c += 1
            else:
                ft.append(line)
        self.file_text = ft
        ft = []
        for idx, (skip, bracket, line) in enumerate(zip(self.skip_map, self.bracket_map, self.file_text)):
            if (re.search("^import .*,", line) != None and skip[line.find("import")] == "T"):
                if(idx > c):
                    ft.insert(c, line)
                else:
                    ft.append(line)
                c += 1

    def parse_whitespace(self):
        pass

    def parse_newline(self):
        pass
    
    def parse_max_length(self):
        ft = []
        for idx, (skip, bracket, line) in enumerate(zip(self.skip_map, self.bracket_map, self.file_text)):
            if (len(line) >= 72 and re.search("^#", line)):
                for l in self.recursive_split(line[1:-1], 72).split("$-$"):
                    print(l)
                    ft.append("# " + l + "\n")
            elif (len(line) > 72):
                print(skip)
                print(line)
                if (skip[72] == "M"):
                    for l in self.recursive_split(line[0:-1], 72).split("$-$"):
                        print(l)
                        ft.append(l + "\n")
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
        pass

    def file_save(self):
        fh = open(self.filepath.replace(".py", "_PEP8.txt"), "w")
        fh.writelines(self.file_text)

cp = CodeParser("D:/PythonProjects/PEP8CodeReview/test_folder/test2.py")
cp.create_skip_map()
cp.create_brackets_map()
#print(cp.file_text)
#cp.test_skip_map()
#cp.test_bracket_map()
cp.parse_tab()
cp.test_skip_map()
cp.create_skip_map()
cp.create_brackets_map()
cp.test_skip_map()
cp.parse_import()
cp.create_brackets_map()
cp.create_skip_map()
cp.test_skip_map()
cp.test_bracket_map()
cp.parse_max_length()
cp.file_save()
for x, (y, z) in enumerate(zip(["a","d","w","s"], [9,8,6,5])):
    print(x)

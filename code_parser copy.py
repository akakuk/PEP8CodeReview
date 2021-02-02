
class CodeParser:
    
    def __init__(self, filepath):
        self.is_inside_line_comment = False
        self.is_inside_multiline_comment = False
        self.is_inside_string1 = False
        self.is_inside_string2 = False
        self.brackets_stack = []
        self.sensitivity_list = ["'", '"', '"""', "#", "\n", "\t", "{", "}", "(", ")", "[", "]"]
        with open(filepath, "r") as file_handle:
            self.file_text = file_handle.readlines()

    def skippable(self):
        return any([self.is_inside_line_comment, self.is_inside_multiline_comment, self.is_inside_string1, self.is_inside_string2])

    def parse_import(self):
        self.skip_map = []
        self.bracket_map = []
        for line in self.file_text:
            for (idx, char) in enumerate(line):
                if (char in self.sensitivity_list):
                    if (char == "'" and self.is_inside_string1 and not self.skippable()):
                        self.is_inside_string1 = False
                    elif (char == "'" and not self.is_inside_string1 and not self.skippable()):
                        self.is_inside_string1 = True
                    elif (char == '"' and self.is_inside_string2 and not self.skippable()):
                        if (line.find('"""') == idx):
                            self.is_inside_multiline_comment = False
                    elif (char == '"' and not self.is_inside_string2 and not self.skippable()):
                        self.is_inside_string2 = True
                    elif (char == '"' and self.is_inside_string2 and not self.skippable()):
                        self.is_inside_string2 = False
                    elif (char == '"' and not self.is_inside_string2 and not self.skippable()):
                        self.is_inside_string2 = True
                    elif (char == '"' and self.is_inside_string2 and not self.skippable()):
                        self.is_inside_string2 = False
                    elif (char == '"' and not self.is_inside_string2 and not self.skippable()):
                        self.is_inside_string2 = True
    def parse_whitespace(self):
        pass

    def parse_newline(self):
        pass
    
    def parse_max_length(self):
        pass

    def parse_tab(self):
        for line in self.file_text:
    
    def parse_all(self):
        pass

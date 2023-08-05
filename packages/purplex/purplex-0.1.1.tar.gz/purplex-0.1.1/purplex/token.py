import re


class TokenDef(object):
    def __init__(self, regexp, ignore=False):
        self.regexp = re.compile(regexp, re.UNICODE)
        self.ignore = ignore


class Token(object):
    def __init__(self, name, value, defn, line_num, line_pos):
        self.name = name
        self.value = value
        self.defn = defn
        self.line_num = line_num
        self.line_pos = line_pos

        # For compatibility with yacc
        self.type = name

    def __str__(self):
        return '{}({})<line {}, col {}>'.format(self.name, repr(self.value),
                                                self.line_num, self.line_pos)

    def __len__(self):
        return len(self.value)

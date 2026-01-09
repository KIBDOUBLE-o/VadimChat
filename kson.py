import re
from io import TextIOWrapper
import json


class Kson(dict):
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(item)

    def __setattr__(self, key, value):
        self[key] = value

    def keys(self) -> list:
        return list(super().keys())

    @staticmethod
    def load(f: TextIOWrapper, req_comma=True) -> 'Kson':
        return KsonParser(f.read()).parse(req_comma)

    @staticmethod
    def loads(data: str, req_comma=True) -> 'Kson':
        return KsonParser(data).parse(req_comma)

    def to_json(self) -> str:
        return json.dumps(super())


class KsonParser:
    def __init__(self, text: str):
        self.text = self._strip_comments(text)
        self.pos = 0
        self.length = len(self.text)

    # ---------- public ----------
    def parse(self, req_comma=True) -> Kson:
        result = Kson()
        first = True
        while self._skip_ws():
            if not first:
                matched = self._match(',')
                if req_comma and not matched:
                    raise SyntaxError("Expected ',' between root entries")
            first = False

            key = self._parse_identifier()
            self._skip_ws()
            self._expect('=', ':')
            self._skip_ws()
            value = self._parse_value(req_comma)
            result[key] = value
            self._skip_ws()
        return result

    # ---------- value ----------
    def _parse_value(self, req_comma=True):
        if self._peek() == '{':
            return self._parse_object(req_comma)
        if self._peek() == '[':
            return self._parse_array(req_comma)
        if self._peek() == '"':
            return self._parse_string()
        if self._peek() == "'":
            return self._parse_single_string()
        if self._peek().isdigit() or self._peek() == '-':
            return self._parse_number()

        ident = self._parse_identifier()
        if ident == 'true':
            return True
        if ident == 'false':
            return False
        if ident == 'null':
            return None

        raise SyntaxError(f"Unknown value: {ident}")

    # ---------- object ----------
    def _parse_object(self, req_comma=True):
        obj = {}
        self._expect('{')
        first = True
        while self._skip_ws():
            if self._peek() == '}':
                break
            if not first:
                matched = self._match(',')
                if req_comma and not matched:
                    raise SyntaxError("Expected ',' between object entries")
            first = False

            key = self._parse_identifier()
            self._skip_ws()
            self._expect(':', '=')
            self._skip_ws()
            obj[key] = self._parse_value()
            self._skip_ws()
        self._expect('}')
        return obj

    # ---------- array ----------
    def _parse_array(self, req_comma=True):
        arr = []
        self._expect('[')
        first = True
        while self._skip_ws():
            if self._peek() == ']':
                break
            if not first:
                matched = self._match(',')
                if req_comma and not matched:
                    raise SyntaxError("Expected ',' between array items")
            first = False

            arr.append(self._parse_value())
            self._skip_ws()
        self._expect(']')
        return arr

    # ---------- primitives ----------
    def _parse_string(self):
        self._expect('"')
        start = self.pos
        while self.text[self.pos] != '"':
            if self.text[self.pos] == '\\':
                self.pos += 2
            else:
                self.pos += 1
        s = self.text[start:self.pos]
        self.pos += 1
        return bytes(s, "utf-8").decode("unicode_escape")

    def _parse_single_string(self):
        self._expect("'")
        start = self.pos
        while self.text[self.pos] != "'":
            if self.text[self.pos] == '\\':
                self.pos += 2
            else:
                self.pos += 1
        s = self.text[start:self.pos]
        self.pos += 1
        return bytes(s, "utf-8").decode("unicode_escape")

    def _parse_bare_string(self):
        start = self.pos
        while self.pos < self.length and self.text[self.pos] not in r",}\]\n\r":
            self.pos += 1
        return self.text[start:self.pos].strip()

    def _parse_number(self):
        start = self.pos
        while self.pos < self.length and re.match(r'[0-9eE\+\-\.]', self.text[self.pos]):
            self.pos += 1
        num = self.text[start:self.pos]
        return float(num) if '.' in num or 'e' in num.lower() else int(num)

    def _parse_identifier(self):
        start = self.pos
        if not re.match(r'[A-Za-z_]', self._peek()):
            raise SyntaxError("Expected identifier")
        while self.pos < self.length and re.match(r'[A-Za-z0-9_]', self.text[self.pos]):
            self.pos += 1
        return self.text[start:self.pos]

    # ---------- utils ----------
    def _strip_comments(self, text):
        text = re.sub(r'//.*', '', text)
        text = re.sub(r'#.*', '', text)
        return text

    def _skip_ws(self):
        while self.pos < self.length and self.text[self.pos].isspace():
            self.pos += 1
        return self.pos < self.length

    def _peek(self):
        return self.text[self.pos]

    def _expect(self, *chars):
        if self.text[self.pos] not in chars:
            raise SyntaxError(f"Expected one of {chars}")
        self.pos += 1

    def _match(self, char):
        if self.pos < self.length and self.text[self.pos] == char:
            self.pos += 1
            return True
        return False
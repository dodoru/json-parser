from enum import Enum


class TokenType(Enum):
    colon = 1  # :
    comma = 2  # ,
    braceLeft = 3  # {
    braceRight = 4  # }
    bracketLeft = 5  # [
    bracketRight = 6  # ]
    number = 7  # 123
    string = 8  # "name"
    true = 8  # True
    false = 9  # False
    null = 10  # None


class Token(object):
    is_valid = True

    def __init__(self, _type, value):
        super(Token, self).__init__()
        self.type = _type
        self.value = value

    def __repr__(self):
        return '({})'.format(self.value)


class TokenSeparator(Token):
    is_valid = False

    _map_type = {
        ':': TokenType.colon,
        ',': TokenType.comma,
        '{': TokenType.braceLeft,
        '}': TokenType.braceRight,
        '[': TokenType.bracketLeft,
        ']': TokenType.bracketRight,
    }

    def __init__(self, value):
        _type = self._map_type[value]
        super(TokenSeparator, self).__init__(_type, value)


class TokenString(Token):
    # 支持转义符 \t \n " \\ (分别表示 tab 回车 " \)
    _map_escape = {
        '\\n': '\n',
        '\\t': '\t',
        '\\"': '"',
        "\\'": "'",
        '\\\\': '\\',
        '\\\/': '\/',
        '\\b': '\b',
        '\\f': '\f',
        # 'u': '\u',
    }

    @classmethod
    def seek(cls, text, index=0):
        offset = index
        s = ''
        while offset < len(text):
            c = text[offset]
            offset += 1
            if c == '"':
                # 找到了字符串的结尾
                tk = cls(TokenType.string, s)
                return tk, offset
            elif c == '\\':
                c += text[offset + 1]
                v = cls._map_escape.get(c)
                if v is not None:
                    offset += 1
                    s += v
                else:
                    # 这是一个错误, 非法转义符
                    raise ValueError('[4001]invalid escape character at<{}>'.format(k))
            else:
                s += c
        # 程序出错, 没有找到反引号 "
        raise ValueError('[4002]invalid string parse at<{}>'.format(text))


class TokenKeyword(Token):
    _map = dict(
        null=Token(TokenType.null, None),
        true=Token(TokenType.true, True),
        false=Token(TokenType.false, False),
    )

    @classmethod
    def seek(cls, text, index=0):
        for k, tk in cls._map.items():
            if text[index:].startswith(k):
                offset = index + len(k)
                return tk, offset


class TokenNumber(Token):
    @classmethod
    def seek(cls, text, index=0):
        for i, c in enumerate(text[index:]):
            if not c.isdigit():
                offset = index + i
                s = text[index: offset]
                tk = cls(TokenType.number, int(s))
                return tk, offset


def json_tokens(text):
    length = len(text)
    tokens = []
    i = 0
    while i < length:
        c = text[i]
        i += 1
        if c.isspace():
            # 空白符号要跳过, space tab return
            continue
        elif c in '::,{}[]':
            # 处理 6 种单个符号
            t = TokenSeparator(c)
            tokens.append(t)
        elif c == '"':
            # 处理字符串
            t, i = TokenString.seek(text, i)
            tokens.append(t)
        elif c.isdigit():
            # 处理数字, 现在不支持小数和负数
            t, i = TokenNumber.seek(text, i - 1)
            tokens.append(t)
        else:
            m = TokenKeyword.seek(text, i - 1)
            if m is not None:
                t, i = m
                tokens.append(t)
            else:
                raise ValueError('[4000] json tokens error')
    return tokens


class JsonParser(object):
    # JSON 解释器
    def __init__(self, tokens):
        self._tokens = tokens
        self._index = 0
        self._length = len(self._tokens)

    def cursor(self):
        return self._tokens[self._index]

    def _parse(self):
        tk = self.cursor()
        self._index += 1
        if tk.is_valid:
            return tk.value
        elif tk.type == TokenType.braceLeft:
            return self._parse_object()
        elif tk.type == TokenType.bracketLeft:
            return self._parse_array()
        else:
            raise ValueError('[2000] invalid json parse')

    def _parse_object(self):
        data = {}
        while self._index < self._length - 1:
            tk = self.cursor()
            if isinstance(tk, TokenString):
                # JSON要求字典键值，必须是字符串
                self._index += 1
                q = self.cursor()
                if q.type == TokenType.colon:
                    k = tk.value
                    # 键值和冒号后，取对象值
                    self._index += 1
                    data[k] = self._parse()
                else:
                    raise ValueError('[2001] invalid json parse object')
            elif tk.type == TokenType.comma:
                self._index += 1
            elif tk.type == TokenType.braceRight:
                self._index += 1
                return data
            else:
                raise ('[2002] invalid json parse object')
        return data

    def _parse_array(self):
        data = []
        while self._index < self._length - 1:
            tk = self.cursor()
            if tk.type == TokenType.bracketRight:
                self._index += 1
                return data
            elif tk.type == TokenType.comma:
                self._index += 1
            else:
                m = self._parse()
                data.append(m)
        return data

    @classmethod
    def parse(cls, tokens):
        count = len(tokens)
        tk = tokens[0]
        if count == 1 and not tk.is_valid:
            raise ValueError('[1000] invalid json tokens', tokens)
        else:
            m = cls(tokens)._parse()
            return m

    @classmethod
    def loads(cls, text):
        tokens = json_tokens(text)
        data = cls.parse(tokens)
        return data

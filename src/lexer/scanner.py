from typing import List, Optional
import re
from .token import Token, TokenType
from .error import ErrorHandler

class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0          # Начало текущего лексемы
        self.current = 0        # Текущая позиция
        self.line = 1            # Текущая строка
        self.column = 1          # Текущая колонка
        self.errors = ErrorHandler()
        
        # Таблица ключевых слов для быстрого поиска
        self.keywords = {
            'if': TokenType.KW_IF,
            'else': TokenType.KW_ELSE,
            'while': TokenType.KW_WHILE,
            'for': TokenType.KW_FOR,
            'int': TokenType.KW_INT,
            'float': TokenType.KW_FLOAT,
            'bool': TokenType.KW_BOOL,
            'return': TokenType.KW_RETURN,
            'true': TokenType.KW_TRUE,
            'false': TokenType.KW_FALSE,
            'void': TokenType.KW_VOID,
            'struct': TokenType.KW_STRUCT,
            'fn': TokenType.KW_FN,
        }
        
    def scan_tokens(self) -> List[Token]:
        """Сканирует весь исходный код и возвращает список токенов"""
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
            
        # Добавляем EOF токен
        self.tokens.append(Token(TokenType.END_OF_FILE, "", self.line, self.column))
        return self.tokens
    
    def scan_token(self):
        """Сканирует один токен"""
        c = self.advance()
        
        if c == '\n':
            self.line += 1
            self.column = 1
        elif c.isspace():  # пробел, табуляция
            pass  # просто пропускаем
        elif c == '/':
            if self.match('/'):  # комментарий //
                self.scan_comment()
            elif self.match('*'):  # комментарий /*
                self.scan_multiline_comment()
            else:
                self.add_token(TokenType.OP_DIV)
        elif c == '+':
            if self.match('='):
                self.add_token(TokenType.OP_PLUS_ASSIGN)
            else:
                self.add_token(TokenType.OP_PLUS)
        elif c == '-':
            if self.match('='):
                self.add_token(TokenType.OP_MINUS_ASSIGN)
            else:
                self.add_token(TokenType.OP_MINUS)
        elif c == '*':
            if self.match('='):
                self.add_token(TokenType.OP_MULT_ASSIGN)
            else:
                self.add_token(TokenType.OP_MULT)
        elif c == '%':
            self.add_token(TokenType.OP_MOD)
        elif c == '=':
            if self.match('='):
                self.add_token(TokenType.OP_EQ)
            else:
                self.add_token(TokenType.OP_ASSIGN)
        elif c == '!':
            if self.match('='):
                self.add_token(TokenType.OP_NEQ)
            else:
                self.add_token(TokenType.OP_NOT)
        elif c == '<':
            if self.match('='):
                self.add_token(TokenType.OP_LE)
            else:
                self.add_token(TokenType.OP_LT)
        elif c == '>':
            if self.match('='):
                self.add_token(TokenType.OP_GE)
            else:
                self.add_token(TokenType.OP_GT)
        elif c == '&':
            if self.match('&'):
                self.add_token(TokenType.OP_AND)
            else:
                self.error("Ожидался '&' для оператора &&")
        elif c == '|':
            if self.match('|'):
                self.add_token(TokenType.OP_OR)
            else:
                self.error("Ожидался '|' для оператора ||")
        elif c == '(':
            self.add_token(TokenType.LPAREN)
        elif c == ')':
            self.add_token(TokenType.RPAREN)
        elif c == '{':
            self.add_token(TokenType.LBRACE)
        elif c == '}':
            self.add_token(TokenType.RBRACE)
        elif c == '[':
            self.add_token(TokenType.LBRACKET)
        elif c == ']':
            self.add_token(TokenType.RBRACKET)
        elif c == ';':
            self.add_token(TokenType.SEMICOLON)
        elif c == ',':
            self.add_token(TokenType.COMMA)
        elif c == ':':
            self.add_token(TokenType.COLON)
        elif c == '"':
            self.scan_string()
        elif c.isdigit() or (c == '-' and self.peek().isdigit()):
            self.scan_number()
        elif c.isalpha() or c == '_':
            self.scan_identifier()
        else:
            self.error(f"Неизвестный символ '{c}'")
    
    def scan_identifier(self):
        """Сканирует идентификатор или ключевое слово"""
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
            
        text = self.source[self.start:self.current]
        
        # Проверяем, не ключевое ли это слово
        token_type = self.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type)
    
    def scan_number(self):
        """Сканирует число (целое или с плавающей точкой)"""
        is_float = False
        
        # Сканируем целую часть
        while self.peek().isdigit():
            self.advance()
            
        # Проверяем на десятичную точку
        if self.peek() == '.' and self.peek_next().isdigit():
            is_float = True
            self.advance()  # точка
            while self.peek().isdigit():
                self.advance()
                
        # Извлекаем число
        number_str = self.source[self.start:self.current]
        
        if is_float:
            value = float(number_str)
            self.add_token(TokenType.FLOAT_LITERAL, value)
        else:
            value = int(number_str)
            # Проверяем на выход за пределы int
            if value < -2**31 or value > 2**31 - 1:
                self.error(f"Число {value} выходит за пределы допустимого диапазона [-2^31, 2^31-1]")
            self.add_token(TokenType.INT_LITERAL, value)
    
    def scan_string(self):
        """Сканирует строковый литерал"""
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
                self.column = 1
            self.advance()
            
        if self.is_at_end():
            self.error("Незакрытая строка")
            return
            
        # Закрывающая кавычка
        self.advance()
        
        value = self.source[self.start+1:self.current-1]
        self.add_token(TokenType.STRING_LITERAL, value)
    
    def scan_comment(self):
        """Сканирует однострочный комментарий"""
        while self.peek() != '\n' and not self.is_at_end():
            self.advance()
    
    def scan_multiline_comment(self):
        """Сканирует многострочный комментарий"""
        depth = 1
        while depth > 0 and not self.is_at_end():
            if self.peek() == '*' and self.peek_next() == '/':
                self.advance()
                self.advance()
                depth -= 1
            elif self.peek() == '/' and self.peek_next() == '*':
                self.advance()
                self.advance()
                depth += 1
            else:
                if self.peek() == '\n':
                    self.line += 1
                    self.column = 1
                self.advance()
                
        if depth > 0:
            self.error("Незакрытый многострочный комментарий")
    
    def advance(self) -> str:
        """Продвигается на один символ вперед"""
        self.current += 1
        self.column += 1
        return self.source[self.current - 1]
    
    def match(self, expected: str) -> bool:
        """Проверяет, совпадает ли следующий символ с ожидаемым"""
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
            
        self.current += 1
        self.column += 1
        return True
    
    def peek(self) -> str:
        """Возвращает текущий символ без продвижения"""
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    
    def peek_next(self) -> str:
        """Возвращает следующий символ без продвижения"""
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]
    
    def is_at_end(self) -> bool:
        """Проверяет, достигнут ли конец файла"""
        return self.current >= len(self.source)
    
    def add_token(self, token_type: TokenType, literal_value=None):
        """Добавляет токен в список"""
        text = self.source[self.start:self.current]
        token = Token(token_type, text, self.line, self.start + 1, literal_value)
        self.tokens.append(token)
    
    def error(self, message: str):
        """Добавляет ошибку"""
        # Находим строку с ошибкой для контекста
        lines = self.source.split('\n')
        source_line = lines[self.line - 1] if self.line <= len(lines) else ""
        self.errors.add_error(message, self.line, self.column, source_line)
        self.add_token(TokenType.ERROR)

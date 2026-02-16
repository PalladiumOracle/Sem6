from dataclasses import dataclass
from typing import List, Optional

@dataclass
class LexicalError:
    message: str
    line: int
    column: int
    source_line: str
    
    def __str__(self):
        return f"Ошибка в {self.line}:{self.column}: {self.message}\n{self.source_line}\n{' ' * (self.column-1)}^"

class ErrorHandler:
    def __init__(self):
        self.errors: List[LexicalError] = []
        
    def add_error(self, message: str, line: int, column: int, source_line: str = ""):
        self.errors.append(LexicalError(message, line, column, source_line))
        
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    def print_errors(self):
        for error in self.errors:
            print(error)
            
    def clear(self):
        self.errors.clear()

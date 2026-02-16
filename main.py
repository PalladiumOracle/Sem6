#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# Добавляем путь к src в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lexer.scanner import Scanner

def main():
    parser = argparse.ArgumentParser(description='MiniCompiler - Лексический анализатор')
    parser.add_argument('--input', '-i', required=True, help='Входной файл с исходным кодом')
    parser.add_argument('--output', '-o', help='Выходной файл для токенов (если не указан, вывод в консоль)')
    
    args = parser.parse_args()
    
    try:
        # Читаем входной файл
        with open(args.input, 'r', encoding='utf-8') as f:
            source = f.read()
            
        # Сканируем
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        
        # Выводим ошибки, если есть
        if scanner.errors.has_errors():
            print("Найдены ошибки:", file=sys.stderr)
            scanner.errors.print_errors()
            if args.output:
                sys.exit(1)
        
        # Выводим токены
        output_lines = [str(token) for token in tokens]
        output_text = '\n'.join(output_lines)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_text)
        else:
            print(output_text)
            
    except FileNotFoundError:
        print(f"Ошибка: Файл '{args.input}' не найден", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Добавляем путь к проекту в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lexer.scanner import Scanner

def run_test(test_file):
    """Запускает один тест и сравнивает результат с ожидаемым"""
    print(f"Тестирование: {test_file}")
    
    # Читаем входной файл
    with open(test_file, 'r', encoding='utf-8') as f:
        source = f.read()
    
    # Сканируем
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    
    # Формируем вывод
    actual_output = [str(token) for token in tokens]
    
    # Ищем файл с ожидаемым результатом
    expected_file = test_file.replace('.src', '.expected')
    
    if os.path.exists(expected_file):
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected_output = f.read().strip().split('\n')
        
        # Сравниваем
        if actual_output == expected_output:
            print("  ✅ УСПЕХ")
            return True
        else:
            print("  ❌ НЕУДАЧА")
            print("  Ожидалось:")
            for line in expected_output:
                print(f"    {line}")
            print("  Получено:")
            for line in actual_output:
                print(f"    {line}")
            return False
    else:
        print("  ⚠️  Нет файла с ожидаемым результатом, сохраняем текущий вывод")
        with open(expected_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(actual_output))
        return True

def main():
    test_dir = Path(__file__).parent / 'lexer'
    success_count = 0
    total_count = 0
    
    # Тестируем валидные случаи
    print("=" * 50)
    print("ТЕСТИРОВАНИЕ ВАЛИДНЫХ СЛУЧАЕВ")
    print("=" * 50)
    
    valid_dir = test_dir / 'valid'
    if valid_dir.exists():
        for test_file in valid_dir.glob('*.src'):
            if run_test(test_file):
                success_count += 1
            total_count += 1
            print()
    
    # Тестируем невалидные случаи
    print("=" * 50)
    print("ТЕСТИРОВАНИЕ НЕВАЛИДНЫХ СЛУЧАЕВ")
    print("=" * 50)
    
    invalid_dir = test_dir / 'invalid'
    if invalid_dir.exists():
        for test_file in invalid_dir.glob('*.src'):
            if run_test(test_file):
                success_count += 1
            total_count += 1
            print()
    
    # Результаты
    print("=" * 50)
    print(f"ИТОГИ: {success_count}/{total_count} тестов пройдено")
    
    if success_count == total_count:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
        return 0
    else:
        print(f"❌ ПРОВАЛЕНО {total_count - success_count} ТЕСТОВ")
        return 1

if __name__ == '__main__':
    sys.exit(main())

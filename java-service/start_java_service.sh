#!/bin/bash

echo "🚀 Запуск Java сервиса..."

# Проверяем Java
if ! command -v java &> /dev/null; then
    echo "❌ Java не установлена!"
    echo "Установите Java:"
    echo "  Ubuntu/Debian: sudo apt install openjdk-17-jdk"
    echo "  CentOS/RHEL: sudo yum install java-17-openjdk"
    exit 1
fi

# Проверяем компиляцию
if [ ! -f "SimpleJavaService.class" ]; then
    echo "🔨 Компилируем Java сервис..."
    javac SimpleJavaService.java
    
    if [ $? -ne 0 ]; then
        echo "❌ Ошибка компиляции!"
        exit 1
    fi
fi

# Запускаем сервис
echo "✅ Запускаем Java сервис на порту 8090..."
java SimpleJavaService
#!/bin/bash

echo "🚀 Запуск всех сервисов для бенчмарка..."

# Функция для запуска сервиса в фоне
start_service() {
    local name=$1
    local command=$2
    local directory=$3
    
    echo "Запускаем $name..."
    cd "$directory"
    $command &
    cd ..
    sleep 3
}

# Запускаем сервисы
start_service "Rust" "cargo run --release" "rust-service"
start_service "Go" "go run main.go" "go-service" 
start_service "Java" "java JavaSimpleServer" "java-service"
start_service "Python" "python app.py" "python-service"

echo "✅ Все сервисы запущены!"
echo "📊 Запустите бенчмарк: python benchmark.py"
echo "🔍 Или быструю проверку: python quick_test.py"

# Ждем Ctrl+C для остановки
echo "Нажмите Ctrl+C для остановки всех сервисов"
wait
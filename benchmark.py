import requests
import time
import statistics
import matplotlib.pyplot as plt
import json
from concurrent.futures import ThreadPoolExecutor

def test_single_request(service_url: str, number: int) -> float:
    """Тестирование одного запроса"""
    start_time = time.perf_counter()
    response = requests.get(f"{service_url}/fibonacci/{number}")
    end_time = time.perf_counter()
    
    if response.status_code == 200:
        return (end_time - start_time) * 1000  # в миллисекундах
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def run_benchmark(service_name: str, service_url: str, num_requests: int = 1000, concurrent_requests: int = 10):
    """Запуск бенчмарка для сервиса"""
    print(f"\n=== Тестирование {service_name} ===")
    
    # Тестовые числа Фибоначчи
    test_numbers = [10, 20, 30, 40]
    
    results = {}
    
    for number in test_numbers:
        print(f"Тестирование для n={number}...")
        
        # Последовательные запросы
        sequential_times = []
        for i in range(num_requests):
            latency = test_single_request(service_url, number)
            if latency is not None:
                sequential_times.append(latency)
        
        # Параллельные запросы
        def make_request(_):
            return test_single_request(service_url, number)
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            concurrent_times = list(filter(None, executor.map(make_request, range(num_requests))))
        
        results[number] = {
            'sequential': {
                'mean': statistics.mean(sequential_times),
                'median': statistics.median(sequential_times),
                'stdev': statistics.stdev(sequential_times) if len(sequential_times) > 1 else 0,
                'min': min(sequential_times),
                'max': max(sequential_times)
            },
            'concurrent': {
                'mean': statistics.mean(concurrent_times),
                'median': statistics.median(concurrent_times),
                'stdev': statistics.stdev(concurrent_times) if len(concurrent_times) > 1 else 0,
                'min': min(concurrent_times),
                'max': max(concurrent_times)
            }
        }
        
        print(f"n={number}: Среднее время последовательных запросов: {results[number]['sequential']['mean']:.3f}ms")
        print(f"n={number}: Среднее время параллельных запросов: {results[number]['concurrent']['mean']:.3f}ms")
    
    return results

def plot_results(rust_results, python_results):
    """Построение графиков результатов"""
    numbers = list(rust_results.keys())
    
    # Подготовка данных для графиков
    rust_seq_means = [rust_results[n]['sequential']['mean'] for n in numbers]
    python_seq_means = [python_results[n]['sequential']['mean'] for n in numbers]
    rust_conc_means = [rust_results[n]['concurrent']['mean'] for n in numbers]
    python_conc_means = [python_results[n]['concurrent']['mean'] for n in numbers]
    
    # График последовательных запросов
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(numbers, rust_seq_means, 'b-', label='Rust', marker='o')
    plt.plot(numbers, python_seq_means, 'r-', label='Python', marker='s')
    plt.xlabel('Число Фибоначчи (n)')
    plt.ylabel('Время (мс)')
    plt.title('Последовательные запросы')
    plt.legend()
    plt.grid(True)
    
    # График параллельных запросов
    plt.subplot(1, 2, 2)
    plt.plot(numbers, rust_conc_means, 'b-', label='Rust', marker='o')
    plt.plot(numbers, python_conc_means, 'r-', label='Python', marker='s')
    plt.xlabel('Число Фибоначчи (n)')
    plt.ylabel('Время (мс)')
    plt.title('Параллельные запросы (10 потоков)')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('benchmark_results.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    # Конфигурация тестирования
    NUM_REQUESTS = 500
    CONCURRENT_REQUESTS = 10
    
    # Запуск бенчмарков
    rust_results = run_benchmark(
        "Rust Service", 
        "http://127.0.0.1:8080", 
        NUM_REQUESTS, 
        CONCURRENT_REQUESTS
    )
    
    python_results = run_benchmark(
        "Python Service", 
        "http://127.0.0.1:8000", 
        NUM_REQUESTS, 
        CONCURRENT_REQUESTS
    )
    
    # Сохранение результатов
    with open('benchmark_results.json', 'w') as f:
        json.dump({
            'rust': rust_results,
            'python': python_results,
            'config': {
                'num_requests': NUM_REQUESTS,
                'concurrent_requests': CONCURRENT_REQUESTS
            }
        }, f, indent=2)
    
    # Построение графиков
    plot_results(rust_results, python_results)
    
    print("\n=== Сводные результаты ===")
    for number in rust_results.keys():
        rust_speedup = python_results[number]['concurrent']['mean'] / rust_results[number]['concurrent']['mean']
        print(f"n={number}: Rust быстрее Python в {rust_speedup:.2f} раз")
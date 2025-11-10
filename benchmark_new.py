import requests
import time
import statistics
import matplotlib.pyplot as plt
import json
from concurrent.futures import ThreadPoolExecutor

def test_single_request(service_url: str, number: int) -> float:
    """Тестирование одного запроса"""
    try:
        start_time = time.perf_counter()
        response = requests.get(f"{service_url}/fibonacci/{number}", timeout=10)
        end_time = time.perf_counter()
        
        if response.status_code == 200:
            return (end_time - start_time) * 1000  # в миллисекундах
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request error for {service_url}: {e}")
        return None

def run_benchmark(service_name: str, service_url: str, num_requests: int = 500, concurrent_requests: int = 10):
    """Запуск бенчмарка для сервиса"""
    print(f"\n=== Тестирование {service_name} ===")
    
    # Тестовые числа Фибоначчи
    test_numbers = [10, 20, 30, 40]
    
    results = {}
    
    for number in test_numbers:
        print(f"Тестирование для n={number}...")
        
        # Последовательные запросы
        sequential_times = []
        successful_sequential = 0
        
        for i in range(num_requests):
            latency = test_single_request(service_url, number)
            if latency is not None:
                sequential_times.append(latency)
                successful_sequential += 1
            
            if (i + 1) % 100 == 0:
                print(f"  Последовательные: {i + 1}/{num_requests}")
        
        # Параллельные запросы
        def make_request(_):
            return test_single_request(service_url, number)
        
        concurrent_times = []
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            results_list = list(executor.map(make_request, range(num_requests)))
            concurrent_times = [t for t in results_list if t is not None]
        
        if sequential_times and concurrent_times:
            results[number] = {
                'sequential': {
                    'mean': statistics.mean(sequential_times),
                    'median': statistics.median(sequential_times),
                    'stdev': statistics.stdev(sequential_times) if len(sequential_times) > 1 else 0,
                    'min': min(sequential_times),
                    'max': max(sequential_times),
                    'success_rate': len(sequential_times) / num_requests
                },
                'concurrent': {
                    'mean': statistics.mean(concurrent_times),
                    'median': statistics.median(concurrent_times),
                    'stdev': statistics.stdev(concurrent_times) if len(concurrent_times) > 1 else 0,
                    'min': min(concurrent_times),
                    'max': max(concurrent_times),
                    'success_rate': len(concurrent_times) / num_requests
                }
            }
            
            print(f"n={number}: Последовательные - {results[number]['sequential']['mean']:.3f}ms (успех: {results[number]['sequential']['success_rate']:.1%})")
            print(f"n={number}: Параллельные   - {results[number]['concurrent']['mean']:.3f}ms (успех: {results[number]['concurrent']['success_rate']:.1%})")
        else:
            print(f"n={number}: Не удалось получить результаты")
    
    return results

def plot_results(results_dict):
    """Построение графиков результатов для всех сервисов"""
    services = list(results_dict.keys())
    numbers = list(next(iter(results_dict.values())).keys())
    
    # Цвета для разных сервисов
    colors = {
        'rust': 'blue',
        'go': 'green', 
        'java': 'orange',
        'python': 'red'
    }
    
    markers = {
        'rust': 'o',
        'go': 's',
        'java': '^',
        'python': 'D'
    }
    
    # График последовательных запросов
    plt.figure(figsize=(15, 6))
    
    plt.subplot(1, 2, 1)
    for service in services:
        if service in results_dict:
            seq_means = [results_dict[service][n]['sequential']['mean'] for n in numbers]
            plt.plot(numbers, seq_means, 
                    color=colors.get(service, 'black'),
                    marker=markers.get(service, 'o'),
                    label=service.capitalize(),
                    linewidth=2)
    
    plt.xlabel('Число Фибоначчи (n)')
    plt.ylabel('Время (мс)')
    plt.title('Последовательные запросы')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # График параллельных запросов
    plt.subplot(1, 2, 2)
    for service in services:
        if service in results_dict:
            conc_means = [results_dict[service][n]['concurrent']['mean'] for n in numbers]
            plt.plot(numbers, conc_means,
                    color=colors.get(service, 'black'),
                    marker=markers.get(service, 'o'), 
                    label=service.capitalize(),
                    linewidth=2)
    
    plt.xlabel('Число Фибоначчи (n)')
    plt.ylabel('Время (мс)')
    plt.title('Параллельные запросы (10 потоков)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('benchmark_results_all.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_throughput_comparison(results_dict):
    """График сравнения пропускной способности"""
    services = list(results_dict.keys())
    numbers = list(next(iter(results_dict.values())).keys())
    
    plt.figure(figsize=(12, 8))
    
    # Рассчитываем пропускную способность (запросов в секунду)
    for i, service in enumerate(services):
        if service in results_dict:
            throughputs = []
            for n in numbers:
                # Пропускная способность = 1000 / время в ms
                mean_time_ms = results_dict[service][n]['concurrent']['mean']
                throughput = 1000 / mean_time_ms if mean_time_ms > 0 else 0
                throughputs.append(throughput)
            
            plt.plot(numbers, throughputs,
                    marker='o',
                    linewidth=2,
                    label=service.capitalize())
    
    plt.xlabel('Число Фибоначчи (n)')
    plt.ylabel('Пропускная способность (запросов/секунду)')
    plt.title('Сравнение пропускной способности сервисов')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.yscale('log')  # Логарифмическая шкала для лучшей визуализации
    
    plt.tight_layout()
    plt.savefig('throughput_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def print_comprehensive_results(results_dict):
    """Вывод комплексных результатов"""
    print("\n" + "="*80)
    print("СВОДНЫЕ РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*80)
    
    services = list(results_dict.keys())
    numbers = list(next(iter(results_dict.values())).keys())
    
    # Таблица результатов для параллельных запросов
    print(f"\n{'Сервис':<10} {'n':<4} {'Латентность (мс)':<18} {'Пропускная способность':<22} {'Успешных':<10}")
    print("-" * 70)
    
    for service in services:
        for n in numbers:
            if service in results_dict and n in results_dict[service]:
                data = results_dict[service][n]['concurrent']
                latency = data['mean']
                throughput = 1000 / latency if latency > 0 else 0
                success_rate = data['success_rate']
                
                print(f"{service:<10} {n:<4} {latency:<18.3f} {throughput:<22.0f} {success_rate:<10.1%}")

def calculate_speedup(results_dict, baseline_service='python'):
    """Расчет ускорения относительно базового сервиса"""
    print(f"\n" + "="*80)
    print(f"СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ ОТНОСИТЕЛЬНО {baseline_service.upper()}")
    print("="*80)
    
    services = [s for s in results_dict.keys() if s != baseline_service]
    numbers = list(next(iter(results_dict.values())).keys())
    
    for service in services:
        print(f"\n--- {service.upper()} vs {baseline_service.upper()} ---")
        for n in numbers:
            if (service in results_dict and baseline_service in results_dict and 
                n in results_dict[service] and n in results_dict[baseline_service]):
                
                service_time = results_dict[service][n]['concurrent']['mean']
                baseline_time = results_dict[baseline_service][n]['concurrent']['mean']
                
                if service_time > 0:
                    speedup = baseline_time / service_time
                    print(f"n={n}: {service.upper()} быстрее в {speedup:.2f} раз")
                else:
                    print(f"n={n}: невозможно рассчитать ускорение")

def check_services_health():
    """Проверка доступности сервисов перед тестированием"""
    services = {
        'rust': 'http://127.0.0.1:8080',
        'go': 'http://127.0.0.1:8081', 
        'java': 'http://127.0.0.1:8082',
        'python': 'http://127.0.0.1:8000'
    }
    
    print("🔍 Проверка доступности сервисов...")
    available_services = {}
    
    for name, url in services.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} сервис доступен")
                available_services[name] = url
            else:
                print(f"❌ {name} сервис недоступен (HTTP {response.status_code})")
        except Exception as e:
            print(f"❌ {name} сервис недоступен: {e}")
    
    return available_services

if __name__ == "__main__":
    # Конфигурация тестирования
    NUM_REQUESTS = 500
    CONCURRENT_REQUESTS = 10
    
    # Проверяем доступность сервисов
    available_services = check_services_health()
    
    if not available_services:
        print("❌ Нет доступных сервисов для тестирования!")
        exit(1)
    
    print(f"\n🎯 Начинаем тестирование {len(available_services)} сервисов...")
    
    # Запуск бенчмарков для каждого доступного сервиса
    all_results = {}
    
    for service_name, service_url in available_services.items():
        results = run_benchmark(
            f"{service_name.capitalize()} Service", 
            service_url, 
            NUM_REQUESTS, 
            CONCURRENT_REQUESTS
        )
        all_results[service_name] = results
    
    # Сохранение результатов
    with open('benchmark_results_all.json', 'w', encoding='utf-8') as f:
        json.dump({
            'results': all_results,
            'config': {
                'num_requests': NUM_REQUESTS,
                'concurrent_requests': CONCURRENT_REQUESTS,
                'timestamp': time.time()
            }
        }, f, indent=2, ensure_ascii=False)
    
    # Построение графиков
    if len(all_results) > 1:
        try:
            plot_results(all_results)
            plot_throughput_comparison(all_results)
        except Exception as e:
            print(f"⚠️ Ошибка при построении графиков: {e}")
    
    # Вывод результатов
    print_comprehensive_results(all_results)
    
    # Сравнение производительности
    if len(all_results) > 1:
        calculate_speedup(all_results, 'python')
    
    print(f"\n💾 Результаты сохранены в benchmark_results_all.json")
    print("📊 Графики сохранены в benchmark_results_all.png и throughput_comparison.png")
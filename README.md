## Инструкция по запуску ##
### Запуск Rust сервиса:



```sh
cd rust-service
cargo build --release
cargo run --release
```



### Запуск Python сервиса:


```sh
pip install fastapi uvicorn requests
cd python-service
uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
```

### Запуск бенчмарка:

#### Полный замер:

```sh
python benchmark.py
```

#### Одиночный замер:

```sh
python simple_test.py
```
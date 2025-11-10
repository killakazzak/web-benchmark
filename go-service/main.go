package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"time"
)

type FibonacciResponse struct {
	Number          int    `json:"number"`
	Result          int64  `json:"result"`
	CalculationTime int64  `json:"calculation_time_ns"`
	Service         string `json:"service"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}

func fibonacci(n int) int64 {
	if n == 0 {
		return 0
	}
	if n == 1 {
		return 1
	}

	var a, b int64 = 0, 1
	for i := 2; i <= n; i++ {
		a, b = b, a+b
	}
	return b
}

func fibonacciHandler(w http.ResponseWriter, r *http.Request) {
	// Устанавливаем заголовки CORS
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	// Получаем число из URL
	numStr := r.URL.Path[len("/fibonacci/"):]
	n, err := strconv.Atoi(numStr)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "Invalid number"})
		return
	}

	if n > 90 {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "Number too large. Maximum is 90."})
		return
	}

	// Вычисляем Фибоначчи и замеряем время
	startTime := time.Now()
	result := fibonacci(n)
	calculationTime := time.Since(startTime).Nanoseconds()

	// Формируем ответ
	response := FibonacciResponse{
		Number:          n,
		Result:          result,
		CalculationTime: calculationTime,
		Service:         "golang",
	}

	json.NewEncoder(w).Encode(response)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"status":  "healthy",
		"service": "golang",
	})
}

func rootHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"message": "Go Fibonacci Service",
		"usage":   "GET /fibonacci/{number}",
		"endpoints": []string{
			"/fibonacci/{number}",
			"/health",
		},
	})
}

func main() {
	http.HandleFunc("/", rootHandler)
	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/fibonacci/", fibonacciHandler)

	port := ":8081"
	fmt.Printf("🚀 Starting Go Fibonacci server on http://127.0.0.1%s\n", port)
	fmt.Printf("📊 Test endpoint: http://127.0.0.1%s/fibonacci/10\n", port)

	log.Fatal(http.ListenAndServe("127.0.0.1"+port, nil))
}

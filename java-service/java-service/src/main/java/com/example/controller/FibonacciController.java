package com.example.controller;

import org.springframework.web.bind.annotation.*;
import java.util.Map;
import java.util.HashMap;

@RestController
@CrossOrigin(origins = "*")
public class FibonacciController {

    @GetMapping("/")
    public Map<String, Object> home() {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "Java Spring Boot Fibonacci Service");
        response.put("usage", "GET /fibonacci/{number}");
        response.put("endpoints", new String[] {
                "/fibonacci/{number}",
                "/health"
        });
        return response;
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "healthy");
        response.put("service", "java");
        return response;
    }

    @GetMapping("/fibonacci/{number}")
    public FibonacciResponse fibonacci(@PathVariable int number) {
        if (number > 90) {
            throw new IllegalArgumentException("Number too large. Maximum is 90.");
        }

        long startTime = System.nanoTime();
        long result = calculateFibonacci(number);
        long calculationTime = System.nanoTime() - startTime;

        return new FibonacciResponse(number, result, calculationTime, "java");
    }

    private long calculateFibonacci(int n) {
        if (n == 0)
            return 0;
        if (n == 1)
            return 1;

        long a = 0, b = 1;
        for (int i = 2; i <= n; i++) {
            long temp = a + b;
            a = b;
            b = temp;
        }
        return b;
    }

    public static class FibonacciResponse {
        private int number;
        private long result;
        private long calculationTimeNs;
        private String service;

        public FibonacciResponse(int number, long result, long calculationTimeNs, String service) {
            this.number = number;
            this.result = result;
            this.calculationTimeNs = calculationTimeNs;
            this.service = service;
        }

        // Getters and setters
        public int getNumber() {
            return number;
        }

        public void setNumber(int number) {
            this.number = number;
        }

        public long getResult() {
            return result;
        }

        public void setResult(long result) {
            this.result = result;
        }

        public long getCalculationTimeNs() {
            return calculationTimeNs;
        }

        public void setCalculationTimeNs(long calculationTimeNs) {
            this.calculationTimeNs = calculationTimeNs;
        }

        public String getService() {
            return service;
        }

        public void setService(String service) {
            this.service = service;
        }
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public Map<String, String> handleIllegalArgument(IllegalArgumentException e) {
        Map<String, String> errorResponse = new HashMap<>();
        errorResponse.put("error", e.getMessage());
        return errorResponse;
    }
}
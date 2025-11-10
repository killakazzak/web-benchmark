use actix_web::{get, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::time::Instant;

#[derive(Serialize, Deserialize)]
struct FibonacciResponse {
    number: u64,
    result: u64,
    calculation_time_ns: u128,
}

#[derive(Serialize, Deserialize)]
struct ErrorResponse {
    error: String,
}

fn fibonacci(n: u64) -> u64 {
    match n {
        0 => 0,
        1 => 1,
        _ => {
            let mut a = 0;
            let mut b = 1;
            for _ in 2..=n {
                let temp = a + b;
                a = b;
                b = temp;
            }
            b
        }
    }
}

#[get("/")]
async fn hello() -> impl Responder {
    HttpResponse::Ok().body("Fibonacci Web Service - use /fibonacci/{number}")
}

#[get("/fibonacci/{number}")]
async fn fibonacci_handler(path: web::Path<u64>) -> impl Responder {
    let n = path.into_inner();
    
    if n > 90 {
        return HttpResponse::BadRequest().json(ErrorResponse {
            error: "Number too large. Maximum is 90.".to_string(),
        });
    }

    let start_time = Instant::now();
    let result = fibonacci(n);
    let calculation_time = start_time.elapsed().as_nanos();

    let response = FibonacciResponse {
        number: n,
        result,
        calculation_time_ns: calculation_time,
    };

    HttpResponse::Ok().json(response)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    println!("Starting Rust Fibonacci server on http://127.0.0.1:8080");
    
    HttpServer::new(|| {
        App::new()
            .service(hello)
            .service(fibonacci_handler)
    })
    .bind("127.0.0.1:8083")?
    .workers(4)
    .run()
    .await
}
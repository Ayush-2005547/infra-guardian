#app.py
from flask import Flask, jsonify, request
from prometheus_client import Counter, Summary, generate_latest
import logging
import random
import time

# OpenTelemetry setup
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({"service.name": "flask-app"})
    )
)

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

# Prometheus metrics
REQUEST_COUNT = Counter('app_requests_total', 'Total app requests', ['method', 'endpoint'])
REQUEST_LATENCY = Summary('request_latency_seconds', 'Request latency', ['endpoint'])

# Logging setup
logging.basicConfig(level=logging.INFO)

@app.route("/")
@REQUEST_LATENCY.labels(endpoint="/").time()
def hello():
    REQUEST_COUNT.labels(method='GET', endpoint='/').inc()
    app.logger.info("GET / - Hello World hit")
    return "Hello from upgraded Flask app 🚀" 

@app.route("/error")
@REQUEST_LATENCY.labels(endpoint="/error").time()
def error_route():
    REQUEST_COUNT.labels(method='GET', endpoint='/error').inc()
    app.logger.warning("GET /error - Simulated error")
    if random.random() < 0.5:
        raise Exception("Random internal server error") # Simulate a random error                                                                                                       
    return "No error this time."

@app.route("/sleep")
@REQUEST_LATENCY.labels(endpoint="/sleep").time()
def sleep_route():
    REQUEST_COUNT.labels(method='GET', endpoint='/sleep').inc()
    delay = random.uniform(0.5, 3.0)
    time.sleep(delay)
    app.logger.info(f"GET /sleep - Slept for {delay:.2f} seconds")
    return jsonify({"slept_for": delay}) # Sleep route with random delay

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain; version=0.0.4; charset=utf-8'} # Prometheus metrics endpoint

@app.errorhandler(Exception)
def handle_error(e):
    app.logger.error(f"Exception: {e}")
    return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) #Host the app on all interfaces

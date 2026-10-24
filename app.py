from flask import Flask
import os

app = Flask(__name__)

# Dynamically read the environment name from system variables
ENV_NAME = os.getenv("APP_ENV", "Development")

@app.route('/')
def home():
    return f"Welcome to the {ENV_NAME} Environment! - code from SCM!!!!"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    # Read port from environment, fallback to 5001
    port = int(os.getenv("PORT", 5001))
    app.run(host='0.0.0.0', port=port)

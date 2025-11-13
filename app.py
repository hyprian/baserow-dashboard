# app.py

from flask import Flask, jsonify, render_template
from data_processor import get_all_date_ranges
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def index():
    """Serves the main dashboard page."""
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """Provides the date range data as a JSON API endpoint."""
    try:
        data = get_all_date_ranges()
        return jsonify(data)
    except Exception as e:
        logging.error(f"An error occurred in the API endpoint: {e}")
        return jsonify({"error": "Failed to retrieve data from Baserow."}), 500

if __name__ == '__main__':
    # This runs the app in debug mode. For production, we will use Gunicorn.
    app.run(host='0.0.0.0', port=5001, debug=True)
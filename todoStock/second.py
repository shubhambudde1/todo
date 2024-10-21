from flask import Flask, request, jsonify, render_template
import requests
import yfinance as yf

app = Flask(__name__)

# Set your SheetDB API URL
SHEETDB_URL = 'https://sheetdb.io/api/v1/56bch88lplluh'

# Home route to render the HTML form and list stocks
@app.route('/')
def home():
    # Get all stock entries
    response = requests.get(SHEETDB_URL)
    stocks = response.json() if response.ok else []
    return render_template('index.html', stocks=stocks)

# Create a stock entry
@app.route('/stocks', methods=['POST'])
def create_stock():
    data = request.form
    stock = data.get('stock')
    int1 = int(data.get('int1'))

    # Fetch current stock value using yfinance
    stock_data = yf.Ticker(stock + ".NS")
   
    history = stock_data.history(period="1d")

    if history.empty:
        print(f"Error fetching data for stock: {stock}")  # Log error
        return jsonify({"error": "Stock not found or no data available"}), 404

    current_stock_price = history['Close'].iloc[-1]  # Get the latest close price
    int2 = current_stock_price
    difference = int1 - int2

    # Fetch all existing stocks to find the highest ID
    response = requests.get(SHEETDB_URL)
    stocks = response.json() if response.ok else []

    # Calculate new auto-incremented ID
    if stocks:
        max_id = max(int(stock['id']) for stock in stocks if 'id' in stock)
        new_id = max_id + 1
    else:
        new_id = 1  # Start from 1 if no entries exist

    # Prepare data for SheetDB
    payload = {
        "data": [{
            "id": new_id,
            "stock": stock,
            "int1": int1,
            "int2": int2,
            "difference": difference
        }]
    }

    # Send data to SheetDB
    response = requests.post(SHEETDB_URL, json=payload)
    return jsonify(response.json()), response.status_code

# Delete a stock entry by ID
@app.route('/stocks/<int:stock_id>', methods=['DELETE'])
def delete_stock(stock_id):
    response = requests.delete(f"{SHEETDB_URL}/id/{stock_id}")
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(debug=True)

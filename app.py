from collections import OrderedDict
from flask import Flask, request, Response
from flask_cors import CORS
import joblib
import pandas as pd
import json
from datetime import datetime

print("🚀 Starting Flask app...")

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains (dev only)

# Load your trained model
model = joblib.load("xgb_demand_forcast_model.pkl")

expected_columns = [
    'Store ID', 'Product ID', 'Category', 'Region', 'Inventory Level',
    'Units Sold', 'Units Ordered', 'Price', 'Discount',
    'Weather Condition', 'Holiday/Promotion', 'Competitor Pricing',
    'Seasonality', 'Day', 'Month', 'Weekday'
]

def calculate_eoq_rol(predicted_daily_demand, ordering_cost, holding_cost_per_unit, lead_time_days):
    D = predicted_daily_demand * 365  # Annual demand
    EOQ = ((2 * D * ordering_cost) / holding_cost_per_unit) ** 0.5
    ROL = predicted_daily_demand * lead_time_days
    return round(EOQ, 2), round(ROL, 2)

@app.route('/predict', methods=['POST'])
def predict(): 
    try:
        data = request.get_json()  # parsing the request 
        print("📥 Incoming data:", data)

        # Check if Target Date is provided
        if 'Target Date' not in data:
            raise ValueError("Missing 'Target Date'. Please include the date you want to predict for (format: YYYY-MM-DD).")

        # Parse the target prediction date
        try:
            target_date = datetime.strptime(data['Target Date'], "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Please use 'YYYY-MM-DD' for 'Target Date'.")

        # Automatically extract day, month, weekday from target date
        data['Day'] = target_date.day
        data['Month'] = target_date.month
        data['Weekday'] = target_date.weekday()  # Monday=0, Sunday=6

        # Make sure all required fields (except date parts) are present
        required_inputs = [col for col in expected_columns if col not in ['Day', 'Month', 'Weekday']]
        missing_cols = [col for col in required_inputs if col not in data]
        if missing_cols:
            raise ValueError(f"Missing required fields: {missing_cols}")

        # Build the input row for prediction
        input_features = {col: data[col] for col in expected_columns}
        input_df = pd.DataFrame([input_features])

        # Predict demand
        predicted_daily_demand = model.predict(input_df)[0]
        predicted_daily_demand = float(predicted_daily_demand)

        # Optional inputs with defaults
        ordering_cost = float(data.get('Ordering Cost', 50))
        holding_cost_per_unit = float(data.get('Holding Cost', 2))
        lead_time_days = float(data.get('Lead Time', 7))

        # EOQ & ROL
        eoq, rol = calculate_eoq_rol(predicted_daily_demand, ordering_cost, holding_cost_per_unit, lead_time_days)

        response = OrderedDict([
            ("PredictedDemand", round(predicted_daily_demand, 2)),
            ("EOQ", eoq),
            ("ROL", rol)
        ])

        return Response(json.dumps(response), mimetype='application/json')

    except Exception as e:
        error_response = {"error": str(e)}
        print("❌ Error:", e)
        return Response(json.dumps(error_response), status=500, mimetype='application/json')

if __name__ == '__main__':
    print("🔥 Running Flask app on http://127.0.0.1:5000")
    app.run(debug=True)

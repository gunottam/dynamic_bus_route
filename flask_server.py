from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)

# Stops for user to select (exclude ISBT & Pacific Mall because fixed start/end)
stops = ['Clock Tower', 'Prince Chowk', 'Railway Station', 'Survey Chowk',
        'Rajpur Road', 'Mussoorie Bus Stand', 'Balliwala Chowk', 'Doon Hospital', 'Dilaram Chowk']

DATA_FILE = 'user_requests.json'

def load_existing_data():
    """Load existing data from the JSON file or return an empty list."""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []  # Handle the case where the file is corrupted or empty

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_stop = request.form.get('stops')
        if selected_stop:
            existing_data = load_existing_data()
            existing_data.append(selected_stop)  # Append the new stop
            with open(DATA_FILE, 'w') as f:
                json.dump(existing_data, f, indent=4)
            return redirect(url_for('submitted'))
        else:
            return render_template('index.html', stops=stops, selected=[], error="Please select one stop.")

    else:
        selected = []
        try:
            with open(DATA_FILE, 'r') as f:
                selected = json.load(f)
        except FileNotFoundError:
            pass
        return render_template('index.html', stops=stops, selected=selected, error=None)

@app.route('/submitted')
def submitted():
    return render_template('submitted.html')

@app.route('/requests')
def get_requests():
    try:
        with open(DATA_FILE, 'r') as f:
            selected = json.load(f)
    except FileNotFoundError:
        selected = []
    return jsonify(selected)

@app.route('/clear_requests', methods=['POST'])
def clear_requests():
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)  # Clear the file by writing an empty list
        return jsonify({'message': 'Data cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True,port = 5500)

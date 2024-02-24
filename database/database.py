from flask import Flask, request, jsonify

app = Flask(__name__)

# Sample patient data (can be replaced with a database)
patients = [
    {"id": 1, "name": "John Doe", "age": 30, "gender": "Male"},
    {"id": 2, "name": "Jane Smith", "age": 25, "gender": "Female"}
]

# API endpoint to get all patients
@app.route('/patients', methods=['GET'])
def get_patients():
    return jsonify(patients)

# API endpoint to get a specific patient by ID
@app.route('/patients/<int:id>', methods=['GET'])
def get_patient(id):
    patient = next((p for p in patients if p['id'] == id), None)
    if patient:
        return jsonify(patient)
    else:
        return jsonify({"error": "Patient not found"}), 404

# API endpoint to add a new patient
@app.route('/patients', methods=['POST'])
def add_patient():
    data = request.json
    new_patient = {
        "id": len(patients) + 1,
        "name": data['name'],
        "age": data['age'],
        "gender": data['gender']
    }
    patients.append(new_patient)
    return jsonify(new_patient), 201

if __name__ == '__main__':
    app.run(debug=True)

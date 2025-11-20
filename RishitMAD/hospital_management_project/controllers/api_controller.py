from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models.models import Appointment, Doctor, Department, User
from extensions import db
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

api_bp = Blueprint('api', __name__)

# --- Helper Functions ---
def doctor_to_json(doctor):
    """Helper function to convert a Doctor object to a dictionary."""
    return {
        "id": doctor.id,
        "name": doctor.name,
        "user_id": doctor.user_id,
        "specialization": doctor.specialization.name,
        "availability": doctor.availability
    }

# --- Dashboard Stats API ---
@api_bp.route('/appointments/stats')
@login_required
def appointment_stats():
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    labels = []
    data = []
    for i in range(6, -1, -1):
        day = date.today() - timedelta(days=i)
        labels.append(day.strftime('%b %d'))
        count = Appointment.query.filter(db.func.date(Appointment.date) == day).count()
        data.append(count)

    return jsonify({"labels": labels, "data": data})

# --- Doctor API ---

# GET all doctors
@api_bp.route('/doctors', methods=['GET'])
def get_doctors():
    doctors = Doctor.query.all()
    return jsonify([doctor_to_json(doc) for doc in doctors])

# GET a single doctor
@api_bp.route('/doctors/<int:doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return jsonify(doctor_to_json(doctor))

# CREATE a new doctor (requires admin role)
@api_bp.route('/doctors', methods=['POST'])
@login_required
def create_doctor():
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    if not data or not all(k in data for k in ['name', 'username', 'password', 'specialization_id']):
        return jsonify({"error": "Missing data"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 409

    # A simple user needs to be created for the doctor to log in
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data['username'], password=hashed_password, role='doctor')
    db.session.add(new_user)
    db.session.commit() # Commit to get the new_user.id

    new_doctor = Doctor(
        name=data['name'],
        user_id=new_user.id,
        specialization_id=data['specialization_id']
    )
    db.session.add(new_doctor)
    db.session.commit()
    return jsonify(doctor_to_json(new_doctor)), 201

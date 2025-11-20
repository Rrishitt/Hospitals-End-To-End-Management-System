from extensions import db
from flask_login import UserMixin
from sqlalchemy.types import JSON

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    specialization_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    availability = db.Column(db.JSON, nullable=True)
    experience = db.Column(db.Integer, nullable=True)
    qualifications = db.Column(db.String(255), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True, default='default.jpg')
    user = db.relationship('User', backref=db.backref('doctor', uselist=False))
    specialization = db.relationship('Department', backref='doctors')

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=True)
    user = db.relationship('User', backref=db.backref('patient', uselist=False))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Booked')
    patient = db.relationship('Patient', backref='appointments')
    doctor = db.relationship('Doctor', backref='appointments')

class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    visit_type = db.Column(db.String(100), nullable=True)
    tests_done = db.Column(db.Text, nullable=True)
    medicines = db.Column(db.JSON, nullable=True)
    appointment = db.relationship('Appointment', backref=db.backref('treatment', uselist=False))

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import Doctor, Appointment, Patient, Treatment
from extensions import db
from datetime import date, timedelta

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.before_request
@login_required
def check_is_doctor():
    if current_user.role != 'doctor': return "Unauthorized", 403

@doctor_bp.route('/dashboard')
def dashboard():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    today_appointments = Appointment.query.filter_by(doctor_id=doctor.id, date=date.today()).all()
    all_appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
    assigned_patients = sorted(list({app.patient for app in all_appointments}), key=lambda p: p.name)
    return render_template('doctor_dashboard.html', appointments=today_appointments, assigned_patients=assigned_patients)

@doctor_bp.route('/availability', methods=['GET', 'POST'])
def availability():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        avail_data = {}
        for i in range(7):
            current_date = (date.today() + timedelta(days=i)).strftime('%Y-%m-%d')
            slots = request.form.getlist(current_date)
            if slots:
                avail_data[current_date] = slots
        doctor.availability = avail_data
        db.session.commit()
        flash('Availability updated successfully.', 'success')
        return redirect(url_for('doctor.availability'))
    week_dates = [(date.today() + timedelta(days=i)) for i in range(7)]
    return render_template('doctor_availability.html', week_dates=week_dates, current_availability=doctor.availability or {})

@doctor_bp.route('/appointment/<int:appointment_id>/update_history', methods=['GET', 'POST'])
def update_patient_history(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if request.method == 'POST':
        appointment.status = 'Completed'
        medicines_list = []
        medicine_names = request.form.getlist('medicine_name')
        medicine_dosages = request.form.getlist('medicine_dosage')
        for i in range(len(medicine_names)):
            if medicine_names[i]:
                medicines_list.append({"name": medicine_names[i], "dosage": medicine_dosages[i]})
        treatment = Treatment.query.filter_by(appointment_id=appointment.id).first()
        if not treatment:
            treatment = Treatment(appointment_id=appointment.id)
            db.session.add(treatment)
        treatment.visit_type = request.form.get('visit_type')
        treatment.tests_done = request.form.get('tests_done')
        treatment.diagnosis = request.form.get('diagnosis')
        treatment.prescription = request.form.get('prescription')
        treatment.notes = request.form.get('notes')
        treatment.medicines = medicines_list
        db.session.commit()
        flash('Patient history updated and appointment marked as complete.', 'success')
        return redirect(url_for('doctor.dashboard'))
    treatment = Treatment.query.filter_by(appointment_id=appointment.id).first()
    return render_template('update_patient_history.html', appointment=appointment, treatment=treatment)

@doctor_bp.route('/patient_history/<int:patient_id>')
def patient_history(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    appointments = Appointment.query.filter_by(patient_id=patient.id, status='Completed').order_by(Appointment.date.desc()).all()
    return render_template('patient_history.html', patient=patient, appointments=appointments)

@doctor_bp.route('/cancel_appointment/<int:appointment_id>')
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if appointment.doctor_id == doctor.id:
        appointment.status = 'Cancelled'
        db.session.commit()
        flash('Appointment has been cancelled.', 'info')
    else:
        flash('Unauthorized action.', 'danger')
    return redirect(url_for('doctor.dashboard'))

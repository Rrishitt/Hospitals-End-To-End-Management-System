from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import Department, Doctor, Appointment, Patient, Treatment
from extensions import db
from datetime import datetime, timedelta
from sqlalchemy import or_

patient_bp = Blueprint('patient', __name__)

@patient_bp.before_request
@login_required
def check_is_patient():
    if current_user.role != 'patient': return "Unauthorized", 403

@patient_bp.route('/dashboard')
def dashboard():
    query = request.args.get('q', '')
    departments = Department.query.all()
    matched_doctors = []
    if query:
        matched_doctors = Doctor.query.join(Department).filter(
            or_(Doctor.name.ilike(f'%{query}%'), Department.name.ilike(f'%{query}%'))
        ).all()
    # Also fetch appointments for the dashboard view
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status == 'Booked'
    ).order_by(Appointment.date.asc()).all()
    return render_template('patient_dashboard.html', departments=departments, appointments=appointments, matched_doctors=matched_doctors, query=query)

@patient_bp.route('/doctors/<int:department_id>')
def list_doctors(department_id):
    department = Department.query.get_or_404(department_id)
    doctors = Doctor.query.filter_by(specialization_id=department_id).all()
    return render_template('list_doctors.html', doctors=doctors, department=department)

@patient_bp.route('/doctor/<int:doctor_id>/profile')
def doctor_profile(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return render_template('doctor_profile.html', doctor=doctor)

@patient_bp.route('/history')
def history():
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appointments = Appointment.query.join(Treatment).filter(
        Appointment.patient_id == patient.id,
        Appointment.status == 'Completed'
    ).order_by(Appointment.date.desc()).all()
    # FIX: Pass the 'patient' object to the template
    return render_template('user_history.html', appointments=appointments, patient=patient)

# ... (rest of the patient controller remains the same)
@patient_bp.route('/doctor/<int:doctor_id>/availability')
def doctor_availability(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    availability = doctor.availability or {}
    booked_appointments = Appointment.query.filter_by(doctor_id=doctor.id, status='Booked').all()
    booked_slots = set()
    for app in booked_appointments:
        slot_name = 'morning' if 8 <= app.time.hour < 12 else 'evening'
        booked_slots.add(f"{app.date.strftime('%Y-%m-%d')}_{slot_name}")
    week_dates = [(datetime.now().date() + timedelta(days=i)) for i in range(7)]
    return render_template('book_spot.html', doctor=doctor, availability=availability, week_dates=week_dates, booked_slots=booked_slots)

@patient_bp.route('/book_appointment/<int:doctor_id>', methods=['POST'])
def book_appointment(doctor_id):
    slot = request.form.get('slot')
    if not slot:
        flash('Please select an available time slot.', 'warning')
        return redirect(url_for('patient.doctor_availability', doctor_id=doctor_id))
    date_str, time_str = slot.split('_')
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    appointment_time = datetime.strptime(time_str, '%H:%M').time()
    slot_name = 'morning' if appointment_time.hour == 9 else 'evening'
    if f"{date_str}_{slot_name}" in {f"{app.date.strftime('%Y-%m-%d')}_{'morning' if 8 <= app.time.hour < 12 else 'evening'}" for app in Appointment.query.filter_by(doctor_id=doctor_id, status='Booked').all()}:
        flash('This time slot has just been booked. Please choose another.', 'danger')
        return redirect(url_for('patient.doctor_availability', doctor_id=doctor_id))
    new_appointment = Appointment(patient_id=patient.id, doctor_id=doctor_id, date=appointment_date, time=appointment_time)
    db.session.add(new_appointment); db.session.commit()
    flash('Appointment booked successfully!', 'success')
    return redirect(url_for('patient.my_appointments'))

@patient_bp.route('/my_appointments')
def my_appointments():
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.date.desc()).all()
    return render_template('my_appointments.html', appointments=appointments)

@patient_bp.route('/cancel_appointment/<int:appointment_id>')
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if appointment.patient_id == patient.id:
        appointment.status = 'Cancelled'
        db.session.commit()
        flash('Appointment cancelled.', 'info')
    else:
        flash('Unauthorized action.', 'danger')
    return redirect(url_for('patient.my_appointments'))

@patient_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        patient.name = request.form.get('name')
        patient.contact = request.form.get('contact')
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('patient.profile'))
    return render_template('user_profile.html', patient=patient)

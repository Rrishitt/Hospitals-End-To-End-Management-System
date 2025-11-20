from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import Doctor, Patient, Appointment, Department, User, Treatment
from extensions import db
from werkzeug.security import generate_password_hash
from sqlalchemy import or_
from analytics import *

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
def check_is_admin():
    if current_user.role != 'admin': return "Unauthorized", 403

@admin_bp.route('/dashboard')
def dashboard():
    doctors = Doctor.query.all()
    patients = Patient.query.all()
    departments = Department.query.all()
    appointments = Appointment.query.order_by(Appointment.date.desc()).limit(10).all()
    return render_template('admin_dashboard.html', doctors=doctors, patients=patients, departments=departments, appointments=appointments)

@admin_bp.route('/analytics')
def analytics():
    plot1 = generate_appointments_per_dept_fig()
    plot2 = generate_appointment_status_fig()
    plot3 = generate_appointments_over_time_fig()
    plot4 = generate_patients_per_doctor_fig()
    plot5 = generate_doctors_per_dept_fig()
    return render_template('admin_analytics.html', plot1=plot1, plot2=plot2, plot3=plot3, plot4=plot4, plot5=plot5)

@admin_bp.route('/patient_history/<int:patient_id>')
def view_patient_history(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    appointments = Appointment.query.join(Treatment).filter(
        Appointment.patient_id == patient.id,
        Appointment.status == 'Completed'
    ).order_by(Appointment.date.desc()).all()
    return render_template('user_history.html', appointments=appointments, patient=patient)

@admin_bp.route('/departments', methods=['GET', 'POST'])
def manage_departments():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        if not Department.query.filter_by(name=name).first():
            new_dept = Department(name=name, description=description)
            db.session.add(new_dept); db.session.commit()
            flash('Department added successfully.', 'success')
        else:
            flash('Department with this name already exists.', 'warning')
    departments = Department.query.all()
    return render_template('admin_departments.html', departments=departments)

@admin_bp.route('/add_doctor', methods=['POST'])
def add_doctor():
    # ... form processing ...
    name = request.form.get('name'); username = request.form.get('username'); password = request.form.get('password')
    specialization_id = request.form.get('specialization_id'); experience = request.form.get('experience')
    if User.query.filter_by(username=username).first():
        flash('Username already exists.', 'danger')
        return redirect(url_for('admin.dashboard')) # FIX: Redirect to dashboard
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, password=hashed_password, role='doctor')
    db.session.add(new_user); db.session.commit()
    new_doctor = Doctor(user_id=new_user.id, name=name, specialization_id=specialization_id, experience=experience)
    db.session.add(new_doctor); db.session.commit()
    flash('Doctor added successfully.', 'success')
    return redirect(url_for('admin.dashboard')) # FIX: Redirect to dashboard

@admin_bp.route('/edit_doctor/<int:doctor_id>', methods=['POST'])
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.name = request.form.get('name')
    doctor.specialization_id = request.form.get('specialization_id')
    doctor.experience = request.form.get('experience')
    db.session.commit()
    flash('Doctor details updated.', 'success')
    return redirect(url_for('admin.dashboard')) # FIX: Redirect to dashboard

@admin_bp.route('/delete_doctor/<int:doctor_id>')
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    # FIX: Cascade delete appointments
    Appointment.query.filter_by(doctor_id=doctor.id).delete()
    db.session.delete(doctor)
    db.session.delete(User.query.get(doctor.user_id))
    db.session.commit()
    flash('Doctor and all associated appointments have been removed.', 'success')
    return redirect(url_for('admin.dashboard')) # FIX: Redirect to dashboard

@admin_bp.route('/edit_patient/<int:patient_id>', methods=['POST'])
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    patient.name = request.form.get('name')
    patient.contact = request.form.get('contact')
    db.session.commit()
    flash('Patient details updated.', 'success')
    return redirect(url_for('admin.dashboard')) # FIX: Redirect to dashboard

@admin_bp.route('/delete_patient/<int:patient_id>')
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    # FIX: Cascade delete treatments and appointments
    appointments = Appointment.query.filter_by(patient_id=patient.id).all()
    for app in appointments:
        Treatment.query.filter_by(appointment_id=app.id).delete()
    Appointment.query.filter_by(patient_id=patient.id).delete()
    db.session.delete(patient)
    db.session.delete(User.query.get(patient.user_id))
    db.session.commit()
    flash('Patient and all associated records have been removed.', 'success')
    return redirect(url_for('admin.dashboard')) # FIX: Redirect to dashboard

@admin_bp.route('/user/<int:user_id>/blacklist')
def blacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()
    flash(f"User {user.username} has been {'blacklisted' if user.is_blacklisted else 'un-blacklisted'}.", 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))

@admin_bp.route('/search')
def search():
    query = request.args.get('q', '')
    if not query: return redirect(url_for('admin.dashboard'))
    patients = Patient.query.filter(or_(Patient.name.ilike(f'%{query}%'))).all()
    doctors = Doctor.query.filter(Doctor.name.ilike(f'%{query}%')).all()
    departments = Department.query.filter(Department.name.ilike(f'%{query}%')).all()
    return render_template('admin_search_results.html', query=query, patients=patients, doctors=doctors, departments=departments)

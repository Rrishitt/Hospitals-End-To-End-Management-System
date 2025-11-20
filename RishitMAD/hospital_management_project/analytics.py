import plotly
import plotly.express as px
import pandas as pd
import json
from models.models import Appointment, Doctor, Department
from extensions import db

def generate_appointments_per_dept_fig():
    """Generates a bar chart of total appointments for each department."""
    query = db.session.query(Department.name, db.func.count(Appointment.id).label('count')) \
        .join(Doctor, Department.id == Doctor.specialization_id) \
        .join(Appointment, Doctor.id == Appointment.doctor_id) \
        .group_by(Department.name).all()
    
    if not query: return json.dumps({})
        
    df = pd.DataFrame(query, columns=['department', 'count'])
    fig = px.bar(df, 
                 x='department', 
                 y='count', 
                 title='Total Appointments per Department',
                 labels={'department':'Department', 'count':'Number of Appointments'})
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def generate_appointment_status_fig():
    """Generates a donut chart showing the distribution of appointment statuses."""
    query = db.session.query(Appointment.status, db.func.count(Appointment.id).label('count')) \
        .group_by(Appointment.status).all()

    if not query: return json.dumps({})

    df = pd.DataFrame(query, columns=['status', 'count'])
    fig = px.pie(df, 
                 names='status', 
                 values='count', 
                 title='Appointment Status Distribution', 
                 hole=.4) # This creates the donut shape
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def generate_appointments_over_time_fig():
    """Generates a line chart of appointments created over time."""
    query = db.session.query(db.func.date(Appointment.date).label('date'), db.func.count(Appointment.id).label('count')) \
        .group_by(db.func.date(Appointment.date)).order_by('date').all()

    if not query: return json.dumps({})

    df = pd.DataFrame(query, columns=['date', 'count'])
    fig = px.line(df, 
                  x='date', 
                  y='count', 
                  title='Appointments Volume Over Time', 
                  markers=True,
                  labels={'date':'Date', 'count':'Number of Appointments'})
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def generate_patients_per_doctor_fig():
    """Generates a bar chart showing the number of unique patients each doctor has seen, sorted."""
    query = db.session.query(Doctor.name, db.func.count(db.distinct(Appointment.patient_id)).label('patient_count')) \
        .join(Appointment, Doctor.id == Appointment.doctor_id) \
        .group_by(Doctor.name).order_by(db.desc('patient_count')).all()

    if not query: return json.dumps({})

    df = pd.DataFrame(query, columns=['doctor', 'patient_count'])
    fig = px.bar(df, 
                 x='doctor', 
                 y='patient_count', 
                 title='Busiest Doctors (by Unique Patients)',
                 labels={'doctor':'Doctor', 'patient_count':'Unique Patients Seen'})
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def generate_doctors_per_dept_fig():
    """Generates a donut chart showing how many doctors are in each department."""
    # Use outerjoin to include departments with 0 doctors
    query = db.session.query(Department.name, db.func.count(Doctor.id).label('doctor_count')) \
        .outerjoin(Doctor, Department.id == Doctor.specialization_id) \
        .group_by(Department.name).all()

    if not query: return json.dumps({})

    df = pd.DataFrame(query, columns=['department', 'doctor_count'])
    fig = px.pie(df, 
                 names='department', 
                 values='doctor_count', 
                 title='Doctor Distribution by Department',
                 hole=.4)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
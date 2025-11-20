from flask import Flask
from extensions import db, migrate, login_manager
from models.models import User
from werkzeug.security import generate_password_hash
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Import and register blueprints
    from controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp)

    from controllers.admin_controller import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from controllers.doctor_controller import doctor_bp
    app.register_blueprint(doctor_bp, url_prefix='/doctor')

    from controllers.patient_controller import patient_bp
    app.register_blueprint(patient_bp, url_prefix='/patient')

    from controllers.api_controller import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()
        # Create admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            hashed_password = generate_password_hash('admin_password', method='pbkdf2:sha256')
            admin_user = User(username='admin', password=hashed_password, role='admin')
            db.session.add(admin_user)
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/elearning.db'
db = SQLAlchemy(app)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    time = db.Column(db.Time, nullable=False, default=datetime.now().time)
    status = db.Column(db.String(20), nullable=False)  # hadir, sakit, izin
    notes = db.Column(db.Text)

with app.app_context():
    db.create_all()
    print("Attendance table recreated successfully!") 
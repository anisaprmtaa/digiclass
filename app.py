from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from werkzeug.utils import secure_filename
import os
import time
import pandas as pd
from io import BytesIO
import json
from sqlalchemy import distinct

# Dictionary nama lengkap guru
TEACHER_NAMES = {
    'asep.saepudin': 'Asep Saepudin, S.Pd.I',
    'ani.kusrini': 'Ani Kusrini, S.Pd.',
    'heti.mulyani': 'Heti Mulyani, S.Kom.',
    'dina.marliana': 'Dina Marliana, S.Pd.',
    'nia.kurniasih': 'Nia Kurniasih, S.Pd.',
    'rudi.hartono': 'Rudi Hartono, S.Pd',
    'siti.aminah': 'Siti Aminah, S.Pd',
    'tono.wijaya': 'Tono Wijaya, S.Pd',
    'umi.kalsum': 'Umi Kalsum, S.Pd',
    'vina.putri': 'Vina Putri, S.Pd'
}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kunci_rahasia_aplikasi'  # Ganti dengan kunci yang aman
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///elearning.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Menambahkan context processor untuk current_user dan teacher_names
@app.context_processor
def inject_context():
    return dict(
        current_user=current_user,
        teacher_names=TEACHER_NAMES,
        datetime=datetime,
        date=date
    )

# Model User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nisn = db.Column(db.String(20), unique=True)  # Untuk siswa
    nip = db.Column(db.String(20), unique=True)   # Untuk guru
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='siswa')  # 'guru', 'siswa'
    kelas = db.Column(db.String(10))  # Hanya untuk siswa
    profile_photo = db.Column(db.String(255), default='default.jpg')  # Nama file foto profil
    courses = db.relationship('Course', backref='instructor', lazy=True)

    def get_identifier(self):
        return self.nisn if self.role == 'siswa' else self.nip

# Model Mata Pelajaran
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    materials = db.relationship('Material', backref='course', lazy=True)
    quizzes = db.relationship('Quiz', backref='course', lazy=True)
    assignments = db.relationship('Assignment', backref='course', lazy=True)

# Model Materi Pembelajaran
class Material(db.Model):
    __tablename__ = 'material'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    youtube_url = db.Column(db.String(200))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Tambahan untuk file materi
    file_path = db.Column(db.String(255))
    original_filename = db.Column(db.String(255))

    def get_youtube_embed_url(self):
        if not self.youtube_url:
            return None
        video_id = None
        if 'youtube.com/watch?v=' in self.youtube_url:
            video_id = self.youtube_url.split('watch?v=')[1].split('&')[0]
        elif 'youtu.be/' in self.youtube_url:
            video_id = self.youtube_url.split('youtu.be/')[1]
        if video_id:
            return f'https://www.youtube.com/embed/{video_id}'
        return None

# Model Pelacakan Penyelesaian Materi
class MaterialCompletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('student_id', 'material_id', name='_student_material_uc'),)

    student = db.relationship('User', backref='material_completions', lazy=True)
    material = db.relationship('Material', backref='completions', lazy=True)

# Model Kuis
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=True)
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    questions = db.relationship('QuizQuestion', backref='quiz', lazy=True, cascade='all, delete-orphan')

# Model Pertanyaan Kuis
class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False)  # JSON string of options
    correct_answer = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Integer, default=10)

    def set_options(self, options_list):
        """Set options as JSON string"""
        self.options = json.dumps(options_list)

    def get_options(self):
        """Get options as list"""
        try:
            return json.loads(self.options)
        except (json.JSONDecodeError, TypeError):
            return []

# Model Tugas
class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=True)
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    submissions = db.relationship('AssignmentSubmission', backref='assignment', lazy=True)
    # Tambahan untuk file tugas
    task_file_path = db.Column(db.String(255))
    task_original_filename = db.Column(db.String(255))

# Model Pengumpulan Tugas
class AssignmentSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Float)
    feedback = db.Column(db.Text)
    # Tambahan untuk file jawaban
    file_path = db.Column(db.String(255))
    original_filename = db.Column(db.String(255))
    # Relasi ke user (siswa)
    student = db.relationship('User', backref='assignment_submissions', lazy=True)

# Model Hasil Kuis
class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    student_answers = db.Column(db.Text)
    
    quiz = db.relationship('Quiz', backref='results', lazy=True)
    student = db.relationship('User', backref='quiz_results', lazy=True)

# Model Notifikasi
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20))  # 'tugas', 'kuis', 'nilai', 'pengumuman'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notifications', lazy=True)

# Model Forum Post
class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    course = db.relationship('Course', backref='forum_posts', lazy=True)
    user = db.relationship('User', backref='forum_posts', lazy=True)
    comments = db.relationship('ForumComment', backref='post', lazy=True, cascade='all, delete-orphan')

# Model Forum Comment
class ForumComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='forum_comments', lazy=True)

# Model untuk presensi
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    time = db.Column(db.Time, nullable=False, default=datetime.now().time)
    status = db.Column(db.String(20), nullable=False)  # hadir, sakit, izin
    notes = db.Column(db.Text)
    
    student = db.relationship('User', backref='attendance_records')
    course = db.relationship('Course', backref='attendance_records')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route untuk halaman utama
@app.route('/')
def index():
    if not current_user.is_authenticated:
        # Tampilkan semua mata pelajaran untuk pengunjung
        courses = Course.query.all()
    elif current_user.role == 'guru':
        # Tampilkan hanya mata pelajaran yang diampu oleh guru
        courses = Course.query.filter_by(instructor_id=current_user.id).all()
    else:
        # Untuk siswa, tampilkan semua mata pelajaran
        courses = Course.query.all()
        
    # Ambil nama lengkap guru untuk setiap mata pelajaran
    teacher_names = {}
    for course in courses:
        instructor = User.query.get(course.instructor_id)
        if instructor:
            teacher_names[instructor.username] = TEACHER_NAMES.get(instructor.username, instructor.username)
            
    return render_template('index.html', courses=courses, teacher_names=teacher_names)

# Route untuk login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')  # NISN/NIP
        password = request.form.get('password')
        
        # Coba cari user berdasarkan NISN atau NIP
        user = User.query.filter(
            ((User.nisn == identifier) & (User.role == 'siswa')) |
            ((User.nip == identifier) & (User.role == 'guru'))
        ).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Berhasil masuk!', 'success')
            return redirect(url_for('index'))
        flash('NISN/NIP atau password salah.', 'error')
    return render_template('login.html')

# Route untuk logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah keluar.', 'info')
    return redirect(url_for('index'))

# Route untuk melihat daftar mata pelajaran
@app.route('/courses')
def courses():
    if not current_user.is_authenticated:
        # Tampilkan semua mata pelajaran untuk pengunjung
        courses = Course.query.all()
    elif current_user.role == 'guru':
        # Tampilkan hanya mata pelajaran yang diampu oleh guru
        courses = Course.query.filter_by(instructor_id=current_user.id).all()
    else:
        # Untuk siswa, tampilkan semua mata pelajaran
        courses = Course.query.all()
        
    # Ambil nama lengkap guru untuk setiap mata pelajaran
    teacher_names = {}
    for course in courses:
        instructor = User.query.get(course.instructor_id)
        if instructor:
            teacher_names[instructor.username] = TEACHER_NAMES.get(instructor.username, instructor.username)
            
    return render_template('courses.html', courses=courses, teacher_names=teacher_names)

# Fungsi validasi file materi
ALLOWED_MATERIAL_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'ppt', 'pptx', 'xls', 'xlsx'}
def allowed_material_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_MATERIAL_EXTENSIONS

# Route untuk menambah materi pembelajaran
@app.route('/course/<int:course_id>/add_material', methods=['GET', 'POST'])
@login_required
def add_material(course_id):
    course = Course.query.get_or_404(course_id)
    if current_user.id != course.instructor_id:
        flash('Anda tidak memiliki akses untuk menambah materi.', 'error')
        return redirect(url_for('courses'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        youtube_url = request.form.get('youtube_url')
        file_path = None
        original_filename = None

        # Handle upload file materi
        file = request.files.get('material_file')
        if file and file.filename:
            if not allowed_material_file(file.filename):
                flash('Format file tidak diizinkan. Gunakan PDF, DOC, DOCX, TXT, PNG, JPG, JPEG, GIF, PPT, PPTX, XLS, atau XLSX.', 'error')
                return redirect(url_for('add_material', course_id=course_id))
            
            from werkzeug.utils import secure_filename
            import time, os
            filename = secure_filename(f"material_{course_id}_{int(time.time())}{os.path.splitext(file.filename)[1]}")
            upload_dir = os.path.join('static', 'uploads', 'materials')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            file.save(os.path.join(upload_dir, filename))
            file_path = filename
            original_filename = file.filename
        
        material = Material(
            title=title,
            content=content,
            youtube_url=youtube_url if youtube_url else None,
            course_id=course_id,
            file_path=file_path,
            original_filename=original_filename
        )
        db.session.add(material)
        db.session.commit()

        # Kirim notifikasi ke semua siswa
        students = User.query.filter_by(role='siswa').all()
        for student in students:
            create_notification(
                student.id,
                f"Materi Baru - {course.title}",
                f"Ada materi baru: {material.title}",
                "materi"
            )

        flash('Materi berhasil ditambahkan!', 'success')
        return redirect(url_for('view_course', course_id=course_id))
    return render_template('add_material.html', course=course)

# Route untuk melihat detail mata pelajaran
@app.route('/course/<int:course_id>')
@login_required
def view_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Hanya guru yang boleh mengakses filter ini
    if current_user.role == 'guru' and current_user.id == course.instructor_id:
        # Ambil semua kelas unik siswa untuk dropdown filter
        unique_classes = db.session.query(distinct(User.kelas)).filter(User.role == 'siswa').order_by(User.kelas).all()
        unique_classes = [c[0] for c in unique_classes if c[0] is not None] # Hapus None jika ada
        
        selected_class = request.args.get('kelas') # Ambil kelas yang dipilih dari query parameter
        
        # Buat dictionary untuk menyimpan pengumpulan tugas yang sudah difilter per tugas
        filtered_submissions_by_assignment = {}
        for assignment in course.assignments:
            submissions_query = AssignmentSubmission.query.filter_by(assignment_id=assignment.id).join(User)
            if selected_class and selected_class != 'all':
                submissions_query = submissions_query.filter(User.kelas == selected_class)
            
            # Ambil semua siswa untuk mengisi data yang belum mengumpulkan
            all_students_in_course = User.query.filter_by(role='siswa', kelas=selected_class if selected_class and selected_class != 'all' else None).all()
            if not selected_class or selected_class == 'all':
                all_students_in_course = User.query.filter_by(role='siswa').all()

            # Buat dictionary untuk pengumpulan yang sudah ada agar mudah diakses
            submitted_students_map = {sub.student_id: sub for sub in submissions_query.all()}
            
            # Buat daftar yang menggabungkan siswa yang sudah submit dan yang belum
            display_submissions = []
            for student in all_students_in_course:
                submission_found = submitted_students_map.get(student.id)
                if submission_found:
                    # Convert AssignmentSubmission object to a dictionary for consistent access in Jinja
                    display_submissions.append({
                        'id': submission_found.id,
                        'assignment_id': submission_found.assignment_id,
                        'student_id': submission_found.student_id,
                        'content': submission_found.content,
                        'submitted_at': submission_found.submitted_at,
                        'score': submission_found.score,
                        'feedback': submission_found.feedback,
                        'file_path': submission_found.file_path,
                        'original_filename': submission_found.original_filename,
                        'student': submission_found.student, # Still pass the student object
                        'is_submitted': True
                    })
                else:
                    # Tambahkan placeholder untuk siswa yang belum mengumpulkan
                    display_submissions.append({
                        'id': None, # Set ID to None for placeholders
                        'assignment_id': assignment.id,
                        'student_id': student.id,
                        'content': 'Belum Mengumpulkan',
                        'submitted_at': None,
                        'score': None,
                        'feedback': None,
                        'file_path': None,
                        'original_filename': None,
                        'student': student,
                        'is_submitted': False # Flag untuk membedakan
                    })
            
            # Urutkan berdasarkan kelas, lalu nama siswa
            display_submissions.sort(key=lambda x: (x['student'].kelas if 'student' in x and x['student'].kelas else '', 
                                                      x['student'].username if 'student' in x and x['student'].username else ''))

            filtered_submissions_by_assignment[assignment.id] = display_submissions

        return render_template('view_course.html', 
                               course=course, 
                               unique_classes=unique_classes, 
                               selected_class=selected_class,
                               filtered_submissions_by_assignment=filtered_submissions_by_assignment)
    else:
        # Untuk siswa atau user lain, tidak ada filter kelas
        forum_posts = ForumPost.query.filter_by(course_id=course.id).order_by(ForumPost.created_at.desc()).all()
        return render_template('view_course.html', course=course, forum_posts=forum_posts)

# Route untuk melihat profil
@app.route('/profile')
@login_required
def profile():
    if current_user.role == 'guru':
        # Ambil daftar mata pelajaran yang diajar
        courses = Course.query.filter_by(instructor_id=current_user.id).all()
        return render_template('profile.html', user=current_user, courses=courses)
    else:
        # Ambil daftar mata pelajaran untuk kelas siswa
        courses = Course.query.all()  # Karena siswa bisa akses semua mata pelajaran
        return render_template('profile.html', user=current_user, courses=courses)

# Route untuk membuat kuis baru
@app.route('/course/<int:course_id>/add_quiz', methods=['GET', 'POST'])
@login_required
def add_quiz(course_id):
    course = Course.query.get_or_404(course_id)
    if current_user.id != course.instructor_id:
        flash('Anda tidak memiliki akses untuk menambah kuis.', 'error')
        return redirect(url_for('courses'))

    if request.method == 'POST':
        material_id = request.args.get('materi_id') # Get materi_id from query string
        quiz = Quiz(
            title=request.form.get('title'),
            description=request.form.get('description'),
            course_id=course_id,
            material_id=material_id, # Save material_id
            due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
        )
        db.session.add(quiz)
        db.session.flush()  # Untuk mendapatkan ID quiz

        # Tambah pertanyaan kuis
        questions = request.form.getlist('questions[]')
        all_options = request.form.getlist('options[]') # Ambil semua opsi dalam satu list datar
        correct_answers = request.form.getlist('correct_answers[]')
        points = request.form.getlist('points[]')

        options_per_question = 4 # Asumsi setiap pertanyaan memiliki 4 pilihan

        for i in range(len(questions)):
            # Ambil 4 opsi untuk pertanyaan saat ini
            start_index = i * options_per_question
            end_index = start_index + options_per_question
            current_question_options = [opt.strip() for opt in all_options[start_index:end_index]]
            
            question = QuizQuestion(
                quiz_id=quiz.id,
                question=questions[i],
                correct_answer=correct_answers[i],
                points=int(points[i])
            )
            question.set_options(current_question_options)  # Gunakan method set_options
            db.session.add(question)
        
        db.session.commit()

        # Kirim notifikasi ke semua siswa
        students = User.query.filter_by(role='siswa').all()
        for student in students:
            create_notification(
                student.id,
                f"Kuis Baru - {course.title}",
                f"Ada kuis baru: {quiz.title}. Batas waktu: {quiz.due_date.strftime('%d %B %Y')}",
                "kuis"
            )

        flash('Kuis berhasil ditambahkan!', 'success')
        return redirect(url_for('view_course', course_id=course_id))
    return render_template('add_quiz.html', course=course)

# Route untuk mengerjakan kuis
@app.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if current_user.role != 'siswa':
        flash('Hanya siswa yang dapat mengerjakan kuis.', 'error')
        return redirect(url_for('view_course', course_id=quiz.course_id))

    # Cek apakah siswa sudah mengerjakan kuis ini
    existing_result = QuizResult.query.filter_by(
        quiz_id=quiz_id,
        student_id=current_user.id
    ).first()

    # Jika sudah pernah submit, redirect ke hasil
    if existing_result:
        return redirect(url_for('view_quiz_result', quiz_id=quiz_id))

    if request.method == 'POST':
        score = 0
        total_points = 0
        student_submitted_answers = {}
        for question in quiz.questions:
            answer = request.form.get(f'answer_{question.id}')
            student_submitted_answers[question.id] = answer # Store the student's answer (should be A/B/C/D)
            # Penilaian berdasarkan huruf pilihan (A/B/C/D)
            if answer is not None and question.correct_answer is not None:
                if answer.strip().upper() == question.correct_answer.strip().upper():
                    score += question.points
            total_points += question.points
        percentage = (score / total_points) * 100 if total_points > 0 else 0
        result = QuizResult(
            quiz_id=quiz_id,
            student_id=current_user.id,
            score=percentage,
            student_answers=json.dumps(student_submitted_answers) # Save answers as JSON
        )
        db.session.add(result)
        db.session.commit()
        # Notifikasi ke guru pengampu
        create_notification(
            quiz.course.instructor_id,
            f"Siswa Mengerjakan Kuis",
            f"{current_user.username} telah mengerjakan kuis {quiz.title}",
            "kuis"
        )
        flash('Kuis berhasil dikerjakan!', 'success')
        return redirect(url_for('view_quiz_result', quiz_id=quiz_id))

    return render_template('take_quiz.html', quiz=quiz)

# Route untuk melihat hasil kuis
@app.route('/quiz/<int:quiz_id>/result')
@login_required
def view_quiz_result(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if current_user.role != 'siswa':
        flash('Hanya siswa yang dapat melihat hasil kuis.', 'error')
        return redirect(url_for('view_course', course_id=quiz.course_id))

    result = QuizResult.query.filter_by(
        quiz_id=quiz_id,
        student_id=current_user.id
    ).first_or_404()

    # Ambil jawaban siswa dari kolom student_answers
    student_answers = json.loads(result.student_answers) if result.student_answers else {}

    return render_template('quiz_result.html',
                         quiz=quiz,
                         result=result,
                         answers=student_answers) # Pass student_answers to template

# Route untuk membuat tugas baru
@app.route('/course/<int:course_id>/add_assignment', methods=['GET', 'POST'])
@login_required
def add_assignment(course_id):
    course = Course.query.get_or_404(course_id)
    if current_user.id != course.instructor_id:
        flash('Anda tidak memiliki akses untuk menambah tugas.', 'error')
        return redirect(url_for('courses'))

    if request.method == 'POST':
        material_id = request.args.get('materi_id') # Get materi_id from query string
        assignment = Assignment(
            title=request.form.get('title'),
            description=request.form.get('description'),
            course_id=course_id,
            material_id=material_id, # Save material_id
            due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
        )
        
        # Handle file upload for teacher's assignment file
        if 'task_file' in request.files:
            task_file = request.files['task_file']
            if task_file and allowed_assignment_file(task_file.filename):
                from werkzeug.utils import secure_filename
                import time, os
                
                filename = secure_filename(f"assignment_task_{int(time.time())}_{os.path.splitext(task_file.filename)[0]}{os.path.splitext(task_file.filename)[1]}")
                upload_dir = os.path.join('static', 'uploads', 'assignment_tasks')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                task_file.save(os.path.join(upload_dir, filename))
                assignment.task_file_path = filename
                assignment.task_original_filename = task_file.filename

        db.session.add(assignment)
        db.session.commit()

        # Kirim notifikasi ke semua siswa
        students = User.query.filter_by(role='siswa').all()
        for student in students:
            create_notification(
                student.id,
                f"Tugas Baru - {course.title}",
                f"Ada tugas baru: {assignment.title}. Batas waktu: {assignment.due_date.strftime('%d %B %Y')}",
                "tugas"
            )
        
        flash('Tugas berhasil ditambahkan!', 'success')
        return redirect(url_for('view_course', course_id=course_id))
    
    return render_template('add_assignment.html', course=course)

# Route untuk mengumpulkan tugas
@app.route('/assignment/<int:assignment_id>/submit', methods=['GET', 'POST'])
@login_required
def submit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    if current_user.role != 'siswa':
        flash('Hanya siswa yang dapat mengumpulkan tugas.', 'error')
        return redirect(url_for('view_course', course_id=assignment.course_id))

    existing_submission = AssignmentSubmission.query.filter_by(
        assignment_id=assignment_id,
        student_id=current_user.id
    ).first()

    now = datetime.utcnow()
    is_late = assignment.due_date and now > assignment.due_date

    if request.method == 'POST':
        if is_late:
            flash('Waktu pengumpulan sudah habis. Anda tidak dapat mengedit tugas.', 'error')
            return redirect(url_for('submit_assignment', assignment_id=assignment_id))
        content = request.form.get('content')
        file = request.files.get('submission_file')
        if existing_submission:
            existing_submission.content = content
            existing_submission.submitted_at = now
            # Handle upload file
            if file and file.filename:
                from werkzeug.utils import secure_filename
                import time, os
                filename = secure_filename(f"assignment_{assignment_id}_{current_user.id}_{int(time.time())}{os.path.splitext(file.filename)[1]}")
                upload_dir = os.path.join('static', 'uploads')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                file.save(os.path.join(upload_dir, filename))
                # Hapus file lama jika ada dan berbeda
                if existing_submission.file_path and existing_submission.file_path != filename:
                    old_file = os.path.join(upload_dir, existing_submission.file_path)
                    if os.path.exists(old_file):
                        os.remove(old_file)
                existing_submission.file_path = filename
                existing_submission.original_filename = file.filename
        else:
            submission = AssignmentSubmission(
                assignment_id=assignment_id,
                student_id=current_user.id,
                content=content
            )
            # Handle upload file
            if file and file.filename:
                from werkzeug.utils import secure_filename
                import time, os
                filename = secure_filename(f"assignment_{assignment_id}_{current_user.id}_{int(time.time())}{os.path.splitext(file.filename)[1]}")
                upload_dir = os.path.join('static', 'uploads')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                file.save(os.path.join(upload_dir, filename))
                submission.file_path = filename
                submission.original_filename = file.filename
            db.session.add(submission)
        db.session.commit()
        # Notifikasi ke guru pengampu
        create_notification(
            assignment.course.instructor_id,
            f"Siswa Mengumpulkan Tugas",
            f"{current_user.username} telah mengumpulkan tugas {assignment.title}",
            "tugas"
        )
        flash('Tugas berhasil dikumpulkan!', 'success')
        return redirect(url_for('view_course', course_id=assignment.course_id))
    return render_template('submit_assignment.html', 
                         assignment=assignment, 
                         existing_submission=existing_submission,
                         is_late=is_late)

# Route untuk melihat dan menilai semua pengumpulan tugas untuk tugas tertentu
@app.route('/assignment/<int:assignment_id>/submissions', methods=['GET', 'POST'])
@login_required
def assignment_submissions(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Hanya guru pengampu yang boleh mengakses
    if current_user.id != assignment.course.instructor_id:
        flash('Anda tidak memiliki akses untuk melihat pengumpulan tugas ini.', 'error')
        return redirect(url_for('view_course', course_id=assignment.course_id))
    
    # Filter berdasarkan kelas
    selected_class = request.args.get('kelas')

    submissions_query = AssignmentSubmission.query.filter_by(assignment_id=assignment_id).join(User)

    if selected_class and selected_class != 'all':
        submissions_query = submissions_query.filter(User.kelas == selected_class)
    
    submissions = submissions_query.all()
    
    # Ambil daftar kelas unik untuk filter dropdown
    unique_classes = db.session.query(distinct(User.kelas)).filter(User.role == 'siswa').order_by(User.kelas).all()
    unique_classes = [c[0] for c in unique_classes if c[0] is not None] # Hapus None jika ada

    # Ambil semua siswa untuk mengisi data yang belum mengumpulkan
    all_students_in_course = User.query.filter_by(role='siswa').all()
    if selected_class and selected_class != 'all':
        all_students_in_course = User.query.filter_by(role='siswa', kelas=selected_class).all()

    # Buat dictionary untuk pengumpulan yang sudah ada agar mudah diakses
    submitted_students = {sub.student_id for sub in submissions}
    
    # Buat daftar yang menggabungkan siswa yang sudah submit dan yang belum
    display_submissions = []
    for student in all_students_in_course:
        submission_found = next((sub for sub in submissions if sub.student_id == student.id), None)
        if submission_found:
            display_submissions.append(submission_found)
        else:
            # Tambahkan placeholder untuk siswa yang belum mengumpulkan
            display_submissions.append({
                'student': student,
                'content': 'Belum Mengumpulkan',
                'submitted_at': None,
                'score': None,
                'feedback': None,
                'file_path': None,
                'original_filename': None,
                'is_submitted': False # Flag untuk membedakan
            })
    
    # Urutkan berdasarkan kelas, lalu nama siswa
    display_submissions.sort(key=lambda x: (x['student'].kelas if 'student' in x and x['student'].kelas else '', 
                                              x['student'].username if 'student' in x and x['student'].username else ''))
    
    return render_template('assignment_submissions.html',
                           assignment=assignment,
                           submissions=display_submissions,
                           unique_classes=unique_classes,
                           selected_class=selected_class)

# Route untuk menilai tugas (guru)
@app.route('/assignment/<int:assignment_id>/grade/<int:submission_id>', methods=['GET', 'POST'])
@login_required
def grade_assignment(assignment_id, submission_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    submission = AssignmentSubmission.query.get_or_404(submission_id)
    
    if current_user.id != assignment.course.instructor_id:
        flash('Anda tidak memiliki akses untuk menilai tugas.', 'error')
        return redirect(url_for('courses'))

    if request.method == 'POST':
        submission.score = float(request.form.get('score'))
        submission.feedback = request.form.get('feedback')
        db.session.commit()

        # Kirim notifikasi ke siswa
        create_notification(
            submission.student_id,
            f"Nilai Tugas - {assignment.title}",
            f"Tugas Anda telah dinilai. Nilai: {submission.score}",
            "nilai"
        )
        
        flash('Nilai berhasil diberikan!', 'success')
        return redirect(url_for('view_course', course_id=assignment.course_id))
    
    return render_template('grade_assignment.html', 
                         assignment=assignment, 
                         submission=submission)

# Helper function untuk menghitung nilai akhir
def calculate_final_grade(quiz_results, assignment_submissions, total_quiz=0, total_assignment=0):
    # total_quiz dan total_assignment adalah jumlah kuis/tugas yang tersedia untuk pelajaran ini
    # quiz_results dan assignment_submissions adalah list hasil siswa
    quiz_scores = [result.score if result.score is not None else 0 for result in quiz_results] if quiz_results else []
    assignment_scores = [sub.score if sub.score is not None else 0 for sub in assignment_submissions] if assignment_submissions else []

    # Jika tidak ada kuis sama sekali, bobot kuis = 0
    quiz_weight = 0.4 if total_quiz > 0 else 0
    assignment_weight = 0.6 if total_assignment > 0 else 0
    total_weight = quiz_weight + assignment_weight
    if total_weight == 0:
        return None

    quiz_average = sum(quiz_scores) / total_quiz if total_quiz > 0 else 0
    assignment_average = sum(assignment_scores) / total_assignment if total_assignment > 0 else 0
    final_score = (quiz_average * quiz_weight + assignment_average * assignment_weight) / total_weight
    return final_score

# Helper function untuk mendapatkan grade letter
def get_grade_letter(score):
    if score is None:
        return '-'
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'E'

# Filter kustom untuk format tanggal
@app.template_filter('format_date')
def format_date(value):
    if value is None:
        return '-'
    try:
        if isinstance(value, (datetime, date)):
            return value.strftime('%d %B %Y')
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime('%d %B %Y')
            except ValueError:
                return value
        return str(value)
    except Exception as e:
        print(f"Error formatting date: {str(e)}")
        return str(value)

# Route untuk melihat nilai
@app.route('/grades')
@login_required
def grades():
    if current_user.role == 'siswa':
        courses = Course.query.all()
        course_grades = {}
        
        for course in courses:
            quiz_results = QuizResult.query.filter_by(
                student_id=current_user.id
            ).join(QuizResult.quiz).filter(
                Quiz.course_id == course.id
            ).all()
            
            assignment_submissions = AssignmentSubmission.query.filter_by(
                student_id=current_user.id
            ).join(AssignmentSubmission.assignment).filter(
                Assignment.course_id == course.id
            ).all()
            
            total_quiz = len(course.quizzes)
            total_assignment = len(course.assignments)
            final_grade = calculate_final_grade(quiz_results, assignment_submissions, total_quiz, total_assignment)
            grade_letter = get_grade_letter(final_grade)
            
            # Format tanggal saat menyimpan data
            quiz_grades = {
                quiz.quiz.title: {
                    'score': quiz.score,
                    'date': quiz.submitted_at,  # Kirim datetime object langsung
                    'max_score': 100
                } for quiz in quiz_results
            }
            
            assignment_grades = {
                sub.assignment.title: {
                    'score': sub.score,
                    'file_path': sub.file_path,
                    'original_filename': sub.original_filename,
                    'date': sub.submitted_at,  # Menambahkan tanggal pengumpulan
                    'feedback': sub.feedback # Menambahkan feedback
                }
                for sub in assignment_submissions if sub.score is not None or sub.file_path
            }
            
            course_grades[course.id] = {
                'course': course,
                'quiz_grades': quiz_grades,
                'assignment_grades': assignment_grades,
                'final_grade': final_grade,
                'grade_letter': grade_letter,
                'instructor': course.instructor
            }
        
        # Hitung rata-rata nilai akhir keseluruhan
        all_final_grades = [data['final_grade'] for data in course_grades.values() if data['final_grade'] is not None]
        overall_final_grade = sum(all_final_grades) / len(all_final_grades) if all_final_grades else 0.0 # Tampilkan 0.0 jika tidak ada nilai
        overall_grade_letter = get_grade_letter(overall_final_grade)

        return render_template('grades.html', 
                             course_grades=course_grades,
                             is_student=True,
                             overall_final_grade=overall_final_grade,
                             overall_grade_letter=overall_grade_letter)
    else:
        # Untuk guru, tampilkan daftar siswa dan nilai mereka di mata pelajaran yang diajar
        courses = Course.query.filter_by(instructor_id=current_user.id).all()
        # Ambil semua kelas unik
        all_classes = sorted(set([s.kelas for s in User.query.filter_by(role='siswa').all() if s.kelas]))
        selected_class = request.args.get('kelas')
        if selected_class:
            students = User.query.filter_by(role='siswa', kelas=selected_class).all()
        else:
            students = User.query.filter_by(role='siswa').all()
        # Siapkan data untuk setiap mata pelajaran
        course_data = {}
        for course in courses:
            student_grades = {}
            total_quiz = len(course.quizzes)
            total_assignment = len(course.assignments)
            for student in students:
                # Ambil nilai kuis
                quiz_results = QuizResult.query.filter_by(
                    student_id=student.id
                ).join(QuizResult.quiz).filter(
                    Quiz.course_id == course.id
                ).all()
                
                # Ambil nilai tugas
                assignment_submissions = AssignmentSubmission.query.filter_by(
                    student_id=student.id
                ).join(AssignmentSubmission.assignment).filter(
                    Assignment.course_id == course.id
                ).all()
                
                # Hitung nilai akhir
                final_grade = calculate_final_grade(quiz_results, assignment_submissions, total_quiz, total_assignment)
                grade_letter = get_grade_letter(final_grade)
                
                # Kelompokkan nilai
                quiz_grades = {
                    quiz.quiz.title: quiz.score for quiz in quiz_results
                }
                
                assignment_grades = {
                    sub.assignment.title: {
                        'score': sub.score,
                        'file_path': sub.file_path,
                        'original_filename': sub.original_filename,
                        'date': sub.submitted_at,  # Menambahkan tanggal pengumpulan
                        'feedback': sub.feedback # Menambahkan feedback
                    }
                    for sub in assignment_submissions if sub.score is not None or sub.file_path
                }
                
                student_grades[student.id] = {
                    'student': student,
                    'quiz_grades': quiz_grades,
                    'assignment_grades': assignment_grades,
                    'final_grade': final_grade,
                    'grade_letter': grade_letter
                }
            
            # Hitung statistik kelas
            final_grades = [data['final_grade'] for data in student_grades.values() 
                          if data['final_grade'] is not None]
            
            if final_grades:
                course_stats = {
                    'average': sum(final_grades) / len(final_grades),
                    'highest': max(final_grades),
                    'lowest': min(final_grades),
                    'passing_count': sum(1 for grade in final_grades if grade >= 70),
                    'total_students': len(final_grades)
                }
            else:
                course_stats = {
                    'average': None,
                    'highest': None,
                    'lowest': None,
                    'passing_count': 0,
                    'total_students': 0
                }
            
            course_data[course.id] = {
                'course': course,
                'student_grades': student_grades,
                'stats': course_stats
            }
        
        return render_template('grades.html', 
                             course_data=course_data,
                             is_student=False,
                             all_classes=all_classes,
                             selected_class=selected_class)

# Route untuk melihat notifikasi
@app.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifications)

# Route untuk menandai notifikasi sebagai telah dibaca
@app.route('/notification/read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id == current_user.id:
        notification.is_read = True
        db.session.commit()
    return redirect(url_for('notifications'))

# Routes untuk Forum Diskusi
@app.route('/course/<int:course_id>/forum')
@login_required
def course_forum(course_id):
    course = Course.query.get_or_404(course_id)
    posts = ForumPost.query.filter_by(course_id=course_id).order_by(ForumPost.created_at.desc()).all()
    return render_template('forum/index.html', course=course, posts=posts)

@app.route('/course/<int:course_id>/forum/create', methods=['GET', 'POST'])
@login_required
def create_forum_post(course_id):
    course = Course.query.get_or_404(course_id)
    if request.method == 'POST':
        post = ForumPost(
            title=request.form.get('title'),
            content=request.form.get('content'),
            course_id=course_id,
            user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        # Notifikasi ke semua siswa di course
        students = User.query.filter_by(role='siswa').all()
        for student in students:
            create_notification(
                student.id,
                "Diskusi Baru",
                f"Diskusi baru: {post.title} telah dibuat di {course.title}",
                "forum"
            )
        flash('Diskusi baru berhasil dibuat!', 'success')
        return redirect(url_for('course_forum', course_id=course_id))
    return render_template('forum/create.html', course=course)

@app.route('/forum/post/<int:post_id>')
@login_required
def view_forum_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    return render_template('forum/view.html', post=post)

@app.route('/forum/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_forum_comment(post_id):
    post = ForumPost.query.get_or_404(post_id)
    comment = ForumComment(
        content=request.form.get('content'),
        post_id=post_id,
        user_id=current_user.id
    )
    db.session.add(comment)
    db.session.commit()
    flash('Komentar berhasil ditambahkan!', 'success')
    return redirect(url_for('view_forum_post', post_id=post_id))

@app.route('/forum/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_forum_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    if current_user.id != post.user_id:
        flash('Anda tidak memiliki akses untuk mengedit diskusi ini.', 'error')
        return redirect(url_for('view_forum_post', post_id=post_id))
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        db.session.commit()
        flash('Diskusi berhasil diperbarui!', 'success')
        return redirect(url_for('view_forum_post', post_id=post_id))
    return render_template('forum/edit.html', post=post)

@app.route('/forum/post/<int:post_id>/delete')
@login_required
def delete_forum_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    if current_user.id != post.user_id and current_user.role != 'guru':
        flash('Anda tidak memiliki akses untuk menghapus diskusi ini.', 'error')
        return redirect(url_for('view_forum_post', post_id=post_id))
    
    course_id = post.course_id
    db.session.delete(post)
    db.session.commit()
    flash('Diskusi berhasil dihapus!', 'success')
    return redirect(url_for('course_forum', course_id=course_id))

# Route untuk mengedit materi
@app.route('/material/<int:material_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_material(material_id):
    material = Material.query.get_or_404(material_id)
    course = material.course
    
    if current_user.id != course.instructor_id:
        flash('Anda tidak memiliki akses untuk mengedit materi ini.', 'error')
        return redirect(url_for('view_course', course_id=course.id))
    
    if request.method == 'POST':
        material.title = request.form.get('title')
        material.content = request.form.get('content')
        material.youtube_url = request.form.get('youtube_url')

        # Handle upload file materi
        if 'material_file' in request.files:
            file = request.files['material_file']
            if file and file.filename:
                if not allowed_material_file(file.filename):
                    flash('Format file tidak diizinkan. Gunakan PDF, DOC, DOCX, TXT, PNG, JPG, JPEG, GIF, PPT, PPTX, XLS, atau XLSX.', 'error')
                    return redirect(url_for('edit_material', material_id=material_id))
                
                from werkzeug.utils import secure_filename
                import time, os
                filename = secure_filename(f"material_{material.id}_{int(time.time())}{os.path.splitext(file.filename)[1]}")
                upload_dir = os.path.join('static', 'uploads', 'materials')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                file.save(os.path.join(upload_dir, filename))
                # Hapus file lama jika ada dan berbeda
                if material.file_path and material.file_path != filename:
                    old_file = os.path.join(upload_dir, material.file_path)
                    if os.path.exists(old_file):
                        os.remove(old_file)
                material.file_path = filename
                material.original_filename = file.filename
        db.session.commit()
        flash('Materi berhasil diperbarui!', 'success')
        return redirect(url_for('view_course', course_id=course.id))
    
    return render_template('edit_material.html', material=material)

# Route untuk menghapus materi
@app.route('/material/<int:material_id>/delete')
@login_required
def delete_material(material_id):
    material = Material.query.get_or_404(material_id)
    course = material.course
    
    if current_user.id != course.instructor_id:
        flash('Anda tidak memiliki akses untuk menghapus materi ini.', 'error')
        return redirect(url_for('view_course', course_id=course.id))
    
    db.session.delete(material)
    db.session.commit()
    flash('Materi berhasil dihapus!', 'success')
    return redirect(url_for('view_course', course_id=course.id))

# Route untuk mengedit kuis
@app.route('/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    course = quiz.course
    
    if current_user.id != course.instructor_id:
        flash('Anda tidak memiliki akses untuk mengedit kuis ini.', 'error')
        return redirect(url_for('view_course', course_id=course.id))
    
    if request.method == 'POST':
        quiz.title = request.form.get('title')
        quiz.description = request.form.get('description')
        quiz.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
        
        # Hapus pertanyaan lama
        QuizQuestion.query.filter_by(quiz_id=quiz.id).delete()
        
        # Tambah pertanyaan baru
        questions = request.form.getlist('question[]')
        all_options = request.form.getlist('options[]') # Ambil semua opsi dalam satu list datar
        correct_answers = request.form.getlist('correct_answer[]')
        points = request.form.getlist('points[]')

        options_per_question = 4 # Asumsi setiap pertanyaan memiliki 4 pilihan

        for i in range(len(questions)):
            # Ambil 4 opsi untuk pertanyaan saat ini
            start_index = i * options_per_question
            end_index = start_index + options_per_question
            current_question_options = [opt.strip() for opt in all_options[start_index:end_index]]
            
            question = QuizQuestion(
                quiz_id=quiz.id,
                question=questions[i],
                correct_answer=correct_answers[i],
                points=int(points[i])
            )
            question.set_options(current_question_options)  # Gunakan method set_options
            db.session.add(question)
        
        db.session.commit()
        flash('Kuis berhasil diperbarui!', 'success')
        return redirect(url_for('view_course', course_id=course.id))
    
    return render_template('edit_quiz.html', quiz=quiz)

# Route untuk menghapus kuis
@app.route('/quiz/<int:quiz_id>/delete')
@login_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    course = quiz.course
    
    if current_user.id != course.instructor_id:
        flash('Anda tidak memiliki akses untuk menghapus kuis ini.', 'error')
        return redirect(url_for('view_course', course_id=course.id))
    
    db.session.delete(quiz)
    db.session.commit()
    flash('Kuis berhasil dihapus!', 'success')
    return redirect(url_for('view_course', course_id=course.id))

# Route untuk mengedit tugas
@app.route('/assignment/<int:assignment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    course = assignment.course
    
    if current_user.id != course.instructor_id:
        flash('Anda tidak memiliki akses untuk mengedit tugas ini.', 'error')
        return redirect(url_for('view_course', course_id=course.id))
    
    if request.method == 'POST':
        assignment.title = request.form.get('title')
        assignment.description = request.form.get('description')
        assignment.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')

        # Handle file upload for teacher's assignment file
        if 'task_file' in request.files:
            task_file = request.files['task_file']
            if task_file and task_file.filename:
                if not allowed_assignment_file(task_file.filename):
                    flash('Format file tidak diizinkan. Gunakan PDF, DOC, DOCX, TXT, PNG, JPG, JPEG, GIF.', 'error')
                    return redirect(url_for('edit_assignment', assignment_id=assignment.id))
                from werkzeug.utils import secure_filename
                import time, os
                filename = secure_filename(f"assignment_task_{int(time.time())}_{os.path.splitext(task_file.filename)[0]}{os.path.splitext(task_file.filename)[1]}")
                upload_dir = os.path.join('static', 'uploads', 'assignment_tasks')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                task_file.save(os.path.join(upload_dir, filename))
                # Hapus file lama jika ada dan berbeda
                if assignment.task_file_path and assignment.task_file_path != filename:
                    old_file = os.path.join(upload_dir, assignment.task_file_path)
                    if os.path.exists(old_file):
                        os.remove(old_file)
                assignment.task_file_path = filename
                assignment.task_original_filename = task_file.filename

        db.session.commit()
        flash('Tugas berhasil diperbarui!', 'success')
        return redirect(url_for('view_course', course_id=course.id))
    
    return render_template('edit_assignment.html', assignment=assignment)

# Route untuk menghapus tugas
@app.route('/assignment/<int:assignment_id>/delete')
@login_required
def delete_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    course = assignment.course
    
    if current_user.id != course.instructor_id:
        flash('Anda tidak memiliki akses untuk menghapus tugas ini.', 'error')
        return redirect(url_for('view_course', course_id=course.id))
    
    db.session.delete(assignment)
    db.session.commit()
    flash('Tugas berhasil dihapus!', 'success')
    return redirect(url_for('view_course', course_id=course.id))

# Route untuk update profil
@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        # Validasi password saat ini
        current_password = request.form.get('current_password')
        if not check_password_hash(current_user.password_hash, current_password):
            flash('Password saat ini salah.', 'error')
            return redirect(url_for('profile'))

        # Update username dan email
        username = request.form.get('username')
        email = request.form.get('email')

        # Cek apakah username sudah digunakan (kecuali oleh user saat ini)
        existing_user = User.query.filter(
            User.username == username,
            User.id != current_user.id
        ).first()
        if existing_user:
            flash('Username sudah digunakan.', 'error')
            return redirect(url_for('profile'))

        # Cek apakah email sudah digunakan (kecuali oleh user saat ini)
        existing_user = User.query.filter(
            User.email == email,
            User.id != current_user.id
        ).first()
        if existing_user:
            flash('Email sudah digunakan.', 'error')
            return redirect(url_for('profile'))

        # Update password jika diisi
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password:
            if new_password != confirm_password:
                flash('Password baru dan konfirmasi password tidak cocok.', 'error')
                return redirect(url_for('profile'))
            current_user.password_hash = generate_password_hash(new_password)

        # Update data user
        current_user.username = username
        current_user.email = email
        
        try:
            db.session.commit()
            flash('Profil berhasil diperbarui!', 'success')
        except:
            db.session.rollback()
            flash('Terjadi kesalahan saat memperbarui profil.', 'error')
            
        return redirect(url_for('profile'))

# Route untuk halaman bantuan
@app.route('/help', endpoint='help')
def help_page():
    return render_template('help.html')

# Route untuk halaman pengembang
@app.route('/developers', endpoint='developers')
def developers_page():
    return render_template('developers.html')

def create_notification(user_id, title, message, type):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type
    )
    db.session.add(notification)
    db.session.commit()

# Route untuk presensi
@app.route('/course/<int:course_id>/attendance/', methods=['GET'])
@app.route('/course/<int:course_id>/attendance', methods=['GET'])
@login_required
def attendance(course_id):
    try:
        # Debug: Print course_id
        print(f"Accessing attendance for course_id: {course_id}")
        
        course = Course.query.get_or_404(course_id)
        # Debug: Print course details
        print(f"Course found: {course.title}")
        
        today = date.today()
        current_time = datetime.now().time()
        
        if current_user.role == 'siswa':
            # Debug: Print student details
            print(f"Student accessing: {current_user.username}")
            
            # Cek apakah sudah presensi hari ini untuk mata pelajaran ini
            today_attendance = Attendance.query.filter_by(
                student_id=current_user.id,
                course_id=course_id,
                date=today
            ).first()
            
            # Ambil riwayat kehadiran untuk mata pelajaran ini
            attendance_history = Attendance.query.filter_by(
                student_id=current_user.id,
                course_id=course_id
            ).order_by(Attendance.date.desc()).all()
            
            return render_template('attendance.html',
                course=course,
                today=today,
                current_time=current_time,
                has_attended=bool(today_attendance),
                attendance=today_attendance,
                attendance_history=attendance_history
            )
        else:
            # Debug: Print teacher details
            print(f"Teacher accessing: {current_user.username}")
            
            # Untuk guru: tampilkan rekap kehadiran siswa di mata pelajaran yang diampu
            if current_user.id != course.instructor_id:
                flash('Anda tidak memiliki akses ke presensi mata pelajaran ini.', 'error')
                return redirect(url_for('courses'))
                
            classes = db.session.query(User.kelas).filter_by(role='siswa').distinct().all()
            classes = [c[0] for c in classes if c[0]]  # Filter out None values
            
            # Default: tampilkan kehadiran hari ini untuk mata pelajaran ini
            student_attendance = Attendance.query.filter_by(
                course_id=course_id,
                date=today
            ).join(Attendance.student)\
             .filter(User.role == 'siswa')\
             .order_by(User.kelas, User.username).all()
            
            # Hitung statistik untuk mata pelajaran ini
            total_records = len(student_attendance) or 1  # Avoid division by zero
            stats = {
                'present': int(sum(1 for a in student_attendance if a.status == 'hadir') / total_records * 100),
                'sick': int(sum(1 for a in student_attendance if a.status == 'sakit') / total_records * 100),
                'permission': int(sum(1 for a in student_attendance if a.status == 'izin') / total_records * 100)
            }
            
            return render_template('attendance.html',
                course=course,
                today=today,
                current_time=current_time,
                classes=classes,
                student_attendance=student_attendance,
                stats=stats
            )
    except Exception as e:
        # Print detailed error information
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in attendance route: {str(e)}")
        print(f"Detailed error: {error_details}")
        
        # Show more specific error message to user
        if isinstance(e, AttributeError):
            flash('Terjadi kesalahan saat mengakses data. Mohon pastikan data mata pelajaran valid.', 'error')
        elif isinstance(e, KeyError):
            flash('Terjadi kesalahan saat memproses data. Mohon coba lagi.', 'error')
        else:
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
        
        return redirect(url_for('view_course', course_id=course_id))

@app.route('/course/<int:course_id>/attendance/submit', methods=['POST'])
@login_required
def submit_attendance(course_id):
    if current_user.role != 'siswa':
        flash('Hanya siswa yang dapat melakukan presensi.', 'error')
        return redirect(url_for('attendance', course_id=course_id))
    
    course = Course.query.get_or_404(course_id)
    today = date.today()
    
    # Cek apakah sudah presensi hari ini untuk mata pelajaran ini
    existing_attendance = Attendance.query.filter_by(
        student_id=current_user.id,
        course_id=course_id,
        date=today
    ).first()
    
    if existing_attendance:
        flash('Anda sudah melakukan presensi untuk mata pelajaran ini hari ini.', 'warning')
    else:
        # Simpan presensi baru
        attendance = Attendance(
            student_id=current_user.id,
            course_id=course_id,
            status=request.form.get('status'),
            notes=request.form.get('notes')
        )
        db.session.add(attendance)
        db.session.commit()
        flash('Presensi berhasil disimpan.', 'success')
    
    return redirect(url_for('attendance', course_id=course_id))

@app.route('/course/<int:course_id>/attendance/filter', methods=['POST'])
@login_required
def filter_attendance(course_id):
    course = Course.query.get_or_404(course_id)
    if current_user.role != 'guru' or current_user.id != course.instructor_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Perbaikan: baca data dari JSON, bukan form
    data = request.get_json()
    kelas = data.get('class')
    tanggal = data.get('date')
    
    query = Attendance.query.filter_by(course_id=course_id)\
        .join(Attendance.student)\
        .filter(User.role == 'siswa')
    
    if kelas:
        query = query.filter(User.kelas == kelas)
    if tanggal:
        query = query.filter(Attendance.date == datetime.strptime(tanggal, '%Y-%m-%d').date())
    
    records = query.order_by(User.kelas, User.username).all()
    
    # Format data untuk response
    data = [{
        'student_name': record.student.username,
        'class': record.student.kelas,
        'status': record.status,
        'time': record.time.strftime('%H:%M'),
        'notes': record.notes or '-'
    } for record in records]
    
    return jsonify(data)

# Route untuk upload foto profil
@app.route('/upload_profile_photo', methods=['POST'])
@login_required
def upload_profile_photo():
    if 'photo' not in request.files:
        flash('Tidak ada file yang dipilih', 'error')
        return redirect(url_for('profile'))
    
    photo = request.files['photo']
    if photo.filename == '':
        flash('Tidak ada file yang dipilih', 'error')
        return redirect(url_for('profile'))
    
    if photo and allowed_file(photo.filename):
        try:
            # Membuat nama file yang aman dengan timestamp
            timestamp = int(time.time())
            filename = secure_filename(f"{current_user.username}_{timestamp}{os.path.splitext(photo.filename)[1]}")
            
            # Pastikan direktori uploads ada
            upload_dir = os.path.join('static', 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Hapus foto lama jika bukan default
            if current_user.profile_photo and current_user.profile_photo != 'default.jpg':
                old_photo = os.path.join(upload_dir, current_user.profile_photo)
                if os.path.exists(old_photo):
                    os.remove(old_photo)
            
            # Simpan file baru
            photo_path = os.path.join(upload_dir, filename)
            photo.save(photo_path)
            
            # Update profil user
            current_user.profile_photo = filename
            db.session.commit()
            
            flash('Foto profil berhasil diperbarui!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan saat mengupload foto: {str(e)}', 'error')
    else:
        flash('Format file tidak diizinkan. Gunakan JPG, JPEG, atau PNG.', 'error')
    
    return redirect(url_for('profile'))

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/download_grades/<int:course_id>')
@login_required
def download_grades(course_id):
    if current_user.role != 'guru':
        flash('Anda tidak memiliki akses untuk mengunduh nilai', 'error')
        return redirect(url_for('grades'))
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id:
        flash('Anda tidak memiliki akses untuk mengunduh nilai kelas ini', 'error')
        return redirect(url_for('grades'))
    kelas = request.args.get('kelas')
    if kelas:
        students = User.query.filter_by(role='siswa', kelas=kelas).all()
    else:
        students = User.query.filter_by(role='siswa').all()
    # Data untuk Excel
    data = []
    quiz_headers = [quiz.title for quiz in course.quizzes]
    assignment_headers = [assignment.title for assignment in course.assignments]
    for student in students:
        student_data = {
            'Nama Siswa': student.username,
            'Email': student.email
        }
        # Get quiz results
        quiz_results = []
        for quiz in course.quizzes:
            result = QuizResult.query.filter_by(
                quiz_id=quiz.id,
                student_id=student.id
            ).first()
            student_data[quiz.title] = f"{result.score}" if result else "-"
            if result:
                quiz_results.append(result)
        
        # Get assignment submissions
        assignment_submissions = []
        for assignment in course.assignments:
            submission = AssignmentSubmission.query.filter_by(
                assignment_id=assignment.id,
                student_id=student.id
            ).first()
            if submission and submission.score is not None:
                student_data[assignment.title] = f"{submission.score}"
                assignment_submissions.append(submission)
            elif submission:
                student_data[assignment.title] = "Belum dinilai"
            else:
                student_data[assignment.title] = "-"
        
        # Calculate final grade
        final_grade = calculate_final_grade(
            quiz_results, 
            assignment_submissions,
            len(course.quizzes),
            len(course.assignments)
        )
        grade_letter = get_grade_letter(final_grade) if final_grade is not None else "-"
        
        # Add final grade and grade letter to student data
        student_data['Nilai Akhir'] = f"{final_grade}" if final_grade is not None else "-"
        student_data['Grade'] = grade_letter
        
        data.append(student_data)
    
    import pandas as pd
    from io import BytesIO
    df = pd.DataFrame(data)
    columns = ['Nama Siswa', 'Email'] + quiz_headers + assignment_headers + ['Nilai Akhir', 'Grade']
    df = df[columns]
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Nilai', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Nilai']
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#0d6efd',
            'font_color': 'white',
            'border': 1
        })
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        for idx, col in enumerate(df):
            series = df[col]
            max_len = max(
                series.astype(str).map(len).max(),
                len(str(series.name))
            ) + 2
            worksheet.set_column(idx, idx, max_len)
    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"nilai_{course.title.lower().replace(' ', '_')}{'_' + kelas if kelas else ''}_{timestamp}.xlsx"
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if profile_photo column exists
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('user')]
        
        if 'profile_photo' not in columns:
            # Add profile_photo column
            with db.engine.connect() as conn:
                conn.execute('ALTER TABLE user ADD COLUMN profile_photo VARCHAR(255) DEFAULT "default.jpg"')
                conn.commit()
            print("Added profile_photo column")
        
        # Update existing users with default profile photo
        try:
            users_without_photo = User.query.filter_by(profile_photo=None).all()
            for user in users_without_photo:
                user.profile_photo = 'default.jpg'
            db.session.commit()
            print("Updated users with default profile photo")
        except Exception as e:
            print(f"Error updating users: {str(e)}")
            db.session.rollback()

# Tambahkan filter from_json
@app.template_filter('from_json')
def from_json_filter(value):
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value

# Route untuk detail materi
@app.route('/material/<int:material_id>')
@login_required
def view_material(material_id):
    material = Material.query.get_or_404(material_id)
    course = Course.query.get_or_404(material.course_id)
    
    # Catat penyelesaian materi jika user adalah siswa
    if current_user.is_authenticated and current_user.role == 'siswa':
        existing_completion = MaterialCompletion.query.filter_by(
            student_id=current_user.id,
            material_id=material.id
        ).first()
        if not existing_completion:
            new_completion = MaterialCompletion(
                student_id=current_user.id,
                material_id=material.id
            )
            db.session.add(new_completion)
            db.session.commit()

    # Hanya tampilkan kuis dan tugas yang terkait dengan materi ini, ATAU yang tidak memiliki material_id (general)
    quizzes = Quiz.query.filter(
        Quiz.course_id == course.id,
        (Quiz.material_id == material.id) | (Quiz.material_id == None) # Filter kuis berdasarkan material_id atau jika material_id None
    ).all()
    assignments = Assignment.query.filter(
        Assignment.course_id == course.id,
        (Assignment.material_id == material.id) | (Assignment.material_id == None) # Filter tugas berdasarkan material_id atau jika material_id None
    ).all()

    # Mendapatkan status kuis dan tugas untuk siswa
    quiz_status = {}
    assignment_status = {}
    if current_user.role == 'siswa':
        for quiz in quizzes:
            quiz_status[quiz.id] = get_quiz_status_for_student(quiz, current_user.id)
        for assignment in assignments:
            assignment_status[assignment.id] = get_assignment_status_for_student(assignment, current_user.id)
    return render_template('material.html', material=material, course=course, quizzes=quizzes, assignments=assignments, quiz_status=quiz_status, assignment_status=assignment_status)

# Fungsi validasi file tugas
ALLOWED_ASSIGNMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'ppt', 'pptx'}
def allowed_assignment_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_ASSIGNMENT_EXTENSIONS

@app.route('/download_assignment_file/<filename>')
@login_required
def download_assignment_file(filename):
    # Hanya guru yang boleh download file jawaban siswa
    if current_user.role != 'guru':
        flash('Anda tidak memiliki akses untuk mendownload file ini.', 'error')
        return redirect(url_for('grades'))
    import os
    uploads_dir = os.path.join('static', 'uploads')
    assignment_tasks_dir = os.path.join('static', 'uploads', 'assignment_tasks')
    # Cek di uploads (jawaban siswa)
    file_path_uploads = os.path.join(uploads_dir, filename)
    file_path_tasks = os.path.join(assignment_tasks_dir, filename)
    if os.path.exists(file_path_uploads):
        # Cari submission berdasarkan file_path
        submission = AssignmentSubmission.query.filter_by(file_path=filename).first()
        if submission and submission.student and submission.assignment:
            nama_tugas = submission.assignment.title.replace(' ', '_')
            nama = submission.student.username.replace(' ', '_')
            kelas = (submission.student.kelas or 'unknown').replace(' ', '_')
            ext = os.path.splitext(filename)[1]
            download_name = f"{nama_tugas}_{nama}_{kelas}{ext}"
        else:
            download_name = filename
        return send_from_directory(uploads_dir, filename, as_attachment=True, download_name=download_name)
    elif os.path.exists(file_path_tasks):
        # File referensi/guru, gunakan nama asli
        return send_from_directory(assignment_tasks_dir, filename, as_attachment=True)
    else:
        from flask import abort
        abort(404)

@app.route('/preview_assignment_file/<filename>')
@login_required
def preview_assignment_file(filename):
    # Hanya guru yang boleh melihat pratinjau file jawaban siswa
    if current_user.role != 'guru':
        flash('Anda tidak memiliki akses untuk melihat pratinjau file ini.', 'error')
        return redirect(url_for('grades'))
    import os
    return send_from_directory(os.path.join('static', 'uploads', 'assignment_tasks'), filename, as_attachment=False)

def get_quiz_status_for_student(quiz, student_id):
    # Hanya return True jika ada QuizResult untuk quiz dan student_id
    return QuizResult.query.filter_by(quiz_id=quiz.id, student_id=student_id).first() is not None

def get_assignment_status_for_student(assignment, student_id):
    # Hanya return True jika ada AssignmentSubmission untuk assignment dan student_id
    return AssignmentSubmission.query.filter_by(assignment_id=assignment.id, student_id=student_id).first() is not None

@app.template_filter('simple_float')
def simple_float(value):
    try:
        if value is None:
            return '-'
        value = float(value)
        if value.is_integer():
            return str(int(value))
        return f"{value:.2f}".rstrip('0').rstrip('.')
    except Exception:
        return value

@app.route('/progress')
@login_required
def progress():
    if current_user.role != 'siswa':
        flash('Anda tidak memiliki akses ke halaman progres.', 'error')
        return redirect(url_for('index'))

    # Progres Materi
    total_materials = Material.query.join(Course).filter(Course.id == Material.course_id).count()
    materi_done = MaterialCompletion.query.filter_by(student_id=current_user.id).count()
    materi_total = total_materials
    materi_progress = (materi_done / materi_total) * 100 if materi_total > 0 else 0

    # Progres Kuis
    total_quizzes = Quiz.query.join(Course).filter(Course.id == Quiz.course_id).count()
    quizzes_done = QuizResult.query.filter_by(student_id=current_user.id).count()
    kuis_done = quizzes_done
    kuis_total = total_quizzes
    kuis_progress = (kuis_done / kuis_total) * 100 if kuis_total > 0 else 0

    # Progres Tugas
    total_assignments = Assignment.query.join(Course).filter(Course.id == Assignment.course_id).count()
    assignments_done = AssignmentSubmission.query.filter_by(student_id=current_user.id).count()
    tugas_done = assignments_done
    tugas_total = total_assignments
    tugas_progress = (tugas_done / tugas_total) * 100 if tugas_total > 0 else 0

    # Perbarui progres keseluruhan tanpa presensi
    overall_progress_percentage = 0
    if materi_total > 0 or kuis_total > 0 or tugas_total > 0:
        total_done_items = materi_done + kuis_done + tugas_done
        total_available_items = materi_total + kuis_total + tugas_total
        overall_progress_percentage = (total_done_items / total_available_items) * 100 if total_available_items > 0 else 0

    return render_template('progress.html',
        materi_progress=materi_progress, materi_done=materi_done, materi_total=materi_total,
        kuis_progress=kuis_progress, kuis_done=kuis_done, kuis_total=kuis_total,
        tugas_progress=tugas_progress, tugas_done=tugas_done, tugas_total=tugas_total,
        overall_progress_percentage=overall_progress_percentage)

@app.route('/badge')
@login_required
def badge():
    if current_user.role != 'siswa':
        flash('Anda tidak memiliki akses ke halaman lencana.', 'error')
        return redirect(url_for('index'))

    # Ambil data progres yang sama seperti di route /progress
    # Progres Materi
    total_materials = Material.query.join(Course).filter(Course.id == Material.course_id).count()
    materi_done = MaterialCompletion.query.filter_by(student_id=current_user.id).count()
    materi_total = total_materials

    # Progres Kuis
    total_quizzes = Quiz.query.join(Course).filter(Course.id == Quiz.course_id).count()
    quizzes_done = QuizResult.query.filter_by(student_id=current_user.id).count()
    kuis_done = quizzes_done
    kuis_total = total_quizzes

    # Progres Tugas
    total_assignments = Assignment.query.join(Course).filter(Course.id == Assignment.course_id).count()
    assignments_done = AssignmentSubmission.query.filter_by(student_id=current_user.id).count()
    tugas_done = assignments_done
    tugas_total = total_assignments

    # Tentukan status lencana
    badge_materi = "Selesai" if materi_done == materi_total and materi_total > 0 else "Belum"
    badge_kuis = "Selesai" if kuis_done == kuis_total and kuis_total > 0 else "Belum"
    badge_tugas = "Selesai" if tugas_done == tugas_total and tugas_total > 0 else "Belum"

    # Lencana Nilai Akhir
    # Hitung rata-rata nilai akhir keseluruhan
    all_student_final_grades = []
    courses = Course.query.all()
    for course in courses:
        quiz_results = QuizResult.query.filter_by(
            student_id=current_user.id
        ).join(QuizResult.quiz).filter(
            Quiz.course_id == course.id
        ).all()
        assignment_submissions = AssignmentSubmission.query.filter_by(
            student_id=current_user.id
        ).join(AssignmentSubmission.assignment).filter(
            Assignment.course_id == course.id
        ).all()
        total_quiz = len(course.quizzes)
        total_assignment = len(course.assignments)

        final_grade_for_course = calculate_final_grade(quiz_results, assignment_submissions, total_quiz, total_assignment)
        if final_grade_for_course is not None:
            all_student_final_grades.append(final_grade_for_course)

    overall_final_grade = sum(all_student_final_grades) / len(all_student_final_grades) if all_student_final_grades else 0.0
    
    badge_nilai = "-"
    if overall_final_grade >= 90:
        badge_nilai = "Emas"
    elif overall_final_grade >= 80:
        badge_nilai = "Perak"
    elif overall_final_grade >= 70:
        badge_nilai = "Perunggu"

    return render_template('badge.html',
        badge_materi=badge_materi, badge_kuis=badge_kuis, badge_tugas=badge_tugas,
        badge_nilai=badge_nilai)

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 
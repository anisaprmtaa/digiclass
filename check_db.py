from app import app, db, User, Course, Material

def check_database():
    with app.app_context():
        # Cek jumlah user
        users = User.query.all()
        print(f"\nJumlah user: {len(users)}")
        print("\nData Guru:")
        for user in User.query.filter_by(role='guru').all():
            print(f"- {user.username} (NIP: {user.nip})")
        
        print("\nData Siswa:")
        for user in User.query.filter_by(role='siswa').all():
            print(f"- {user.username} (NISN: {user.nisn})")
        
        # Cek jumlah mata pelajaran
        courses = Course.query.all()
        print(f"\nJumlah mata pelajaran: {len(courses)}")
        print("\nDaftar Mata Pelajaran:")
        for course in courses:
            print(f"\nMata Pelajaran: {course.title}")
            print(f"Pengajar: {course.instructor.username}")
            print(f"Deskripsi: {course.description}")
            print("Materi:")
            for material in course.materials:
                print(f"- {material.title}")

if __name__ == '__main__':
    check_database() 
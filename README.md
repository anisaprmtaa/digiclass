# Aplikasi DigiClass

Aplikasi DigiClass adalah platform pembelajaran online yang dirancang untuk memudahkan proses belajar mengajar antara guru dan siswa. Aplikasi ini menyediakan berbagai fitur untuk mendukung pembelajaran jarak jauh secara efektif.

## Fitur-Fitur Utama

### 1. Manajemen Pengguna (User Management)
- Registrasi dan Login: Pengguna dapat masuk sebagai siswa atau guru menggunakan NISN/NIP dan password
- Multi-Role: Sistem membedakan hak akses antara siswa dan guru
- Profil Pengguna: Setiap pengguna memiliki halaman profil, dapat mengubah data diri, password, dan mengunggah foto profil

### 2. Manajemen Mata Pelajaran (Course Management)
- Daftar Mata Pelajaran: Semua pengguna dapat melihat daftar mata pelajaran yang tersedia
- Guru Pengampu: Setiap mata pelajaran diampu oleh satu guru
- Deskripsi Mata Pelajaran: Setiap course memiliki deskripsi dan daftar materi

### 3. Materi Pembelajaran (Learning Materials)
- Upload Materi: Guru dapat menambah, mengedit, dan menghapus materi pembelajaran
- Konten Multimedia: Materi dapat berupa teks, file (Docs, PDF, dll), dan video YouTube
- Akses Materi: Siswa dapat membaca dan mengakses semua materi yang tersedia

### 4. Kuis (Quiz)
- Pembuatan Kuis: Guru dapat membuat kuis, menambah/edit soal pilihan ganda, dan menentukan jawaban benar
- Pengerjaan Kuis: Siswa dapat mengerjakan kuis secara online
- Penilaian Otomatis: Nilai kuis dihitung otomatis dan siswa dapat langsung melihat hasilnya
- Riwayat Kuis: Siswa dapat melihat riwayat dan hasil kuis yang telah dikerjakan

### 5. Tugas (Assignment)
- Pembuatan Tugas: Guru dapat membuat tugas, mengunggah file tugas, dan menentukan tenggat waktu
- Pengumpulan Tugas: Siswa dapat mengumpulkan tugas secara online, baik berupa teks maupun file
- Penilaian & Feedback: Guru dapat memberikan nilai dan umpan balik pada tugas yang dikumpulkan siswa
- Riwayat Tugas: Siswa dapat melihat status dan nilai tugas yang telah dikumpulkan

### 6. Notifikasi
- Sistem Notifikasi: Pengguna menerima notifikasi untuk materi baru, tugas baru, kuis baru, nilai, dan aktivitas penting lainnya
- Penanda Sudah Dibaca: Notifikasi dapat ditandai sebagai sudah dibaca

### 7. Forum Diskusi
- Forum per Mata Pelajaran: Setiap course memiliki forum diskusi
- Posting & Komentar: Guru dapat membuat topik diskusi dan memberikan komentar
- Komentar: Siswa dapat memberikan komentar
- Edit & Hapus: Guru dapat mengedit atau menghapus forum diskusi yang telah dibuat

### 8. Presensi (Attendance)
- Presensi Siswa: Siswa dapat melakukan presensi kehadiran pada setiap mata pelajaran
- Rekap Presensi: Guru dapat melihat rekap kehadiran siswa per kelas dan statistik kehadiran (hadir, sakit, izin)
- Catatan Presensi: Siswa dapat menambahkan catatan pada presensi

### 9. Pelacakan Progres (Progress Tracking)
- Progress Materi: Siswa dapat melihat persentase materi yang sudah dipelajari
- Progress Kuis & Tugas: Siswa dapat memantau progres pengerjaan kuis dan tugas
- Overall Progress: Terdapat halaman khusus untuk melihat progres keseluruhan belajar

### 10. Lencana (Badge)
- Pencapaian: Siswa mendapatkan lencana jika menyelesaikan semua materi, kuis, tugas, dan lencana untuk nilai akhir keseluruhan mata pelajaran
- Motivasi Belajar: Lencana diberikan secara otomatis untuk memotivasi siswa

### 11. Nilai & Rapor (Grades & Report)
- Lihat Nilai: Siswa dapat melihat nilai kuis, tugas, nilai akhir per mata pelajaran, dan nilai akhir keseluruhan mata pelajaran
- Statistik Nilai: Guru dapat melihat statistik nilai siswa (rata-rata, tertinggi, terendah, tingkat kelulusan)
- Download Nilai: Guru dapat mengunduh nilai siswa dalam format Excel

### 12. Manajemen File
- Upload & Download: Mendukung upload/download file materi, tugas, dan jawaban tugas
- Preview File: Guru dapat melihat pratinjau file jawaban siswa

### 13. Keamanan
- Password Hashing: Password disimpan dalam bentuk hash
- Session Management: Menggunakan Flask-Login untuk mengelola sesi pengguna
- Role-based Access: Hak akses dibatasi sesuai peran (guru/siswa)

### 14. Bantuan & Pengembang
- Halaman Bantuan: Tersedia panduan penggunaan, pertanyaan yang sering diajukan, kontak support
- Halaman Pengembang: Tersedia profil singkat pengembang, teknologi yang digunakan dalam membangun e-learning, dan alamat serta kontak tim pengembang

## Teknologi yang Digunakan
- Backend: Python dengan framework Flask
- Frontend: HTML, Boostrap
- Database: SQLite
- Authentication: Flask-Login
- File Storage: Local Storage

## Cara Penggunaan
1. Clone repository ini
   ```bash
   git clone hhttps://github.com/anisaprmtaa/DigiClass.git
   cd DigiClass
   ```

2. Install dependencies yang diperlukan
   ```bash
   # Buat virtual environment
   python -m venv venv
   
   # Aktifkan virtual environment
   # Untuk Windows:
   venv\Scripts\activate
   # Untuk Linux/Mac:
   source venv/bin/activate
   
   # Install package yang diperlukan
   pip install -r requirements.txt
   ```

3. Setup database SQLite
   ```bash
   # Jalankan script setup database
   python db_setup.py
   ```
   Script ini akan membuat file database SQLite dan tabel-tabel yang diperlukan secara otomatis.

4. Jalankan aplikasi
   ```bash
   python app.py
   ```

5. Akses aplikasi melalui browser di `http://localhost:5000`


from app import app, db, User, Course, Material, Quiz, QuizQuestion, Assignment
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import json
from shutil import copyfile
import os

# Data siswa per kelas
data_siswa = {
    '7A': [
        ('7123', 'Ahmad Rizki', '7A', 'siswa7123', 'ahmad@siswa.com'),
        ('7124', 'Budi Santoso', '7A', 'siswa7124', 'budi@siswa.com'),
        ('7125', 'Citra Dewi', '7A', 'siswa7125', 'citra@siswa.com'),
        ('7126', 'Dian Pratama', '7A', 'siswa7126', 'dian@siswa.com'),
        ('7127', 'Eka Putri', '7A', 'siswa7127', 'eka@siswa.com')
    ],
    '7B': [
        ('7131', 'Fajar Ramadhan', '7B', 'siswa7131', 'fajar@siswa.com'),
        ('7132', 'Gita Sari', '7B', 'siswa7132', 'gita@siswa.com'),
        ('7133', 'Hadi Wijaya', '7B', 'siswa7133', 'hadi@siswa.com'),
        ('7134', 'Indah Permata', '7B', 'siswa7134', 'indah@siswa.com'),
        ('7135', 'Joko Susilo', '7B', 'siswa7135', 'joko@siswa.com')
    ],
    '8A': [
        ('8123', 'Kartika Sari', '8A', 'siswa8123', 'kartika@siswa.com'),
        ('8124', 'Lina Wijaya', '8A', 'siswa8124', 'lina@siswa.com'),
        ('8125', 'Muhammad Ali', '8A', 'siswa8125', 'muhammad@siswa.com'),
        ('8126', 'Nina Putri', '8A', 'siswa8126', 'nina@siswa.com'),
        ('8127', 'Oscar Pratama', '8A', 'siswa8127', 'oscar@siswa.com')
    ],
    '8B': [
        ('8131', 'Putri Anggraini', '8B', 'siswa8131', 'putri@siswa.com'),
        ('8132', 'Rudi Hartono', '8B', 'siswa8132', 'rudi@siswa.com'),
        ('8133', 'Siti Aminah', '8B', 'siswa8133', 'siti@siswa.com'),
        ('8134', 'Tono Wijaya', '8B', 'siswa8134', 'tono@siswa.com'),
        ('8135', 'Umi Kalsum', '8B', 'siswa8135', 'umi@siswa.com')
    ],
    '9A': [
        ('9123', 'Vina Putri', '9A', 'siswa9123', 'vina@siswa.com'),
        ('9124', 'Wahyu Pratama', '9A', 'siswa9124', 'wahyu@siswa.com'),
        ('9125', 'Xena Wijaya', '9A', 'siswa9125', 'xena@siswa.com'),
        ('9126', 'Yudi Santoso', '9A', 'siswa9126', 'yudi@siswa.com'),
        ('9127', 'Zahra Putri', '9A', 'siswa9127', 'zahra@siswa.com')
    ],
    '9B': [
        ('9131', 'Ade Kurniawan', '9B', 'siswa9131', 'ade@siswa.com'),
        ('9132', 'Bella Sari', '9B', 'siswa9132', 'bella@siswa.com'),
        ('9133', 'Candra Wijaya', '9B', 'siswa9133', 'candra@siswa.com'),
        ('9134', 'Dewi Lestari', '9B', 'siswa9134', 'dewi@siswa.com'),
        ('9135', 'Eko Pratama', '9B', 'siswa9135', 'eko@siswa.com')
    ]
}

# Data guru dengan mata pelajaran yang diampu
data_guru = [
    ('1122', 'Asep Saepudin, S.Pd.I', 'guru1122', 'asep@guru.com', 'Pendidikan Agama Islam'),
    ('2233', 'Ani Kusrini, S.Pd', 'guru2233', 'ani@guru.com', 'PPKN'),
    ('3344', 'Heti Mulyani, S.Kom', 'guru3344', 'heti@guru.com', 'Informatika'),
    ('4455', 'Dina Marliana, S.Pd', 'guru4455', 'dina@guru.com', 'Matematika'),
    ('5566', 'Nia Kurniasih, S.Pd', 'guru5566', 'nia@guru.com', 'Olahraga'),
    ('6677', 'Rudi Hartono, S.Pd', 'guru6677', 'rudi@guru.com', 'Bahasa Indonesia'),
    ('7788', 'Siti Aminah, S.Pd', 'guru7788', 'siti@guru.com', 'Bahasa Inggris'),
    ('8899', 'Tono Wijaya, S.Pd', 'guru8899', 'tono@guru.com', 'IPA'),
    ('9900', 'Umi Kalsum, S.Pd', 'guru9900', 'umi@guru.com', 'IPS'),
    ('0011', 'Vina Putri, S.Pd', 'guru0011', 'vina@guru.com', 'Seni Budaya')
]

# Data mata pelajaran dan materi
data_mapel = [
    {
        'title': 'Pendidikan Agama Islam',
        'description': 'Pembelajaran tentang nilai-nilai keagamaan dan akhlak mulia dalam Islam',
        'materials': [
            {
                'title': 'Materi 1: Iman kepada Malaikat Allah', 
                'content': 
'''<p><strong>A. Pengertian Iman kepada Malaikat</strong><br>
Iman kepada malaikat adalah meyakini dengan sepenuh hati bahwa malaikat adalah makhluk Allah yang diciptakan dari cahaya (nur), tidak memiliki hawa nafsu, dan senantiasa taat kepada perintah Allah.</p>

<p><strong>B. Ciri-ciri Malaikat</strong></p>
<ul>
    <li>Diciptakan dari cahaya.</li>
    <li>Tidak berjenis kelamin.</li>
    <li>Tidak makan dan minum.</li>
    <li>Tidak pernah membangkang terhadap perintah Allah.</li>
    <li>Selalu berdzikir dan beribadah.</li>
</ul>

<p><strong>C. Nama dan Tugas 10 Malaikat</strong></p>
<table class="table table-bordered table-striped">
    <thead>
        <tr>
            <th style="text-align: center;">No.</th>
            <th style="text-align: center;">Nama Malaikat</th>
            <th style="text-align: center;">Tugas</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="text-align: center;">1.</td>
            <td>Jibril</td>
            <td>Menyampaikan wahyu</td>
        </tr>
        <tr>
            <td style="text-align: center;">2.</td>
            <td>Mikail</td>
            <td>Mengatur rezeki dan alam</td>
        </tr>
        <tr>
            <td style="text-align: center;">3.</td>
            <td>Israfil</td>
            <td>Meniup sangkakala</td>
        </tr>
        <tr>
            <td style="text-align: center;">4.</td>
            <td>Izrail</td>
            <td>Mencabut nyawa</td>
        </tr>
        <tr>
            <td style="text-align: center;">5.</td>
            <td>Munkar</td>
            <td>Menanyai di alam kubur</td>
        </tr>
        <tr>
            <td style="text-align: center;">6.</td>
            <td>Nakir</td>
            <td>Menanyai di alam kubur</td>
        </tr>
        <tr>
            <td style="text-align: center;">7.</td>
            <td>Raqib</td>
            <td>Mencatat amal baik</td>
        </tr>
        <tr>
            <td style="text-align: center;">8.</td>
            <td>Atid</td>
            <td>Mencatat amal buruk</td>
        </tr>
        <tr>
            <td style="text-align: center;">9.</td>
            <td>Malik</td>
            <td>Penjaga neraka</td>
        </tr>
        <tr>
            <td style="text-align: center;">10.</td>
            <td>Ridwan</td>
            <td>Penjaga surga</td>
        </tr>
    </tbody>
</table>

<p><strong>D. Hikmah Beriman kepada Malaikat</strong></p>
<ul>
    <li>Menambah keimanan kepada Allah.</li>
    <li>Menjadi lebih berhati-hati dalam bertindak.</li>
    <li>Selalu berusaha berbuat baik.</li>
    <li>Menumbuhkan rasa takut dan cinta kepada Allah.</li>
</ul>''',
                'youtube_url': 'https://youtu.be/cIGX_-MDaOE?si=5cpJQdUqsdHSRYZt'
            },
            {
                'title': 'Materi 2: Tata Cara Wudhu dan Shalat', 
                'content': 
'''<p><strong>A. Pengertian Wudhu</strong><br>
Wudhu adalah bersuci dari hadas kecil dengan cara tertentu menggunakan air yang suci dan mensucikan.</p>

<p><strong>B. Rukun Wudhu</strong></p>
<ul style="margin-left: 20px;">
    <li>Niat.</li>
    <li>Membasuh muka.</li>
    <li>Membasuh kedua tangan hingga siku.</li>
    <li>Mengusap sebagian kepala.</li>
    <li>Membasuh kedua kaki hingga mata kaki.</li>
    <li>Tertib (berurutan).</li>
</ul>

<p><strong>C. Hal yang Membatalkan Wudhu</strong></p>
<ul style="margin-left: 20px;">
    <li>Keluar sesuatu dari qubul atau dubur.</li>
    <li>Hilang akal (tidur lelap, pingsan).</li>
    <li>Menyentuh kemaluan tanpa penghalang.</li>
    <li>Menyentuh lawan jenis yang bukan mahram dengan syahwat.</li>
</ul>

<p><strong>D. Shalat Fardu 5 Waktu</strong></p>
<table style="width: 100%; border-collapse: collapse; border: 1px solid #000;">
    <thead>
        <tr>
            <th style="border: 1px solid #000; text-align: center; background-color: #f2f2f2;">No</th>
            <th style="border: 1px solid #000; text-align: center; background-color: #f2f2f2;">Nama Salat</th>
            <th style="border: 1px solid #000; text-align: center; background-color: #f2f2f2;">Waktu</th>
            <th style="border: 1px solid #000; text-align: center; background-color: #f2f2f2;">Jumlah Rakaat</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="border: 1px solid #000; text-align: center;">1</td>
            <td style="border: 1px solid #000;">Subuh</td>
            <td style="border: 1px solid #000;">Fajar</td>
            <td style="border: 1px solid #000;">2 rakaat</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000; text-align: center;">2</td>
            <td style="border: 1px solid #000;">Zuhur</td>
            <td style="border: 1px solid #000;">Tengah hari</td>
            <td style="border: 1px solid #000;">4 rakaat</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000; text-align: center;">3</td>
            <td style="border: 1px solid #000;">Asar</td>
            <td style="border: 1px solid #000;">Sore</td>
            <td style="border: 1px solid #000;">4 rakaat</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000; text-align: center;">4</td>
            <td style="border: 1px solid #000;">Magrib</td>
            <td style="border: 1px solid #000;">Senja</td>
            <td style="border: 1px solid #000;">3 rakaat</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000; text-align: center;">5</td>
            <td style="border: 1px solid #000;">Isya</td>
            <td style="border: 1px solid #000;">Malam</td>
            <td style="border: 1px solid #000;">4 rakaat</td>
        </tr>
    </tbody>
</table>

<p><strong>E. Hikmah Menjaga Wudhu dan hSalat</strong></p>
<ul style="margin-left: 20px;">
    <li>Membiasakan hidup bersih.</li>
    <li>Mendekatkan diri kepada Allah.</li>
    <li>Menjauhkan diri dari perbuatan keji dan mungkar.</li>
    <li>Meningkatkan disiplin dan tanggung jawab.</li>
</ul>''',
                'youtube_url': 'https://youtu.be/LwnLurexn1Y?si=KW4LhdxKrxAQArd5'
            }
        ]
    },
    {
        'title': 'PPKN',
        'description': 'Pembelajaran tentang kewarganegaraan, nilai-nilai Pancasila, dan hak serta kewajiban warga negara',
        'materials': [
            {
                'title': 'Materi 1: Pancasila sebagai Dasar Negara dan Pandangan Hidup Bangsa', 
                'content': 
'''<p><strong>A. Pengertian Pancasila</strong><br>
Pancasila adalah dasar negara Indonesia yang menjadi panduan dalam kehidupan berbangsa dan bernegara, terdiri dari lima sila yang mencerminkan nilai-nilai luhur bangsa.</p>

<p><strong>B. Lima Sila dalam Pancasila</strong></p>
<ol style="margin-left: 20px;">
    <li>Ketuhanan Yang Maha Esa</li>
    <li>Kemanusiaan yang adil dan beradab</li>
    <li>Persatuan Indonesia</li>
    <li>Kerakyatan yang dipimpin oleh hikmat kebijaksanaan dalam permusyawaratan/perwakilan</li>
    <li>Keadilan sosial bagi seluruh rakyat Indonesia</li>
</ol>

<p><strong>C. Fungsi Pancasila</strong></p>
<ul style="margin-left: 20px;">
    <li>Dasar negara dan sumber hukum tertinggi.</li>
    <li>Pedoman dalam kehidupan bermasyarakat, berbangsa, dan bernegara.</li>
    <li>Pemersatu bangsa Indonesia.</li>
</ul>

<p><strong>D. Contoh Pengamalan Pancasila dalam Kehidupan Sehari-hari</strong></p>
<table style="width: 100%; border-collapse: collapse; border: 1px solid #000;">
    <thead>
        <tr>
            <th style="border: 1px solid #000; text-align: center; background-color: #f2f2f2;">No</th>
            <th style="border: 1px solid #000; text-align: center; background-color: #f2f2f2;">Sila</th>
            <th style="border: 1px solid #000; text-align: center; background-color: #f2f2f2;">Contoh Sikap</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="border: 1px solid #000; text-align: center;">1</td>
            <td style="border: 1px solid #000;">Ketuhanan Yang Maha Esa</td>
            <td style="border: 1px solid #000;">Beribadah sesuai agama masing-masing</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000; text-align: center;">2</td>
            <td style="border: 1px solid #000;">Kemanusiaan yang adil dan beradab</td>
            <td style="border: 1px solid #000;">Membantu teman yang sedang kesulitan</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000; text-align: center;">3</td>
            <td style="border: 1px solid #000;">Persatuan Indonesia</td>
            <td style="border: 1px solid #000;">Menghargai perbedaan budaya</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000; text-align: center;">4</td>
            <td style="border: 1px solid #000;">Kerakyatan yang dipimpin oleh hikmat kebijaksanaan</td>
            <td style="border: 1px solid #000;">Musyawarah saat memilih ketua kelas</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000; text-align: center;">5</td>
            <td style="border: 1px solid #000;">Keadilan sosial bagi seluruh rakyat Indonesia</td>
            <td style="border: 1px solid #000;">Bersikap adil kepada semua teman</td>
        </tr>
    </tbody>
</table>''',
                'youtube_url': 'https://youtu.be/kaPdk3kwx8g?si=eJAP3Aq-Cjz969bM'
            },
            {
                'title': 'Materi 2: Norma dalam Kehidupan Bermasyarakat', 
                'content': 
'''<p><strong>A. Pengertian Norma</strong><br>
Norma adalah aturan atau ketentuan yang berlaku dalam masyarakat sebagai pedoman perilaku yang dianggap pantas dan diharapkan.</p>

<p><strong>B. Macam-macam Norma</strong></p>
<table style="width: 100%; border-collapse: collapse; border: 1px solid #000;">
    <thead>
        <tr>
            <th style="border: 1px solid #000; text-align: center; background-color: #f2f2f2;">No</th>
            <th style="border: 1px solid #000; text-align: center; background-color: #f2f2f2;">Jenis Norma</th>
            <th style="border: 1px solid #000; text-align: center; background-color: #f2f2f2;">Contoh</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="border: 1px solid #000; text-align: center;">1</td>
            <td style="border: 1px solid #000;">Norma Agama</td>
            <td style="border: 1px solid #000;">Beribadah sesuai ajaran agama</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000; text-align: center;">2</td>
            <td style="border: 1px solid #000;">Norma Kesusilaan</td>
            <td style="border: 1px solid #000;">Bersikap jujur dan tidak mencuri</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000; text-align: center;">3</td>
            <td style="border: 1px solid #000;">Norma Kesopanan</td>
            <td style="border: 1px solid #000;">Mengucapkan salam saat bertemu</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000; text-align: center;">4</td>
            <td style="border: 1px solid #000;">Norma Hukum</td>
            <td style="border: 1px solid #000;">Mematuhi rambu lalu lintas</td>
        </tr>
    </tbody>
</table>

<p><strong>C. Fungsi Norma dalam Masyarakat</strong></p>
<ul style="margin-left: 20px;">
    <li>Mengatur tingkah laku individu dalam masyarakat.</li>
    <li>Menjaga ketertiban dan keamanan.</li>
    <li>Mewujudkan kehidupan yang harmonis.</li>
</ul>''',
                'youtube_url': 'https://youtu.be/tnitr4ldcQ0?si=0tAd2hCinSXcQ6oE'
            }
        ]
    },
    {
        'title': 'Informatika',
        'description': 'Pembelajaran dasar pemrograman, teknologi informasi, dan literasi digital',
        'materials': [
            {
                'title': 'Materi 1: Mengenal Perangkat Keras (Hardware) Komputer', 
                'content': 
'''<p><strong>A. Pengertian Perangkat Keras</strong><br>
Perangkat keras (hardware) adalah semua komponen fisik yang dapat dilihat dan disentuh secara langsung pada sistem komputer. Perangkat keras berfungsi untuk mendukung proses input, proses, dan output data.</p>

<p><strong>B. Jenis-jenis Perangkat Keras Komputer</strong></p>
<table style="width: 100%; border-collapse: collapse; border: 1px solid #000;">
    <thead>
        <tr>
            <th style="border: 1px solid #000; text-align: center; background-color: #f2f2f2;">Jenis</th>
            <th style="border: 1px solid #000; text-align: center; background-color: #f2f2f2;">Contoh</th>
            <th style="border: 1px solid #000; text-align: center; background-color: #f2f2f2;">Fungsi</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="border: 1px solid #000;">Input Device</td>
            <td style="border: 1px solid #000;">Keyboard, Mouse, Scanner</td>
            <td style="border: 1px solid #000;">Memasukkan data ke komputer</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000;">Process Device</td>
            <td style="border: 1px solid #000;">CPU (Processor), RAM</td>
            <td style="border: 1px solid #000;">Mengolah data yang masuk</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000;">Output Device</td>
            <td style="border: 1px solid #000;">Monitor, Printer, Speaker</td>
            <td style="border: 1px solid #000;">Menampilkan hasil pengolahan data</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000;">Storage Device</td>
            <td style="border: 1px solid #000;">Harddisk, Flashdisk, SSD</td>
            <td style="border: 1px solid #000;">Menyimpan data secara permanen</td>
        </tr>
    </tbody>
</table>

<p><strong>C. Kesimpulan</strong></p>
<ul style="margin-left: 20px;">
    <li>Hardware berperan penting dalam menjalankan sistem komputer.</li>
    <li>Setiap jenis perangkat keras memiliki fungsi yang saling melengkapi.</li>
</ul>''',
                'youtube_url': 'https://youtu.be/ERDQQt1CHac?si=CX-YirDAZOwsaG-P'
            },
            {
                'title': 'Materi 2: Etika dan Keamanan dalam Menggunakan Teknologi Informasi', 
                'content': 
'''<p><strong>A. Pengertian Etika dalam Teknologi</strong><br>
Etika dalam penggunaan teknologi informasi adalah aturan atau pedoman moral dalam menggunakan perangkat digital agar tidak merugikan diri sendiri dan orang lain.</p>

<p><strong>B. Contoh Etika Menggunakan Teknologi</strong></p>
<ul style="margin-left: 20px;">
    <li>Tidak menyebarkan berita bohong (hoaks).</li>
    <li>Tidak melakukan plagiarisme saat mengerjakan tugas.</li>
    <li>Menghargai privasi orang lain di media sosial.</li>
    <li>Tidak mengunduh atau menyebarkan konten ilegal.</li>
</ul>

<p><strong>C. Keamanan dalam Dunia Digital</strong></p>
<table style="width: 100%; border-collapse: collapse; border: 1px solid #000;">
    <thead>
        <tr>
            <th style="border: 1px solid #000; text-align: center; background-color: #f2f2f2;">Aspek</th>
            <th style="border: 1px solid #000; text-align: center; background-color: #f2f2f2;">Penjelasan</th>
            <th style="border: 1px solid #000; text-align: center; background-color: #f2f2f2;">Contoh</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="border: 1px solid #000;">Keamanan Data</td>
            <td style="border: 1px solid #000;">Melindungi informasi pribadi dari penyalahgunaan</td>
            <td style="border: 1px solid #000;">Menggunakan password yang kuat</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000;">Perangkat Lunak Keamanan</td>
            <td style="border: 1px solid #000;">Aplikasi yang melindungi komputer dari virus/malware</td>
            <td style="border: 1px solid #000;">Antivirus, Firewall</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000;">Keamanan Jaringan</td>
            <td style="border: 1px solid #000;">Mengamankan jaringan internet dari penyusup</td>
            <td style="border: 1px solid #000;">Menggunakan jaringan Wi-Fi yang aman</td>
        </tr>
    </tbody>
</table>

<p><strong>D. Kesimpulan</strong></p>
<ul style="margin-left: 20px;">
    <li>Pengguna teknologi harus bertanggung jawab atas aktivitas digitalnya.</li>
    <li>Etika dan keamanan saling melengkapi dalam menjaga lingkungan digital yang sehat dan aman.</li>
</ul>''',
                'youtube_url': 'https://youtu.be/dz_kxLtYFT0?si=OG1BBNA2Nz32r5tF'
            }
        ]
    },
    {
        'title': 'Matematika',
        'description': 'Pembelajaran konsep matematika, pemecahan masalah, dan aplikasinya dalam kehidupan',
        'materials': [
            {
                'title': 'Aljabar dan Persamaan', 
                'content': 'Pengenalan konsep aljabar dasar dan persamaan linear',
                'youtube_url': 'https://youtu.be/example7'
            },
            {
                'title': 'Geometri dan Trigonometri', 
                'content': 'Pembelajaran tentang bangun datar, ruang, dan trigonometri dasar',
                'youtube_url': 'https://youtu.be/example8'
            }
        ]
    },
    {
        'title': 'Olahraga',
        'description': 'Pembelajaran aktivitas fisik, kesehatan, dan kebugaran jasmani',
        'materials': [
            {
                'title': 'Senam dan Kebugaran', 
                'content': 'Panduan gerakan senam dan latihan kebugaran yang benar',
                'youtube_url': 'https://youtu.be/example9'
            },
            {
                'title': 'Permainan Bola', 
                'content': 'Teknik dasar bermain bola basket, voli, dan sepak bola',
                'youtube_url': 'https://youtu.be/example10'
            }
        ]
    },
    {
        'title': 'Bahasa Indonesia',
        'description': 'Pembelajaran bahasa Indonesia, sastra, dan keterampilan berbahasa',
        'materials': [
            {
                'title': 'Teks Narasi', 
                'content': 'Pembelajaran tentang struktur dan ciri-ciri teks narasi',
                'youtube_url': 'https://youtu.be/example11'
            },
            {
                'title': 'Puisi dan Prosa', 
                'content': 'Pengenalan genre sastra puisi dan prosa',
                'youtube_url': 'https://youtu.be/example12'
            }
        ]
    },
    {
        'title': 'Bahasa Inggris',
        'description': 'Pembelajaran bahasa Inggris untuk komunikasi internasional',
        'materials': [
            {
                'title': 'Grammar Dasar', 
                'content': 'Pengenalan tata bahasa Inggris dasar',
                'youtube_url': 'https://youtu.be/example13'
            },
            {
                'title': 'Conversation', 
                'content': 'Praktik percakapan bahasa Inggris sehari-hari',
                'youtube_url': 'https://youtu.be/example14'
            }
        ]
    },
    {
        'title': 'IPA',
        'description': 'Pembelajaran sains dan aplikasinya dalam kehidupan sehari-hari',
        'materials': [
            {
                'title': 'Fisika Dasar', 
                'content': 'Pengenalan konsep fisika dasar dan aplikasinya',
                'youtube_url': 'https://youtu.be/example15'
            },
            {
                'title': 'Biologi Dasar', 
                'content': 'Pembelajaran tentang sistem tubuh manusia dan makhluk hidup',
                'youtube_url': 'https://youtu.be/example16'
            }
        ]
    },
    {
        'title': 'IPS',
        'description': 'Pembelajaran ilmu sosial dan sejarah untuk memahami masyarakat',
        'materials': [
            {
                'title': 'Sejarah Indonesia', 
                'content': 'Pembelajaran sejarah Indonesia dari masa pra-sejarah hingga kemerdekaan',
                'youtube_url': 'https://youtu.be/example17'
            },
            {
                'title': 'Geografi', 
                'content': 'Pengenalan konsep geografi dan peta Indonesia',
                'youtube_url': 'https://youtu.be/example18'
            }
        ]
    },
    {
        'title': 'Seni Budaya',
        'description': 'Pembelajaran seni rupa, musik, tari, dan budaya Indonesia',
        'materials': [
            {
                'title': 'Seni Rupa', 
                'content': 'Pengenalan teknik dasar menggambar dan melukis',
                'youtube_url': 'https://youtu.be/example19'
            },
            {
                'title': 'Seni Musik', 
                'content': 'Pembelajaran dasar musik dan alat musik tradisional',
                'youtube_url': 'https://youtu.be/example20'
            }
        ]
    }
]

def setup_database():
    with app.app_context():
        # Hapus semua data yang ada
        db.drop_all()
        db.create_all()
        
        print("Membuat data guru...")
        # Buat akun guru
        guru_dict = {}  # Untuk menyimpan referensi guru
        for nip, nama, password, email, mapel in data_guru:
            guru = User(
                nip=nip,
                username=nama,
                email=email,
                password_hash=generate_password_hash(password),
                role='guru'
            )
            db.session.add(guru)
            db.session.flush()  # Untuk mendapatkan ID
            guru_dict[mapel] = guru.id

        print("Membuat data siswa...")
        # Buat akun siswa untuk setiap kelas
        for kelas, siswa_list in data_siswa.items():
            for nisn, nama, kelas, password, email in siswa_list:
                siswa = User(
                    nisn=nisn,
                    username=nama,
                    email=email,
                    password_hash=generate_password_hash(password),
                    role='siswa',
                    kelas=kelas
                )
                db.session.add(siswa)

        print("Membuat mata pelajaran dan materi...")
        # Buat mata pelajaran dan materi
        for mapel in data_mapel:
            course = Course(
                title=mapel['title'],
                description=mapel['description'],
                instructor_id=guru_dict[mapel['title']]  # Gunakan ID guru yang sesuai
            )
            db.session.add(course)
            db.session.flush()  # Untuk mendapatkan ID course

            # Tambah materi untuk mata pelajaran ini
            for materi in mapel['materials']:
                content = materi['content']
                material = Material(
                    title=materi['title'],
                    content=content,
                    youtube_url=materi['youtube_url'],
                    course_id=course.id
                )
                db.session.add(material)

            # Buat contoh kuis untuk setiap mata pelajaran
            # quiz = Quiz(
            #     title=f"Kuis {mapel['title']}",
            #     description=f"Kuis untuk menguji pemahaman {mapel['title']}",
            #     course_id=course.id,
            #     due_date=datetime.now() + timedelta(days=7)
            # )
            # db.session.add(quiz)
            # db.session.flush()

            # Tambah pertanyaan kuis
            # question = QuizQuestion(
            #     quiz_id=quiz.id,
            #     question=f"Pertanyaan tentang {mapel['title']}?",
            #     options=json.dumps(["A", "B", "C", "D"]),
            #     correct_answer="A",
            #     points=10
            # )
            # db.session.add(question)

            # Buat contoh tugas untuk setiap mata pelajaran
            # assignment = Assignment(
            #     title=f"Tugas {mapel['title']}",
            #     description=f"Tugas untuk mata pelajaran {mapel['title']}",
            #     course_id=course.id,
            #     due_date=datetime.now() + timedelta(days=14)
            # )
            # db.session.add(assignment)

        db.session.commit()
        print("Database berhasil diinisialisasi!")

        # Cek atau buat Course
        course_title = 'Pendidikan Agama Islam'
        course = Course.query.filter_by(title=course_title).first()
        if not course:
            # Ganti instructor_id sesuai user guru yang ada
            instructor = User.query.filter_by(role='guru').first()
            if not instructor:
                raise Exception('Tidak ada guru di database!')
            course = Course(title=course_title, description='Pelajaran Agama Islam', instructor_id=instructor.id)
            db.session.add(course)
            db.session.commit()

        # MATERI 1: Iman Kepada Malaikat Allah
        material_title = 'Materi 1: Iman kepada Malaikat Allah'
        material = Material.query.filter_by(title=material_title, course_id=course.id).first()
        if not material:
            material = Material(title=material_title, content='Iman kepada Malaikat Allah', course_id=course.id)
            db.session.add(material)
            db.session.commit()
        materi_pdf = 'Iman_Kepada_Malaikat.pdf'
        materi_pdf_path = 'static/uploads/materials/' + materi_pdf
        if os.path.exists(materi_pdf_path):
            material.file_path = materi_pdf
            material.original_filename = materi_pdf
            db.session.commit()
        
        # MATERI 2: Tata Cara Wudhu dan Shalat
        material2_title = 'Materi 2: Tata Cara Wudhu dan Shalat'
        material2 = Material.query.filter_by(title=material2_title, course_id=course.id).first()
        if not material2:
            material2 = Material(title=material2_title, content='Tata Cara Wudhu dan Shalat', course_id=course.id)
            db.session.add(material2)
            db.session.commit()
        materi2_pdf = 'Cara Wudhu.pdf'
        materi2_pdf_path = 'static/uploads/materials/' + materi2_pdf
        if os.path.exists(materi2_pdf_path):
            material2.file_path = materi2_pdf
            material2.original_filename = materi2_pdf
            db.session.commit()

        # KUIS 1
        quiz_title = 'Kuis 1: Iman kepada Malaikat Allah'
        quiz = Quiz.query.filter_by(title=quiz_title, course_id=course.id, material_id=material.id).first()
        if not quiz:
            quiz = Quiz(title=quiz_title, description='Kuis tentang Iman kepada Malaikat Allah', course_id=course.id, material_id=material.id)
            db.session.add(quiz)
            db.session.commit()
        # Hapus soal lama pada quiz ini
        QuizQuestion.query.filter_by(quiz_id=quiz.id).delete()
        db.session.commit()
        # Load soal dari file JSON
        with open('instance/soal_malaikat.json', 'r', encoding='utf-8') as f:
            soal_list = json.load(f)
        for soal in soal_list:
            question = QuizQuestion(
                quiz_id=quiz.id,
                question=soal['pertanyaan'],
                correct_answer=soal['correct_answer'],
                points=10
            )
            question.set_options(soal['options'])
            db.session.add(question)
            db.session.commit()
        if quiz:
            quiz.due_date = datetime(2025, 6, 20)
            db.session.commit()

        # KUIS 2
        quiz2_title = 'Kuis 2: Iman kepada Malaikat Allah'
        quiz2 = Quiz.query.filter_by(title=quiz2_title, course_id=course.id, material_id=material.id).first()
        if not quiz2:
            quiz2 = Quiz(title=quiz2_title, description='Kuis 2 tentang Iman kepada Malaikat Allah', course_id=course.id, material_id=material.id)
            db.session.add(quiz2)
            db.session.commit()
        QuizQuestion.query.filter_by(quiz_id=quiz2.id).delete()
        db.session.commit()
        with open('instance/kuis2_malaikat.json', 'r', encoding='utf-8') as f:
            soal_list2 = json.load(f)
        for soal in soal_list2:
            question = QuizQuestion(
                quiz_id=quiz2.id,
                question=soal['pertanyaan'],
                correct_answer=soal['correct_answer'],
                points=10
            )
            question.set_options(soal['options'])
            db.session.add(question)
            db.session.commit()
        if quiz2:
            quiz2.due_date = datetime(2025, 6, 25)
            db.session.commit()

        # TUGAS 1
        tugas_title = 'Tugas 1: Iman kepada Malaikat Allah'
        tugas_desc = 'Kerjakan soal berikut tentang Iman kepada Malaikat Allah. Upload jawaban Anda dalam format PDF.'
        tugas_filename = 'tugas_malaikat.pdf'
        tugas_file_src = 'instance/tugas_malaikat.pdf'  # File sumber (siapkan file ini di instance/)
        tugas_file_dest = f'static/uploads/assignment_tasks/{tugas_filename}'
        # Copy file tugas ke static/uploads jika belum ada
        if not os.path.exists('static/uploads'):
            os.makedirs('static/uploads')
        if not os.path.exists(tugas_file_dest) and os.path.exists(tugas_file_src):
            copyfile(tugas_file_src, tugas_file_dest)
        # Cek atau buat Assignment
        assignment = Assignment.query.filter_by(title=tugas_title, course_id=course.id, material_id=material.id).first()
        if not assignment:
            assignment = Assignment(
                title=tugas_title,
                description=tugas_desc,
                course_id=course.id,
                material_id=material.id,
                due_date=datetime(2025, 6, 30),
                task_file_path=tugas_filename,
                task_original_filename=tugas_filename
            )
            db.session.add(assignment)
            db.session.commit()
        if assignment:
            assignment.due_date = datetime(2025, 6, 28)
            db.session.commit()

        # TUGAS 2
        tugas2_title = 'Tugas 2: Iman kepada Malaikat Allah'
        tugas2_desc = 'Kerjakan soal berikut tentang Iman kepada Malaikat Allah. Upload jawaban Anda dalam format PDF.'
        tugas2_filename = 'Tugas2_Iman_kepada_Malaikat_Allah.pdf'
        tugas2_file_src = 'instance/Tugas2_Iman_kepada_Malaikat_Allah.pdf'
        tugas2_file_dest = f'static/uploads/assignment_tasks/{tugas2_filename}'
        if not os.path.exists('static/uploads'):
            os.makedirs('static/uploads')
        if not os.path.exists(tugas2_file_dest) and os.path.exists(tugas2_file_src):
            copyfile(tugas2_file_src, tugas2_file_dest)
        assignment2 = Assignment.query.filter_by(title=tugas2_title, course_id=course.id, material_id=material.id).first()
        if not assignment2:
            assignment2 = Assignment(
                title=tugas2_title,
                description=tugas2_desc,
                course_id=course.id,
                material_id=material.id,
                due_date=datetime(2025, 6, 28),
                task_file_path=tugas2_filename,
                task_original_filename=tugas2_filename
            )
            db.session.add(assignment2)
            db.session.commit()
        if assignment2:
            assignment2.due_date = datetime(2025, 6, 30)
            db.session.commit()

if __name__ == '__main__':
    setup_database() 
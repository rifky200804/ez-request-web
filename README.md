# EzRequest

EzRequest adalah aplikasi web berbasis Django yang dirancang untuk mengelola permintaan layanan (Service Requests), data karyawan, dan manajemen pengguna. Aplikasi ini menyediakan antarmuka untuk melacak status permintaan, mengelola profil karyawan, dan autentikasi pengguna.

## Fitur Utama

*   **Manajemen Pengguna (Users)**: Autentikasi kustom, registrasi, dan login.
*   **Manajemen Karyawan (Employees)**: Pengelolaan data karyawan.
*   **Layanan Permintaan (Service Requests)**: Pembuatan dan pelacakan permintaan layanan.
*   **API Support**: Menggunakan Django Rest Framework.

## Teknologi yang Digunakan

*   **Backend**: Python, Django 5.x
*   **Database**: MySQL
*   **Autentikasi**: Django Auth (Custom User Model)
*   **Utilities**: `python-dotenv` untuk manajemen environment variable.

## Prasyarat

Sebelum menjalankan aplikasi, pastikan Anda telah menginstal:

*   [Python](https://www.python.org/) (versi 3.10 atau lebih baru disarankan)
*   [MySQL Server](https://dev.mysql.com/downloads/mysql/)
*   [Git](https://git-scm.com/)

## Panduan Instalasi dan Menjalankan Aplikasi

Ikuti langkah-langkah berikut untuk menjalankan aplikasi di komputer lokal Anda.

### 1. Clone Repository (Jika ada)

```bash
git clone <url-repository-anda>
cd ez_request
```

### 2. Buat dan Aktifkan Virtual Environment

Disarankan menggunakan virtual environment agar dependencies tidak tercampur.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instal Dependencies

File `requirements.txt` sudah disertakan dalam proyek ini.

```bash
pip install -r requirements.txt
```

Paket utama yang digunakan adalah:
*   `Django`
*   `djangorestframework`
*   `python-dotenv`
*   `pymysql` (Digunakan sebagai driver MySQL)

### 4. Konfigurasi Environment Variables

Buat file `.env` di dalam folder `ez_request/`. Struktur folder harus terlihat seperti ini:

```
ez_request/
├── requirements.txt
├── manage.py
├── ez_request/
│   ├── __init__.py
│   ├── settings.py
│   ├── .env  <-- Buat file ini di sini
│   └── ...
└── ...
```

Isi file `.env` dengan konfigurasi berikut (sesuaikan dengan setting MySQL Anda):

```env
SECRET_KEY=kunci_rahasia_anda_disini
DEBUG=True
DB_NAME=ez_request
DB_USER=root
DB_PASSWORD=password_mysql_anda
DB_HOST=127.0.0.1
DB_PORT=3306
```

**Catatan Penting:**
Aplikasi utama (`settings.py`) membaca `.env` dari dalam folder `ez_request/ez_request/`, sedangkan script bantu `reset_db.py` mencarinya di folder root (`ez_request/`). Jika Anda berencana menggunakan `reset_db.py`, disarankan untuk menyalin file `.env` ke kedua lokasi tersebut.

### 5. Setup Database

Pastikan service MySQL sudah berjalan. Kemudian buat database kosong bernama `ez_request` (atau sesuai nama di `.env`):

```sql
CREATE DATABASE ez_request;
```

### 6. Migrasi Database

Jalankan perintah berikut untuk membuat tabel-tabel di database:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Buat Superuser (Opsional)

Untuk mengakses halaman admin Django:

```bash
python manage.py createsuperuser
```

### 8. Jalankan Server

Jalankan server pengembangan Django:

```bash
python manage.py runserver
```

Buka browser dan kunjungi `http://127.0.0.1:8000/`.

## Struktur Project

*   `ez_request/`: Direktori utama project dan settings.
*   `users/`: Aplikasi untuk manajemen user (login, register).
*   `employees/`: Aplikasi untuk data karyawan.
*   `service_requests/`: Aplikasi untuk mengelola request layanan.
*   `media/`: Folder untuk file yang diupload user.
*   `manage.py`: Utilitas command-line Django (sudah dikonfigurasi menggunakan `pymysql`).

## Reset Database (Hanya untuk Development)

Terdapat script `reset_db.py` yang dapat digunakan untuk menghapus semua tabel di database (Hard Reset). **Gunakan dengan hati-hati!**

```bash
python reset_db.py
```

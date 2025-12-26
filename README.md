# 🍴 Restaurant Management System

CS 353 - Database Systems Project  
Team 15 - Bilkent University Fall 2025

---

## 🚀 Quick Setup

### Prerequisites
- Python 3.8+
- MySQL 8.0+

### 1. Setup Python
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Setup MySQL
Create MySQL user:
```sql
sudo mysql

CREATE USER 'rms_user'@'localhost' IDENTIFIED BY 'rms_password';
GRANT ALL PRIVILEGES ON rms.* TO 'rms_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Create `.env` file
```env
DB_HOST=127.0.0.1
DB_USER=rms_user
DB_PASSWORD=rms_password
DB_NAME=rms
SECRET_KEY=your-secret-key-here
```

### 4. Initialize database
```bash
sudo mysql < schema.sql
sudo mysql < insert.sql
```

### 5. Run the app
```bash
python app.py
```

Open http://127.0.0.1:5000

---

## 👤 Test Accounts

**Password for all accounts**: `password123`

| Username | Role |
|----------|------|
| jmanager | Manager |
| ewilliams | Staff |


---

## 👥 Team 15
- Deniz Yazıcı
- Hamza Chaaba
- Guillaume-Alain Priso Totto
- Ismail Temmar
- Amir Aliyev
# 🍴 Restaurant Management System

CS 353 - Database Systems Project  
Team 15 - Bilkent University Fall 2025

---

## 🚀 Quick Setup

### Prerequisites
- Python 3.8+
- MySQL 8.0+

### 1. Clone the repo
```bash
git clone <your-repo>
cd restaurant-management-system
```

### 2. Setup Python
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Setup MySQL
Create MySQL user:
```sql
mysql -u root -p

CREATE USER 'rms_user'@'localhost' IDENTIFIED BY 'rms_password';
GRANT ALL PRIVILEGES ON rms.* TO 'rms_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. Create `.env` file
```env
DB_HOST=127.0.0.1
DB_USER=rms_user
DB_PASSWORD=rms_password
DB_NAME=rms
SECRET_KEY=your-secret-key-here
```

### 5. Initialize database
```bash
mysql -u rms_user -prms_password < schema.sql
mysql -u rms_user -prms_password rms < seed_data.sql
```

### 6. Run the app
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
| ewilliams | Server |

---

## 🛠️ Troubleshooting

**"Access denied"** → Check `.env` credentials  
**"Table doesn't exist"** → Re-run `schema.sql`  
**"Invalid credentials"** → Password is `password123`

---

## 📂 Project Structure
```
├── app.py              # Flask application
├── db.py               # MySQL connection
├── schema.sql          # Database schema
├── seed_data.sql       # Demo data
├── templates/          # HTML pages
└── static/             # CSS/JS files
```

---

## 👥 Team 15
- Deniz Yazıcı
- Hamza Chaaba
- Guillaume-Alain Priso Totto
- Ismail Temmar
- Amir Aliyev
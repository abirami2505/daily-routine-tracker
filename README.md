# 🗓️ Personalized Daily Routine Tracker

A full-stack web application to track your daily habits, calculate a Discipline Score, and gain behavioral insights — built with **Flask + MySQL**.

---

## 🚀 Quick Start

### 1. Set Up MySQL Database

Open your MySQL client (MySQL Workbench, shell, or XAMPP) and run:

```sql
SOURCE schema.sql;
```

Or copy-paste the contents of `schema.sql` manually.

### 2. Configure Database Password

Edit `app.py` and update this line with your MySQL root password:

```python
app.config['MYSQL_PASSWORD'] = ''   # ← put your password here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
python app.py
```

Visit: **http://127.0.0.1:5000**

---

## 📁 Project Structure

```
daily_routine_tracker/
├── app.py                  # Flask backend (routes, logic)
├── schema.sql              # MySQL database schema
├── requirements.txt        # Python dependencies
├── templates/
│   ├── base.html           # Base layout (header, footer, nav)
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── dashboard.html      # Today's checklist + score ring
│   ├── history.html        # Past 30 days performance table
│   └── insights.html       # Behavioral insights + chart
└── static/
    ├── css/style.css       # Full design system (orange/white theme)
    └── js/main.js          # Shared JS utilities
```

---

## 🎯 Features

| Feature | Status |
|---|---|
| Register / Login / Logout | ✅ |
| Personalized site name (e.g., "Ram Routine") | ✅ |
| Full daily checklist (12 tasks across 6 categories) | ✅ |
| Daily Reflection textarea | ✅ |
| Animated discipline score ring | ✅ |
| Save progress to MySQL | ✅ |
| 30-day history table with badges | ✅ |
| Behavioral insights with Chart.js trend | ✅ |
| Streak counter | ✅ |
| Personalized tips based on performance | ✅ |
| Responsive mobile layout | ✅ |

---

## 🎨 Design

- **Background:** White (#FFFFFF)
- **Primary Orange:** #FF7A00
- **Secondary Orange:** #FFA94D
- **Text:** Dark Gray (#333333)
- **Font:** Inter (Google Fonts)
- **Layout:** Full-width, section-based (no cards on main pages)





    

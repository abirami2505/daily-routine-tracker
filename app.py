from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import mysql.connector
from mysql.connector import Error as MySQLError
import hashlib
import os
import pandas as pd
import joblib
from datetime import date, timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)

# ─── MySQL Configuration ───────────────────────────────────────────────────────
DB_CONFIG = {
    'host':     os.getenv('DB_HOST', 'crossover.proxy.rlwy.net'),
    'user':     os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'eQZPyCodLWczbWwlczEfxfvNLxuUKbyD'),
    'database': os.getenv('DB_NAME', 'railway'),
    'port':     int(os.getenv('DB_PORT', 49592)),
    'charset':  'utf8mb4',
    'autocommit': False,
}

# ─── Task Definitions ─────────────────────────────────────────────────────────
TASKS = [
    # Morning
    {"id": "wake_up",          "label": "Wake up – 5:30 AM",                            "category": "Morning",  "points": 10},
    {"id": "hot_water_chia",   "label": "Hot water with chia seeds",                     "category": "Morning",  "points": 8},
    {"id": "exercise",         "label": "Exercise (at least 30 mins)",                   "category": "Morning",  "points": 12},
    # Day
    {"id": "skill_college",    "label": "Learned any skill in college",                  "category": "Day",      "points": 10},
    # Evening
    {"id": "seeds_evening",    "label": "Sunflower & pumpkin seeds – 5:10 PM",           "category": "Evening",  "points": 8},
    {"id": "sql_practice",     "label": "SQL Practice – 5:30 PM to 6:30 PM",             "category": "Evening",  "points": 12},
    # Night
    {"id": "leetcode",         "label": "Solve 1 LeetCode problem – 7:45 PM to 8:30 PM","category": "Night",    "points": 12},
    {"id": "dsa_learning",     "label": "DSA Learning – 8:35 PM to 9:30 PM",             "category": "Night",    "points": 12},
    {"id": "build_projects",   "label": "Build Projects – 9:30 PM to 11:00 PM",          "category": "Night",    "points": 15},
    # Health
    {"id": "hot_water_sleep",  "label": "Drink hot water before sleep",                  "category": "Health",   "points": 5},
    {"id": "stay_hydrated",    "label": "Stay hydrated throughout the day",               "category": "Health",   "points": 5},
    # Optional
    {"id": "daily_reflection", "label": "Daily Reflection",                               "category": "Optional", "points": 3},
]

TOTAL_POINTS = sum(t["points"] for t in TASKS)


# ─── DB Helpers ───────────────────────────────────────────────────────────────

def get_db():
    """Open a fresh connection per request."""
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    """
    Create the database and all tables if they don't exist.
    Uses a temporary connection WITHOUT specifying the database.
    """
    try:
        cfg = {k: v for k, v in DB_CONFIG.items() if k != 'database'}
        conn = mysql.connector.connect(**cfg)
        cur  = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id         INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
                username   VARCHAR(50)  NOT NULL UNIQUE,
                password   VARCHAR(64)  NOT NULL,
                created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS daily_logs (
                id               INT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
                user_id          INT       NOT NULL,
                log_date         DATE      NOT NULL,
                tasks_completed  TINYINT   NOT NULL DEFAULT 0,
                discipline_score SMALLINT  NOT NULL DEFAULT 0,
                reflection       TEXT,
                created_at       DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uq_user_date (user_id, log_date),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS completed_tasks (
                id      INT         NOT NULL AUTO_INCREMENT PRIMARY KEY,
                log_id  INT         NOT NULL,
                task_id VARCHAR(50) NOT NULL,
                FOREIGN KEY (log_id) REFERENCES daily_logs(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("[DB] Database `routine_tracker` and all tables are ready.")
    except MySQLError as e:
        print(f"[DB ERROR] {e}")
        print("[DB ERROR] Check that MySQL is running and credentials in app.py are correct.")


# ─── Auth helpers ─────────────────────────────────────────────────────────────

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ─── Routes: Auth ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        cur.execute(
            'SELECT * FROM users WHERE username = %s AND password = %s',
            (username, hash_password(password))
        )
        account = cur.fetchone()
        cur.close(); conn.close()

        if account:
            session['loggedin'] = True
            session['id']       = account['id']
            session['username'] = account['username']
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password.'

    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if not username or not password:
            error = 'Username and password are required.'
        elif len(username) < 3:
            error = 'Username must be at least 3 characters.'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters.'
        elif password != confirm:
            error = 'Passwords do not match.'
        else:
            conn = get_db()
            cur  = conn.cursor(dictionary=True)
            cur.execute('SELECT id FROM users WHERE username = %s', (username,))
            if cur.fetchone():
                error = 'Username already exists. Please choose another.'
            else:
                cur.execute(
                    'INSERT INTO users (username, password) VALUES (%s, %s)',
                    (username, hash_password(password))
                )
                conn.commit()
            cur.close(); conn.close()

            if not error:
                return redirect(url_for('login'))

    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ─── Routes: Dashboard ────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    today = date.today().isoformat()
    conn  = get_db()
    cur   = conn.cursor(dictionary=True)

    cur.execute(
        'SELECT * FROM daily_logs WHERE user_id = %s AND log_date = %s',
        (session['id'], today)
    )
    today_log = cur.fetchone()

    completed_ids   = set()
    reflection_text = ''
    if today_log:
        cur.execute(
            'SELECT task_id FROM completed_tasks WHERE log_id = %s',
            (today_log['id'],)
        )
        completed_ids   = {row['task_id'] for row in cur.fetchall()}
        reflection_text = today_log.get('reflection', '') or ''

    cur.close(); conn.close()

    categories_order = ["Morning", "Day", "Evening", "Night", "Health", "Optional"]
    category_icons   = {
        "Morning":  "🌅", "Day": "🎓", "Evening": "🌆",
        "Night":    "🌙", "Health": "💧", "Optional": "✍️",
    }
    grouped_tasks = {
        cat: {"icon": category_icons[cat], "tasks": [t for t in TASKS if t["category"] == cat]}
        for cat in categories_order
    }

    return render_template(
        'dashboard.html',
        username=session['username'],
        tasks=TASKS,
        grouped_tasks=grouped_tasks,
        completed_ids=completed_ids,
        reflection_text=reflection_text,
        today=today,
        total_points=TOTAL_POINTS,
        today_log=today_log,
        categories_order=categories_order,
    )


# ─── Routes: Save Progress ────────────────────────────────────────────────────

@app.route('/save_progress', methods=['POST'])
@login_required
def save_progress():
    data               = request.get_json()
    completed_task_ids = data.get('completed_tasks', [])
    reflection_text    = data.get('reflection', '')
    today              = date.today().isoformat()

    score      = sum(t['points'] for t in TASKS if t['id'] in completed_task_ids)
    total_done = len(completed_task_ids)

    conn = get_db()
    cur  = conn.cursor(dictionary=True)

    cur.execute(
        'SELECT id FROM daily_logs WHERE user_id = %s AND log_date = %s',
        (session['id'], today)
    )
    existing = cur.fetchone()

    if existing:
        log_id = existing['id']
        cur.execute(
            '''UPDATE daily_logs
               SET tasks_completed = %s, discipline_score = %s, reflection = %s
               WHERE id = %s''',
            (total_done, score, reflection_text, log_id)
        )
        cur.execute('DELETE FROM completed_tasks WHERE log_id = %s', (log_id,))
    else:
        cur.execute(
            '''INSERT INTO daily_logs (user_id, log_date, tasks_completed, discipline_score, reflection)
               VALUES (%s, %s, %s, %s, %s)''',
            (session['id'], today, total_done, score, reflection_text)
        )
        log_id = cur.lastrowid

    for tid in completed_task_ids:
        cur.execute(
            'INSERT INTO completed_tasks (log_id, task_id) VALUES (%s, %s)',
            (log_id, tid)
        )

    conn.commit()
    cur.close(); conn.close()

    percentage = round((score / TOTAL_POINTS) * 100, 1)
    return jsonify({
        'success':    True,
        'score':      score,
        'total':      TOTAL_POINTS,
        'percentage': percentage,
        'completed':  total_done,
        'total_tasks': len(TASKS),
    })


# ─── Routes: History ──────────────────────────────────────────────────────────

@app.route('/history')
@login_required
def history():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute(
        '''SELECT log_date, tasks_completed, discipline_score
           FROM daily_logs
           WHERE user_id = %s
           ORDER BY log_date DESC
           LIMIT 30''',
        (session['id'],)
    )
    logs = [dict(row) for row in cur.fetchall()]
    cur.close(); conn.close()

    for log in logs:
        pct = round((log['discipline_score'] / TOTAL_POINTS) * 100, 1)
        log['percentage']   = pct
        log['total_tasks']  = len(TASKS)
        log['total_points'] = TOTAL_POINTS
        if pct >= 80:   log['badge'] = ('Excellent', 'badge-excellent')
        elif pct >= 60: log['badge'] = ('Good',      'badge-good')
        elif pct >= 40: log['badge'] = ('Average',   'badge-average')
        else:           log['badge'] = ('Needs Work', 'badge-low')

    return render_template('history.html', username=session['username'], logs=logs)


# ─── Routes: Insights ─────────────────────────────────────────────────────────

@app.route('/insights')
@login_required
def insights():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute(
        '''SELECT log_date, tasks_completed, discipline_score
           FROM daily_logs
           WHERE user_id = %s
           ORDER BY log_date DESC
           LIMIT 30''',
        (session['id'],)
    )
    logs = [dict(row) for row in cur.fetchall()]
    cur.close(); conn.close()

    if not logs:
        return render_template('insights.html', username=session['username'], has_data=False)

    scores    = [l['discipline_score'] for l in logs]
    avg_score = round(sum(scores) / len(scores), 1)
    avg_pct   = round((avg_score / TOTAL_POINTS) * 100, 1)
    max_score = max(scores)
    min_score = min(scores)
    streak    = _calculate_streak(logs)

    if avg_pct >= 80:
        insight_message = "🏆 Outstanding discipline! You're building an elite routine. Keep it up!"
        insight_level   = 'high'
    elif avg_pct >= 60:
        insight_message = "💪 Great consistency! A few more pushes and you'll be elite."
        insight_level   = 'medium-high'
    elif avg_pct >= 40:
        insight_message = "📈 Decent progress. Focus on completing 2–3 more tasks each day."
        insight_level   = 'medium'
    else:
        insight_message = "⚠️ Improve consistency. Small wins compound—start with one more task tomorrow!"
        insight_level   = 'low'

    logs_asc   = list(reversed(logs))
    chart_data = {
        'dates':  [str(l['log_date']) for l in logs_asc],
        'scores': [round((l['discipline_score'] / TOTAL_POINTS) * 100, 1) for l in logs_asc],
    }

    return render_template(
        'insights.html',
        username=session['username'],
        has_data=True,
        avg_score=avg_score,
        avg_pct=avg_pct,
        max_score=max_score,
        min_score=min_score,
        total_days=len(logs),
        streak=streak,
        insight_message=insight_message,
        insight_level=insight_level,
        chart_data=chart_data,
        total_points=TOTAL_POINTS,
    )


def _calculate_streak(logs):
    """Count consecutive day streak (logs are DESC ordered)."""
    if not logs:
        return 0
    streak = 0
    prev   = None
    for log in logs:
        d = log['log_date'] if isinstance(log['log_date'], date) else date.fromisoformat(str(log['log_date']))
        if prev is None:
            prev   = d
            streak = 1
        elif (prev - d).days == 1:
            streak += 1
            prev = d
        else:
            break
    return streak


# ─── Start ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

import sqlite3


def init_db():
    conn = sqlite3.connect('fitness_bot.db')
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                lang TEXT,
                points INTEGER DEFAULT 0,
                streak INTEGER DEFAULT 0,
                tasks_completed INTEGER DEFAULT 0,
                strength_modifier REAL DEFAULT 1.0,
                streak_timestamp INTEGER DEFAULT 0
            )
            """)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            task_code TEXT,
            number INTEGER,
            multiplier REAL DEFAULT 1.0,
            created_at INTEGER,
            status TEXT DEFAULT 'pending',
            task_index INTEGER
        )
    ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS friends (
                user_id INTEGER,
                friend_id INTEGER,
                PRIMARY KEY (user_id, friend_id)
            )
        ''')
    conn.commit()
    conn.close()


def add_user(user_id, username, lang):
    with sqlite3.connect("fitness_bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (id, username, lang) VALUES (?, ?, ?)", (user_id, username, lang))
        cursor.execute("UPDATE users SET lang = ? WHERE id = ?", (lang, user_id))
        conn.commit()


def get_user(id):
    conn = sqlite3.connect('fitness_bot.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (id,))
    user = c.fetchone()
    conn.close()
    return {
        'user_id': user[0],
        'username': user[1],
        'lang': user[2],
        'points': user[3],
        'streak': user[4],
        'tasks_completed': user[5],
        'strength_modifier': user[6]
    }


def get_leaderboard():
    with sqlite3.connect("fitness_bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, points, streak FROM users ORDER BY points DESC")
        return cursor.fetchall()


def update_user(user_id, points, streak, tasks_completed):
    with sqlite3.connect("fitness_bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE users
        SET points = ?, streak = ?, tasks_completed = ?
        WHERE id = ?
        """, (points, streak, tasks_completed, user_id))
        conn.commit()


def add_task(user_id, task_code, number, multiplier, created_at, task_index):
    conn = sqlite3.connect('fitness_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (user_id, task_code, number, multiplier, created_at, task_index) VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, task_code, number, multiplier, created_at, task_index))
    conn.commit()
    conn.close()


def mark_task_done(user_id, task_code):
    with sqlite3.connect("fitness_bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE user_id = ? AND task_code = ?", (user_id, task_code))
        conn.commit()


def get_today_tasks(user_id):
    conn = sqlite3.connect('fitness_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT task_code, number, multiplier, task_index FROM tasks WHERE user_id = ? AND status = 'pending' ORDER BY task_index
    ''', (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks


def get_streak_timestamp(user_id):
    conn = sqlite3.connect('fitness_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT streak_timestamp FROM users WHERE id = ?
    ''', (user_id,))
    streak_timestamp = cursor.fetchone()
    conn.close()
    return streak_timestamp


def update_streak_timestamp(user_id, streak_timestamp):
    with sqlite3.connect("fitness_bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE users
        SET streak_timestamp = ?
        WHERE id = ?
        """, (streak_timestamp, user_id))
        conn.commit()


# Create an accepting system from the friend-side
def accept_friend(user_id, friend_id):
    with sqlite3.connect("fitness_bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO friends (user_id, friend_id) VALUES (?, ?)", (user_id, friend_id))
        conn.commit()


def get_friends(user_id):
    conn = sqlite3.connect('fitness_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.username, u.points, u.streak FROM friends f
        JOIN users u ON (f.friend_id = u.id OR f.user_id = u.id)
        WHERE (f.user_id = ? OR f.friend_id = ?) AND u.id != ?
    ''', (user_id, user_id, user_id))
    friends = cursor.fetchall()
    conn.close()
    return friends

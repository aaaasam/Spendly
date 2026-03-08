from flask import Flask, render_template, request, jsonify, Response
import sqlite3
import csv
import io
from datetime import datetime, date
import json

app = Flask(__name__)
DB = 'expenses.db'

CATEGORIES = ['Food', 'Transport', 'Housing', 'Entertainment', 'Health', 'Shopping', 'Education', 'Other']

CATEGORY_COLORS = {
    'Food': '#FF6B6B',
    'Transport': '#4ECDC4',
    'Housing': '#45B7D1',
    'Entertainment': '#96CEB4',
    'Health': '#FFEAA7',
    'Shopping': '#DDA0DD',
    'Education': '#98D8C8',
    'Other': '#F0A500'
}

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                note TEXT
            )
        ''')
        # Seed some demo data if empty
        count = conn.execute('SELECT COUNT(*) FROM expenses').fetchone()[0]
        if count == 0:
            seed = [
                ('Groceries', 85.50, 'Food', '2025-03-01', 'Weekly shop'),
                ('Uber ride', 12.00, 'Transport', '2025-03-02', ''),
                ('Netflix', 18.00, 'Entertainment', '2025-03-03', 'Monthly sub'),
                ('Electricity bill', 120.00, 'Housing', '2025-03-04', 'March bill'),
                ('Lunch out', 22.00, 'Food', '2025-03-05', 'With colleagues'),
                ('Gym membership', 45.00, 'Health', '2025-03-06', ''),
                ('Books', 35.00, 'Education', '2025-03-07', 'Python textbook'),
                ('Online shopping', 78.00, 'Shopping', '2025-03-10', 'Clothes'),
                ('Petrol', 60.00, 'Transport', '2025-03-12', 'Full tank'),
                ('Coffee & snacks', 15.00, 'Food', '2025-03-14', ''),
                ('Doctor visit', 80.00, 'Health', '2025-03-15', 'Check-up'),
                ('Restaurant', 95.00, 'Food', '2025-03-18', 'Birthday dinner'),
                ('Bus pass', 30.00, 'Transport', '2025-02-01', 'Monthly pass'),
                ('Rent', 1200.00, 'Housing', '2025-02-01', 'February rent'),
                ('Takeaway', 40.00, 'Food', '2025-02-14', 'Valentine dinner'),
                ('Cinema', 25.00, 'Entertainment', '2025-02-20', 'With friends'),
                ('Spotify', 10.00, 'Entertainment', '2025-02-03', ''),
                ('Groceries', 92.00, 'Food', '2025-02-08', ''),
                ('Train tickets', 55.00, 'Transport', '2025-02-22', 'Weekend trip'),
                ('Pharmacy', 28.00, 'Health', '2025-02-25', 'Vitamins'),
                ('Rent', 1200.00, 'Housing', '2025-01-01', 'January rent'),
                ('Groceries', 77.00, 'Food', '2025-01-05', ''),
                ('New headphones', 150.00, 'Shopping', '2025-01-10', ''),
                ('Bus pass', 30.00, 'Transport', '2025-01-01', ''),
                ('Online course', 49.00, 'Education', '2025-01-15', 'Udemy'),
            ]
            conn.executemany(
                'INSERT INTO expenses (title, amount, category, date, note) VALUES (?,?,?,?,?)', seed
            )

init_db()

@app.route('/')
def index():
    return render_template('index.html', categories=CATEGORIES, colors=json.dumps(CATEGORY_COLORS))

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    category = request.args.get('category', '')
    month = request.args.get('month', '')
    with get_db() as conn:
        query = 'SELECT * FROM expenses WHERE 1=1'
        params = []
        if category:
            query += ' AND category = ?'
            params.append(category)
        if month:
            query += ' AND strftime("%Y-%m", date) = ?'
            params.append(month)
        query += ' ORDER BY date DESC'
        rows = conn.execute(query, params).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    data = request.json
    with get_db() as conn:
        conn.execute(
            'INSERT INTO expenses (title, amount, category, date, note) VALUES (?,?,?,?,?)',
            (data['title'], float(data['amount']), data['category'], data['date'], data.get('note', ''))
        )
    return jsonify({'ok': True})

@app.route('/api/expenses/<int:eid>', methods=['DELETE'])
def delete_expense(eid):
    with get_db() as conn:
        conn.execute('DELETE FROM expenses WHERE id = ?', (eid,))
    return jsonify({'ok': True})

@app.route('/api/monthly-summary')
def monthly_summary():
    with get_db() as conn:
        rows = conn.execute('''
            SELECT strftime("%Y-%m", date) as month, SUM(amount) as total
            FROM expenses
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        ''').fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/category-summary')
def category_summary():
    month = request.args.get('month', '')
    with get_db() as conn:
        query = '''
            SELECT category, SUM(amount) as total
            FROM expenses
        '''
        params = []
        if month:
            query += ' WHERE strftime("%Y-%m", date) = ?'
            params.append(month)
        query += ' GROUP BY category ORDER BY total DESC'
        rows = conn.execute(query, params).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/export')
def export_csv():
    category = request.args.get('category', '')
    month = request.args.get('month', '')
    with get_db() as conn:
        query = 'SELECT title, amount, category, date, note FROM expenses WHERE 1=1'
        params = []
        if category:
            query += ' AND category = ?'
            params.append(category)
        if month:
            query += ' AND strftime("%Y-%m", date) = ?'
            params.append(month)
        query += ' ORDER BY date DESC'
        rows = conn.execute(query, params).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Title', 'Amount', 'Category', 'Date', 'Note'])
    for r in rows:
        writer.writerow([r['title'], r['amount'], r['category'], r['date'], r['note']])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=expenses.csv'}
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)

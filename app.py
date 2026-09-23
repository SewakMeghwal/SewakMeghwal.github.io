from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SENDFILE_MAX_AGE_DEFAULT'] = 0

db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    status = request.args.get('status', '')
    is_admin = session.get('admin', False)
    return render_template('index.html', status=status, is_admin=is_admin)

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()

    if not name or not email or not message:
        return redirect(url_for('home', status='error'))

    new_message = Message(name=name, email=email, message=message)
    db.session.add(new_message)
    db.session.commit()

    return redirect(url_for('home', status='success'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin123':  # Change this password
            session['admin'] = True
            return redirect(url_for('messages'))
        else:
            return render_template('login.html', error='Invalid password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/messages')
def messages():
    if not session.get('admin'):
        return redirect(url_for('login'))
    all_messages = Message.query.order_by(Message.timestamp.desc()).all()
    return render_template('messages.html', messages=all_messages)

if __name__ == '__main__':
    app.run(debug=True)

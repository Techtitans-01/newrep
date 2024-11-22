from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Required for flash messages
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)  # Deadline as DateTime
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = db.Column(db.DateTime, nullable=True)  # Completion timestamp

    def __repr__(self):
        return f'Task {self.id} - {self.title}'

@app.route('/')
def index():
    # Fetch tasks from the database
    tasks = Task.query.all()
    # Sort tasks by deadline (earliest deadline first)
    sorted_tasks = sorted(tasks, key=lambda task: task.deadline)
    # Render the tasks in the template
    return render_template('index.html', tasks=sorted_tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')
    deadline = request.form.get('deadline')

    # Validate deadline
    if deadline:
        deadline_date = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')
        if deadline_date < datetime.now():
            flash('Deadline must be today or in the future!', 'error')
            return redirect(url_for('index'))

    # Create task with deadline as a datetime object
    new_task = Task(title=title, description=description, deadline=deadline_date)
    db.session.add(new_task)
    db.session.commit()
    flash('Task added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    else:
        flash('Task not found!', 'error')
    return redirect(url_for('index'))

@app.route('/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    task = Task.query.get(task_id)
    if task:
        status = request.form['status']
        task.status = status
        if status == "Completed":
            task.updated_at = datetime.utcnow()  # Set the completion timestamp
        db.session.commit()
        flash('Task updated successfully!', 'success')
    else:
        flash('Task not found!', 'error')
    return redirect(url_for('index'))

@app.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.status = "Completed"
        task.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Task marked as completed!', 'success')
    else:
        flash('Task not found!', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

from flask import Blueprint, render_template, request, g, redirect, url_for, abort, Response
from app.auth import login_required
from . models import User, Expense
from app import db
#Tools to export csv
import csv
from io import StringIO
#Some DB query spicy
from sqlalchemy import func

bp = Blueprint('tracker', __name__, url_prefix='/tracker')

#Tracker landing page (once loged in) - Dashboard is supossed to be here
@bp.route('/index')
@login_required
def index():
    #Metrics to show in the dashboard
    total_expense = db.session.query(
        func.sum(Expense.amount)
    ).filter(Expense.user_id==g.user.id).scalar()

    avg_spent = db.session.query(
        func.avg(Expense.amount)
    ).filter(Expense.user_id==g.user.id).scalar()

    max_expense = Expense.query.filter_by(
        user_id=g.user.id).order_by(Expense.amount.desc()).first()
    
    avg_per_type = (
        db.session.query(
            Expense.expense_type,
            func.avg(Expense.amount)
        ).filter(Expense.user_id==g.user.id).group_by(Expense.expense_type).all()
    )

    #Chart Elements
    expense_types = [row[0] for row in avg_per_type]
    avg_amounts = [float(row[1]) for row in avg_per_type]
    
    return render_template(
        'tracker/index.html',
        total_expense=total_expense,
        avg_spent=avg_spent,
        max_expense=max_expense,
        avg_per_type=avg_per_type,
        expense_types=expense_types,
        avg_amounts=avg_amounts)

#Expense list - Register/Delete/Edit and see history
@bp.route('/expenses')
@login_required
def expenses():
    expenses = Expense.query.all()
    return render_template('tracker/expenses.html', expenses=expenses)

@bp.route('/add_expense' ,methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        expense_type = request.form['expense_type']
        amount = request.form['amount']
        description = request.form['description']

        expense = Expense(g.user.id, expense_type, amount, description)
        db.session.add(expense)
        db.session.commit()
        return redirect(url_for('tracker.expenses'))

    return render_template('tracker/add_expense.html')

#Get expense for UPDATE and DELETE
def get_expense(id):
    expense = Expense.query.get_or_404(id)
    #Some security 
    if expense.user_id != g.user.id:
        abort(403)
    return expense

@bp.route('/delete/<int:id>', methods = ['GET', 'POST'])
@login_required
def delete(id):
    expense = get_expense(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('tracker.expenses'))

@bp.route('/update/<int:id>', methods = ['GET', 'POST'])
@login_required
def update(id):
    expense = get_expense(id)
    if request.method == 'POST':
        #expense.expense_type = request.form['expense_type']
        expense.amount = request.form['amount']
        expense.description = request.form['description']
        db.session.commit()
        return redirect(url_for('tracker.expenses'))
    return render_template('tracker/update.html' , expense=expense)

@bp.route('export_csv/')
@login_required
def export_csv():
    #Get only user's expense list
    expenses = Expense.query.filter_by(
        user_id=g.user.id
    ).all()

    #Setting up CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Category',
        'Amount',
        'Description',
        'Date'
    ])

    # Getting every record
    for expense in expenses:
        writer.writerow([
            expense.expense_type,
            expense.amount,
            expense.description,
            expense.date.strftime('%Y-%m-%d')
        ])

    #Get CSV data
    csv_data = output.getvalue()

    #Dowloading file when the user clicks on "export CSV"
    return Response(csv_data,
                    mimetype='text/csv',
                    headers={
                        'Content-Disposition':
                        'attachment; filename=expenses.csv'
                    }
                    )

    
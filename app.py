from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Expense, User, Household
from werkzeug.security import generate_password_hash, check_password_hash
from utils import check_password, login_required, generate_join_code ,convert_to_hebrew_ai
from datetime import datetime
from flask_migrate import Migrate # 1

#create the app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.secret_key = 'dev-secret-change-in-production'

#initialize the database
db.init_app(app)
migrate = Migrate(app, db) # 2

#routes
@app.route("/")
@login_required
def home():
    user_id = session['user_id']
    household_id = session['household_id']
    today = datetime.now()
    date_from = datetime(today.year, today.month, 1)

    current_household = Household.query.filter_by(id=household_id).first()
    join_code = current_household.join_code

    #get all the expenses for the current month
    household_expenses = Expense.query.filter(Expense.household_id==household_id, Expense.date_posted>=date_from).all()
    total_expenses = sum(expense.amount for expense in household_expenses)

    expenses_by_category = {expense.category: [] for expense in household_expenses}
    for expense in household_expenses:
        expenses_by_category[expense.category].append(expense)
    return render_template('index.html', household_expenses=household_expenses,
     total_expenses=total_expenses, expenses_by_category=expenses_by_category,
      join_code=join_code)

@app.route("/history", methods = ['GET'])
@login_required
def history():
    user_id = session['user_id']
    household_id = session['household_id']
    all_expenses = Expense.query.filter_by(household_id=household_id).order_by(Expense.date_posted.desc()).all()

    all_history = {}
    for exp in all_expenses:
        month_key = exp.date_posted.strftime('%m/%Y')
        category_key = exp.category

        if month_key not in all_history:
            all_history[month_key] = {}
        if category_key not in all_history[month_key]:
            all_history[month_key][category_key] = []
        all_history[month_key][category_key].append(exp)
    month_keys = sorted(
        all_history.keys(),
        key=lambda m: datetime.strptime(m, '%m/%Y'),
        reverse=True,
    )
    return render_template(
        'history.html',
        all_history=all_history,
        month_keys=month_keys,
    )


@app.route("/setting", methods=["GET", "POST"])
@login_required
def setting():
    user_id = session["user_id"]
    household_id = session["household_id"]
    user = User.query.get(user_id)
    household = Household.query.get(household_id)
    if not user or not household:
        return redirect(url_for("home"))

    error_msg = None
    if request.method == "POST":
        hebrew_name = (request.form.get("hebrew_name") or "").strip()
        if not hebrew_name:
            error_msg = "יש להזין שם תצוגה."
        elif len(hebrew_name) > 50:
            error_msg = "השם ארוך מדי (עד 50 תווים)."
        else:
            user.hebrew_name = hebrew_name
            db.session.commit()
            session["hebrew_name"] = hebrew_name
            return redirect(url_for("setting"))

    return render_template(
        "setting.html",
        user=user,
        join_code=household.join_code,
        error_msg=error_msg,
    )


@app.route("/login", methods = ['GET','POST'])
def login():
    error_msg = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = username
            session['household_id'] = user.household_id
            session['hebrew_name'] = user.hebrew_name
            return redirect(url_for('home'))
        else: error_msg = "Invalid username or password"
    
    return render_template('login.html', error_msg=error_msg)

@app.route("/logout", methods = ['GET'])
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('household_id', None)
    session.pop('hebrew_name', None)
    return redirect(url_for('login'))


@app.route("/register", methods = ['GET','POST'])
def register():
    errors = []
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        join_code_input = request.form.get('join_code')
        hebrew_name = request.form.get('hebrew_name')
        if not hebrew_name:
            hebrew_name = convert_to_hebrew_ai(username)

        errors = check_password(password)
        if not errors:
            hashed_password = generate_password_hash(password)

            try:
                if join_code_input:
                    existing_household = Household.query.filter_by(join_code=join_code_input).first()
                    if not existing_household:
                        errors.append("Invalid Join Code. Please try again or leave blank to create a new household.")
                        return render_template('register.html', errors=errors)
                    target_household = existing_household.id
                else:
                    new_household = Household(join_code=generate_join_code())
                    db.session.add(new_household)
                    db.session.commit()
                    target_household = new_household.id
                new_user = User(username=username, email=email, password=hashed_password, household_id=target_household, hebrew_name=hebrew_name)
                db.session.add(new_user)
                db.session.commit()
                session['user_id'] = new_user.id
                session['username'] = username
                session['household_id'] = target_household
                session['hebrew_name'] = hebrew_name
                return redirect(url_for('home'))
            except:
                db.session.rollback()
                errors.append( "There was an issue registering the user")

    #if the request is a GET request, render the register.html template
    return render_template('register.html', errors=errors)


@app.route("/add" , methods=["GET", "POST"])
@login_required
def add_expense():
    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        description = request.form.get("description")
        user_id = session['user_id']
        household_id = session['household_id']

        new_expense = Expense(amount=amount, category=category, description=description,user_id=user_id, household_id=household_id)

        try:
            db.session.add(new_expense)
            db.session.commit()
            return redirect(url_for('home'))
        except:
            return "There was an issue adding your expense to the database"
    #if the request is a GET request, render the add_expense.html template
    return render_template("add_expense.html")

@app.route("/delete_expense", methods=["POST"])
@login_required
def delete_expense():
    expense_id = request.form.get("expense_id") 
    
    if not expense_id:
         return "Invalid request", 400

    expense = Expense.query.get(expense_id)
    
    if expense and expense.household_id == session.get('household_id'):
        db.session.delete(expense)
        db.session.commit()
        return redirect(url_for('home'))
        
    return "שגיאה: אין לך הרשאה למחוק הוצאה זו.", 403

@app.route("/edit_expense", methods=["POST"])
@login_required
def edit_expense():
    expense_id = request.form.get("expense_id")
    amount_str = request.form.get("amount") # קולטים כטקסט
    category = request.form.get("category")
    description = request.form.get("description")

    if not expense_id or not amount_str:
        return "Invalid request", 400

    expense = Expense.query.get(expense_id)
    
    # בדיקת האבטחה (מעולה!)
    if expense and expense.household_id == session.get('household_id'):
        try:
            # המרה ממחרוזת למספר עשרוני
            expense.amount = float(amount_str) 
        except ValueError:
            return "שגיאה: הסכום חייב להיות מספר תקין.", 400
            
        expense.category = category
        expense.description = description
        db.session.commit()
        
        return redirect(url_for('home'))
        
    return "שגיאה: אין לך הרשאה לערוך הוצאה זו.", 403
#run the app
if __name__ == "__main__":
    app.run(debug=True)
    
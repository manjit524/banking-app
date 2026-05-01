from flask import Flask, request, render_template, redirect, session, flash
from banking_logic import deposit, withdraw, transfer
from db import get_connection
import bcrypt

app = Flask(__name__)
app.secret_key = "supersecretkey"


# 🔹 HOME ROUTE
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/dashboard')
    else:
        return redirect('/login')


# 🔹 REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        Mpin = request.form['Mpin']
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        Mpin_hashed = bcrypt.hashpw(Mpin.encode('utf-8'), bcrypt.gensalt())
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # insert user
        cursor.execute(
            "INSERT INTO users (name, email, password, mpin) VALUES (%s, %s, %s, %s)",
            (name, email, hashed,Mpin_hashed)
        )
        
        user_id = cursor.lastrowid   # ✅ get new user ID
        
        # 🔥 CREATE ACCOUNT AUTOMATICALLY
        cursor.execute(
            "INSERT INTO accounts (user_id, balance, account_type) VALUES (%s, %s, %s)",
            (user_id, 0, 'Savings')
        )
        
        conn.commit()
        conn.close()
        
        return redirect('/login')
    
    return render_template('register.html')

# 🔹 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id, password FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        
        if user:
            user_id, stored_hash = user
            
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                session['user_id'] = user_id
                return redirect('/dashboard')
            else:
                return "Invalid Password"
        else:
            return "User not found"
    
    return render_template('login.html')


# 🔹 DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM accounts WHERE user_id = %s", (user_id,))
    account = cursor.fetchone()
    
    conn.close()

    return render_template('dashboard.html', account=account)

# 🔹 BALANCE CHECK
@app.route('/balance', methods=['GET', 'POST'])
def balance_page():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    balance_to_show = None
    
    if request.method == 'POST':
        mpin = request.form.get('Mpin', '')
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT mpin FROM users WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        
        if user_data and user_data['mpin']:
            stored_hash = user_data['mpin']
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            
            if bcrypt.checkpw(mpin.encode('utf-8'), stored_hash):
                cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_id,))
                account = cursor.fetchone()
                if account:
                    balance_to_show = account['balance']
                else:
                    flash("No account found", "danger")
            else:
                flash("Invalid MPIN", "danger")
        else:
            flash("User not found or MPIN not set", "danger")
            
        conn.close()

    return render_template('balance.html', balance=balance_to_show)

# 🔹 LOGOUT
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')


# 🔹 DEPOSIT
@app.route('/deposit', methods=['GET', 'POST'])
def deposit_page():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (user_id,))
    account = cursor.fetchone()
    
    if not account:
        flash("No account found", "danger")
        return redirect('/dashboard')

    account_id = account[0]

    if request.method == 'POST':
        amount = float(request.form['amount'])

        if amount <= 0:
            flash("Amount must be greater than 0", "danger")
        else:
            mpin = request.form.get('Mpin', '')
            cursor.execute("SELECT mpin FROM users WHERE user_id = %s", (user_id,))
            user_data = cursor.fetchone()
            
            if user_data and user_data[0]:
                stored_hash = user_data[0]
                if isinstance(stored_hash, str):
                    stored_hash = stored_hash.encode('utf-8')
                
                if bcrypt.checkpw(mpin.encode('utf-8'), stored_hash):
                    deposit(account_id, amount)
                    flash("Deposit Successful", "success")
                else:
                    flash("Invalid MPIN", "danger")
            else:
                flash("User not found or MPIN not set", "danger")
        
        return redirect('/dashboard')
    
    return render_template('deposit.html')


# 🔹 WITHDRAW (FIXED)
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw_page():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (user_id,))
    account = cursor.fetchone()

    if not account:
        flash("No account found", "danger")
        return redirect('/dashboard')

    account_id = account[0]

    if request.method == 'POST':
        amount = float(request.form['amount'])

        if amount <= 0:
            flash("Invalid amount", "danger")
        else:
            mpin = request.form.get('Mpin', '')
            cursor.execute("SELECT mpin FROM users WHERE user_id = %s", (user_id,))
            user_data = cursor.fetchone()
            
            if user_data and user_data[0]:
                stored_hash = user_data[0]
                if isinstance(stored_hash, str):
                    stored_hash = stored_hash.encode('utf-8')
                
                if bcrypt.checkpw(mpin.encode('utf-8'), stored_hash):
                    withdraw(account_id, amount)
                    flash("Withdraw Successful", "success")
                else:
                    flash("Invalid MPIN", "danger")
            else:
                flash("User not found or MPIN not set", "danger")
            
        
        return redirect('/dashboard')

    return render_template('withdraw.html')


# 🔹 TRANSFER (FIXED)
@app.route('/transfer', methods=['GET', 'POST'])
def transfer_page():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Fetch the sender's account ID
    cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (user_id,))
    account_row = cursor.fetchone()

    if not account_row:
        flash("No account found", "danger")
        return redirect('/dashboard')

    # account_row is a tuple like (101,), so we grab the first element
    from_account_id = account_row[0]

    if request.method == 'POST':
        try:
            to_account_id = int(request.form.get('to_acc'))
            amount = float(request.form.get('amount', 0))
            mpin = request.form.get('Mpin', '')

            if amount <= 0:
                flash("Amount must be greater than zero", "danger")
                return redirect('/transfer')

            # Verify MPIN
            cursor.execute("SELECT mpin FROM users WHERE user_id = %s", (user_id,))
            user_data = cursor.fetchone()
            
            if user_data and user_data[0]:
                stored_hash = user_data[0]
                if isinstance(stored_hash, str):
                    stored_hash = stored_hash.encode('utf-8')
                
                if bcrypt.checkpw(mpin.encode('utf-8'), stored_hash):
                    # CALL TRANSFER: Pass from, to, and amount
                    # Ensure your transfer() function accepts these 3 arguments
                    transfer(from_account_id, to_account_id, amount)
                    flash("Transfer Successful", "success")
                    return redirect('/dashboard')
                else:
                    flash("Invalid MPIN", "danger")
            else:
                flash("User not found or MPIN not set", "danger")
                
        except ValueError:
            flash("Invalid input. Please enter numbers for account and amount.", "danger")
        
        return redirect('/transfer')

    return render_template('transfer.html')

# Transactions
@app.route('/transactions')
def transactions_page():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # get user's account
    cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (user_id,))
    account = cursor.fetchone()
    
    if not account:
        return "No account found"
    
    account_id = account['account_id']
    
    # get transactions
    cursor.execute(
        "SELECT * FROM transactions WHERE account_id = %s ORDER BY date DESC",
        (account_id,)
    )
    transactions = cursor.fetchall()
    
    conn.close()

    return render_template('transactions.html', transactions=transactions)


# 🔹 RUN APP
if __name__ == '__main__':
    app.run(debug=True)
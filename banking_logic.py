from db import get_connection

def deposit(account_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM accounts WHERE account_id = %s", (account_id,))
    if not cursor.fetchone():
        conn.close()
        return "Account does not exist"

    cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, account_id))
    
    cursor.execute("INSERT INTO transactions (account_id, type, amount) VALUES (%s, %s, %s)",
                   (account_id, "deposit", amount))
    
    conn.commit()
    conn.close()
    return "Deposit Successful"

def withdraw(account_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return "Account does not exist"
        
    balance = row[0]
    
    if balance >= amount:
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, account_id))
        
        cursor.execute("INSERT INTO transactions (account_id, type, amount) VALUES (%s, %s, %s)",
                       (account_id, "withdraw", amount))
        
        conn.commit()
        msg = "Withdraw Successful"
    else:
        msg = "Insufficient Balance"
    
    conn.close()
    return msg

def transfer(from_acc, to_acc, amount):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check sender balance
    cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (from_acc,))
    sender = cursor.fetchone()
    
    # Check receiver exists
    cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (to_acc,))
    receiver = cursor.fetchone()
    
    if not sender:
        conn.close()
        return "Sender account does not exist"
    
    if not receiver:
        conn.close()
        return "Receiver account does not exist"
    
    if sender[0] >= amount:
        # Deduct
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, from_acc))
        
        # Add
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, to_acc))
        
        # Record transactions
        cursor.execute("INSERT INTO transactions (account_id, type, amount) VALUES (%s, %s, %s)",
                       (from_acc, "transfer_out", amount))
        
        cursor.execute("INSERT INTO transactions (account_id, type, amount) VALUES (%s, %s, %s)",
                       (to_acc, "transfer_in", amount))
        
        conn.commit()
        msg = "Transfer Successful"
    else:
        msg = "Insufficient Balance"
    
    conn.close()
    return msg
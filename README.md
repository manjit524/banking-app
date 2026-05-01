# 🏦 NexusBank

A fully functional, professional web-based banking application built with Python and Flask. This system features secure user authentication, transaction authorizations via MPIN, and a modern, glassmorphic UI built with Bootstrap and vanilla CSS.

🌍 **Live Demo:** [Check out the live website here!](https://manjitpal524.pythonanywhere.com/)

---

## ✨ Features

- **Secure Authentication:** Users can securely register and log in. Passwords are hashed using `bcrypt`.
- **MPIN Authorization:** Sensitive actions like viewing balances, transferring funds, and making withdrawals require a 4-6 digit MPIN for an extra layer of security.
- **Account Dashboard:** Users can view their account ID, account type, and access quick actions.
- **Transactions:** 
  - 📥 **Deposit:** Add funds to the account.
  - 📤 **Withdraw:** Remove funds securely.
  - 💸 **Transfer:** Send money instantly to other account IDs.
- **Transaction History:** A detailed, color-coded ledger of all past transactions.
- **Modern UI/UX:** Responsive design featuring Google Fonts (`Outfit`), FontAwesome icons, and sleek CSS animations.

---

## 🛠️ Technology Stack

- **Backend:** Python, Flask
- **Database:** SQLite (Auto-generating local database) / MySQL compatible
- **Security:** Bcrypt password hashing
- **Frontend:** HTML5, CSS3, Bootstrap 5, FontAwesome
- **Deployment:** PythonAnywhere

---

## 🚀 How to Run Locally

If you want to run this project on your own machine:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/manjitpal524/banking-system.git
   cd banking-system
   ```

2. **Install the dependencies:**
   Make sure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```
   *Note: The SQLite database (`bank.db`) and all required tables will be generated automatically the very first time the app is run!*

4. **View in browser:**
   Open `http://127.0.0.1:5000/` in your web browser.

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/manjitpal524/banking-system/issues).

## 📝 License
This project is open source and available under the [MIT License](LICENSE).

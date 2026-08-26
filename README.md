# NexusBank — Modern Digital Banking & Transaction Platform

NexusBank is a full-featured, secure, real-time digital banking application built with Flask, SQLAlchemy, lightweight AJAX polling, and Bootstrap 5.

---

## 🌟 Key Features

* **Modern Responsive UI**: Built with Bootstrap 5.3, FontAwesome 6.4, and a clean custom emerald green theme. Supports desktop sidebar navigation and mobile bottom navigation.
* **Double-Entry Ledger Engine**: Financial integrity backed by immutable ledger entries (`LedgerEntry`). Account balances act as a cached state.
* **Multi-Account Support**: Users can own multiple accounts (Savings, Current, Salary, Demo Wallet).
* **Atomic Money Transfers**: Concurrent row locking (`with_for_update`) with deadlock-prevention ordering.
* **Idempotency Protection**: Unique transaction keys prevent double-charge or duplicate transfer bugs.
* **Real-Time Polling Updates**: Client-side JS polls `/api/notifications/poll` every 3 seconds to update balances, alert popups (toasts), and unread badges dynamically without holding open synchronous server threads.
* **Virtual Debit Cards**: Issue, freeze/unfreeze, and manage online/international payment permissions on virtual VISA cards.
* **Bill Payments & Scheduled Transfers**: Pay utility bills (electricity, water, broadband) and set up automated recurring payments.
* **Analytics & Reporting**: Interactive Chart.js charts showing monthly income vs. expenses, net cash flow, and category spending.
* **Statement & Receipt Downloads**: PDF and CSV export support.
* **Zero-Config Database**: SQLite database file (`instance/nexusbank.db`) automatically initializes and seeds on application startup if it does not exist.

---

## 🛠️ Tech Stack

* **Backend**: Python 3, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Limiter, Flask-Mail, Flask-Bcrypt
* **Frontend**: Jinja2 Templates, Bootstrap 5.3, FontAwesome 6.4, Chart.js, Vanilla JS (Polling client)
* **Database**: SQLite (SQLAlchemy ORM with WAL logging enabled for concurrency)
* **Testing**: pytest, pytest-flask

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install dependencies:

```bash
cd banking-app
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python run.py
```

*Note: On your very first run, the SQLite database `instance/nexusbank.db` will be created and seeded automatically.*

Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 🔑 Demo Credentials

The database automatically populates the following accounts for testing:

| User | Email | Password | MPIN |
| --- | --- | --- | --- |
| **User 1 (Demo)** | `demo@nexusbank.com` | `Demo@1234` | `112233` |
| **User 2 (Priya)** | `priya@nexusbank.com` | `Demo@1234` | `445566` |
| **User 3 (Rahul)** | `rahul@nexusbank.com` | `Demo@1234` | `778899` |

---

## 🧪 Running Tests

Execute the automated test suite:

```bash
python -m pytest tests/
```

---

## 📁 Project Structure

```
banking-app/
├── app.py                 # Application Factory & Auto-DB creation
├── config.py              # Configuration settings (Dev, Prod, Testing)
├── extensions.py          # Flask extensions (DB, Login, Bcrypt, Limiter, etc.)
├── run.py                 # Application entry point
├── seed.py                # Database seeder code
├── models/                # SQLAlchemy Models
│   ├── user.py            # User schema
│   ├── account.py         # Bank Account model
│   ├── transaction.py     # Transaction lifecycle
│   ├── ledger.py          # Double-entry ledger
│   ├── beneficiary.py     # Beneficiary management
│   ├── card.py            # Virtual debit cards
│   ├── bill.py            # Billers & Bills
│   ├── scheduled_payment.py # Recurring transfers
│   └── notification.py    # User notifications
├── services/              # Business Logic & Banking Services
│   ├── auth_service.py
│   ├── account_service.py
│   ├── transaction_service.py
│   ├── transfer_service.py
│   ├── beneficiary_service.py
│   ├── card_service.py
│   ├── payment_service.py
│   ├── analytics_service.py
│   ├── profile_service.py
│   └── notification_service.py
├── routes/                # Blueprint Controllers
│   ├── auth.py
│   ├── dashboard.py
│   ├── accounts.py
│   ├── transactions.py
│   ├── transfers.py
│   ├── beneficiaries.py
│   ├── payments.py
│   ├── cards.py
│   ├── analytics.py
│   ├── profile.py
│   └── api/
│       └── notifications_api.py (Stateless JSON APIs)
├── templates/             # Jinja2 HTML Templates
├── static/                # CSS, JS & Assets
└── tests/                 # Unit & Integration Tests
```

FRESHEGGS DELIVERY — PYTHON + FLASK
===================================

WHAT IS INCLUDED
- Customer-facing egg catalogue and ordering form.
- SQLite database created automatically on first run.
- Stock validation and automatic stock reduction when an order is saved.
- Order confirmation page with an order number.
- Customer order tracking using order number and phone number.
- Admin dashboard to update prices, stock quantities and order statuses.
- Basic sales summary and responsive design.

REQUIREMENTS
- Python 3.10 or newer (Python 3.11+ recommended).
- VS Code and a web browser.
- Internet connection only to install Flask the first time.
- XAMPP and JDK are NOT required for this Python version.

RUN ON WINDOWS
1. Extract the ZIP file to a folder such as C:\Users\YourName\Documents\fresheggs_python
2. Open that folder in VS Code.
3. Open Terminal > New Terminal.
4. Create a virtual environment:
       py -m venv .venv
5. Activate it in PowerShell:
       .\.venv\Scripts\Activate.ps1
   If using Command Prompt instead:
       .venv\Scripts\activate.bat
6. Install Flask:
       python -m pip install -r requirements.txt
7. Start the application:
       python app.py
8. Open the local website:
       http://127.0.0.1:5000

ADMIN
- Open http://127.0.0.1:5000/admin/login
- Username: success
- Password: lungwe04!

The database is created automatically at instance/fresheggs.sqlite3.
No sample data is included. The database starts with no products: log in as the
admin and use "Add a product" in the dashboard (prices are in Malawi Kwacha).
Use Hide/Show to remove a product from the shop without deleting its order history.

IMPORTANT SECURITY NOTES
This is a school-project prototype, not a production-ready e-commerce system.
The default admin password is intended only for local development. Set the
ADMIN_PASSWORD environment variable before the first run to choose a different
password. If the database already exists, changing that variable will not update
the existing admin password automatically.
Set a strong SECRET_KEY environment variable before deployment.
The app's debug mode is enabled by app.py only for local development. Do not
expose the debug server to the public internet.
No online payment gateway, automatic driver dispatch or SMS/WhatsApp notification
is configured. The seller must confirm orders and delivery charges with customers.

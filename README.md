<h1>Vehicle-Parking-App-V2</h1>

IITM BS Diploma Level MAD II Project

Vehicle Parking App V2 A comprehensive Flask-based web application for managing and booking parking spots. The system supports user accounts, admin management of parking lots and real-time reservation tracking.

<h2>Features</h2>

User Dashboard User Authentication: Secure user registration and login.

Profile Management: Users can view and edit their personal information, including full name, phone number, and vehicle details.

Password Management: Users can securely change their passwords.

Parking Spot Booking: Book an available parking spot.

Reservations: View active and past reservations, with real-time tracking of duration and cost for active bookings.

Admin Panel Parking Lot Management: Admins can create, update, and delete parking lots, defining their layout (rows x columns), price per hour, and features like security and lighting.

Live Occupancy View: The admin dashboard provides a grid view of each parking lot's layout, showing which spots are occupied and by whom.

Analytics: View key statistics such as total revenue, total bookings, and user counts.

User Management: View a list of all registered users and their details.

<h2>Technology Stack Backend:</h2> 

Flask

Database: SQLite (Flask-SQLAlchemy)

User Management: Flask-Login

Styling: Bootstrap 5.3, Font Awesome 6.4

Getting Started Follow these steps to set up and run the application.

Prerequisites Python 3.x installed

Git installed

Installation Clone the repository:

git clone https://github.com/21f3001485/Vehicle-Parking-App-V2 cd Vehicle-Parking-App-V2 Create and activate a virtual environment:

<h1>On Windows</h1>

python -m venv venv venv\Scripts\activate

<h1>On macOS/Linux</h1>

python3 -m venv venv source venv/bin/activate Install the required Python libraries:

pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug Database Setup The application uses an SQLite database. The database_creator.py script will set up the database and create a default admin user for you.

Run the script from your project directory:

python database_creator.py This will create a parking.db file in the instance/ folder and output the default admin login credentials:

Username: admin

Password: admin123

Running the Application Ensure your virtual environment is active.

Run the main application file:

python app.py Open your web browser and navigate to http://127.0.0.1:5000 to access the application.

Usage Admin Access: Log in with the default admin credentials to access the admin dashboard and manage lots.

User Access: From the login page, you can create a new user account to access the user dashboard and book parking spots.

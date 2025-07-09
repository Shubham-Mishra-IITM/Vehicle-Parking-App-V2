# Vehicle Parking App

## Overview
The Vehicle Parking App is a multi-user web application designed to manage parking lots, parking spots, and parked vehicles. It provides functionalities for both administrators and users, allowing for efficient management of parking resources.

## Technologies Used
- **Backend**: Flask (Python)
- **Frontend**: Vue.js
- **Database**: SQLite
- **Caching**: Redis
- **Task Queue**: Celery
- **Styling**: Bootstrap

## Features
### Admin Features
- Admin login (single superuser)
- Create, edit, and delete parking lots
- View status of all parking spots
- Manage registered users
- View summary charts of parking lots and spots

### User Features
- User registration and login
- Reserve parking spots
- Release parking spots
- View personal parking history and summary charts

## Project Structure
```
vehicle-parking-app
├── backend
│   ├── app.py
│   ├── config.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── parking_lot.py
│   │   ├── parking_spot.py
│   │   └── reservation.py
│   ├── routes
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── user.py
│   │   └── parking.py
│   ├── utils
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── cache.py
│   │   └── helpers.py
│   ├── tasks
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   ├── daily_reminders.py
│   │   ├── monthly_reports.py
│   │   └── export_csv.py
│   ├── templates
│   │   └── index.html
│   ├── static
│   │   ├── css
│   │   └── js
│   └── requirements.txt
├── frontend
│   ├── public
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── components
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   ├── AdminDashboard.vue
│   │   │   ├── UserDashboard.vue
│   │   │   ├── ParkingLotCard.vue
│   │   │   └── Charts.vue
│   │   ├── views
│   │   │   ├── Home.vue
│   │   │   ├── Admin.vue
│   │   │   └── User.vue
│   │   ├── router
│   │   │   └── index.js
│   │   ├── store
│   │   │   └── index.js
│   │   └── services
│   │       └── api.js
│   ├── package.json
│   └── vue.config.js
├── docker-compose.yml
├── .env
├── .gitignore
└── README.md
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd vehicle-parking-app
   ```

2. Set up the backend:
   - Navigate to the `backend` directory.
   - Install required Python packages:
     ```
     pip install -r requirements.txt
     ```

3. Set up the frontend:
   - Navigate to the `frontend` directory.
   - Install required Node packages:
     ```
     npm install
     ```

4. Configure environment variables in the `.env` file.

5. Run the application using Docker:
   ```
   docker-compose up
   ```

## Usage
- Access the application at `http://localhost:5000` for the backend and `http://localhost:8080` for the frontend.
- Use the admin credentials to log in as an admin and manage parking lots.
- Users can register and log in to reserve parking spots.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License.
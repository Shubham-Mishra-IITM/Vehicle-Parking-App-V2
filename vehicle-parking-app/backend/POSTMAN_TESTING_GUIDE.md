# 🧪 Vehicle Parking App V2 - Postman Testing Guide

## 📋 Setup Instructions

### 1. Import Collection & Environment
1. Open Postman
2. Click **Import** → **Upload Files**
3. Import both files:
   - `Postman_Collection_Vehicle_Parking_App_V2.json`
   - `Postman_Environment_Vehicle_Parking_App_V2.json`
4. Select the **Vehicle Parking App V2 - Local** environment

### 2. Start the Flask App
```bash
cd backend
python3 app.py
```

## 🧪 Testing Workflow

### Step 1: Health Check
- **GET** `/` - Basic health check
- **GET** `/health` - Detailed health check
- ✅ Should return status 200 with app info

### Step 2: Authentication Testing

#### A. Admin Login
1. **POST** `/api/auth/admin-login`
   ```json
   {
       "username": "admin",
       "password": "admin123"
   }
   ```
   - ✅ Token automatically saved to `{{admin_token}}`

#### B. User Registration
1. **POST** `/api/auth/register`
   ```json
   {
       "username": "test_user",
       "email": "test@example.com", 
       "password": "password123",
       "phone_number": "9876543210"
   }
   ```

#### C. User Login
1. **POST** `/api/auth/login`
   ```json
   {
       "username": "john_doe",
       "password": "password123"
   }
   ```
   - ✅ Token automatically saved to `{{auth_token}}`

### Step 3: Admin Operations (Requires Admin Token)

#### A. Dashboard
- **GET** `/api/admin/dashboard`
- ✅ Should show stats: users, lots, spots, reservations

#### B. Create Parking Lot
- **POST** `/api/admin/parking-lots`
- ✅ Creates lot + automatically generates parking spots

#### C. View Data
- **GET** `/api/admin/parking-lots` - All parking lots
- **GET** `/api/admin/users` - All registered users

### Step 4: User Operations (Requires User Token)
- **GET** `/api/user/profile` - User profile
- **GET** `/api/user/reservations` - User's reservations

### Step 5: Public Parking Info
- **GET** `/api/parking/lots` - Available parking lots
- **GET** `/api/parking/spots/{lot_id}` - Spots in a specific lot

## 🔑 Default Credentials

### Admin User
- **Username:** `admin`
- **Password:** `admin123`
- **Email:** `admin@parkingapp.com`

### Sample User
- **Username:** `john_doe`
- **Password:** `password123`
- **Email:** `john@example.com`

## 📊 Sample Data Created

### 3 Parking Lots:
1. **City Center Mall** - 50 spots, $25/hour
2. **Airport Terminal** - 100 spots, $40/hour  
3. **Business District** - 75 spots, $30/hour

### Parking Spots:
- Auto-generated with format: A1, A2, B1, B2, etc.
- All initially set to "Available" status

## 🚀 Quick Test Sequence

1. **Health Check** → Verify app is running
2. **Admin Login** → Get admin access
3. **Admin Dashboard** → View system stats
4. **Create Parking Lot** → Test admin functionality
5. **User Registration** → Create new user
6. **User Login** → Get user access
7. **View Parking Lots** → Test public endpoints

## 🔧 Troubleshooting

### Token Issues
- Make sure to run **Admin Login** or **User Login** first
- Tokens are auto-saved to collection variables
- Check the **Authorization** header: `Bearer {{auth_token}}`

### Database Issues
- Run: `python3 simple_init_db.py --reset`
- This recreates all tables and sample data

### Server Issues
- Ensure Flask app is running on `http://127.0.0.1:5000`
- Check for Redis connection (optional for basic testing)

## 📝 Expected Response Codes

- **200** - Success (GET requests)
- **201** - Created (POST requests)
- **400** - Bad Request (validation errors)
- **401** - Unauthorized (missing/invalid token)
- **403** - Forbidden (insufficient permissions)
- **404** - Not Found
- **500** - Server Error

## 🎯 Key Features to Test

### ✅ Authentication
- [x] User registration with validation
- [x] User/Admin login with JWT tokens
- [x] Token verification
- [x] Role-based access control

### ✅ Admin Functions
- [x] Dashboard statistics
- [x] Parking lot CRUD operations
- [x] User management
- [x] Automatic parking spot generation

### ✅ User Functions
- [x] Profile access
- [x] Reservation management (placeholders ready)

### ✅ Data Models
- [x] User model with roles
- [x] Parking lot with pricing
- [x] Parking spots with status
- [x] Reservation system structure

Happy Testing! 🎉

#!/usr/bin/env python3
"""
Data Consistency Verification Tool
Compares user dashboard data with monthly reports data to ensure consistency
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5004"

def login_user(username, password):
    """Login as a regular user and get JWT token"""
    print(f"🔐 Logging in as user: {username}")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        token = result.get('access_token') or result.get('token')
        if token:
            print("✅ Login successful!")
            return token
        else:
            print(f"❌ No token in response: {result}")
            return None
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def get_user_dashboard_data(token):
    """Get user dashboard data"""
    print("📊 Fetching user dashboard data...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/user/dashboard",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        stats = data.get('statistics', {})
        print("✅ Dashboard data fetched successfully!")
        return {
            'total_reservations': stats.get('total_reservations', 0),
            'completed_reservations': stats.get('completed_reservations', 0),
            'total_spent': stats.get('total_spent', 0),
            'most_used_lot': data.get('most_used_lot', {}),
            'raw_data': data
        }
    else:
        print(f"❌ Failed to get dashboard data: {response.text}")
        return None

def get_user_monthly_report_data(token, month=None, year=None):
    """Get user monthly report data"""
    current_month = month or datetime.now().month
    current_year = year or datetime.now().year
    
    print(f"📋 Fetching monthly report data for {current_month}/{current_year}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/user/monthly-report?month={current_month}&year={current_year}&format=json",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        report_data = data.get('report_data', {})
        print("✅ Monthly report data fetched successfully!")
        return {
            'total_reservations': report_data.get('total_reservations', 0),
            'completed_reservations': report_data.get('completed_reservations', 0),
            'total_spent': report_data.get('total_amount_spent', 0),
            'most_used_lot': report_data.get('most_used_lot', ('None', 0)),
            'raw_data': data
        }
    else:
        print(f"❌ Failed to get monthly report data: {response.text}")
        return None

def get_user_reservations(token):
    """Get user's all reservations for analysis"""
    print("📋 Fetching user reservations...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/user/reservations",
        headers=headers
    )
    
    if response.status_code == 200:
        reservations = response.json()
        print(f"✅ Found {len(reservations)} reservations")
        return reservations
    else:
        print(f"❌ Failed to get reservations: {response.text}")
        return []

def analyze_data_consistency(dashboard_data, monthly_data, reservations, month, year):
    """Analyze and compare data consistency"""
    print(f"\n📈 DATA CONSISTENCY ANALYSIS for {month}/{year}")
    print("=" * 60)
    
    # Filter reservations for the month
    monthly_reservations = []
    for res in reservations:
        try:
            created_at = datetime.fromisoformat(res['created_at'].replace('Z', '+00:00'))
            if created_at.month == month and created_at.year == year:
                monthly_reservations.append(res)
        except:
            continue
    
    print(f"📊 SUMMARY:")
    print(f"   Total reservations in database: {len(reservations)}")
    print(f"   Reservations for {month}/{year}: {len(monthly_reservations)}")
    
    print(f"\n🎯 DASHBOARD vs MONTHLY REPORT COMPARISON:")
    print(f"   {'Metric':<25} {'Dashboard':<12} {'Monthly Report':<15} {'Match':<8}")
    print(f"   {'-'*25} {'-'*12} {'-'*15} {'-'*8}")
    
    # Compare total reservations
    dash_total = dashboard_data['total_reservations']
    monthly_total = monthly_data['total_reservations']
    match_total = "✅" if dash_total == len(monthly_reservations) else "❌"
    print(f"   {'Total Reservations':<25} {dash_total:<12} {monthly_total:<15} {match_total:<8}")
    
    # Compare completed reservations
    dash_completed = dashboard_data['completed_reservations']
    monthly_completed = monthly_data['completed_reservations']
    actual_completed = len([r for r in monthly_reservations if r.get('status') == 'completed'])
    match_completed = "✅" if monthly_completed == actual_completed else "❌"
    print(f"   {'Completed':<25} {dash_completed:<12} {monthly_completed:<15} {match_completed:<8}")
    
    # Compare total spent
    dash_spent = float(dashboard_data['total_spent'])
    monthly_spent = float(monthly_data['total_spent'])
    actual_spent = sum([float(r.get('parking_cost', 0)) for r in monthly_reservations if r.get('status') == 'completed'])
    match_spent = "✅" if abs(monthly_spent - actual_spent) < 0.01 else "❌"
    print(f"   {'Total Spent':<25} {dash_spent:<12.2f} {monthly_spent:<15.2f} {match_spent:<8}")
    
    print(f"\n🔍 DETAILED BREAKDOWN:")
    print(f"   Monthly reservations by status:")
    status_count = {}
    for res in monthly_reservations:
        status = res.get('status', 'unknown')
        status_count[status] = status_count.get(status, 0) + 1
    
    for status, count in status_count.items():
        print(f"     {status}: {count}")
    
    print(f"\n   Monthly reservations with costs:")
    total_with_cost = 0
    cost_sum = 0
    for res in monthly_reservations:
        if res.get('parking_cost') and res.get('status') == 'completed':
            total_with_cost += 1
            cost_sum += float(res['parking_cost'])
            print(f"     ID: {res.get('id')}, Cost: Rs.{float(res['parking_cost']):.2f}, Status: {res.get('status')}")
    
    print(f"\n   Calculated totals from reservations:")
    print(f"     Reservations with cost: {total_with_cost}")
    print(f"     Sum of costs: Rs.{cost_sum:.2f}")
    print(f"     Monthly report shows: Rs.{monthly_spent:.2f}")
    
    # Check for discrepancies
    issues = []
    if dash_total != len(reservations):
        issues.append(f"Dashboard total ({dash_total}) doesn't match actual total ({len(reservations)})")
    
    if monthly_total != len(monthly_reservations):
        issues.append(f"Monthly report total ({monthly_total}) doesn't match filtered monthly total ({len(monthly_reservations)})")
    
    if abs(monthly_spent - actual_spent) > 0.01:
        issues.append(f"Monthly report spending ({monthly_spent:.2f}) doesn't match calculated spending ({actual_spent:.2f})")
    
    if issues:
        print(f"\n❌ ISSUES FOUND:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print(f"\n✅ ALL DATA CONSISTENT!")
    
    return len(issues) == 0

def test_user_data_consistency(username, password, month=None, year=None):
    """Test data consistency for a specific user"""
    current_month = month or datetime.now().month
    current_year = year or datetime.now().year
    
    print(f"🧪 Testing data consistency for user: {username}")
    print(f"📅 Target month/year: {current_month}/{current_year}")
    print("=" * 60)
    
    # Login
    token = login_user(username, password)
    if not token:
        return False
    
    # Get dashboard data
    dashboard_data = get_user_dashboard_data(token)
    if not dashboard_data:
        return False
    
    # Get monthly report data
    monthly_data = get_user_monthly_report_data(token, current_month, current_year)
    if not monthly_data:
        return False
    
    # Get all reservations
    reservations = get_user_reservations(token)
    
    # Analyze consistency
    is_consistent = analyze_data_consistency(dashboard_data, monthly_data, reservations, current_month, current_year)
    
    return is_consistent

def main():
    """Test data consistency for multiple users"""
    print("🔍 USER DATA CONSISTENCY VERIFICATION TOOL")
    print("=" * 60)
    
    # Test users - you can modify these based on your test data
    test_users = [
        ("john_doe", "password123"),
        ("jane_smith", "password123"),
        ("testuser", "password123"),
        ("abc", "123"),  # User with known data for verification
        # Add more test users as needed
    ]
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    successful_tests = 0
    total_tests = len(test_users)
    
    for username, password in test_users:
        try:
            print(f"\n" + "="*80)
            is_consistent = test_user_data_consistency(username, password, current_month, current_year)
            if is_consistent:
                successful_tests += 1
            print("="*80)
        except Exception as e:
            print(f"❌ Error testing user {username}: {e}")
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"   Successful tests: {successful_tests}/{total_tests}")
    print(f"   Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("✅ ALL USERS HAVE CONSISTENT DATA!")
    else:
        print("❌ SOME USERS HAVE DATA INCONSISTENCIES - CHECK LOGS ABOVE")

if __name__ == "__main__":
    main()

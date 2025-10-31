# employee_module_postgres.py

import psycopg2
from db_config import create_connection
import sys
import re
from tabulate import tabulate

# ---------------- Employee Registration ----------------
def register_employees():
    """
    Registers a new employee with default approval=FALSE
    """
    conn = create_connection()
    cursor = conn.cursor()
    try:
        name = input("Enter employee name: ").strip()
        emailid = input("Enter employee email: ").strip()
        password = input("Enter password: ").strip()
        skill = input("Enter skill: ").strip()
        department = input("Enter department: ").strip()
        qualification = input("Enter qualification: ").strip()
        phonenumber = input("Enter phonenumber: ").strip()
        yoe = input("Enter year of experience: ").strip()
        approved = False  # PostgreSQL boolean

        cursor.execute("""
            INSERT INTO employees (name, emailid, password, skill, department, qualification, phonenumber, yoe, approved)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
        """, (name,emailid,password,skill,department,qualification,phonenumber,yoe,approved))
        new_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ Employee registered successfully! Assigned ID: {new_id}")
    except Exception as e:
        print(f"❌ Error registering employee: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


# ---------------- Employee Login ----------------
def employee_login():
    """
    Login employee and pass emp_id to employee_menu
    """
    conn = create_connection()
    cursor = conn.cursor()
    try:
        email = input("Enter your email: ").strip()
        password = input("Enter your password: ").strip()
        cursor.execute("""
            SELECT id, name FROM employees
            WHERE emailid=%s AND password=%s AND approved=TRUE
        """, (email, password))
        result = cursor.fetchone()
        if result:
            emp_id, name = result
            print(f"✅ Login successful! Welcome, {name}")
            employee_menu(emp_id)
        else:
            print("❌ Invalid credentials or account not approved.")
    except Exception as e:
        print(f"❌ Error during login: {e}")
    finally:
        cursor.close()
        conn.close()


# ---------------- Employee Menu ----------------
def employee_menu(emp_id):
    while True:
        print("\n--- Employee Menu ---")
        print("1. Add/Update Services")
        print("2. View My Service Booking")
        print("3. Update Availability")
        print("4. View Projects")
        print("5. Book a Project")
        print("6. Update Service Booking Requests")
        print("7. Update Work Status")
        print("8. View My Review")
        print("9. View My Project Booking")
        print("10. Logout")
        choice = input("Enter your choice: ").strip()
        if choice == '1':
            add_or_update_services(emp_id)
        elif choice == '2':
            view_my_service_booking(emp_id)
        elif choice == '3':
            update_availability(emp_id)
        elif choice == '4':
            view_project()
        elif choice == '5':
            book_project(emp_id)
        elif choice == '6':
            update_service_booking_requests(emp_id)
        elif choice == '7':
            update_work_status(emp_id)
        elif choice == '8':
            view_my_review(emp_id)
        elif choice == '9':
            view_my_project_booking(emp_id)
        elif choice == '10':
            print("👋 Logged out successfully.")
            sys.exit()
        else:
            print("⚠️ Invalid choice.")


# ---------------- Add/Update Services ----------------
def add_or_update_services(emp_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, skill, department, qualification, yoe FROM employees WHERE id=%s", (emp_id,))
        result = cursor.fetchone()
        if not result:
            print("❌ Employee not found.")
            return
        emp_id, skill, department, qualification, yoe = result
        rate_hour = float(input("Enter hourly rate: "))
        rate_day = float(input("Enter daily rate: "))
        rate_month = float(input("Enter monthly rate: "))
        availability = input("Enter availability (TRUE/FALSE): ").strip().lower() in ['true','1','yes']

        cursor.execute("SELECT id FROM service WHERE emp_id=%s", (emp_id,))
        existing_service = cursor.fetchone()
        if existing_service:
            cursor.execute("""
                UPDATE service
                SET rate_hourly=%s, rate_daily=%s, rate_monthly=%s, availability=%s
                WHERE emp_id=%s
            """, (rate_hour, rate_day, rate_month, availability, emp_id))
            print("✅ Service updated successfully.")
        else:
            cursor.execute("""
                INSERT INTO service (emp_id, skill, rate_hourly, rate_daily, rate_monthly, availability, department, qualification, yoe)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (emp_id, skill, rate_hour, rate_day, rate_month, availability, department, qualification, yoe))
            print("✅ Service added successfully.")
        conn.commit()
    except Exception as e:
        print(f"❌ Error in adding/updating service: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


# ---------------- View My Service Booking ----------------
def view_my_service_booking(emp_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT s.id, u.name, s.service_id, s.duration, s.project_name, s.cost, s.status
            FROM servicebooking s
            JOIN users u ON s.user_id = u.id
            WHERE s.emp_id = %s
        """, (emp_id,))
        bookings = cursor.fetchall()
        if not bookings:
            print("❌ No service bookings.")
            return
        headers = ["Booking ID", "User", "Service ID", "Duration", "Project Name", "Cost", "Status"]
        print(tabulate(bookings, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"❌ Error viewing bookings: {e}")
    finally:
        cursor.close()
        conn.close()


# ---------------- Update Availability ----------------
def update_availability(emp_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        availability = input("Enter availability (TRUE/FALSE): ").strip().lower() in ['true','1','yes']
        cursor.execute("UPDATE service SET availability=%s WHERE emp_id=%s", (availability, emp_id))
        conn.commit()
        print("✅ Availability updated.")
    except Exception as e:
        print(f"❌ Error updating availability: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


# ---------------- View Projects ----------------
def view_project():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT p.id, u.name, p.project_name, p.duration
            FROM project p
            JOIN users u ON p.user_id = u.id
        """)
        projects = cursor.fetchall()
        if not projects:
            print("❌ No projects found.")
            return
        headers = ["Project ID", "Username", "Project Name", "Duration"]
        print(tabulate(projects, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"❌ Error fetching projects: {e}")
    finally:
        cursor.close()
        conn.close()


# ---------------- Parse Duration Helper ----------------
def parse_duration(user_input: str) -> int:
    user_input = user_input.lower().strip()
    match = re.match(r"(\d+)\s*(day|days|week|weeks|month|months)", user_input)
    if not match:
        raise ValueError("Invalid duration format. Example: '30 days', '2 weeks', '1 month'.")
    number = int(match.group(1))
    unit = match.group(2)
    if "day" in unit:
        return number
    elif "week" in unit:
        return number * 7
    elif "month" in unit:
        return number * 30
    return number


# ---------------- Book a Project ----------------
def book_project(emp_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, rate_daily FROM service WHERE emp_id=%s", (emp_id,))
        service = cursor.fetchone()
        if not service:
            print("❌ Employee has no registered service.")
            return
        service_id, rate_daily = service

        cursor.execute("SELECT id, user_id, project_name FROM project")
        projects = cursor.fetchall()
        if not projects:
            print("❌ No projects available.")
            return
        headers = ["Project ID", "User ID", "Project Name"]
        print(tabulate(projects, headers=headers, tablefmt="grid"))

        project_id = int(input("Enter Project ID to book: "))
        cursor.execute("SELECT user_id FROM project WHERE id=%s", (project_id,))
        row = cursor.fetchone()
        if not row:
            print("❌ Invalid project ID.")
            return
        user_id = row[0]

        project_name = input("Enter project name: ")
        while True:
            try:
                duration_days = parse_duration(input("Enter duration (e.g., '30 days'): "))
                break
            except ValueError as e:
                print("❌", e)

        cost = rate_daily * duration_days
        status = "pending"

        cursor.execute("""
            INSERT INTO projectbooking (user_id, emp_id, project_id, service_id, project_name, cost, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id
        """, (user_id, emp_id, project_id, service_id, project_name, cost, status))
        new_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ Project booked! ID: {new_id}, Cost: ₹{cost}, Status: {status}")
    except Exception as e:
        print(f"❌ Error booking project: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


# ---------------- Update Service Booking Requests ----------------
def update_service_booking_requests(emp_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT b.id, u.name, b.duration, b.project_name, b.cost, b.status
            FROM servicebooking b
            JOIN users u ON b.user_id = u.id
            WHERE b.emp_id=%s AND b.status='pending'
        """, (emp_id,))
        requests = cursor.fetchall()
        if not requests:
            print("📭 No pending requests.")
            return
        headers = ["Booking ID","User","Duration","Project Name","Cost","Status"]
        print(tabulate(requests, headers=headers, tablefmt="grid"))

        booking_id = int(input("Enter Booking ID to respond: "))
        action = input("Enter 'a' to accept or 'd' to decline: ").lower()
        if action == 'a':
            starting_date = input("Enter starting date (YYYY-MM-DD): ").strip()
            cursor.execute("UPDATE servicebooking SET status='accepted' WHERE id=%s AND emp_id=%s", (booking_id, emp_id))
            cursor.execute("""
                INSERT INTO accepted_bookings (booking_id, booking_type, emp_id, user_id, service_id, project_name, duration, cost, status, starting_date)
                SELECT sb.id,'service',sb.emp_id,sb.user_id,sb.service_id,sb.project_name,sb.duration,sb.cost,'accepted',%s
                FROM servicebooking sb WHERE sb.id=%s AND sb.emp_id=%s
            """, (starting_date, booking_id, emp_id))
            conn.commit()
            print("✅ Booking accepted.")
        elif action == 'd':
            cursor.execute("UPDATE servicebooking SET status='declined' WHERE id=%s AND emp_id=%s", (booking_id, emp_id))
            conn.commit()
            print("❌ Booking declined.")
        else:
            print("⚠️ Invalid choice.")
    except Exception as e:
        print(f"❌ Error updating booking requests: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


# ---------------- Update Work Status ----------------
def update_work_status(emp_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, booking_id, booking_type, user_id, status FROM accepted_bookings WHERE emp_id=%s
        """, (emp_id,))
        bookings = cursor.fetchall()
        if not bookings:
            print("❌ No bookings found.")
            return
        headers = ["ID","Booking ID","Type","User ID","Current Status"]
        print(tabulate(bookings, headers=headers, tablefmt="grid"))
        booking_id = int(input("Enter booking ID to update: "))
        status = input("Enter new work status: ").strip()
        cursor.execute("UPDATE accepted_bookings SET status=%s WHERE id=%s AND emp_id=%s", (status, booking_id, emp_id))
        conn.commit()
        print("✅ Work status updated.")
    except Exception as e:
        print(f"❌ Error updating work status: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


# ---------------- View My Review ----------------
def view_my_review(emp_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT r.id, r.user_id, u.name, r.review FROM review r JOIN users u ON r.user_id=u.id WHERE emp_id=%s
        """, (emp_id,))
        reviews = cursor.fetchall()
        if not reviews:
            print("📭 No reviews found.")
            return
        headers = ["ID","User ID","User Name","Review"]
        print(tabulate(reviews, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"❌ Error fetching reviews: {e}")
    finally:
        cursor.close()
        conn.close()


# ---------------- View My Project Booking ----------------
def view_my_project_booking(emp_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT b.id, u.name, b.project_id, b.project_name, b.cost, b.status
            FROM projectbooking b
            JOIN users u ON b.user_id=u.id
            WHERE b.emp_id=%s
        """, (emp_id,))
        bookings = cursor.fetchall()
        if not bookings:
            print("📭 No project bookings found.")
            return
        headers = ["Booking ID","User","Project ID","Project Name","Cost","Status"]
        print(tabulate(bookings, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"❌ Error fetching project bookings: {e}")
    finally:
        cursor.close()
        conn.close()


# ---------------- Run CLI ----------------
def main():
    while True:
        print("\n--- Employee Module ---")
        print("1. Register Employee")
        print("2. Employee Login")
        print("3. Exit")
        choice = input("Enter choice: ").strip()
        if choice=='1':
            register_employees()
        elif choice=='2':
            employee_login()
        elif choice=='3':
            print("👋 Exiting...")
            sys.exit()
        else:
            print("⚠️ Invalid choice.")
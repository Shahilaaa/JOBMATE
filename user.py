# user_module_pg.py
import psycopg2
from db_config import create_connection  # PostgreSQL connection function
import sys
import re
from tabulate import tabulate

# -----------------------------
# USER REGISTRATION
# -----------------------------
def register_users():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        name = input("Enter user name: ").strip()
        emailid = input("Enter user email: ").strip()
        password = input("Enter password: ").strip()
        phonenumber = input("Enter phone number: ").strip()
        approved = False  # default not approved
        previous_work = input("Enter previous work (any work links): ").strip()
        location = input("Enter location: ").strip()
        aadharnumber = input("Enter aadhar number: ").strip()
        address = input("Enter address: ").strip()
        bio = input("Enter bio: ").strip()
        category = input("Enter category (company/freelancer): ").strip().lower()

        companyname = None
        gstnumber = None
        licensenumber = None
        professionaltitle = None

        if category == "company":
            companyname = input("Enter company name: ").strip()
            gstnumber = input("Enter GST number: ").strip()
            licensenumber = input("Enter license number: ").strip()
        elif category == "freelancer":
            professionaltitle = input("Enter professional title: ").strip()
        else:
            print("❌ Category not valid.")
            return

        cursor.execute("""
            INSERT INTO users (
                name, emailid, password, phonenumber, approved,
                previous_work, location, aadharnumber, address, bio, category,
                companyname, gstnumber, licensenumber, professionaltitle
            ) VALUES (%s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s, %s,
                      %s, %s, %s, %s)
            RETURNING id
        """, (name, emailid, password, phonenumber, approved,
              previous_work, location, aadharnumber, address, bio, category,
              companyname, gstnumber, licensenumber, professionaltitle))

        new_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ User registered successfully! Assigned ID: {new_id}")
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# -----------------------------
# USER LOGIN
# -----------------------------
def users_login():
    conn = create_connection()
    cursor = conn.cursor()
    email = input("Enter your email: ").strip()
    password = input("Enter your password: ").strip()
    try:
        cursor.execute("""
            SELECT id, name FROM users
            WHERE emailid = %s AND password = %s AND approved = TRUE
        """, (email, password))
        result = cursor.fetchone()

        if result:
            user_id, name = result
            print(f"✅ Login successful! Welcome, {name}")
            user_menu(user_id)
        else:
            print("❌ Invalid credentials or account not approved.")
    except Exception as e:
        print(f"❌ Error during login: {e}")
    finally:
        cursor.close()
        conn.close()

# -----------------------------
# USER MENU
# -----------------------------
def user_menu(user_id):
    while True:
        print("\n--- User Menu ---")
        print("1. Browse Available Employees")
        print("2. Add a Project")
        print("3. Book a Service")
        print("4. View My Service Booking")
        print("5. Add Review")
        print("6. Update Project Booking Request")
        print("7. View My Project Booking")
        print("8. View Work Tracking")
        print("9. Logout")
        choice = input("Enter your choice: ")

        if choice == '1':
            browse_employees()
        elif choice == '2':
            add_project(user_id)
        elif choice == '3':
            book_service(user_id)
        elif choice == '4':
            view_my_service_booking(user_id)
        elif choice == '5':
            add_review(user_id)
        elif choice == '6':
            update_project_booking_request(user_id)
        elif choice == '7':
            view_my_project_booking(user_id)
        elif choice == '8':
            view_work_tracking(user_id)
        elif choice == '9':
            print("👋 You have logged out successfully.")
            sys.exit()
        else:
            print("⚠️ Invalid choice.")

# -----------------------------
# BROWSE EMPLOYEES
# -----------------------------
def browse_employees():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT s.id, e.name, s.skill, s.rate_hourly, s.rate_daily,
                   s.rate_monthly, s.department, s.qualification, s.yoe, s.availability
            FROM service s
            JOIN employees e ON s.emp_id = e.id
            WHERE s.availability = TRUE
        """)
        employees = cursor.fetchall()
        if not employees:
            print("❌ No available employees.")
            return

        headers = ["Service ID","Name","Skill","Rate Hourly","Rate Daily","Rate Monthly",
                   "Department","Qualification","Experience (Years)","Availability"]

        rows = []
        for s_id, name, skill, r_h, r_d, r_m, dept, qual, yoe, avail in employees:
            rows.append([
                s_id, name, skill,
                f"₹{float(r_h):,.2f}/hr" if r_h else "",
                f"₹{float(r_d):,.2f}/day" if r_d else "",
                f"₹{float(r_m):,.2f}/month" if r_m else "",
                dept, qual, yoe or "", "Yes" if avail else "No"
            ])
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()

# -----------------------------
# ADD PROJECT
# -----------------------------
def parse_duration(user_input: str):
    """
    Convert natural language durations like '30 days', '2 weeks', '1 month'
    into (duration_unit, quantity) for structured storage.
    """
    user_input = user_input.lower().strip()
    match = re.match(r"(\d+)\s*(hour|hours|day|days|month|months)", user_input)
    if not match:
        raise ValueError("Invalid duration format. Example: '1 hour', '3 days', '1 month'.")
    
    quantity = int(match.group(1))
    unit = match.group(2)
    
    if "hour" in unit:
        return "hour", quantity
    elif "day" in unit:
        return "day", quantity
    elif "month" in unit:
        return "month", quantity
    else:
        raise ValueError("Unsupported duration unit.")
    
def add_project(user_id):
    conn = create_connection()
    cursor = conn.cursor()

    project_name = input("Enter project name: ").strip()
    starting_date = input("Enter starting date (YYYY-MM-DD): ").strip()
    job_roles = input("Enter job roles you want: ").strip()
    duration_input = input("Enter duration (e.g., '30 days', '2 hours', '1 month'): ").strip()

    try:
        duration_type, qty = parse_duration(duration_input)
        duration_str = f"{qty} {duration_type}(s)"
    except ValueError as e:
        print(f"❌ {e}")
        cursor.close()
        conn.close()
        return

    try:
        cursor.execute("""
            INSERT INTO project (user_id, project_name, duration, starting_date, job_roles)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (user_id, project_name, duration_str, starting_date, job_roles))

        result = cursor.fetchone()
        if result:
            new_id = result[0]
            print(f"✅ Project added successfully! ID: {new_id}")
        else:
            print("✅ Project added successfully!")

        conn.commit()

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        cursor.close()
        conn.close()
# BOOK SERVICE
# -----------------------------
def book_service(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT s.id, s.emp_id, e.name, s.skill, s.rate_hourly, s.rate_daily, s.rate_monthly
            FROM service s
            JOIN employees e ON s.emp_id = e.id
            WHERE s.availability = TRUE
        """)
        services = cursor.fetchall()
        if not services:
            print("❌ No services available for booking.")
            return

        headers = ["Service ID", "Employee", "Skill", "Rate Hourly", "Rate Daily", "Rate Monthly"]
        print(tabulate([(s[0], s[2], s[3], s[4], s[5], s[6]) for s in services], headers=headers, tablefmt="grid"))

        service_id = int(input("Enter Service ID to book: "))
        cursor.execute("SELECT emp_id, rate_hourly, rate_daily, rate_monthly FROM service WHERE id=%s", (service_id,))
        service = cursor.fetchone()
        if not service:
            print("❌ Invalid Service ID.")
            return

        emp_id, r_h, r_d, r_m = service
        duration_input = input("Enter duration (e.g., '2 days'): ").strip()
        duration_type, qty = parse_duration(duration_input)
        cost = r_h*qty if duration_type=="hour" else r_d*qty if duration_type=="day" else r_m*qty
        project_name = input("Enter project name: ").strip()

        cursor.execute("""
            INSERT INTO servicebooking (user_id, emp_id, service_id, duration, cost, project_name)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """, (user_id, emp_id, service_id, duration_input, cost, project_name))
        new_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ Service booked successfully! Booking ID: {new_id}")
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
# VIEW SERVICE BOOKINGS
# -----------------------------
def view_my_service_booking(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT sb.id, e.name, sb.service_id, sb.project_name, sb.duration, sb.cost, sb.status
            FROM servicebooking sb
            JOIN employees e ON sb.emp_id = e.id
            WHERE sb.user_id = %s
        """, (user_id,))
        bookings = cursor.fetchall()
        if not bookings:
            print("❌ No service bookings found.")
            return

        headers = ["Booking ID", "Employee Name", "Service ID", "Project Name", "Duration", "Cost", "Status"]
        print(tabulate(bookings, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()

# -----------------------------
# ADD REVIEW
# -----------------------------
def add_review(user_id):
    conn = create_connection()
    cursor = conn.cursor()

    # 1️⃣ Fetch employees from accepted service bookings
    cursor.execute("""
        SELECT sb.id AS booking_id, e.id AS emp_id, e.name AS emp_name, 'service' AS booking_type, sb.service_id
        FROM servicebooking sb
        JOIN employees e ON sb.emp_id = e.id
        WHERE sb.user_id = %s AND sb.status='accepted'
    """, (user_id,))
    service_employees = cursor.fetchall()

    # 2️⃣ Fetch employees from accepted project bookings
    cursor.execute("""
        SELECT pb.id AS booking_id, e.id AS emp_id, e.name AS emp_name, 'project' AS booking_type, pb.project_id
        FROM projectbooking pb
        JOIN employees e ON pb.emp_id = e.id
        WHERE pb.user_id = %s AND pb.status='accepted'
    """, (user_id,))
    project_employees = cursor.fetchall()

    # Combine both lists
    employees = service_employees + project_employees

    if not employees:
        print("❌ You have no accepted bookings (service/project) to leave a review for.")
        cursor.close()
        conn.close()
        return

    # Show employees in a table
    headers = ["No.", "Booking ID", "Employee ID", "Employee Name", "Type"]
    table_data = [(idx, emp[0], emp[1], emp[2], emp[3]) for idx, emp in enumerate(employees, start=1)]
    print("\n📌 Employees you booked:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    # Select which employee to review
    while True:
        try:
            choice = int(input("\nChoose an employee to review (No.): "))
            if 1 <= choice <= len(employees):
                booking_id, emp_id, emp_name, booking_type, target_id = employees[choice - 1]
                break
            else:
                print("⚠️ Invalid choice. Please select a valid number.")
        except ValueError:
            print("⚠️ Please enter a number.")

    # Get review input (1-5 stars)
    while True:
        review = input("Enter review using * (1-5 stars): ").strip()
        if review and all(ch == "*" for ch in review) and 1 <= len(review) <= 5:
            break
        else:
            print("⚠️ Please enter between 1 and 5 '*' characters only.")

    try:
        if booking_type == "service":
            # target_id contains the actual service_id
            cursor.execute("""
                INSERT INTO review (user_id, emp_id, booking_type, service_id, review)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, emp_id, "service", target_id, review))
        else:  # project
            # target_id contains the actual project_id
            cursor.execute("""
                INSERT INTO review (user_id, emp_id, booking_type, project_id, review)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, emp_id, "project", target_id, review))

        conn.commit()

        # Show confirmation
        confirm_headers = ["User ID", "Employee ID", "Employee Name", "Type", "Review"]
        confirm_data = [(user_id, emp_id, emp_name, booking_type, review)]
        print("\n✅ Review Added Successfully!")
        print(tabulate(confirm_data, headers=confirm_headers, tablefmt="grid"))

    except Exception as e:
        print(f"❌ Error while adding review: {e}")

    finally:
        cursor.close()
        conn.close()
# -----------------------------
# UPDATE PROJECT BOOKING REQUEST
# -----------------------------
def update_project_booking_request(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT pb.id, e.name, pb.project_id, pb.project_name, pb.cost, pb.status
            FROM projectbooking pb
            JOIN employees e ON pb.emp_id = e.id
            WHERE pb.user_id=%s AND pb.status='pending'
        """, (user_id,))
        requests = cursor.fetchall()
        if not requests:
            print("❌ No pending project requests.")
            return

        headers = ["Booking ID", "Employee", "Project ID", "Project Name", "Cost", "Status"]
        print(tabulate(requests, headers=headers, tablefmt="grid"))

        booking_id = int(input("Enter Booking ID to respond: "))
        action = input("Enter 'a' to Accept or 'd' to Decline: ").lower()
        if action == 'a':
            cursor.execute("UPDATE projectbooking SET status='accepted' WHERE id=%s AND user_id=%s", (booking_id, user_id))
            conn.commit()
            print(f"✅ Booking {booking_id} accepted.")
        elif action == 'd':
            cursor.execute("UPDATE projectbooking SET status='declined' WHERE id=%s AND user_id=%s", (booking_id, user_id))
            conn.commit()
            print(f"❌ Booking {booking_id} declined.")
        else:
            print("⚠️ Invalid choice.")
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# -----------------------------
# VIEW PROJECT BOOKINGS
# -----------------------------
def view_my_project_booking(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT pb.id, e.name, pb.project_id, pb.project_name, pb.cost, pb.status
            FROM projectbooking pb
            JOIN employees e ON pb.emp_id = e.id
            WHERE pb.user_id=%s
        """, (user_id,))
        bookings = cursor.fetchall()
        if not bookings:
            print("❌ No project bookings found.")
            return
        headers = ["Booking ID", "Employee", "Project ID", "Project Name", "Cost", "Status"]
        print(tabulate(bookings, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()

# -----------------------------
# VIEW WORK TRACKING
# -----------------------------
def view_work_tracking(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT ab.id, ab.emp_id, e.name, ab.project_name, ab.starting_date, ab.duration, ab.cost, ab.status
            FROM accepted_bookings ab
            JOIN employees e ON ab.emp_id = e.id
            WHERE ab.user_id=%s
        """, (user_id,))
        bookings = cursor.fetchall()
        if not bookings:
            print("❌ No accepted bookings.")
            return
        headers = ["Booking ID","Employee ID","Employee Name","Project Name","Starting Date","Duration","Cost","Status"]
        print(tabulate(bookings, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()
import psycopg2
from psycopg2 import sql
from db_config import create_connection  # Your function must return psycopg2 connection
import sys
from tabulate import tabulate
import textwrap
from decimal import Decimal


# ------------------ ADMIN LOGIN ------------------
def admin_login():
    username = input("Enter admin username: ").strip()
    password = input("Enter admin password: ").strip()

    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            query = "SELECT id, name FROM admins WHERE name = %s AND password = %s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()

        if result:
            admin_id, name = result
            print(f"\n✅ Login successful! Welcome {name}")
            admin_menu()
        else:
            print("❌ Invalid credentials")
    except Exception as e:
        print(f"❌ Error during login: {e}")
    finally:
        conn.close()


# ------------------ ADMIN MENU ------------------
def admin_menu():
    while True:
        print("\n--- Admin Panel ---")
        print("1. Approve new users")
        print("2. View all users")
        print("3. View all service bookings")
        print("4. Approve new employees")
        print("5. View all employees")
        print("6. View all projects")
        print("7. Remove users")
        print("8. Remove employees")
        print("9. View work tracking")
        print("10. View reviews")
        print("11. View total revenue")
        print("12. Exit")
        choice = input("Enter your choice: ").strip()

        menu_options = {
            '1': approve_users,
            '2': view_users,
            '3': view_service_booking,
            '4': approve_employees,
            '5': view_employees,
            '6': view_project,
            '7': remove_users,
            '8': remove_employees,
            '9': view_work_tracking,
            '10': view_review,
            '11': view_total_revenue,
            '12': exit_program
        }

        action = menu_options.get(choice)
        if action:
            action()
        else:
            print("❌ Invalid choice. Please try again.")


def exit_program():
    print("👋 You have logged out successfully.")
    sys.exit()


# ------------------ APPROVE USERS ------------------
def approve_users():
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, emailid, phonenumber, category, aadharnumber,
                       location, professionaltitle, bio, preivous_work, companyname, 
                       gstnumber, licensenumber, address
                FROM users
                WHERE approved = FALSE
                           
            """)
            pending = cursor.fetchall()

            if not pending:
                print("✅ No users pending approval.")
                return

            headers = ["ID", "Name", "Email", "Phone", "Category", "Aadhar", "Location"]
            table_data = []
            extra_info = {}

            for row in pending:
                (user_id, name, email, phone, category, aadharnumber,
                 location, professionaltitle, bio, exp, company, gst, license_no, address) = row

                bio = "\n".join(textwrap.wrap(bio, width=40)) if bio else "-"
                exp = "\n".join(textwrap.wrap(exp, width=40)) if exp else "-"
                address = "\n".join(textwrap.wrap(address, width=40)) if address else "-"
                professionaltitle = "\n".join(textwrap.wrap(professionaltitle, width=40)) if professionaltitle else "-"

                table_data.append([user_id, name, email, phone, category, aadharnumber, location])
                extra_info[user_id] = {
                    "Bio": bio,
                    "Experience": exp,
                    "Company": company or "-",
                    "GST": gst or "-",
                    "License": license_no or "-",
                    "Address": address,
                    "Professional Title": professionaltitle
                }

            print("\n🌟 Pending Users for Approval 🌟\n")
            print(tabulate(table_data, headers=headers, tablefmt="double_grid", stralign="center"))

            for uid, details in extra_info.items():
                print(f"\n📌 Extra Info for User ID {uid}:")
                for key, val in details.items():
                    print(f"   {key}: {val}")

            ids = input("\n✏️ Enter comma-separated IDs to approve: ").strip()
            id_list = [int(i.strip()) for i in ids.split(",") if i.strip().isdigit()]

            if id_list:
                for uid in id_list:
                    cursor.execute("UPDATE users SET approved = TRUE WHERE id = %s", (uid,))
                conn.commit()
                print(f"\n✅ Approved users: {', '.join(map(str, id_list))}")
            else:
                print("❌ No valid IDs entered.")

    except Exception as e:
        print(f"❌ Error while approving users: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("🎉 Operation completed.")


# ------------------ VIEW USERS ------------------
def view_users():
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, emailid, phonenumber, approved FROM users")
            users = cursor.fetchall()

            if not users:
                print("❌ No users found.")
                return

            table_data = [[u[0], u[1], u[2], u[3], "✅ Approved" if u[4] else "⏳ Pending"] for u in users]
            headers = ["ID", "Name", "Email ID", "Phone Number", "Status"]
            print("\n--- All Users ---")
            print(tabulate(table_data, headers=headers, tablefmt="grid"))

    except Exception as e:
        print(f"❌ Error while viewing users: {e}")
    finally:
        conn.close()


# ------------------ VIEW SERVICE BOOKING ------------------
def view_service_booking():
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT b.id, u.name, e.name, b.duration, b.cost, b.status
                FROM servicebooking b
                JOIN users u ON b.user_id = u.id
                JOIN employees e ON b.emp_id = e.id
            """)
            bookings = cursor.fetchall()

            if not bookings:
                print("❌ No service bookings found.")
                return

            table_data = [[b[0], b[1], b[2], b[3], f"₹{b[4]}", b[5]] for b in bookings]
            headers = ["ID", "User", "Employee", "Duration", "Cost", "Status"]
            print("\n--- All Service Bookings ---")
            print(tabulate(table_data, headers=headers, tablefmt="grid"))

    except Exception as e:
        print(f"❌ Error while viewing bookings: {e}")
    finally:
        conn.close()


# ------------------ APPROVE EMPLOYEES ------------------
def approve_employees():
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, emailid, skill, department, qualification, phonenumber, yoe
                FROM employees
                WHERE approved = FALSE
            """)
            pending = cursor.fetchall()

            if not pending:
                print("✅ No employees pending approval.")
                return

            headers = ["ID", "Name", "Email ID", "Skill", "Department", "Qualification", "Phone Number", "YOE"]
            print("\n--- Pending Employees ---")
            print(tabulate(pending, headers=headers, tablefmt="grid"))

            ids = input("\nEnter comma-separated IDs to approve: ").strip()
            id_list = [int(i) for i in ids.split(",") if i.isdigit()]

            if id_list:
                for empid in id_list:
                    cursor.execute("UPDATE employees SET approved = TRUE WHERE id = %s", (empid,))
                conn.commit()

                approved_data = [row for row in pending if row[0] in id_list]
                print("\n✅ Approved Employees:")
                print(tabulate(approved_data, headers=headers, tablefmt="grid"))
            else:
                print("❌ No valid IDs entered.")

    except Exception as e:
        print(f"❌ Error while approving employees: {e}")
        conn.rollback()
    finally:
        conn.close()


# ------------------ VIEW EMPLOYEES ------------------
def view_employees():
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, emailid, skill, department, qualification, phonenumber, yoe, approved 
                FROM employees
            """)
            employees = cursor.fetchall()

            if not employees:
                print("❌ No employees found.")
                return

            table_data = [[
                e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], "✅ Approved" if e[8] else "⏳ Pending"
            ] for e in employees]

            headers = ["ID", "Name", "Email ID", "Skill", "Department", "Qualification", "Phone Number", "YOE", "Status"]
            print("\n--- All Employees ---")
            print(tabulate(table_data, headers=headers, tablefmt="grid"))

    except Exception as e:
        print(f"❌ Error while viewing employees: {e}")
    finally:
        conn.close()


# ------------------ VIEW PROJECTS ------------------
def view_project():
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.id, u.name, p.project_name, p.duration
                FROM project p
                JOIN users u ON p.user_id = u.id
            """)
            projects = cursor.fetchall()

            if not projects:
                print("❌ No projects found.")
                return

            table_data = [[p[0], p[1], p[2], p[3]] for p in projects]
            headers = ["ID", "Username", "Project Name", "Duration"]
            print("\n--- All Projects ---")
            print(tabulate(table_data, headers=headers, tablefmt="grid"))

    except Exception as e:
        print(f"❌ Error while viewing projects: {e}")
    finally:
        conn.close()


# ------------------ REMOVE USERS ------------------
def remove_users():
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, emailid FROM users")
            users = cursor.fetchall()
            if not users:
                print("❌ No users found.")
                return

            headers = ["ID", "Name", "Email ID"]
            print("\n--- Registered Users ---")
            print(tabulate(users, headers=headers, tablefmt="grid"))

            try:
                user_id = int(input("\nEnter User ID to remove: ").strip())
            except ValueError:
                print("❌ Invalid input.")
                return

            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not cursor.fetchone():
                print("❌ User not found.")
                return

            confirm = input(f"⚠️ Delete User ID {user_id} and all related data? (y/n): ").lower()
            if confirm != "y":
                print("❌ Operation cancelled.")
                return

            # Delete child table entries first
            cursor.execute("DELETE FROM review WHERE user_id=%s", (user_id,))
            cursor.execute("DELETE FROM servicebooking WHERE user_id=%s", (user_id,))
            cursor.execute("DELETE FROM projectbooking WHERE user_id=%s", (user_id,))
            cursor.execute("DELETE FROM project WHERE user_id=%s", (user_id,))
            cursor.execute("DELETE FROM accepted_bookings WHERE user_id=%s", (user_id,))
            cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
            conn.commit()
            print(f"✅ User ID {user_id} removed successfully.")
    except Exception as e:
        print(f"❌ Error removing user: {e}")
        conn.rollback()
    finally:
        conn.close()


# ------------------ REMOVE EMPLOYEES ------------------
def remove_employees():
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, emailid FROM employees")
            employees = cursor.fetchall()
            if not employees:
                print("❌ No employees found.")
                return

            headers = ["ID", "Name", "Email ID"]
            print("\n--- Registered Employees ---")
            print(tabulate(employees, headers=headers, tablefmt="grid"))

            try:
                emp_id = int(input("\nEnter Employee ID to remove: ").strip())
            except ValueError:
                print("❌ Invalid input.")
                return

            cursor.execute("SELECT id, name, emailid FROM employees WHERE id=%s", (emp_id,))
            emp_record = cursor.fetchone()
            if not emp_record:
                print("❌ Employee not found.")
                return

            confirm = input(f"⚠️ Delete Employee ID {emp_id} and all related data? (y/n): ").lower()
            if confirm != "y":
                print("❌ Operation cancelled.")
                return

            cursor.execute("DELETE FROM review WHERE emp_id=%s", (emp_id,))
            cursor.execute("DELETE FROM servicebooking WHERE emp_id=%s", (emp_id,))
            cursor.execute("DELETE FROM projectbooking WHERE emp_id=%s", (emp_id,))
            cursor.execute("DELETE FROM service WHERE emp_id=%s", (emp_id,))
            cursor.execute("DELETE FROM accepted_bookings WHERE emp_id=%s", (emp_id,))
            cursor.execute("DELETE FROM employees WHERE id=%s", (emp_id,))
            conn.commit()
            print(f"✅ Employee ID {emp_id} removed successfully.")
    except Exception as e:
        print(f"❌ Error removing employee: {e}")
        conn.rollback()
    finally:
        conn.close()


# ------------------ VIEW WORK TRACKING ------------------
def view_work_tracking():
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT ab.id, ab.emp_id, e.name, ab.project_name, ab.starting_date, ab.duration, ab.cost, ab.status
                FROM accepted_bookings ab
                JOIN employees e ON ab.emp_id = e.id
            """)
            bookings = cursor.fetchall()
            if not bookings:
                print("❌ No service bookings found.")
                return

            headers = ["Booking ID", "Employee ID", "Employee Name", "Project Name", "Starting Date", "Duration", "Cost", "Status"]
            table_data = [[b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7]] for b in bookings]
            print("\n📌 Current Service Bookings:")
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"❌ Error viewing work tracking: {e}")
    finally:
        conn.close()


# ------------------ VIEW REVIEWS ------------------
def view_review():
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT r.id, r.user_id, u.name, r.emp_id, e.name, r.review
                FROM review r
                JOIN users u ON r.user_id = u.id
                JOIN employees e ON r.emp_id = e.id
            """)
            reviews = cursor.fetchall()
            if not reviews:
                print("❌ No reviews found.")
                return

            headers = ["ID", "User ID", "User Name", "Employee ID", "Employee Name", "Review"]
            table_data = [[r[0], r[1], r[2], r[3], r[4], r[5]] for r in reviews]
            print("\n📌 Reviews:")
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"❌ Error viewing reviews: {e}")
    finally:
        conn.close()


# ------------------ VIEW TOTAL REVENUE ------------------
def view_total_revenue():
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT ab.id, ab.user_id, u.name, ab.project_name, ab.emp_id, e.name, ab.cost
                FROM accepted_bookings ab
                JOIN employees e ON ab.emp_id = e.id
                JOIN users u ON ab.user_id = u.id
            """)
            bookings = cursor.fetchall()
            if not bookings:
                print("❌ No bookings found.")
                return

            headers = ["Booking ID", "User ID", "User Name", "Project Name", "Employee ID", "Employee Name", "Cost"]
            table_data = []
            total_revenue = Decimal(0)

            for b in bookings:
                cost = b[6] if b[6] else Decimal(0)
                total_revenue += cost
                table_data.append([b[0], b[1], b[2], b[3], b[4], b[5], float(cost)])

            table_data.append(["", "", "", "", "", "TOTAL REVENUE", float(total_revenue)])
            print("\n📌 Current Bookings and Revenue:")
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"❌ Error viewing total revenue: {e}")
    finally:
        conn.close()



from admin import admin_login
from emp import register_employees, employee_login
from user import register_users, users_login


def main_menu():
    while True:
        print("\n--- Main Menu ---")
        print("1. ADMIN")
        print("2. EMPLOYEE")
        print("3. USER")
        print("4. EXIT")

        choice = input("Enter your choice: ")

        if choice == '1':
            # Admin menu
            print("\n--- Admin Menu ---")
            print("1. Admin Login")
            print("2. Back to Main Menu")
            admin_choice = input("Enter your choice: ")

            if admin_choice == '1':
                admin_login()
            elif admin_choice == '2':
                continue
            else:
                print("Invalid choice! Try again.")

        elif choice == '2':
            # Employee menu
            print("\n--- Employee Menu ---")
            print("1. Register Employee")
            print("2. Employee Login")
            print("3. Back to Main Menu")
            emp_choice = input("Enter your choice: ")

            if emp_choice == '1':
                register_employees()
            elif emp_choice == '2':
                employee_login()
            elif emp_choice == '3':
                continue
            else:
                print("Invalid choice! Try again.")

        elif choice == '3':
            # User menu
            print("\n--- User Menu ---")
            print("1. Register User")
            print("2. User Login")
            print("3. Back to Main Menu")
            user_choice = input("Enter your choice: ")

            if user_choice == '1':
                register_users()
            elif user_choice == '2':
                users_login()
            elif user_choice == '3':
                continue   # 👈 go back to main menu instead of exit
            else:
                print("Invalid choice! Try again.")

        elif choice == '4':
            print("Exiting program. Goodbye!")
            break

        else:
            print("Invalid choice! Try again.")


# ✅ Correct entry point
if __name__ == "__main__":
    main_menu()
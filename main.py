from tkinter import *
from tkinter import messagebox
from functools import partial
import sqlite3
from tkinter.ttk import Combobox
from cryptography.fernet import Fernet
import xml.etree.cElementTree as ET


sql_queries_flags = ["--", ";", "/*", "*/", " OR", " AND", "'"]
current_user = None
Admin = False

#key = Fernet.generate_key()
key=b't3M7EHNbF7mDvrW9An5useVRS7NW90ro3TsjeDeREsQ='
#print(key)
fernet = Fernet(key)

def write_xml():
    conn = sqlite3.connect("carsales.db")
    cursor_obj = conn.cursor()

    cursor_obj.execute("SELECT * FROM user")
    get_user_details = cursor_obj.fetchall()

    data = ET.Element('users')

    for row in get_user_details:
        element = ET.SubElement(data, 'user')
        s_elem1 = ET.SubElement(element, 'user_id')
        s_elem2 = ET.SubElement(element, 'salutation_id')
        s_elem3 = ET.SubElement(element, 'first_name')
        s_elem4 = ET.SubElement(element, 'last_name')
        s_elem5 = ET.SubElement(element, 'email')
        s_elem6 = ET.SubElement(element, 'password')
        s_elem7 = ET.SubElement(element, 'address')
        s_elem8 = ET.SubElement(element, 'postcode_id')

        s_elem1.text = str(row[0])
        s_elem2.text = str(row[1])
        s_elem3.text = str(row[2])
        s_elem4.text = str(row[3])
        s_elem5.text = str(row[4])
        s_elem6.text = str(row[5])
        s_elem7.text = str(row[6])
        s_elem8.text = str(row[7])


    b_xml = ET.tostring(data)

    with open("carsales.xml", "wb") as file:
        file.write(b_xml)

def read_xml():
    tree = ET.parse("carsales.xml")
    root = tree.getroot()

    for user in root.findall('user'):
        user_id = user.find('user_id').text
        salutation_id = user.find('salutation_id').text
        first_name = user.find('first_name').text
        last_name = user.find('last_name').text
        email = user.find('email').text
        password = user.find('password').text
        address = user.find('address').text
        postcode = user.find('postcode_id').text

        print(user_id, salutation_id, first_name, last_name, email, password, address, postcode)

import sqlite3

def send_media_to_sql():
    file_path_name = r'C:\Users\0hampg66\Downloads\bmw.jpg'

    with open(file_path_name, 'rb') as file:
        file_blob = file.read()

    print("[INFO] : Last 100 bytes of the blob =", file_blob[:100])
    conn = None
    cur = None

    try:
        conn = sqlite3.connect("carsales.db")
        print("[INFO] : Successful connection")
        cur = conn.cursor()

        sql_update = "UPDATE storage SET BLOB=? WHERE car_id=?"
        cur.execute(sql_update, (file_blob, 3))
        conn.commit()

        print("[INFO] : The blob for", file_path_name, "was saved to the database.")

    except Exception as e:
        print("[ERROR] :", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()




def insert_car(make_var, model_var, price_var, condition_var):
    conn = sqlite3.connect("carsales.db")
    cursor = conn.cursor()

    make = make_var.get().strip()
    model = model_var.get().strip()
    condition = condition_var.get().strip()
    price = price_var.get()

    if not make or not model:
        messagebox.showerror("Error", "Make and model cannot be empty.")
        return

    cursor.execute("SELECT make_id FROM makes WHERE makes = ?", (make,))
    row = cursor.fetchone()
    if row:
        make_id = row[0]
    else:
        cursor.execute("INSERT INTO makes (makes) VALUES (?)", (make,))
        make_id = cursor.lastrowid

    cursor.execute("SELECT model_id FROM models WHERE model = ?", (model,))
    row = cursor.fetchone()
    if row:
        model_id = row[0]
    else:
        cursor.execute("INSERT INTO models (model) VALUES (?)", (model,))
        model_id = cursor.lastrowid

    cursor.execute("SELECT condition_id FROM conditions WHERE conditions = ?", (condition,))
    row = cursor.fetchone()
    if not row:
        messagebox.showerror("Error", "Invalid condition selected.")
        conn.close()
        return
    condition_id = row[0]

    cursor.execute("""
        INSERT INTO storage (make_id, model_id, price, condition_id, status_id)
        VALUES (?, ?, ?, ?, ?)
    """, (make_id, model_id, price, condition_id, 2))

    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Your car has been successfully added.")





def add_car():
    add_car_window = Toplevel()
    add_car_window.geometry("400x400")
    add_car_window.title("Register")

    frame = Frame(add_car_window)
    frame.place(relx=0.5, rely=0.5, anchor="center")
    frame.grid_columnconfigure(0, weight=1)

    Label(frame, text="Car Make:").grid(row=0, column=0, pady=0)
    make_var = StringVar()
    Entry(frame, textvariable=make_var).grid(row=1, column=0, pady=(0, 5))

    Label(frame, text="Car Model:").grid(row=2, column=0, pady=0)
    model_var = StringVar()
    Entry(frame, textvariable=model_var).grid(row=3, column=0, pady=(0, 5))

    Label(frame, text="Price:").grid(row=4, column=0, pady=0)
    price_var = IntVar()
    Entry(frame, textvariable=price_var).grid(row=5, column=0, pady=(0, 5))

    Label(frame, text="Car Condition:").grid(row=6, column=0, pady=0)
    condition_var = StringVar()
    conditionEntry = Combobox(frame, textvariable=condition_var, values=('Brand New', 'Used - Like New', 'Used - Excellent','Used - Good', 'Used - Fair', 'Used - Bad'))
    conditionEntry.grid(row=7, column=0, pady=(0, 5))
    conditionEntry.current(0)

    Button(frame, text="Add Car", command=lambda: insert_car(make_var, model_var, price_var, condition_var)).grid(row=8, column=0, pady=5)


def validate_update_email(oldEmail, newEmail):
    global current_user


    if any(flag.lower() in oldEmail.lower() for flag in sql_queries_flags):
        messagebox.showerror("Invalid Old Email", "Invalid Old email.")

    elif any(flag.lower() in newEmail.lower() for flag in sql_queries_flags):
        messagebox.showerror("Invalid New Email", "Invalid New email.")

    else:
        connection_obj = sqlite3.connect('carsales.db')
        cursor_obj = connection_obj.cursor()

        cursor_obj.execute("SELECT email FROM user WHERE user_id = ?", (current_user,))
        user_data = cursor_obj.fetchone()

        if user_data:
            try:
                decrypted_email = fernet.decrypt(user_data[0].encode()).decode()

            except Exception as e:
                messagebox.showerror("Error", f"Decryption failed: {str(e)}")
                connection_obj.close()
                return

            if decrypted_email == oldEmail:
                try:
                    encrypted_new_email = fernet.encrypt(newEmail.encode()).decode()
                    cursor_obj.execute("UPDATE user SET email = ? WHERE user_id = ?", (encrypted_new_email, current_user))
                    connection_obj.commit()
                    messagebox.showinfo("Email Updated", "Your email has been updated successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update email: {str(e)}")
            else:
                messagebox.showerror("Error", "Old email does not match our records.")
        else:
            messagebox.showerror("Error", "User not found.")

        cursor_obj.close()
        connection_obj.close()



def update_email():
    settings_window = Toplevel()
    settings_window.geometry("400x200")
    settings_window.title("Update Email")

    frame = Frame(settings_window)
    frame.place(relx=0.5, rely=0.5, anchor="center")
    frame.grid_columnconfigure(0, weight=1)

    oldEmailLabel = Label(frame, text="Old Email Address:")
    oldEmailLabel.grid(row=0, column=0, padx=5, pady=0)
    oldEmail = StringVar()
    oldEmailEntry = Entry(frame, textvariable=oldEmail)
    oldEmailEntry.grid(row=1, column=0, padx=5, pady=0)

    newEmailLabel = Label(frame, text="New Email Address:")
    newEmailLabel.grid(row=2, column=0, padx=5, pady=(5,0))
    newEmail = StringVar()
    newEmailEntry = Entry(frame, textvariable=newEmail)
    newEmailEntry.grid(row=3, column=0, padx=5, pady=(0,5))

    updateEmailButton = Button(frame, text="Update Email", command=lambda: validate_update_email(oldEmail.get(), newEmail.get()))
    updateEmailButton.grid(row=4, column=0, padx=5, pady=5)



def update_password():
    pass

def settings():
    global current_user
    if not current_user:
        messagebox.showerror("Error", "No user logged in.")
        return

    settings_window = Toplevel()
    settings_window.geometry("400x400")
    settings_window.title("Settings")

    frame = Frame(settings_window)
    frame.place(relx=0.5, rely=0.5, anchor="center")
    frame.grid_columnconfigure(0, weight=1)

    connection_obj = sqlite3.connect('carsales.db')
    cursor_obj = connection_obj.cursor()

    cursor_obj.execute("SELECT email FROM user WHERE user_id = ?", (current_user,))
    user_data = cursor_obj.fetchone()
    connection_obj.close()

    if not user_data:
        messagebox.showerror("Error", "User not found.")
        settings_window.destroy()
        return

    emailButton = Button(frame, text="Change Email", command=partial(update_email)).grid(row=4, column=0, padx=5, pady=5)
    passwordButton = Button(frame, text="Change Password", command=partial(update_password)).grid(row=5, column=0, padx=5, pady=5)




def main():
    global Admin

    main_window = Toplevel()
    main_window.geometry("800x800")
    main_window.title("Main Window")

    sideBar_colour = "#9E9E9E"

    sidebar_frame = Frame(main_window, bg=sideBar_colour)
    sidebar_frame.pack(side="left", fill="y")

    main_frame = Frame(main_window)
    main_frame.pack(side="right", fill="both")

    button_style = {"width": 15, "height": 2}

    if Admin:
        addCar = Button(sidebar_frame, command=add_car ,text="Add Car", **button_style)
        addCar.pack(padx=5, pady=(5,0))

    else:
        loginButton = Button(sidebar_frame, text="Login", command=login, **button_style)
        loginButton.pack(padx=5, pady=(5,0))

        setting_button = Button(sidebar_frame, text="Settings", command=settings, **button_style)
        setting_button.pack(padx=5)

        exitButton = Button(sidebar_frame, text="Exit", command=main_window.destroy, **button_style)
        exitButton.pack(padx=5)

    main_window.mainloop()


def validate_login(email, password):
    global current_user
    global Admin

    if not email.get() or not password.get():
        messagebox.showerror("Missing Fields", "Please enter both email and password.")

    if any(flag.lower() in password.get().lower() for flag in sql_queries_flags):
        messagebox.showerror("Invalid Password", "Invalid password.")

    elif any(flag.lower() in email.get().lower() for flag in sql_queries_flags):
        messagebox.showerror("Invalid Email", "Invalid email.")

    else:
        connection_obj = sqlite3.connect('carsales.db')
        cursor_obj = connection_obj.cursor()

        cursor_obj.execute("SELECT user_id, email, password, is_admin FROM user")
        users = cursor_obj.fetchall()
        found = False

        for user_id, enc_email, enc_password, is_admin in users:
            try:
                decrypted_email = fernet.decrypt(enc_email.encode()).decode()
                decrypted_password = fernet.decrypt(enc_password.encode()).decode()
            except Exception:
                continue

            if decrypted_email == email.get() and decrypted_password == password.get():
                current_user = user_id
                found = True
                if is_admin == "TRUE":
                    Admin = True
                elif is_admin == "FALSE":
                    Admin = False
                break

        if found:
            messagebox.showinfo(message="Login Successful", title="Login Successful")
            main()
        else:
            messagebox.showerror(message="Login Failed", title="Login Failed")


def validate_register(salutation_var, firstName, lastName, email, address, postcode, password):
    if (not salutation_var.get() or not firstName.get() or not lastName.get() or not email.get() or not address.get() or not postcode.get() or not password.get()):
        messagebox.showerror("Missing Fields", "Please fill in all fields before registering.")
        return

    if any(flag.lower() in password.get().lower() for flag in sql_queries_flags):
        messagebox.showerror("Invalid Password", "Invalid password.")

    elif any(flag.lower() in salutation_var.get().lower() for flag in sql_queries_flags):
        messagebox.showerror("Invalid Salutation", "Invalid salutation.")

    elif any(flag.lower() in firstName.get().lower() for flag in sql_queries_flags):
        messagebox.showerror("Invalid First Name", "Invalid first name.")

    elif any(flag.lower() in lastName.get().lower() for flag in sql_queries_flags):
        messagebox.showerror("Invalid Last Name", "Invalid last name.")

    elif any(flag.lower() in address.get().lower() for flag in sql_queries_flags):
        messagebox.showerror("Invalid Address", "Invalid address.")

    elif any(flag.lower() in postcode.get().lower() for flag in sql_queries_flags):
        messagebox.showerror("Invalid Postcode", "Invalid postcode.")

    elif any(flag.lower() in email.get().lower() for flag in sql_queries_flags):
        messagebox.showerror("Invalid Email", "Invalid email.")

    else:
        connection_obj = sqlite3.connect('carsales.db')
        cursor_obj = connection_obj.cursor()
        value_email = email.get()

        cursor_obj.execute("SELECT * FROM user WHERE email = ?", (value_email,))
        output = cursor_obj.fetchall()

        if len(output) > 0:
            messagebox.showerror(message="Email already exists", title="Registration Failed")
        else:
            cursor_obj.execute("SELECT salutation_id FROM salutations WHERE salutation = ?", (salutation_var.get(),))
            salutation_id = cursor_obj.fetchone()

            if not salutation_id:
                raise ValueError("Invalid salutation.")
            salutation_id = salutation_id[0]


            cursor_obj.execute("SELECT postcode_id FROM postcodes WHERE postcode = ?", (postcode.get(),))
            postcode_id = cursor_obj.fetchone()

            if not postcode_id:
                cursor_obj.execute("INSERT INTO postcodes (postcode) VALUES(?)", (postcode.get(),))
                cursor_obj.execute("SELECT postcode_id FROM postcodes WHERE postcode = ?", (postcode.get(),))
                postcode_id = cursor_obj.fetchone()

            postcode_id = postcode_id[0]

            encrypted_email = fernet.encrypt(email.get().encode()).decode()
            encrypted_password = fernet.encrypt(password.get().encode()).decode()

            cursor_obj.execute(
                "INSERT INTO user (salutations_id, first_name, last_name, email, address, postcode_id, password, is_admin) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (salutation_id, firstName.get(), lastName.get(), encrypted_email, address.get(), postcode_id,
                 encrypted_password, "FALSE")
            )

            connection_obj.commit()
            messagebox.showinfo(message="Registration Successful", title="Success")

        connection_obj.close()


def register():
    register_window = Toplevel()
    register_window.geometry("400x400")
    register_window.title("Register")

    frame = Frame(register_window)
    frame.place(relx=0.5, rely=0.5, anchor="center")
    frame.grid_columnconfigure(0, weight=1)

    salutationLabel = Label(frame, text="Salutation:")
    salutationLabel.grid(row=0, column=0, padx=5, pady=0)
    salutation_var = StringVar()
    salutationEntry = Combobox(frame, textvariable=salutation_var)
    salutationEntry['values'] = ('Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Mx.')
    salutationEntry.current(0)
    salutation_var.set(salutationEntry.get())
    salutationEntry.grid(row=1, column=0, padx=5, pady=(0,5))

    firstName = Label(frame, text="First Name:")
    firstName.grid(row=2, column=0, padx=5, pady=0)
    firstName = StringVar()
    firstNameEntry = Entry(frame, textvariable=firstName)
    firstNameEntry.grid(row=3, column=0, padx=5, pady=(0,5))

    lastName = Label(frame, text="Last Name:")
    lastName.grid(row=4, column=0, padx=5, pady=0)
    lastName = StringVar()
    lastNameEntry = Entry(frame, textvariable=lastName)
    lastNameEntry.grid(row=5, column=0, padx=5, pady=(0, 5))

    emailLabel = Label(frame, text="Email Address:")
    emailLabel.grid(row=6, column=0, padx=5, pady=0)
    email = StringVar()
    emailEntry = Entry(frame, textvariable=email)
    emailEntry.grid(row=7, column=0, padx=5, pady=0)

    addressLabel = Label(frame, text="Street Address:")
    addressLabel.grid(row=8, column=0, padx=5, pady=0)
    address = StringVar()
    addressEntry = Entry(frame, textvariable=address)
    addressEntry.grid(row=9, column=0, padx=5, pady=0)

    postcodeLabel = Label(frame, text="Post Code:")
    postcodeLabel.grid(row=10, column=0, padx=5, pady=0)
    postcode = StringVar()
    postcodeEntry = Entry(frame, textvariable=postcode)
    postcodeEntry.grid(row=11, column=0, padx=5, pady=0)

    passwordLabel = Label(frame, text="Password:")
    passwordLabel.grid(row=12, column=0, padx=5, pady=(5, 0))
    password = StringVar()
    passwordEntry = Entry(frame, textvariable=password)
    passwordEntry.grid(row=13, column=0, padx=5, pady=(0, 5))

    registerButton = Button(frame, text="Register", command=partial(validate_register, salutation_var, firstName, lastName, email, address, postcode, password)
    )
    registerButton.grid(row=14, column=0, padx=5, pady=5)

    register_window.mainloop()

def login():
    tkWindow = Tk()
    tkWindow.geometry("400x250")
    tkWindow.title("Start Page")

    frame = Frame(tkWindow)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    frame.grid_columnconfigure(0, weight=1)

    emailLabel = Label(frame, text="Email Address:")
    emailLabel.grid(row=0, column=0, padx=5, pady=0)
    email =StringVar()
    emailEntry = Entry(frame, textvariable=email)
    emailEntry.grid(row=1, column=0, padx=5, pady=0)

    passwordLabel = Label(frame, text="Password:")
    passwordLabel.grid(row=2, column=0, padx=5, pady=(5,0))
    password =StringVar()
    passwordEntry = Entry(frame, textvariable=password)
    passwordEntry.grid(row=3, column=0, padx=5, pady=(0,5))

    loginButton = Button(frame, text="Login", command=partial(validate_login, email, password)).grid(row=4, column=0, padx=5, pady=5)
    loginButton2 = Button(frame, text="Register", command=partial(register)).grid(row=5, column=0, padx=5, pady=5)

    tkWindow.mainloop()

def create_car_make_graph():
    connection_obj = sqlite3.connect('carsales.db')
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("SELECT * FROM car_storage")

    output1 = cursor_obj.fetchall()
    connection_obj.close()

    tkWindow = Tk()
    tkWindow.geometry("500x300")
    tkWindow.title("Car Make Graph")

    frame = Frame(tkWindow)
    frame.pack(fill="both", expand=True)

    canvas = Canvas(frame, width=450, height=250, bg="white")
    canvas.pack()

    start_point_text_x = 30
    start_point_text_y = 30
    start_point_rect_x = 120
    start_point_rect_y = 20
    step = 30

    for count, row in enumerate(output1):
        make = row[0]
        value = int(row[1])
        canvas.create_text(start_point_text_x, start_point_text_y + step * count, text=make, anchor="w")
        canvas.create_rectangle(start_point_rect_x, start_point_rect_y + step * count, start_point_rect_x + (value*10), start_point_rect_y + 20 + step * count, fill='red')
        canvas.create_text(start_point_rect_x + (value*10) + 10, start_point_text_y + step * count, text=f"{value}")

    tkWindow.mainloop()



if __name__ == '__main__':
    login()
import tkinter as tk
from tkinter import messagebox


def add_contact():
    name = name_entry.get().strip()
    phone = phone_entry.get().strip()

    if name == "" or phone == "":
        messagebox.showwarning("Warning", "Please enter both name and phone number.")
        return

    with open("numbers.txt", "a") as file:
        file.write(name + " - " + phone + "\n")

    messagebox.showinfo("Success", "Contact added successfully!")

    name_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)


def view_contacts():
    try:
        with open("numbers.txt", "r") as file:
            contacts = file.read()

        if contacts.strip() == "":
            messagebox.showinfo("Telephone Directory", "No contacts found.")
        else:
            messagebox.showinfo("Telephone Directory", contacts)

    except FileNotFoundError:
        messagebox.showinfo("Telephone Directory", "No contacts found.")


def search_contact():
    name = name_entry.get().strip()

    if name == "":
        messagebox.showwarning("Warning", "Enter a name to search.")
        return

    try:
        with open("numbers.txt", "r") as file:
            contacts = file.readlines()

        results = []

        for contact in contacts:
            if name.lower() in contact.lower():
                results.append(contact.strip())

        if results:
            messagebox.showinfo("Search Result", "\n".join(results))
        else:
            messagebox.showinfo("Search Result", "Contact not found.")

    except FileNotFoundError:
        messagebox.showinfo("Search Result", "No contacts found.")


def delete_contact():
    name = name_entry.get().strip()

    if name == "":
        messagebox.showwarning("Warning", "Enter a name to delete.")
        return

    try:
        with open("numbers.txt", "r") as file:
            contacts = file.readlines()

        new_contacts = []
        found = False

        for contact in contacts:
            if name.lower() not in contact.lower():
                new_contacts.append(contact)
            else:
                found = True

        with open("numbers.txt", "w") as file:
            file.writelines(new_contacts)

        if found:
            messagebox.showinfo("Success", "Contact deleted successfully!")
        else:
            messagebox.showinfo("Result", "Contact not found.")

    except FileNotFoundError:
        messagebox.showinfo("Result", "No contacts found.")


# Main window
window = tk.Tk()
window.title("Telephone Directory")
window.geometry("450x400")

title = tk.Label(
    window,
    text="TELEPHONE DIRECTORY",
    font=("Arial", 20, "bold")
)
title.pack(pady=20)

name_label = tk.Label(window, text="Name:", font=("Arial", 12))
name_label.pack()

name_entry = tk.Entry(window, width=35, font=("Arial", 12))
name_entry.pack(pady=5)

phone_label = tk.Label(window, text="Phone Number:", font=("Arial", 12))
phone_label.pack()

phone_entry = tk.Entry(window, width=35, font=("Arial", 12))
phone_entry.pack(pady=5)

add_button = tk.Button(
    window,
    text="Add Contact",
    width=18,
    command=add_contact
)
add_button.pack(pady=10)

search_button = tk.Button(
    window,
    text="Search Contact",
    width=18,
    command=search_contact
)
search_button.pack(pady=5)

view_button = tk.Button(
    window,
    text="View Contacts",
    width=18,
    command=view_contacts
)
view_button.pack(pady=5)

delete_button = tk.Button(
    window,
    text="Delete Contact",
    width=18,
    command=delete_contact
)
delete_button.pack(pady=5)

exit_button = tk.Button(
    window,
    text="Exit",
    width=18,
    command=window.destroy
)
exit_button.pack(pady=5)

window.mainloop()
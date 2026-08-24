# Telephone Directory

A simple **Telephone Directory desktop application** built with **Python and Tkinter**. It allows users to add, search, view, and delete contacts through an easy-to-use graphical interface.

## Features

* Add new contacts with name and phone number
* Search contacts by name
* View all saved contacts
* Delete contacts
* Local file-based storage using `numbers.txt`
* Simple and lightweight Tkinter GUI

## Tech Stack

* **Python 3**
* **Tkinter**
* **Text File Storage**

## Getting Started

### Clone the repository

```bash
git clone https://github.com/harshitaagar2880/telephone-directory
cd telephone-directory
```

### Run the application

```bash
python telephone_directory.py
```

> Make sure Python 3 is installed on your system.

## How It Works

Contacts are stored locally in a `numbers.txt` file using the following format:

```text
Name - Phone Number
```

The file is created automatically when the first contact is added.

## Project Structure

```text
Telephone-Directory/
├── telephone_directory.py
├── numbers.txt
└── README.md
```

## Future Improvements

* Edit existing contacts
* Prevent duplicate contacts
* Add phone number validation
* Use SQLite for database storage
* Improve the GUI design

## License

This project is open source and available under the **MIT License**.

Tkinter Inventory Management System
Project Overview
This is a straightforward desktop application built with Python's Tkinter, designed for basic inventory management. It allows users to track items by name, quantity, unit price, and automatically calculated stock value. The system features an intuitive graphical interface for adding, updating, deleting, and checking item details, with all data persistently stored in a local JSON file.

Features
Add/Update Items: Add new items or update existing ones by name, quantity, and unit price. New quantities are added to existing stock.

Update Item Quantity: Adjust stock levels for any item using its name.

Check Stock Value: View current quantity, unit price, and total stock value (Current Qty x Unit Price) for a specified item.

Delete Items: Remove items from inventory by name.

Persistent Data: Inventory data is automatically saved to and loaded from inventory.json.

User-Friendly GUI: Clear Tkinter interface with a dynamic table (Treeview) for displaying inventory.

Autocomplete: Autocomplete suggestions for item names in input fields.

Currency Formatting: Prices and values are displayed with the Indian Rupee symbol (₹).

Error Handling: Basic input validation and error messages.

How to Use
Prerequisites
Python 3.x

Pillow library (pip install Pillow)

Running the Application
Save the Python code as mod.py.

Place the logo image (2.png) in the same directory.

Run from your terminal:

python mod.py

File Structure
.
├── mod.py                # Main application script
├── inventory.json        # (Automatically created) Inventory data file
└── 2.png                 # Application logo/icon

Technologies Used
Python 3.x: Core programming language.

Tkinter: GUI toolkit for the desktop application.

Pillow: For image handling within the GUI.

JSON: For local data persistence.

Future Enhancements
Reporting features (e.g., low stock).

Advanced search and filtering.

Category management.

User authentication.

Undo/redo functionality.

Barcode scanning integration.

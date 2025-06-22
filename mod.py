print('-------------------------------------------------------------------------------------------------')
import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import uuid
from PIL import Image, ImageTk # Import Image and ImageTk from Pillow
import tkinter.font as tkFont # Import for custom fonts

class InventoryManager:
    
    def __init__(self, data_file="inventory.json"):
        
        self.data_file = data_file
        self.items = {}
        self._load_data()

    def _load_data(self):
        
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    loaded_items = json.load(f).get("items", {})
                    for item_id, details in loaded_items.items():
                        details["quantity"] = details.get("quantity", 0)
                        details["price"] = details.get("price", 0.0)
                        details["stock_value"] = details["quantity"] * details["price"]

                        if "spent_value" in details:
                            del details["spent_value"]
                        if "spent_quantity" in details:
                            del details["spent_quantity"]
                    self.items = loaded_items
                print(f"Great! Loaded {len(self.items)} items from '{self.data_file}'.")
            except json.JSONDecodeError:
                print(f"Oops! Problem reading '{self.data_file}'. It seems corrupted. Starting with an empty inventory to be safe.")
                self.items = {}
            except Exception as e:
                print(f"An unexpected error happened while loading data: {e}. Starting with an empty inventory.")
                self.items = {}
        else:
            print(f"Couldn't find the inventory file at '{self.data_file}'. Starting with a brand new, empty inventory.")

    def _save_data(self):
        
        try:
            with open(self.data_file, 'w') as f:
                json.dump({"items": self.items}, f, indent=4)
            print(f"Inventory saved! We now have {len(self.items)} items recorded in '{self.data_file}'.")
        except Exception as e:
            print(f"Oh dear! Couldn't save the inventory to '{self.data_file}': {e}")

    def add_item(self, name, quantity, price):
        """
        This is how we add a brand new item to our inventory, or update an existing one if the name matches.

        """
        cleaned_name = name.strip().lower()
        if not cleaned_name:
            return "Error: Please give your item a name. It can't be empty!"
        if quantity <= 0:
            return "Error: Quantity in stock must be a positive number when adding new items."
        if price <= 0:
            return "Error: Price per unit must be a positive number. Items usually cost more than zero!"

        existing_item_id = None
        for item_id, item_details in self.items.items():
            if item_details["name"].lower() == cleaned_name:
                existing_item_id = item_id
                break

        if existing_item_id:
            item = self.items[existing_item_id]
            old_quantity = item["quantity"]
            item["quantity"] += quantity
            item["price"] = price
            item["stock_value"] = item["quantity"] * item["price"]
            self._save_data()
            return f"Success: Item '{name}' (ID: {existing_item_id}) already exists. Quantity updated from {old_quantity} to {item['quantity']}, and Unit Price updated to ₹{price:.2f}."
        else:
            item_id = str(uuid.uuid4())
            self.items[item_id] = {
                "name": name.strip(),
                "quantity": quantity,
                "price": price,
                "stock_value": quantity * price
            }
            self._save_data()
            return f"Success! Added new item '{name}' (ID: {item_id}) to your inventory."

    def update_item(self, item_id, new_quantity=None, new_price=None):
       
        if item_id not in self.items:
            return f"Error: Couldn't find any item with ID '{item_id}'. Are you sure that's the right one?"

        item = self.items[item_id]
        updated_something = False

        if new_quantity is not None:
            if new_quantity >= 0:
                item["quantity"] = new_quantity
                updated_something = True
            else:
                return "Error: New quantity for total stock can't be negative."
        
        if new_price is not None:
            if new_price > 0:
                item["price"] = new_price
                updated_something = True
            else:
                return "Error: New price must be a positive number. Even free items are ₹0.00, not negative!"

        if updated_something:
            item["stock_value"] = item["quantity"] * item["price"]
            self._save_data()
            return f"Success: Item '{item['name']}' (ID: {item_id}) has been updated."
        else:
            return "No valid updates provided for the item."

    def record_spend(self, item_id, amount_spent):
        """
        This function records when a certain amount of an item has been 'spent' 
        It will decrease the main 'quantity' and then recalculate the 'stock_value' accordingly.
        """
        if item_id not in self.items:
            return f"Error: Item with ID '{item_id}' not found. Cannot record spend."
        
        if amount_spent <= 0:
            return "Error: Amount spent must be a positive number."

        item = self.items[item_id]
        if item["quantity"] >= amount_spent:
            item["quantity"] -= amount_spent
            item["stock_value"] = item["quantity"] * item["price"]
            self._save_data()
            return f"Success: Recorded {amount_spent} units of '{item['name']}' (ID: {item_id}) as spent. Current stock value is now ₹{item['stock_value']:.2f}."
        else:
            return f"Error: Not enough '{item['name']}' (ID: {item_id}) in stock. Available: {item['quantity']}, Tried to spend: {amount_spent}."

    def delete_item(self, item_id):
        """
        This function helps us remove an item from our inventory using its unique ID.

        """
        if item_id in self.items:
            item_name = self.items[item_id]["name"]
            del self.items[item_id]
            self._save_data()
            return f"Success: Item '{item_name}' (ID: {item_id}) has been removed from inventory."
        else:
            return f"Error: Couldn't delete item. ID '{item_id}' not found in inventory."

    def delete_item_by_name(self, name):
        """
        Deletes an item from the inventory based on its name.
        
        """
        cleaned_name = name.strip().lower()
        item_found = False
        item_id_to_delete = None
        item_name_actual = ""

        for item_id, details in self.items.items():
            if details["name"].lower() == cleaned_name:
                item_id_to_delete = item_id
                item_name_actual = details["name"]
                item_found = True
                break
        
        if item_found and item_id_to_delete:
            del self.items[item_id_to_delete]
            self._save_data()
            return f"Success: Item '{item_name_actual}' (ID: {item_id_to_delete}) has been removed from inventory."
        else:
            return f"Error: Couldn't delete item. Item named '{name}' not found in inventory."

    def get_item_by_name(self, name):
        """
        Retrieves an item's details based on its name (case-insensitive).
        
        """
        cleaned_name = name.strip().lower()
        for item_id, details in self.items.items():
            if details["name"].lower() == cleaned_name:
                return item_id, details
        return None


    def get_all_items(self):
        """
        Need to see everything in your inventory? This function gives you a list of all items.

        
        """
        return self.items.copy()

class InventoryApp:
    
    def __init__(self, master_window):
        """
        Sets up our main application window and connects all the pieces.

        
        """
        self.master = master_window
        master_window.title("NeoASJ's Inventory System") # Set a generic title for the main window title bar
        master_window.geometry("900x600")
        master_window.resizable(True, True)

        # Load and resize the image for the custom title/logo
        try:
            # Construct the path to the uploaded image. Assuming it's in the same directory.
            # Updated image path to the new image
            image_path = "2.png" 
            original_image = Image.open(image_path)
            # Define target width and height for the logo
            target_width = 50 # Smaller width for the icon
            target_height = 50 # Smaller height for the icon
            # Resize image while maintaining aspect ratio
            original_width, original_height = original_image.size
            aspect_ratio = original_width / original_height
            if target_width / target_height > aspect_ratio:
                # Target is wider, so scale by height
                new_height = target_height
                new_width = int(new_height * aspect_ratio)
            else:
                # Target is taller or aspect ratios match, so scale by width
                new_width = target_width
                new_height = int(new_width / aspect_ratio)

            resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.app_logo = ImageTk.PhotoImage(resized_image)
        except FileNotFoundError:
            messagebox.showerror("Image Error", f"Logo image not found at '{image_path}'. Make sure it's in the correct directory.")
            self.app_logo = None
        except Exception as e:
            messagebox.showerror("Image Error", f"Failed to load or process logo: {e}")
            self.app_logo = None

        # Define a bold font for "NeoTrack" label
        self.neotrack_font = tkFont.Font(family="Helvetica", size=18, weight="bold")


        self.inventory_manager = InventoryManager()

        master_window.grid_rowconfigure(0, weight=1)
        master_window.grid_columnconfigure(0, weight=1)
        master_window.grid_columnconfigure(1, weight=2)

        # --- Left Pane (Input Frame) ---
        self.input_frame = ttk.LabelFrame(master_window, text="Add / Update / Delete Item")
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Configure columns within the input_frame for the logo and text side-by-side
        self.input_frame.grid_columnconfigure(0, weight=0) # For the image
        self.input_frame.grid_columnconfigure(1, weight=1) # For the text and other widgets

        current_row_input_frame = 0
        # Create a sub-frame to hold the image and text side-by-side
        logo_text_frame = tk.Frame(self.input_frame)
        logo_text_frame.grid(row=current_row_input_frame, column=0, columnspan=2, pady=5, sticky="nw")
        
        # Place the image in the sub-frame, left-aligned
        if self.app_logo:
            self.logo_label_left = tk.Label(logo_text_frame, image=self.app_logo)
            self.logo_label_left.pack(side=tk.LEFT, padx=0, pady=0) # Use pack for tight control, no padx
            
        # Place the bold "NeoTrack" label in the sub-frame, right of the image
        self.neotrack_text_label_left = tk.Label(logo_text_frame, text="NeoTrack", font=self.neotrack_font)
        self.neotrack_text_label_left.pack(side=tk.LEFT, padx=0, pady=0) # Use pack for tight control, no padx
        
        current_row_input_frame += 1 # Advance row for subsequent widgets
        
        # Now, create the rest of the input widgets starting from 'current_row_input_frame'
        # These will span both columns for alignment beneath the combined logo/text header
        self._create_input_widgets(self.input_frame, start_row=current_row_input_frame) 


        # --- Right Pane (Display Frame) ---
        self.display_frame = ttk.LabelFrame(master_window, text="Current Inventory")
        self.display_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.display_frame.grid_rowconfigure(0, weight=1) # Treeview will now start from row 0 and take all vertical space
        self.display_frame.grid_columnconfigure(0, weight=1)
        
        current_row_display_frame = 0 # Start from row 0 as there are no elements above now

        # Now, create the display widgets (Treeview) starting from 'current_row_display_frame'
        self._create_display_widgets(self.display_frame, start_row=current_row_display_frame)
        
        self._update_item_list()

    def _create_input_widgets(self, frame_to_fill, start_row=0):
        """
        This function fills up the 'Add/Update/Delete Item' frame (the left side)
        with all the necessary input boxes and buttons for managing items.
        'start_row' parameter allows to offset the row index for widgets.
        """
        row_index = start_row # Use start_row to place widgets after the logo and text label

        # --- Item Name Input ---
        tk.Label(frame_to_fill, text="Item Name:").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(frame_to_fill)
        self.name_entry.grid(row=row_index, column=1, padx=5, pady=5, sticky="ew")
        row_index += 1

        # --- Quantity Input (Total Stock) ---
        tk.Label(frame_to_fill, text="Total Quantity:").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
        self.quantity_entry = ttk.Entry(frame_to_fill)
        self.quantity_entry.grid(row=row_index, column=1, padx=5, pady=5, sticky="ew")
        row_index += 1

        # --- Price Input (Per Unit) ---
        tk.Label(frame_to_fill, text="Price (per unit):").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
        self.price_entry = ttk.Entry(frame_to_fill)
        self.price_entry.grid(row=row_index, column=1, padx=5, pady=5, sticky="ew")
        row_index += 1

        # --- "Add Item" Button ---
        self.add_button = ttk.Button(frame_to_fill, text="Add Item", command=self._add_item_gui)
        # These buttons and separators should span both columns (0 and 1) to align correctly
        self.add_button.grid(row=row_index, column=0, columnspan=2, pady=5)
        row_index += 1

        # --- Separator for Item Operations ---
        ttk.Separator(frame_to_fill, orient="horizontal").grid(row=row_index, column=0, columnspan=2, sticky="ew", pady=10)
        row_index += 1

        # --- NEW SECTION: Check Stock Value by Item Name ---
        check_stock_frame = ttk.LabelFrame(frame_to_fill, text="Check Stock Value by Item Name")
        check_stock_frame.grid(row=row_index, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        check_stock_frame.grid_columnconfigure(1, weight=1)

        check_stock_row_idx = 0
        tk.Label(check_stock_frame, text="Item Search:").grid(row=check_stock_row_idx, column=0, padx=5, pady=5, sticky="w")
        self.item_search_entry_var = tk.StringVar()
        self.item_search_combobox = ttk.Combobox(check_stock_frame, textvariable=self.item_search_entry_var)
        self.item_search_combobox.grid(row=check_stock_row_idx, column=1, padx=5, pady=5, sticky="ew")
        self.item_search_combobox.bind("<KeyRelease>", self._update_autocomplete_suggestions)
        check_stock_row_idx += 1

        self.check_stock_button = ttk.Button(check_stock_frame, text="Check Stock Value", command=self._check_stock_value_gui)
        self.check_stock_button.grid(row=check_stock_row_idx, column=0, columnspan=2, pady=5)
        check_stock_row_idx += 1

        self.stock_value_display_label = tk.Label(check_stock_frame, text="", wraplength=250, justify=tk.LEFT)
        self.stock_value_display_label.grid(row=check_stock_row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        row_index += 1

        # --- Separator for Quantity Update by Name ---
        ttk.Separator(frame_to_fill, orient="horizontal").grid(row=row_index, column=0, columnspan=2, sticky="ew", pady=10)
        row_index += 1

        # --- NEW SECTION: Update Quantity by Item Name ---
        update_qty_frame = ttk.LabelFrame(frame_to_fill, text="Update Quantity by Item Name")
        update_qty_frame.grid(row=row_index, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        update_qty_frame.grid_columnconfigure(1, weight=1)

        update_qty_row_idx = 0
        tk.Label(update_qty_frame, text="Item Name:").grid(row=update_qty_row_idx, column=0, padx=5, pady=5, sticky="w")
        self.update_qty_name_var = tk.StringVar()
        self.update_qty_name_combobox = ttk.Combobox(update_qty_frame, textvariable=self.update_qty_name_var)
        self.update_qty_name_combobox.grid(row=update_qty_row_idx, column=1, padx=5, pady=5, sticky="ew")
        self.update_qty_name_combobox.bind("<KeyRelease>", self._update_autocomplete_suggestions)
        update_qty_row_idx += 1

        tk.Label(update_qty_frame, text="New Quantity:").grid(row=update_qty_row_idx, column=0, padx=5, pady=5, sticky="w")
        self.new_quantity_entry = ttk.Entry(update_qty_frame)
        self.new_quantity_entry.grid(row=update_qty_row_idx, column=1, padx=5, pady=5, sticky="ew")
        update_qty_row_idx += 1

        self.update_qty_button = ttk.Button(update_qty_frame, text="Update Quantity", command=self._update_quantity_by_name_gui)
        self.update_qty_button.grid(row=update_qty_row_idx, column=0, columnspan=2, pady=5)
        row_index += 1

        # --- Separator for Delete by Name ---
        ttk.Separator(frame_to_fill, orient="horizontal").grid(row=row_index, column=0, columnspan=2, sticky="ew", pady=10)
        row_index += 1

        # --- Delete Item by Name (with Autocomplete) ---
        delete_by_name_frame = ttk.LabelFrame(frame_to_fill, text="Delete Item by Name")
        delete_by_name_frame.grid(row=row_index, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        delete_by_name_frame.grid_columnconfigure(1, weight=1)

        delete_name_row_idx = 0
        tk.Label(delete_by_name_frame, text="Item Name:").grid(row=delete_name_row_idx, column=0, padx=5, pady=5, sticky="w")
        
        self.delete_by_name_entry_var = tk.StringVar()
        self.delete_by_name_combobox = ttk.Combobox(delete_by_name_frame, textvariable=self.delete_by_name_entry_var)
        self.delete_by_name_combobox.grid(row=delete_name_row_idx, column=1, padx=5, pady=5, sticky="ew")
        self.delete_by_name_combobox.bind("<KeyRelease>", self._update_autocomplete_suggestions)
        delete_name_row_idx += 1

        self.delete_by_name_button = ttk.Button(delete_by_name_frame, text="Delete Item", command=self._delete_item_by_name_gui)
        self.delete_by_name_button.grid(row=delete_name_row_idx, column=0, columnspan=2, pady=5)
        row_index += 1


    def _create_display_widgets(self, frame_to_fill, start_row=0):
        """
        This function sets up the Treeview widget in our 'Current Inventory' frame
        (the right side) to neatly display all our inventory items in a table format.
        Now with 'Stock Value' instead of 'Spent Value'.
        
        """
        # --- The Treeview: Our Inventory Table ---
        # We now have columns for Name, Quantity, Price, Stock Value, and ID.
        self.item_tree = ttk.Treeview(frame_to_fill, columns=("Name", "Quantity", "Price", "Stock Value", "ID"), show="headings")

        # --- Setting up the column headings ---
        self.item_tree.heading("Name", text="Item Name", anchor=tk.W)
        self.item_tree.heading("Quantity", text="Current Qty", anchor=tk.W)
        self.item_tree.heading("Price", text="Unit Price", anchor=tk.W)
        self.item_tree.heading("Stock Value", text="Stock Value", anchor=tk.W)
        self.item_tree.heading("ID", text="Item ID", anchor=tk.W) 

        # --- Setting column sizes and behavior ---
        self.item_tree.column("Name", width=150, minwidth=100, stretch=tk.YES)
        self.item_tree.column("Quantity", width=80, minwidth=60, stretch=tk.NO)
        self.item_tree.column("Price", width=80, minwidth=60, stretch=tk.NO)
        self.item_tree.column("Stock Value", width=90, minwidth=70, stretch=tk.NO)
        self.item_tree.column("ID", width=200, minwidth=150, stretch=tk.YES)

        # Place the Treeview in its frame, accounting for the new header labels
        self.item_tree.grid(row=start_row, column=0, sticky="nsew", padx=5, pady=5)

        # --- Adding a Scrollbar for the Treeview ---
        scrollbar = ttk.Scrollbar(frame_to_fill, orient="vertical", command=self.item_tree.yview)
        self.item_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=start_row, column=1, sticky="ns", padx=(0,5), pady=5)

        # --- Making items selectable ---
        self.item_tree.bind("<<TreeviewSelect>>", self._on_item_select)

    def _update_autocomplete_suggestions(self, event=None):
        """
        Updates the suggestions in all comboboxes (delete_by_name, item_search, update_qty_name)
        based on user input. This function is called every time a key is released in a combobox.
        """
        all_item_names = [details["name"] for details in self.inventory_manager.get_all_items().values()]
        
        # --- For Delete by Name Combobox ---
        typed_text_delete = self.delete_by_name_entry_var.get().strip().lower()
        if typed_text_delete:
            filtered_names_delete = sorted([name for name in all_item_names if name.lower().startswith(typed_text_delete)])
        else:
            filtered_names_delete = sorted(all_item_names)
        self.delete_by_name_combobox['values'] = filtered_names_delete
        if filtered_names_delete and len(typed_text_delete) > 0:
             self.delete_by_name_combobox.event_generate('<Button-1>')
        elif not typed_text_delete:
            self.delete_by_name_combobox.event_generate('<Button-1>')

        # --- For Item Search Combobox ---
        typed_text_search = self.item_search_entry_var.get().strip().lower()
        if typed_text_search:
            filtered_names_search = sorted([name for name in all_item_names if name.lower().startswith(typed_text_search)])
        else:
            filtered_names_search = sorted(all_item_names)
        self.item_search_combobox['values'] = filtered_names_search
        if filtered_names_search and len(typed_text_search) > 0:
            self.item_search_combobox.event_generate('<Button-1>')
        elif not typed_text_search:
            self.item_search_combobox.event_generate('<Button-1>')

        # --- For Update Quantity by Name Combobox ---
        typed_text_update_qty = self.update_qty_name_var.get().strip().lower()
        if typed_text_update_qty:
            filtered_names_update_qty = sorted([name for name in all_item_names if name.lower().startswith(typed_text_update_qty)])
        else:
            filtered_names_update_qty = sorted(all_item_names)
        self.update_qty_name_combobox['values'] = filtered_names_update_qty
        if filtered_names_update_qty and len(typed_text_update_qty) > 0:
            self.update_qty_name_combobox.event_generate('<Button-1>')
        elif not typed_text_update_qty:
            self.update_qty_name_combobox.event_generate('<Button-1>')


    def _on_item_select(self, event):
        """
        This function is triggered automatically when you click on an item in the inventory list (Treeview).
        Its job is to take the details of the selected item and fill them into the
        input boxes on the left side of the app.
        """
        selected_item_id_in_tree = self.item_tree.focus()
        
        if selected_item_id_in_tree:
            values_from_tree = self.item_tree.item(selected_item_id_in_tree, 'values')
            
            actual_item_id = values_from_tree[4] 
            
            # --- Populate the main input fields (Add/Update/Delete Item section) ---
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, values_from_tree[0])

            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, values_from_tree[1])

            price_str_from_tree = values_from_tree[2].replace("₹", "")
            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, price_str_from_tree)

            # Populate the delete by name combobox for convenience
            self.delete_by_name_entry_var.set(values_from_tree[0])
            self._update_autocomplete_suggestions() 

            # Populate the item search combobox for convenience
            self.item_search_entry_var.set(values_from_tree[0])
            self.stock_value_display_label.config(text="")

            # Populate the update quantity by name combobox and quantity entry for convenience
            self.update_qty_name_var.set(values_from_tree[0])
            self.new_quantity_entry.delete(0, tk.END)
            self.new_quantity_entry.insert(0, values_from_tree[1])


    def _add_item_gui(self):
        """Handles the 'Add Item' button click."""
        name = self.name_entry.get()
        quantity_str = self.quantity_entry.get()
        price_str = self.price_entry.get()

        try:
            quantity = int(quantity_str)
            price = float(price_str)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a whole number for Total Quantity and a number (e.g., 10.50) for Unit Price.")
            return

        result_message = self.inventory_manager.add_item(name, quantity, price)
        messagebox.showinfo("Add Item Status", result_message)
        
        if "Success" in result_message:
            self.name_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
            self._update_item_list()

    def _delete_item_by_name_gui(self):
        """
        Handles the 'Delete Item' button click in the "Delete Item by Name" section.
        Deletes an item based on the name provided in the combobox input field.
        """
        item_name_to_delete = self.delete_by_name_entry_var.get()
        if not item_name_to_delete.strip():
            messagebox.showwarning("Input Missing", "Please enter an Item Name to delete.")
            return

        confirm_delete = messagebox.askyesno("Confirm Deletion",
                                            f"Are you absolutely sure you want to delete the item named:\n'{item_name_to_delete}'?\nThis cannot be undone!")
        
        if confirm_delete:
            result_message = self.inventory_manager.delete_item_by_name(item_name_to_delete)
            messagebox.showinfo("Delete Item Status", result_message)
            
            if "Success" in result_message:
                self._update_item_list()
                self.delete_by_name_entry_var.set("")
                self.name_entry.delete(0, tk.END)
                self.quantity_entry.delete(0, tk.END)
                self.price_entry.delete(0, tk.END)
                self.stock_value_display_label.config(text="")
                self.update_qty_name_var.set("")
                self.new_quantity_entry.delete(0, tk.END)


    def _check_stock_value_gui(self):
        """
        Handles the 'Check Stock Value' button click.
        Retrieves and displays the stock value for the item name entered in the search box.
        """
        search_name = self.item_search_entry_var.get().strip()
        if not search_name:
            self.stock_value_display_label.config(text="Please enter an Item Name to search.")
            return

        found_item_data = self.inventory_manager.get_item_by_name(search_name)
        
        if found_item_data:
            found_item_id, found_item_details = found_item_data
            display_text = (
                f"Item Name: {found_item_details['name']}\n"
                f"Current Qty: {found_item_details['quantity']}\n"
                f"Unit Price: ₹{found_item_details['price']:.2f}\n"
                f"Stock Value: ₹{found_item_details['stock_value']:.2f}"
            )
            self.stock_value_display_label.config(text=display_text)
        else:
            self.stock_value_display_label.config(text=f"Item '{search_name}' not found in inventory.")

    def _update_quantity_by_name_gui(self):
        """
        Handles the 'Update Quantity' button click in the new section.
        Updates the quantity for a specified item name.
        """
        item_name_to_update = self.update_qty_name_var.get().strip()
        new_quantity_str = self.new_quantity_entry.get().strip()

        if not item_name_to_update:
            messagebox.showwarning("Input Missing", "Please select an Item Name to update quantity.")
            return
        if not new_quantity_str:
            messagebox.showwarning("Input Missing", "Please enter the New Quantity.")
            return

        try:
            new_quantity = int(new_quantity_str)
            if new_quantity < 0:
                messagebox.showerror("Input Error", "New Quantity cannot be negative.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "New Quantity must be a whole number.")
            return

        found_item_data = self.inventory_manager.get_item_by_name(item_name_to_update)
        if not found_item_data:
            messagebox.showerror("Update Error", f"Item '{item_name_to_update}' not found in inventory.")
            return
        
        found_item_id, found_item_details = found_item_data

        result_message = self.inventory_manager.update_item(found_item_id, new_quantity=new_quantity, new_price=None)
        messagebox.showinfo("Update Quantity Status", result_message)

        if "Success" in result_message:
            self._update_item_list()
            self.update_qty_name_var.set("")
            self.new_quantity_entry.delete(0, tk.END)
            self.stock_value_display_label.config(text="")


    def _update_item_list(self):
        
        for item_in_tree in self.item_tree.get_children():
            self.item_tree.delete(item_in_tree)

        all_current_items = self.inventory_manager.get_all_items()
        
        for item_unique_id, item_details in all_current_items.items():
            self.item_tree.insert("", tk.END, iid=item_unique_id,
                                  values=(item_details["name"],
                                          item_details["quantity"],
                                          f"₹{item_details['price']:.2f}",
                                          f"₹{item_details['stock_value']:.2f}",
                                          item_unique_id))
        
        self._update_autocomplete_suggestions()


if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()

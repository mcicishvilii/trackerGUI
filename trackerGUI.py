import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
import requests
import json

class TestScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Test Screen")

        # Set fullscreen
        # self.root.attributes('-fullscreen', True)
        self.root.bind("<F11>", self.toggle_fullscreen)  # Toggle fullscreen mode with F11
        self.root.bind("<Escape>", self.quit_fullscreen)  # Exit fullscreen with Escape

        # Use default ttk style
        self.style = ttk.Style()
        self.style.configure('TButton', padding=6)
        self.style.configure('TLabel', padding=6)
        self.style.configure('TEntry', padding=6)
        self.style.configure('TCombobox', padding=6)

        # Variables to hold form data
        self.order_number = tk.StringVar()
        self.brand_name = tk.StringVar()
        self.pickup_date = tk.StringVar()
        self.delivery_date = tk.StringVar()
        self.status = tk.StringVar()
        self.file_link = tk.StringVar()  # Variable for the file link

        # Create and place widgets
        self.create_widgets()

    def toggle_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))

    def quit_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', False)

    def create_widgets(self):
        # Create a frame for the entire layout
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky='nsew')

        # Configure grid for main frame
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)

        # Top-left frame (for current functionality)
        top_left_frame = ttk.Frame(main_frame, relief="solid", borderwidth=1)
        top_left_frame.grid(row=0, column=0, sticky='nsew')

        # Bottom-left frame (empty or for future use)
        bottom_left_frame = ttk.Frame(main_frame, relief="solid", borderwidth=1)
        bottom_left_frame.grid(row=1, column=0, sticky='nsew')

        # Right frame (for displaying JSON data)
        self.right_frame = ttk.Frame(main_frame, relief="solid", borderwidth=1)
        self.right_frame.grid(row=0, column=1, rowspan=2, sticky='nsew')

        # Create and place widgets in the top-left frame
        ttk.Label(top_left_frame, text="Order Number").grid(row=0, column=0, pady=5, padx=5, sticky='w')
        ttk.Entry(top_left_frame, textvariable=self.order_number).grid(row=0, column=1, pady=5, padx=5, sticky='ew')

        ttk.Label(top_left_frame, text="Brand Name").grid(row=1, column=0, pady=5, padx=5, sticky='w')
        ttk.Entry(top_left_frame, textvariable=self.brand_name).grid(row=1, column=1, pady=5, padx=5, sticky='ew')

        ttk.Label(top_left_frame, text="Pickup Date").grid(row=2, column=0, pady=5, padx=5, sticky='w')
        self.pickup_date_picker = DateEntry(top_left_frame, textvariable=self.pickup_date, date_pattern='yyyy-mm-dd', width=17)
        self.pickup_date_picker.grid(row=2, column=1, pady=5, padx=5, sticky='ew')

        ttk.Label(top_left_frame, text="Delivery Date").grid(row=3, column=0, pady=5, padx=5, sticky='w')
        self.delivery_date_picker = DateEntry(top_left_frame, textvariable=self.delivery_date, date_pattern='yyyy-mm-dd', width=17)
        self.delivery_date_picker.grid(row=3, column=1, pady=5, padx=5, sticky='ew')

        ttk.Label(top_left_frame, text="Status").grid(row=4, column=0, pady=5, padx=5, sticky='w')
        self.status_combobox = ttk.Combobox(top_left_frame, textvariable=self.status, values=[
            "ვიღებთ", 
            "ავიღეთ", 
            "ჩავიდა ბულგარეთში", 
            "გამოვიდა ბულგარეთიდან", 
            "ბაჟდება", 
            "საწყობშია"
        ], state='readonly')
        self.status_combobox.grid(row=4, column=1, pady=5, padx=5, sticky='ew')

        ttk.Label(top_left_frame, text="File Link").grid(row=5, column=0, pady=5, padx=5, sticky='w')
        ttk.Entry(top_left_frame, textvariable=self.file_link).grid(row=5, column=1, pady=5, padx=5, sticky='ew')

        # Submit button
        ttk.Button(top_left_frame, text="Submit", command=self.submit_form).grid(row=6, columnspan=2, pady=10)

        # Status label
        self.status_label = ttk.Label(top_left_frame, text="")
        self.status_label.grid(row=7, columnspan=2, pady=10)

        # Create Treeview in the right frame
        self.tree = ttk.Treeview(self.right_frame, columns=("Edit", "Order Number", "Brand Name", "Pickup Date", "Delivery Date", "Status", "File Link", "Delete",), show="headings")
        self.tree.column("Edit", width=100, anchor="center")
        self.tree.column("Order Number", width=120, anchor="center")
        self.tree.column("Brand Name", width=120, anchor="center")
        self.tree.column("Pickup Date", width=120, anchor="center")
        self.tree.column("Delivery Date", width=120, anchor="center")
        self.tree.column("Status", width=100, anchor="center")
        self.tree.column("File Link", width=200, anchor="center")
        self.tree.column("Delete", width=100, anchor="center")


        # Add vertical scrollbar
        vsb = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        # Add horizontal scrollbar
        hsb = ttk.Scrollbar(self.right_frame, orient="horizontal", command=self.tree.xview)
        hsb.pack(side='bottom', fill='x')
        self.tree.configure(xscrollcommand=hsb.set)

        self.tree.pack(fill='both', expand=True)

        self.tree.bind("<Button-1>", self.on_tree_item_button_click)
        self.tree.bind("<Button-2>", self.on_tree_item_button_click)

        # Load data into Treeview
        self.load_data()


    def on_tree_item_button_click(self, event):
        # Identify which row was clicked
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)

        if row_id:
            # Check if the click was on the "Delete" or "Edit" column
            if col_id == '#7':  # Change #8 to the index of your delete column
                if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
                    self.delete_item(row_id)
            elif col_id == '#1':  # Change #7 to the index of your edit column
                self.edit_item(row_id)


    def load_data(self):
        try:
            response = requests.get('https://ladogudi.serv00.net/getItems.php')
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Clear existing data in the tree
                    for item in self.tree.get_children():
                        self.tree.delete(item)

                    # Insert new data into Treeview
                    for item in data:
                        self.tree.insert("", "end", iid=item["id"], values=(
                            "შეცვლა",
                            item["orderNumber"],
                            item["brandName"],
                            item["pickupDate"],
                            item["deliveryDate"],
                            item["status"],
                            item["fileLink"],
                            "წაშლა",
                        
                        ))
                except ValueError:
                    messagebox.showerror("Error", "Response is not in JSON format")
            else:
                messagebox.showerror("Error", "Failed to connect to the server")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    def delete_item(self, item_id):
        try:
            response = requests.post('https://ladogudi.serv00.net/deleteItem.php', json={'id': item_id})
            if response.status_code == 200:
                result = response.json()
                if 'message' in result and result['message'] == 'Item deleted successfully':
                    # Refresh the data
                    self.load_data()
                    self.status_label.config(text="Item deleted successfully!")
                else:
                    self.status_label.config(text="Failed to delete item")
            else:
                self.status_label.config(text="Failed to connect to the server")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def edit_item(self, item_id):
        item = self.tree.item(item_id)['values']
        # Populate form with selected item's data
        self.order_number.set(item[1])
        self.brand_name.set(item[2])
        self.pickup_date.set(item[3])
        self.delivery_date.set(item[4])
        self.status.set(item[5])
        self.file_link.set(item[6])

        # Store the id for the update operation
        self.current_edit_id = item_id
        self.status_label.config(text="Editing item...")


    def submit_form(self):
        try:
            order_number = self.order_number.get()
            brand_name = self.brand_name.get()
            pickup_date = self.pickup_date_picker.get_date()  # Get date directly from DateEntry widget
            delivery_date = self.delivery_date_picker.get_date()  # Get date directly from DateEntry widget
            status = self.status.get()
            file_link = self.file_link.get()  # Get the file link from the entry widget

            default_link = "https://drive.google.com/drive/folders/1OYlXQtdAVh-iK7ZWdmBKOAPzFSoVWTKm?usp=drive_link"
            file_link = file_link if file_link else default_link

            # Convert dates to string only if they are not empty
            pickup_date_str = pickup_date.strftime('%Y-%m-%d') if pickup_date else ""
            delivery_date_str = delivery_date.strftime('%Y-%m-%d') if delivery_date else ""

            # Prepare the data to send
            payload = {
                'orderNumber': order_number,
                'brandName': brand_name,
                'pickupDate': pickup_date_str, 
                'deliveryDate': delivery_date_str, 
                'status': status,
                'fileLink': file_link
            }

            if hasattr(self, 'current_edit_id') and self.current_edit_id:
                # Update the item
                payload['id'] = self.current_edit_id
                response = requests.post('https://ladogudi.serv00.net/updateItem.php', json=payload)
            else:
                # Insert new item
                response = requests.post('https://ladogudi.serv00.net/insertItem.php', json=payload)

            # Check the response
            if response.status_code == 200:
                self.status_label.config(text="Data submitted successfully!")
                self.load_data()  # Refresh data
            else:
                self.status_label.config(text="Failed to submit data")

            # Reset current_edit_id after submission
            self.current_edit_id = None

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TestScreen(root)
    root.mainloop()

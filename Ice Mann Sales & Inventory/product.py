import json

class Product:
    def __init__(self, name, price, current_stock):
        self.name = name
        self.price = price
        self.current_stock = current_stock
    
    def to_dict(self):
        return {"name":self.name, "price": self.price, "current_stock": self.current_stock}

class IceTracker:
    def __init__(self):
        self.inventory = {}
        self.revenue = 0

    def add_product(self, product):
        self.inventory[product.name] = product

    def display_inventory(self):
        for product_object in self.inventory.values():
            print(f"Product: {product_object.name} | Stock: {product_object.current_stock}")

    def process_sale(self, quantity, name):
        if name in self.inventory.keys():
            product = self.inventory[name]
            if quantity <= product.current_stock:
                product.current_stock -= quantity
                self.revenue += quantity * product.price
                print(f"Sold {quantity} of {name}")
                print(f"Revenue: ${self.revenue}")
            else:
                print("Not enough ice cubes!")
        else:
            print("Incorrect product name! Sample: 1kg ice cubes")

    def save_to_json(self, filename):
        serialized_products = []
        for i in self.inventory.values():
            serialized_products.append(i.to_dict())

        data_to_save = {"products": serialized_products, "total_revenue": self.revenue}

        with open("inventory.json", "w") as json_file:
            json.dump(data_to_save, json_file)

    def load_from_json(self, filename="inventory.json"):
        try:
            with open(filename, "r") as json_file:
                data = json.load(json_file)
                self.revenue = data["total_revenue"]
            for item in data["products"]:
                re_product = Product(item["name"], item["price"], item['current_stock'])
                self.add_product(re_product)
        except FileNotFoundError:
            print("No save file found. Starting with a fresh inventory.")


my_tracker = IceTracker()
my_tracker.load_from_json()

while True:
    print("\n--- ICE TRACKER MENU ---")
    print("1. View Inventory")
    print("2. Record a Sale")
    print("3. Add New Product")
    print("4. Exit")

    choice = int(input("Select an option: "))

    if choice == 1:
        my_tracker.display_inventory()
    elif choice == 2:
        quantity = int(input("Quantity: "))
        name = input("Name: ")
        my_tracker.process_sale(quantity, name)
    elif choice == 3:
        name = input("Enter product name: ")
        price = int(input("Enter price per unit: "))
        stock = int(input("Enter starting stock quantity: "))

        new_product = Product(name, price, stock)
        my_tracker.add_product(new_product)
    elif choice == 4:
        my_tracker.save_to_json("inventory.json")
        print("Goodbye!")
        break
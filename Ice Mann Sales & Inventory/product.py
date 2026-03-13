class Product:
    def __init__(self, name, price, current_stock):
        self.name = name
        self.price = price
        self.current_stock = current_stock
    
    def __str__(self):
        return f"Name: {self.name}, Price: ${self.price}, Stock: {self.current_stock}"

small_bag = Product("1kg ice cubes", 10, 20)
print(small_bag)

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
            if name == product.name:
                if quantity <= product.current_stock:
                    product.current_stock -= quantity
                    self.revenue = quantity * product.price
                    print(f"Sold {quantity} of {name}")
                    print(f"Revenue: ${self.revenue}")
                else:
                    print("Not enough ice cubes!")
        else:
            print("Incorrect product name! Sample: 1kg ice cubes")


my_tracker = IceTracker()
my_tracker.add_product(small_bag)
my_tracker.display_inventory()
my_tracker.process_sale(1, "1kg ice cubes")
my_tracker.display_inventory()

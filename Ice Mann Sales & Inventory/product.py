class Product:
    def __init__(self, name, price, current_stock):
        self.name = name
        self.price = price
        self.current_stock = current_stock
    
    def __str__(self):
        return f"{self.name} (${self.price})"

small_bag = Product("1kg ice cubes", 100, 20)
print(f"Name: {small_bag.name}")
print(f"Price: {small_bag.price}")
print(f"Current Stocks: {small_bag.current_stock}")

class IceTracker:
    def __init__(self):
        self.inventory = {}

    def add_product(self, product):
        self.inventory[product.name] = product

    def display_inventory(self):
        for product_object in self.inventory.values():
            print(f"Product: {product_object.name} | Stock: {product_object.current_stock}")

my_tracker = IceTracker()
my_tracker.add_product(small_bag)
print(my_tracker.inventory["1kg ice cubes"].price)
my_tracker.display_inventory()
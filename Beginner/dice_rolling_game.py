import random

while True:
    game = input("Roll the dice? (y/n): ").lower()

    if game == 'y':
        x = random.randint(1,6)
        y = random.randint(1,6)
        random_tuple = (x,y)
        print(random_tuple)
    elif game == 'n':
        print("Thanks for playing!")
        break
    else:
        print("Invalid choice!")

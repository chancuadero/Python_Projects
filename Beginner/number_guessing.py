import random

print("THE NUMBER GUESSING GAME!")
print("The game begins when you enter a lower and upper bound numbers")

low = int(input("Enter the lower Number: "))
high = int(input("Enter the highest Number: "))
count = 1

random_number = random.randint(low,high)
while count != high:
    guess = int(input("What's your guess? "))
    if guess > random_number:
        print(f"Guess {count}: {guess} -> Too high")
        count += 1
    elif guess < random_number:
        print(f"Guess {count}: {guess} -> Too low")
        count += 1
    else:
        print("Congratulations!")
        print(f"Total Guesses: {count}")
        break
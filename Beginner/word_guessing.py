import random

print("WORD GUESSING GAME!")
print("Guess a character in a preselected word")
words = ["computer", "chocolate", "house", "car", "lights", "holidays"]
list = []

word = random.choice(words)
length_word = len(word)
limit = length_word + 2

while limit != 0:
        print(f"The word consists of {length_word} letters")
        print(f"You only have {limit} guess to try")
        guess = input("Guess a character: ")
        if (guess in word and guess not in list):
            list.append(guess)
        else:
            print("Incorrect!")
        print(*list)
        limit -= 1
        if len(list) == length_word:
             break
print(f"The word is {word}")
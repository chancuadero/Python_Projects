import random

name = input("What's your name? ")
print(f"Hi {name}! Welcome to the Hangman Game!")
print("Guess a character from a randomly generated secret word.")
print("All letters of the word are to be guessed before all the chances are over.")

words = ["christmas", "vacation", "country", "joyful", "exciting"]
my_list = []
positions = []

word = random.choice(words)
length_word = len(word)
limit = length_word + 2
counter = 0

#appending * on the list based on the length of the secret word
for x in range(length_word):
    my_list.append("*")

while counter < length_word:
    print(f"The secret word consists of {length_word} letters")
    print(f"You only have {limit} guess to try")
    guess = input("What's your guess? ")
    counter += 1
    limit -= 1

    if guess not in word:
        print("Not in the secret word. Try again!")
    else:
        for i in range(length_word):
            if word[i] == guess:
                index_value = i + 1
                positions.append(index_value) #appending the index of letter guessed by the user
                my_list[i] = guess
        print(f"{guess} is in position {", ".join(map(str,positions))} of the secret letter")
        positions.clear() #removing contents on the list(positions)
        print(*my_list)
        
    #check if the list is the same as the guess word and stop the game
    if "".join(my_list) == word:
        print(f"Congratulations, {name}! You've got it right!")
        break
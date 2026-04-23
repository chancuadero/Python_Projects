#Rock-Paper-Scissors Game
#The user gets the first chance to pick the option between rock, paper, and scissors.
#After the computer select from the remaining two choices(randomly), the winnder is decided as per the rules.
import random


print("Winning rules of the game ROCK PAPER SCISSORS are:")
print("Rock vs paper -> paper wins")
print("Rock vs scissors -> rock wins")
print("Paper vs scissors -> scissor wins")

choices_dict = {1: "Rock", 2:"Paper", 3:"Scissors"}
play = "Y"
user_choice = ""
comp_choice = ""

#function that returns the random number with its corresponding value in the dictionary
def computer():
    global comp_choice
    comp_num = random.randint(1,3)
    if comp_num in choices_dict:
        comp_choice = choices_dict[comp_num]
    return comp_choice

#function that returns the converted value of the user's input based on its corressponding value in the dictionary
def game():
    global user_choice
    print("\nEnter your choice")
    for key, value in choices_dict.items():
        print(f"{key} - {value}")
    choice = int(input("Enter your choice: "))
    while choice > 3:
         choice = int(input("Enter your choice: "))
    if choice in choices_dict:
        user_choice = choices_dict[choice]
    return user_choice

#accepts two parameters based on the global variables (user_choice, comp_choice) and evaluates the values based on the set conditions
def check(user, comp):
    if user == "Rock" and comp == "Paper":
        print("---Computer Wins!---")
    elif user == "Rock" and comp =="Scissors":
        print("---User Wins!---")
    elif user == "Paper" and comp == "Scissors":
        print("---Computer Wins!---")
    elif user == "Scissors" and comp == "Paper":
        print("---User Wins!---")
    elif user == "Scissors" and comp == "Rock":
         print("---Computer Wins!---")
    else:
        print("---User Wins!---")

while play == "Y":
    game()
    print(f"User choice is: {user_choice}")
    print("Now it's Computer's Turn...")
    computer()
    if comp_choice == user_choice:
        computer()
    print(f"Computer choice is: {comp_choice}")
    print(f"{user_choice} vs {comp_choice}")
    check(user_choice, comp_choice)
    play = input("Do you want to play again? (Y/N) ")

print("Thanks for playing!")
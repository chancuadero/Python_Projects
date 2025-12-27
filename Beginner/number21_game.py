"""
1. The player can choose to start first or second.
2. The list of numbers is shown before the player takes his turn so that
it becomes convenient.
3. If consecutive numbers are not given in input then the player is 
automatically disqualified.
4. The player loses if he gets the chance to call 21 and wins otherwise.
"""

start = input("Do you wish to start the game? (Y/N)")
digits = []
player = "F" #variable player has a default value of F

#To identify if the human player won or lose in the game
def result(r):
    if r == "won":
        print("Congratulations! You've won!")
        exit()
    elif r == "lose":
        print("Better luck next time! Computer has won the game!")
        exit()

#Create a function for computer player where it appends 3 consecutive values in the list
def computer():
    counter = 0
    #if list is empty, it appends 1 on the first index
    if not digits:
        digits.append(1)
    #if the list is not empty, the value depends on the last digit on the last and adds 1 to it.
    else:
        while counter < 3:
            input = digits[-1] + 1
            #if the input is equal to 20, it calls the result function with a lose argument
            if input == 20:
                result("lose")
            digits.append(input)
            counter += 1
    print(digits)


def disqualified():
    print("You've been disqualified!")
    exit()   


def human():
    num = int(input("How many numbers do you wish to enter?"))
    print("Enter your values")
    #a loop based on the value given by the player
    for x in range(num):
        value = int(input())
        #checks if the list is empty, then if the given value is not equal to 1 then calls the disqualified function
        if not digits:
            if value != 1:
                disqualified()
        #if list is not empty, then if the difference of given value and last digit from the list is not equal to 1
        # calls the disqualified function if difference is not equal to 1 and if value is 20, it calls result function 
        else:
            if (value - int(digits[-1])) != 1:
                disqualified()
            elif value == 20:
                result("won")
        digits.append(value)
    print(digits)



if start == "Y":
    print("Enter 'F' to take the first chance.")
    print("Enter 'S to take the second chance.")
    player = input()
else:
    print("Just come back when you're ready!")
    exit()

#while the length of the list is not equal to 21, the loop continues
while len(digits) != 21:
    if player == "S":
        computer()
        human()
    else:
        human()
        computer()
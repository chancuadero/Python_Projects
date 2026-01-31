"""
Rules of the game
Two players play the game against each other; let's assume Player 1 and Player 2.

Player 1 plays first by setting a multi-digit number.
Player 2 now tries his first attempt at guessing the number.
If Player 2 succeeds in his first attempt (despite odds which are highly unlikely) he wins the game and is crowned Mastermind! 
If not, then Player 1 hints by revealing which digits or numbers Player 2 got correct.
The game continues till Player 2 eventually is able to guess the number entirely.
"""
import random
set_num = random.randint(1,10000)

list_set_num = list(map(int,str(set_num)))
check_num = []
count = 0
tries = 0
print(list_set_num)

for x in range(len(list_set_num)):
    check_num.append('x')

while count < len(list_set_num):
    count = 0
    guess_num = input("Player 2, guess the numbers: ")
    list_guess_num = list(map(int,guess_num))
    if len(list_set_num) < len(list_guess_num):
        print("Your guess is more than the set numbers")
    else:
        for i in range(len(list_guess_num)):
            if list_set_num[i] == list_guess_num[i]:
                check_num[i] = list_set_num[i]
                count += 1
        if list_guess_num[i] == check_num[i]:
            break
        else:
            print(f"Not quite the number. You've guessed {count} digits correctly.")
            print(*check_num)
    tries += 1
print('You\'ve become a Mastermind!')
print(f"It took you only {tries} tries.")

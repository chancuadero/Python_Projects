started = False
def game(choice):
    global started
    if choice == 'help':
        print("""
start - to start the car
stop - to stop the car
quit - to exit
        """)
    elif choice == 'start':
        if started:
            print("Car is already started!")
        else:
            started = True
            print("Car started...Ready to go!")
    elif choice == 'stop':
        if not started:
            print("Car already stopped!")
        else:
            started = False
            print("Car stopped.")
    elif choice == 'quit':
        exit()
    else:
        print("sorry, I don't understand...")

while True:
    choice = input().lower()
    game(choice)

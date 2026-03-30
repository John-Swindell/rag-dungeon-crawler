# John Swindell

# dict defining all rooms and items
rooms = {
    'Cell': {'East': 'Mess hall', 'item': 'no items'},
    'Mess hall': {'West': 'Cell', 'North': 'Security office', 'South': 'Showers', 'East': 'Generator room', 'item': 'gas tank'},
    'Showers': {'North': 'Mess hall', 'East': 'Janitor’s closet', 'item': 'tarp'},
    'Janitor’s closet': {'West': 'Showers', 'item': 'rope'},
    'Security office': {'South': 'Mess hall', 'East': 'Temperature control room', 'item': 'computer'},
    'Temperature control room': {'West': 'Security office', 'item': 'valves'},
    'Generator room': {'West': 'Mess hall', 'North': 'Warden Roy’s office', 'item': 'engine'},
    'Warden Roy’s office': {'South': 'Generator room', 'item': 'no items'}
}

state = 'Cell'


# function to get new state based on direction
def get_new_state(state, direction):
    direction = direction.capitalize()
    if direction in rooms[state]:
        return rooms[state][direction]
    else:
        return state


# function for item interaction in the current state
def get_item(state):
    item = rooms[state].get('item', 'no items')
    if item != 'no items':
        print(f'You see a {item}')
        while True:
            pick_up = input('Do you want to pick up the item? (Yes/No): ').strip().lower()
            if pick_up == 'yes':
                if item not in inventory:
                    inventory.append(item)
                    rooms[state]['item'] = 'no items'
                    print(f'{item} added to inventory.')
                else:
                    print('You already have this item.')
                break
            elif pick_up == 'no':
                print(f'You did not pick up the {item}.')
                break
            else:
                print('Invalid input. Please enter Yes or No.')
    else:
        print('There is nothing here.')


# function to show game instructions
def show_instructions():
    print('Prison Escape Adventure Game')
    print('Collect 6 items to escape the prison, or be caught by Warden Roy.')
    print('Move commands: go South, go North, go East, go West')
    print('To pick up an item, you will be prompted when you see it.')


# initialize inventory and start the game
inventory = []
show_instructions()

while True:
    print('---------------------------')
    print('You are in the', state)
    print('Inventory:', inventory)

    # check if the current room is warden office
    if state == 'Warden Roy’s office':
        if len(inventory) == 6:
            print('Congratulations! You have collected all items and successfully escaped!')
        else:
            print('Warden Roy has caught you! Game over!')
        break  # Exit the game loop

    # item in the current room
    get_item(state)

    # prompt for movement
    direction = input('Enter your move: ').strip()
    if direction.startswith('go '):
        move_direction = direction[3:].strip()
        new_state = get_new_state(state, move_direction)
        if new_state == state:
            print('You cannot go that way!')
        else:
            state = new_state
    else:
        print('Invalid input! Please enter a move command like "go North"')

from random import randint
from copy import deepcopy
import itertools


class Box(object):
    '''class for a particular box instance'''

    def __init__(self, number):
        '''constructor for box class'''
        self.location = "source"
        self.box_number = number

    def __repr__(self):
        '''this is output on call to print'''
        return "b" + str(self.box_number)


class Truck(object):
    '''class for a particular truck instance'''

    def __init__(self, number):
        '''constructor for truck class'''
        self.boxes = []
        self.location = "source"
        self.truck_number = number

    def __repr__(self):
        '''this is output on call to print'''
        return "t" + str(self.truck_number)


class World(object):
    '''class for a particular instantiation of box world'''

    def __init__(self, number=1):
        '''class constructor'''
        self.MAXBOXES = 5
        self.MAXTRUCKS = 3
        self.state_number = number
        self.boxes = self.get_boxes()
        self.trucks = self.get_trucks()
        self.trucks_dictionary = {}
        self.make_dictionary()

    def get_boxes(self, number=False):
        '''initializes boxes specified by number or random'''
        if not number:
            number = randint(1, self.MAXBOXES)
        boxes = []
        for i in range(number):
            boxes += [Box(i + 1)]
        return boxes

    def make_dictionary(self):
        '''makes truck dictionary'''
        trucks_dictionary = self.trucks_dictionary
        for truck in self.trucks:
            trucks_dictionary[truck] = [truck.boxes, truck.location]

    def get_trucks(self, number=False):
        '''initializes trucks specified by number of random'''
        if not number:
            number = randint(1, self.MAXTRUCKS)
            if number > len(self.boxes):
                number = len(self.boxes)
        trucks = []
        for i in range(number):
            trucks += [Truck(i + 1)]
        return trucks

    def __repr__(self):
        '''this is output on call to print'''
        output_string = ""
        for box in self.boxes:
            output_string += "b" + str(box.box_number)
            output_string += box.location + "^"
        for truck in self.trucks:
            output_string += "t" + str(truck.truck_number)
            output_string += str(truck.boxes)
            output_string += truck.location + "^"
        return output_string[:-1]

    def take_action(self, action="Noop", truck=False, box=False):
        '''executes specified action'''
        self.state_number += 1
        if action == "Noop":
            return self
        if action == "load":
            if not box:
                print( "there is no box to load")
                return self
            if not truck:


                print("there is no truck to load on")
                return self
            if not box.location == truck.location:


                print( "you have to move to location of box first")
                return self
            if box in truck.boxes:
                return self
            else:
                truck.boxes.append(box)
        if action == "unload":
            if not box:


                print("there is no box to load")
                return self
            if not truck:


                print( "there is no truck to load on")
                return self
            if box not in truck.boxes:


                print( "box has to be on the truck")
                return self
            else:
                truck.boxes.remove(box)
                box.location = truck.location
        if action == "move":
            if not truck:
                print
                "there is nothing to move"
                return self
            else:
                if truck.location == "source":
                    truck.location = "destination"
                    for box in truck.boxes:
                        box.location = "destination"
                else:
                    truck.location = "source"
                    for box in truck.boxes:
                        box.location = "source"
        return self


def get_RDN_facts(world_state, action="Noop", truck=False, box=False):
    '''generates facts,pos,neg'''
    dicti = world_state.trucks_dictionary
    all_boxes = world_state.boxes
    truck_boxes = []
    for truc in dicti:
        value = dicti[truc]
        boxes = value[0]
        truck_boxes += boxes
        location = value[1]
        # print truck,boxes,location
        print ("tIn(t" + str(truc.truck_number) + "," + str(truc.location) + ",s" + str(world_state.state_number) + ").")
        for box in boxes:
            print ("bIn(b" + str(box.box_number) + ",t" + str(truc.truck_number) + ",s" + str(world_state.state_number) + ").")
    boxes_not_on_trucks = [b for b in all_boxes if b not in truck_boxes]
    for b in boxes_not_on_trucks:
        print( "bIn(b" + str(b.box_number) + "," + b.location + ",s" + str(world_state.state_number) + ").")


def goal_state(state):
    '''returns True if goal state attained'''
    for box in state.boxes:
        if box.location == "destination":
            return True
    return False


number_of_trajectories = 1
actions = ["move", "load", "unload"]
Values = {}


def update_values(state_sequence):
    '''updates the values by back propogation
       of the state sequence
    '''
    discount_factor = 0.95
    goal_state_value = 10
    goal_state_string = str(state_sequence[-1])
    state_sequence_without_goal_in_reverse = state_sequence[:-1][::-1]
    length_of_state_sequence_without_goal_in_reverse = len(state_sequence_without_goal_in_reverse)
    for i in range(length_of_state_sequence_without_goal_in_reverse):
        # print state_sequence_without_goal_in_reverse[i]
        state_string = str(state_sequence_without_goal_in_reverse[i][0])
        action_string = state_sequence_without_goal_in_reverse[i][1]
        # print "reached here"
        Values[state_string + "^" + action_string] = (discount_factor ** (i + 1)) * goal_state_value
    Values[goal_state_string] = goal_state_value


def neg_action_generator(action_list,boxes_list,trucks_list,current_action):

    all_neg_actions = []
    trucks_blocks_combo = [(x,y) for x in boxes_list for y in trucks_list]
    print ("trucks_blocks_combo------>",trucks_blocks_combo)
    for each_action in action_list:
        for each_combo in trucks_blocks_combo:
            all_neg_actions.append(each_action+","+str(each_combo[1])+","+str(each_combo[0]))
    print ("all_neg_actions---->",all_neg_actions)
    all_neg_actions.remove(current_action)

    return all_neg_actions





for trajectory in range(number_of_trajectories):
    state = World()
    i = 0
    state_sequence = []
    while not goal_state(state):
        print ("=" * 40)
        print (state.trucks)
        print (state.boxes)
        random_truck = state.trucks[randint(0, len(state.trucks) - 1)]
        random_box = state.boxes[randint(0, len(state.boxes) - 1)]
        random_action = actions[randint(0, len(actions) - 1)]
        state_copy = deepcopy(state)
        get_RDN_facts(state_copy, random_action, random_truck, random_box)
        print ("action: ",random_action,"truck: ",random_truck,"box: ",random_box)


        current_action = random_action + "," + str(random_truck) + "," + str(random_box)
        state_sequence.append((state_copy, random_action + "," + str(random_truck) + "," + str(random_box),neg_action_generator(actions,state.boxes,state.trucks,current_action)))
        state = state.take_action(random_action, random_truck, random_box)
        print ("-" * 40)
        if random_action == "move":
            print ("move(t" + str(random_truck.truck_number) + "," + str(random_truck.location) + ",s" + str(
                state_copy.state_number) + ").")
        elif random_action == "load":
            print ("load(b" + str(random_box.box_number) + ",t" + str(random_truck.truck_number) + ",s" + str(
                state_copy.state_number) + ").")
        else:
            print ("unload(b" + str(random_box.box_number) + ",t" + str(random_truck.truck_number) + ",s" + str(
                state_copy.state_number) + ").")

        # print "-"*40
        i += 1


    state_sequence.append(deepcopy(state))
    print ("state_sequence---------->",state_sequence)
    update_values(state_sequence)

print ("="*40)
for state in Values:
    print (state)
    print (Values[state])
    print ("-"*40)

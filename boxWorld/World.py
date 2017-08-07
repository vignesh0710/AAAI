from random import randint
from copy import deepcopy
import itertools
from subprocess import Popen
from os import system,waitpid,listdir

class Box(object):
    '''class for a particular box instance'''

    def __init__(self,number):
        '''constructor for box class'''
        self.location = "source"
        self.box_number = number
        
    def __repr__(self):
        '''this is output on call to print'''
        return "b"+str(self.box_number)

class Truck(object):
    '''class for a particular truck instance'''

    def __init__(self,number):
        '''constructor for truck class'''
        self.boxes = []
        self.location = "source"
        self.truck_number = number

    def __repr__(self):
        '''this is output on call to print'''
        return "t"+str(self.truck_number)
    
class World(object):
    '''class for a particular instantiation of box world'''
    
    def __init__(self,number=1):
        '''class constructor'''
        self.MAXBOXES = 5
        self.MAXTRUCKS = 3
        self.state_number = number
        self.boxes = self.get_boxes()
        self.trucks = self.get_trucks()
        self.trucks_dictionary = {}
        self.make_dictionary()

    def get_boxes(self,number=False):
        '''initializes boxes specified by number or random'''
        if not number:
            number = randint(1,self.MAXBOXES)
        boxes = []
        for i in range(number):
            boxes += [Box(i+1)]
        return boxes

    def make_dictionary(self):
        '''makes truck dictionary'''
        trucks_dictionary = self.trucks_dictionary
        for truck in self.trucks:
            trucks_dictionary[truck] = [truck.boxes,truck.location]
        
    def get_trucks(self,number=False):
        '''initializes trucks specified by number of random'''
        if not number:
            number = randint(1,self.MAXTRUCKS)
            if number > len(self.boxes):
                number = len(self.boxes)
        trucks = []
        for i in range(number):
            trucks += [Truck(i+1)]
        return trucks

    def __repr__(self):
        '''this is output on call to print'''
        output_string = ""
        for box in self.boxes:
            output_string += "b"+str(box.box_number)
            output_string += box.location+"^"
        for truck in self.trucks:
            output_string += "t"+str(truck.truck_number)
            output_string += str(truck.boxes)
            output_string += truck.location+"^"
        return output_string[:-1]
    
    
    def take_action(self,action="Noop",truck=False,box=False):
        '''executes specified action'''
        self.state_number += 1
        if action == "Noop":
            return self
        if action == "load":
            if not box:
                print "there is no box to load"
                return self
            if not truck:
                print "there is no truck to load on"
                return self
            if not box.location == truck.location:
                print "you have to move to location of box first"
                return self
            if box in truck.boxes:
                return self
            else:
                truck.boxes.append(box)
        if action == "unload":
            if not box:
                print "there is no box to load"
                return self
            if not truck:
                print "there is no truck to load on"
                return self
            if box not in truck.boxes:
                print "box has to be on the truck"
                return self
            else:
                truck.boxes.remove(box)
                box.location = truck.location
        if action == "move":
            if not truck:
                print "there is nothing to move"
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

def get_RDN_facts(world_state):
    '''generates facts,pos,neg'''
    dicti = world_state.trucks_dictionary
    all_boxes = world_state.boxes
    truck_boxes = []
    facts = []
    for truc in dicti:
        value = dicti[truc]
        boxes = value[0]
        truck_boxes += boxes
        location = value[1]
        #print truck,boxes,location
        facts.append("tIn(t"+str(truc.truck_number)+","+str(truc.location)+",s"+str(world_state.state_number)+").")
        for box in boxes:
            facts.append("bOn(b"+str(box.box_number)+",t"+str(truc.truck_number)+",s"+str(world_state.state_number)+").")
    boxes_not_on_trucks = [b for b in all_boxes if b not in truck_boxes]
    for b in boxes_not_on_trucks:
        facts.append("bIn(b"+str(b.box_number)+","+b.location+",s"+str(world_state.state_number)+").")
    return facts

def goal_state(state):
    '''returns True if goal state attained'''
    for box in state.boxes:
        if box.location == "destination":
            return True
    return False

number_of_trajectories = 10
actions = ["move","load","unload"]
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
        #print state_sequence_without_goal_in_reverse[i]
        state_string = str(state_sequence_without_goal_in_reverse[i][0])
        action_string = state_sequence_without_goal_in_reverse[i][1]
        #print "reached here"
        Values[state_string+"^"+action_string] = (discount_factor**(i+1))*goal_state_value
    Values[goal_state_string] = goal_state_value

def neg_action_generator(action_list,boxes_list,trucks_list,state_number,current_action=False):
    '''returns all negative actions'''
    all_neg_actions = []
    trucks_blocks_combo = [(x,y) for x in boxes_list for y in trucks_list]
    #print ("trucks_blocks_combo------>",trucks_blocks_combo)
    #print ("pos: "+current_action)
    for each_action in action_list:
        for each_combo in trucks_blocks_combo:
            if each_action == "move":
                if each_action+"("+str(each_combo[1])+","+"source"+",s"+str(state_number)+")." not in all_neg_actions:
                    all_neg_actions.append(each_action+"("+str(each_combo[1])+","+"source"+",s"+str(state_number)+").")
                if each_action+"("+str(each_combo[1])+","+"destination"+",s"+str(state_number)+")." not in all_neg_actions:
                    all_neg_actions.append(each_action+"("+str(each_combo[1])+","+"destination"+",s"+str(state_number)+").")
            else:
                if each_action+"("+str(each_combo[1])+","+str(each_combo[0])+",s"+str(state_number)+")." not in all_neg_actions:
                    all_neg_actions.append(each_action+"("+str(each_combo[1])+","+str(each_combo[0])+",s"+str(state_number)+").")
    #print ("all_neg_actions---->",all_neg_actions)
    if current_action != False:     
        all_neg_actions.remove(current_action)

    return all_neg_actions

def write_facts(opText):
    '''writes facts to file'''
    with open("train/train_facts.txt", "a") as myfile:
        for i in range(len(opText)):
            myfile.write(opText[i]+'\n')

def write_pos_neg(positiveList,negativeList):
    '''writes positive and negative actions to file'''
    with open("train/train_pos.txt", "a") as myfile:
        for i in range(len(positiveList)):
            myfile.write(positiveList[i]+'\n')

    with open("train/train_neg.txt", "a") as myfile:
        for i in range(len(negativeList)):
            myfile.write(negativeList[i]+'\n')

def write_test_facts(opText):
    '''writes facts to file'''
    with open("test/test_facts.txt", "a") as myfile:
        for i in range(len(opText)):
            myfile.write(opText[i]+'\n')

def write_test_pos(positiveList):
    '''writes positive and negative actions to file'''
    with open("test/test_pos.txt", "a") as myfile:
        for i in range(len(positiveList)):
            myfile.write(positiveList[i]+'\n')


def call_process(call):
    '''spawns a process to execute a shell process'''
    process = Popen(call,shell=True)
    waitpid(process.pid,0)

def make_train_and_test_directory():
    '''makes the train directory'''
    call_process('mkdir train')
    call_process('cp train_bk.txt train')
    call_process('mkdir test')
    call_process('cp train_bk.txt test')
    call_process('mv test/train_bk.txt test/test_bk.txt')

def remove_files():
    '''removes files after each run'''
    call_process('rm train/train_facts.txt')
    call_process('rm train/train_pos.txt')
    call_process('rm train/train_neg.txt')

def perform_inference_and_choose(state,state_number,actions):
    '''returns action in the state with highest probability'''
    test_facts = get_RDN_facts(state)
    #print test_facts
    test_pos = neg_action_generator(actions,state.boxes,state.trucks,state.state_number)
    #print test_pos
    write_test_facts(test_facts)
    write_test_pos(test_pos)
    call_process('touch test/test_neg.txt')
    call_process('java -jar BoostSRL-v1-0.jar -i -test test -model train/models -target move,load,unload -aucJarPath . ')
    exit()

def construct_pos_best_action_for_learning(state_sequence):
    '''picks action with highest value'''
    print Values
    print state_sequence
    exit()

def construct_neg_action_for_learning(pos_action,state_sequence):
    '''constructs negative action as all actions except pos_action for each state'''
    pass # --> CONTINUE HERE TOMORROW

state_number = 1
pos_action  = []
for trajectory in range(number_of_trajectories):
    state = World(state_number)
    i = 0
    state_sequence = []
    while not goal_state(state):
        #print "="*40
        random_truck = state.trucks[randint(0,len(state.trucks)-1)]
        random_box = state.boxes[randint(0,len(state.boxes)-1)]
        state_copy = deepcopy(state)
        random_action = None        
        if "models" not in listdir("train"):
            random_action = actions[randint(0,len(actions)-1)]
        else:
            random_action_truck_and_box = perform_inference_and_choose(state_copy,state_number,actions)
        current_action = ""
        if random_action == "move":
            current_action += random_action+"("+str(random_truck)+","+random_truck.location+",s"+str(state_copy.state_number)+")."
        else:
            current_action += random_action+"("+str(random_truck)+","+str(random_box)+",s"+str(state_copy.state_number)+")."
        facts = get_RDN_facts(state_copy)
        #neg = neg_action_generator(actions,state_copy.boxes,state_copy.trucks,state_copy.state_number,current_action)
        if "train" not in listdir(".") or "test" not in listdir("."):
            make_train_and_test_directory()
        write_facts(facts)
        #write_pos_neg([current_action],neg)
        #print "facts: "+str(facts)
        #print "neg: "+str(neg)
        #print "action: ",random_action,"truck: ",random_truck,"box: ",random_box
        state_sequence.append((state_copy,random_action+","+str(random_truck)+","+str(random_box),state_number,deepcopy(state_copy)))
        state = state.take_action(random_action,random_truck,random_box)
        #print "-"*40
        '''
        if random_action == "move":
            print "move(t"+str(random_truck.truck_number)+","+str(random_truck.location)+",s"+str(state_copy.state_number)+")."
        elif random_action == "load":
            print "load(b"+str(random_box.box_number)+",t"+str(random_truck.truck_number)+",s"+str(state_copy.state_number)+")."
        else:
            print "unload(b"+str(random_box.box_number)+",t"+str(random_truck.truck_number)+",s"+str(state_copy.state_number)+")."
        '''
        #print "-"*40
        i += 1
    state_sequence.append(deepcopy(state))
    update_values(state_sequence)
    pos_actions += construct_pos_best_action_for_learning(state_sequence)
    neg_actions += construct_neg_action_for_learning(pos_action,state_sequence)
    state_number += len(state_sequence)
    if trajectory%5==0:
        raw_input("Continue learning?")
        call_process('rm -rf train/models')
        call_process('java -jar BoostSRL-v1-0.jar -l -train train -target move,load,unload')
        pos_action = []
        neg_actions = []
        remove_files()
'''
print "="*40
for state in Values:
    print state
    print Values[state]
    print "-"*40
'''

from random import randint
from copy import deepcopy
import itertools
from subprocess import Popen
from os import system,waitpid,listdir

'''
global structures defined at the top
'''

Values = {}
Count = {}
actions = ["move","load","unload"]

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
                box.location = str(truck)
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
                else:
                    truck.location = "source"
        return self

def get_facts(world_state):
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

def get_RDN_facts_pos_neg(state_sequence,action_list):#,boxes_list,trucks_list),state_number,current_action=False)
    '''returns facts for state'''
    facts,pos,neg = [],[],[]
    best_action_values = {}
    for key in Values:
        if Values[key] != 10:
            state = '^'.join(key.split('^')[:-1])
            action = key.split('^')[-1]
            action_value = Values[key]
            if state not in best_action_values.keys():
                best_action_values[state] = (action,action_value)
            else:
                if action_value > best_action_values[state][1]:
                    best_action_values[state] = (action,action_value)
    for state in state_sequence[:-1]:
        facts = get_facts(state[0]) #TODO += in the end
        state_string = str(state[0])
        state_id = "s"+str(state[2]) 
        best_action = best_action_values[state_string][0]
        action = best_action.split(',')[0]
        truck = best_action.split(',')[1]
        truck_location = None
        for fact in facts:
            if "tIn" in fact and truck in fact and state_id in fact:
                truck_location = fact.split(',')[1]
        box = best_action.split(',')[2]
        if action == "move":
            move_location = None
            if truck_location == "source":
                move_location = "destination"
            else:
                move_location = "source"
            pos += [action+"("+str(truck)+","+move_location+","+state_id+")."]
        else:
            pos += [action+"("+str(truck)+","+str(box)+","+state_id+")."]
        n = len(pos)-1
        neg += neg_action_generator(action_list,state[0].boxes,state[0].trucks,state[2],pos[n])
    return (facts,pos,neg)

def goal_state(state):
    '''returns True if goal state attained'''
    for box in state.boxes:
        if box.location == "destination":
            return True
    return False

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
        state_string = str(state_sequence_without_goal_in_reverse[i][0])
        action_string = state_sequence_without_goal_in_reverse[i][1]
        key = state_string+"^"+action_string
        if key in Count:
            Count[key] += 1
        else:
            Count[key] = 1
        new_value = (discount_factor**(i+1))*goal_state_value
        if key in Values:
            old_value = Values[key]
        else:
            old_value = 0
        Values[key] = old_value + (1/float(Count[key]))*(new_value-old_value)
    Values[goal_state_string] = goal_state_value

def neg_action_generator(action_list,boxes_list,trucks_list,state_number,current_action=False):
    '''returns all negative actions'''
    all_neg_actions = []
    trucks_blocks_combo = [(x,y) for x in boxes_list for y in trucks_list]
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

def remove_test_files():
    '''remove test files after inference'''
    call_process('rm test/*.db')
    call_process('rm test/test_facts.txt')
    call_process('rm test/test_pos.txt')
    call_process('rm test/test_neg.txt')

def read_file(filename):
    '''reads file lines'''
    if filename in listdir("test"):
        with open(filename) as file:
            return file.read().splitlines()
    else:
        return False

def get_max_prob_action(action_result_file):
    '''returns the action with max value for a state'''
    max_prob = 0
    best_action = False
    for result in action_result_file:
        prob = float(result.split(')')[1])
        if prob > max_prob:
            best_action = result.split(')')[0]+')'
            max_prob = prob
    return (best_action,max_prob)

def perform_inference_and_choose(state,state_number,actions,random=False):
    '''returns action in the state with highest probability'''
    acceptance_threshold = 0.5
    best_action = []
    if random:
        action = actions[randint(0,len(actions)-1)]
        box = state.boxes[randint(0,len(state.boxes)-1)]
        truck = state.trucks[randint(0,len(state.trucks)-1)]
        return (action,truck,box)
    test_facts = get_facts(state)
    test_pos = neg_action_generator(actions,state.boxes,state.trucks,state.state_number)
    write_test_facts(test_facts)
    write_test_pos(test_pos)
    call_process('touch test/test_neg.txt')
    call_process('java -jar BoostSRL-v1-0.jar -i -test test -model train/models -target move,load,unload -aucJarPath . ')
    for action in actions:
        action_result_file = read_file("test/results_"+action+".db")
        if not action_result_file:
            continue
        max_prob_action = get_max_prob_action(action_result_file)
        if max_prob_action[1] > acceptance_threshold:
            best_action.append(max_prob_action)
    if not best_action:
        action = actions[randint(0,len(actions)-1)]
        box = state.boxes[randint(0,len(state.boxes)-1)]
        truck = state.trucks[randint(0,len(state.trucks)-1)]
        return (action,truck,box)
    max_prob_for_all_actions = max([float(item[1]) for item in best_action])
    for item in best_action:
        if item[1] == max_prob_for_all_actions:
            action = item[0].split('(')[0]
            truck_id = item[0].split(',')[0].split('(')[1]
            box_id = False
            if 'b' in item[0]:
                box_id = item[0].split(',')[1].strip()
    print best_action
    truck = [item for item in state.trucks if str(item)==truck_id][0]
    if box_id:
        box = [item for item in state.boxes if str(item)==box_id][0]
    else:
        box = state.boxes[randint(0,len(state.boxes)-1)]
    remove_test_files()
    return (action,truck,box)

def main():
    state_number = 1
    pos_action  = []
    facts,pos,neg = [],[],[]
    max_tolerance = 20
    batch_size = 10
    burn_in_time = 100
    number_of_trajectories = 121
    if "train" not in listdir(".") or "test" not in listdir("."):
        make_train_and_test_directory()
    for trajectory in range(number_of_trajectories):
        max_tolerance_reached = False
        state = World(state_number)
        state_sequence = []
        while not goal_state(state):
            state_copy = deepcopy(state)
            if "models" not in listdir("train") or (trajectory+1) < burn_in_time:
                action_specification = perform_inference_and_choose(state,state_number,actions,random=True)
            else:
                if len(state_sequence) > max_tolerance and not max_tolerance_reached:
                    state_sequence = []
                    max_tolerance_reached = True
                if not max_tolerance_reached:
                    action_specification = perform_inference_and_choose(state,state_number,actions)
                else:
                    action_specification = perform_inference_and_choose(state,state_number,actions,random=True)
            random_action = action_specification[0]
            random_truck = action_specification[1]
            random_box = action_specification[2]
            state_sequence.append((state_copy,random_action+","+str(random_truck)+","+str(random_box),state_copy.state_number,deepcopy(state_copy)))
            state = state.take_action(random_action,random_truck,random_box)
        state_sequence.append(deepcopy(state))
        update_values(state_sequence)
        facts_pos_neg = get_RDN_facts_pos_neg(state_sequence,actions)
        facts += facts_pos_neg[0]
        pos += facts_pos_neg[1]
        neg += facts_pos_neg[2]
        state_number += len(state_sequence)
        if (trajectory+1)%batch_size == 0 and (trajectory+1) > burn_in_time:
            write_facts(facts)
            write_pos_neg(pos,neg)
            facts,pos,neg = [],[],[]
            call_process('rm -rf train/models')
            call_process('java -jar BoostSRL-v1-0.jar -l -train train -target move,load,unload')
            remove_files()

main()

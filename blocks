# Block world simulator

import re
from copy import deepcopy
from random import random
from itertools import permutations
import itertools

stateValues = {}
stateCounts = {}
def checkArguments(configList):
    '''
    :param configList:
    :return:
    '''

    argDict = {}
    tableArgList = []
    clearArgList = []
    onArgList = []
    # print ("error    ",configList)
    for eachState in configList:
        splitEachState = re.compile("(.*?)\s*\((.*?)\)")
        if splitEachState.match(eachState).group(1) == 'TABLE':
            tableArgList.append(splitEachState.match(eachState).group(2))
            argDict[splitEachState.match(eachState).group(1)] = tableArgList
        elif splitEachState.match(eachState).group(1) == 'CLEAR':
            clearArgList.append(splitEachState.match(eachState).group(2))
            argDict[splitEachState.match(eachState).group(1)] = clearArgList
        else:
            argTuple = [item for item in list(splitEachState.match(eachState).group(2)) if item != ","]
            onArgList.append(tuple(argTuple))
            argDict[splitEachState.match(eachState).group(1)] = onArgList

    # print(argDict)
    return argDict


def stackBlock(baseBlock, aboveBlock, configList):
    '''
   case1: Both the blocks are on table. The action is to put a block on the other block
    '''
    stateChange = False
    argDict = checkArguments(configList)
    if baseBlock in argDict['CLEAR'] and aboveBlock in argDict['CLEAR']:
        stateChange = True
        # print("previous state", configList)
        if ("ON" + "(" + baseBlock + "," + aboveBlock + ")") not in configList:
            configList.append("ON" + "(" + baseBlock + "," + aboveBlock + ")")
        configList.remove("CLEAR" + "(" + baseBlock + ")")

        if baseBlock in argDict['TABLE'] and aboveBlock in argDict['TABLE']:
            stateChange = True
            configList.remove("TABLE" + "(" + aboveBlock + ")")


        else:
            if aboveBlock in argDict['TABLE']:
                configList.remove("TABLE" + "(" + aboveBlock + ")")
            for eachTuple in argDict['ON']:
                if aboveBlock in eachTuple:
                    for item in eachTuple:
                        if item != aboveBlock:
                            stateChange = True
                            if ("CLEAR" + "(" + item + ")") not in configList:
                                configList.append("CLEAR" + "(" + item + ")")
                            # print("ON" + "(" + item + "," + aboveBlock + ")"
                            configList.remove("ON" + "(" + item + "," + aboveBlock + ")")

    # print(configList)
    return configList



def unstackBlock(baseBlock, aboveBlock, configList):

    argDict = checkArguments(configList)
    if 'ON' not in argDict.keys():
        stackBlock(baseBlock, aboveBlock, configList)



    elif (baseBlock, aboveBlock) in argDict['ON'] and aboveBlock in argDict['CLEAR']:
        # print("previous state", configList)
        configList.remove("ON" + "(" + baseBlock + "," + aboveBlock + ")")
        if ("CLEAR" + "(" + baseBlock + ")") not in configList:
            configList.append("CLEAR" + "(" + baseBlock + ")")
        if ("CLEAR" + "(" + aboveBlock + ")") not in configList:
            configList.append("CLEAR" + "(" + aboveBlock + ")")
        if ("TABLE" + "(" + aboveBlock + ")") not in configList:
            configList.append("TABLE" + "(" + aboveBlock + ")")
        stateChange = True
    # print(configList)
    return configList



def printTrajectory(trajectory):
    for state in trajectory:
        print(state)
        print(" " * 40 + "|")
        print(" " * 40 + "v")


def getValue(state):
    global stateValues
    keys = list(stateValues.keys())
    if state in keys:
        return stateValues[state]
    else:
        return 0


def incrementCount(state):
    global stateCounts
    if state in list(stateCounts.keys()):
        stateCounts[state] += 1
    else:
        stateCounts[state] = 1


def updateValue(state, value):
    global stateValues
    global stateCounts
    incrementCount(state)
    currentValue = getValue(state)
    updatedValue = currentValue + (1 / stateCounts[state]) * (value - currentValue)
    stateValues[state] = updatedValue


def updateValues(trajectory):
    n = len(trajectory)
    for i in range(n - 2, -1, -1):
        state = trajectory[i]
        transitionState = trajectory[i + 1]
        value = -1 + getValue(transitionState)
        updateValue(state, value)


def permutationsList(blocksList):
    permsBlockList = []
    for perms in permutations(blocksList, 2):
        permsBlockList.append(perms)

    return permsBlockList

def neg_actions_generator(perms,action_list,pos_action):


    neg_actions = []
    for each_perms in perms:
        for each_action in action_list:
            neg_actions.append(each_action+","+each_perms[0]+","+each_perms[1])
    #print("neg_actions----->", neg_actions)
    #print (pos_action)
    neg_actions.remove(pos_action)

    return neg_actions

def writeFacts(opText):

    print (type(opText))
    exit()
    with open("/Users/vigneshsureshbabu/Desktop/train/train_facts.txt", "a") as myfile:
        for i in range(len(opText)):
            myfile.write(opText[i]+'\n')


def writePosNeg(positiveList,negativeList):

    with open("/Users/vigneshsureshbabu/Desktop/train/train_pos.txt", "a") as myfile:
        for i in range(len(positiveList)):
            myfile.write(positiveList[i]+'\n')

    with open("/Users/vigneshsureshbabu/Desktop/train/train_neg.txt", "a") as myfile:
        for i in range(len(negativeList)):
            myfile.write(negativeList[i]+'\n')



def generate_facts(trajectory_list):

    state_counter = 0
    facts= [];pos = [];neg = []
    for each_element in trajectory_list:
        for each_fact in each_element[0]:
            facts.append((each_fact.replace("(","(s"+str(state_counter)+",")+"."))

        pos.append("(s" + str(state_counter) +","+ each_element[1]+")"+".")
        for each_neg_action in each_element[2]:
            neg.append("(s" + str(state_counter) +","+ each_neg_action+")"+".")
            #print ("(s" + str(state_counter) +","+ each_neg_action+")"+".")
    writeFacts(facts)
    writePosNeg(pos,neg)






def takeAction(actionList, blocksList, cstate,gstate):
    perms = permutationsList(blocksList)

    #print (perms)
    trajectory_list = []
    i = 0
    trajectory = []
    while sorted(cstate) != sorted(gstate):
    #while i <1:
        #print("i came in")
        action = actionList[int(random() * len(actionList))]
        perm = perms[int(random() * len(perms))]
        #print (perm)
        if action == "stackBlock":
            cstate = stackBlock(perm[0], perm[1], list(cstate))
            trajectory.append(tuple(cState))
            trajectory_list.append((cState,"stackBlock"+","+perm[0]+","+perm[1],neg_actions_generator(perms,actionList,"stackBlock"+","+perm[0]+","+perm[1])))

        else:
            cstate = unstackBlock(perm[0], perm[1], list(cstate))
            trajectory.append(tuple(cState))
            trajectory_list.append((cState, "unstackBlock"+"," + perm[0]+","+perm[1],neg_actions_generator(perms, actionList, "unstackBlock" + "," + perm[0] + "," + perm[1])))
        i = i+1

    print (trajectory_list)
    updateValues(trajectory)
    generate_facts(trajectory_list)







if __name__ == "__main__":
    blocksList = ['A', 'B', 'C', 'D', 'E', 'F']
    currstateConfiguration = ['TABLE(A)', 'TABLE(B)', 'TABLE(C)','TABLE(D)','CLEAR(A)','CLEAR(B)', 'CLEAR(C)','CLEAR(D)']
    goalStateConfiguration = ['ON(A,B)','ON(B,C)','ON(C,D)','CLEAR(D)','TABLE(A)']
    global stateValues



    goalState = deepcopy(goalStateConfiguration)
    cState = deepcopy(currstateConfiguration)
    cStateSecondIteration = deepcopy(cState)
    actionList = ["stackBlock", "unstackBlock"]
    takeAction(actionList,blocksList,deepcopy(cState),deepcopy(goalState))


    #print(stateValues[tuple(['TABLE(A)', 'TABLE(B)', 'TABLE(D)', 'CLEAR(C)', 'CLEAR(F)', 'ON(D,E)', 'ON(E,F)', 'ON(A,C)', 'CLEAR(B)'])])


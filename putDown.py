from copy import deepcopy
from random import random
import collections
from itertools import combinations_with_replacement
from os import listdir
pathToResults = "/Users/Kaushik/Desktop/Indiana/Research/PolicyGradients"
def combo_generator(l,numberofStacks,numberofBlocks):

    combos = []
    for each in combinations_with_replacement(l, numberofStacks):
        if sum(list(map(int, each))) == numberofBlocks:
            # print (list(map(int, each)))
            combos.append(list(map(int, each)))
    #print (combos)
    return combos

def configuration_generator(blocksList,numList,numberofStacks,numberofBlocks):

    combos = combo_generator(numList,numberofStacks,numberofBlocks)
    cStateList = []
    #print ("combos",combos)
    combo = combos[int(random() * len(combos))]
    print("The length of different stacks in the configuration", combo)

    #print ("combo",combo)
    for eack_stack_length in combo:
        stack = []
        if eack_stack_length == 1:
            random_block = blocksList[int(random() * len(blocksList))]
            stack.append('TABLE(' + random_block + ")");
            stack.append('CLEAR(' + random_block + ")")
            blocksList.remove(random_block)
            # print(stack)
            cStateList.append(stack)
        else:
            random_block1 = blocksList[int(random() * len(blocksList))]
            stack.append('TABLE(' + random_block1 + ")")
            blocksList.remove(random_block1)
            clear_block = None
            for m in range(eack_stack_length - 1):
                random_block2 = blocksList[int(random() * len(blocksList))]
                stack.append("ON" + "(" + random_block1 + "," + random_block2 + ")")
                blocksList.remove(random_block2)
                clear_block = random_block2
                random_block1 = random_block2
            stack.append('CLEAR(' + clear_block + ")")
            cStateList.append(stack)

    print(cStateList)
    return cStateList

def fetchClearBlock(cStateMember):

    """
    :param cStateMember: particular stack in the current state configuration
    :return clearBlock: The clear block in that particular stack
    """

    clearBlock = None
    for each_element in cStateMember:
        if 'CLEAR' in each_element:
            #print(each_element[each_element.index("(") + 1:each_element.rindex(")")].strip())
            clearBlock = each_element[each_element.index("(") + 1:each_element.rindex(")")].strip()
    #print (clearBlock)
    return clearBlock

def fetchLengthStack (cStateMember):

    """
    :param cStateMember: particular stack in the current state configuration
    :return i: the length of the stack
    """
    i = 0
    for each_element in cStateMember:
        if 'ON' in each_element:
            i = i + 1
    #print(i)
    return i

def optimalConditionCheck(cStateList):

    """
    :param cStateList:
    :return:
    """
    opList = []
    for each_stack in cStateList:
        i = 0
        for each_element in each_stack:
            if "ON" in each_element:
                i = i + 1
        if i <= 2:
            opList.append("True")
        else:
            opList.append("False")

    if len(list(set(opList))) == 1 and list(set(opList))[0] == "True":
        #print (True)
        return True
    else:
        #print(False)
        return False

def fetchClrNTabBlocks(cStateList):

    """
    :param cStateList:
    :return:
    """
    anotherresultDict = {}
    for each_stack in cStateList:
        if fetchLengthStack(each_stack) > 2:
            for each_element in each_stack:
                if 'ON' in each_element and each_element[5] == fetchClearBlock(each_stack):
                    anotherresultDict[tuple(sorted(each_stack))] = (fetchClearBlock(each_stack), each_element[3])
    return anotherresultDict


def tupleMaker(str1,str2):

    l1 = []
    l1.append(str1)
    l1.append(str2)
    return tuple(l1)

def modifyState1(str1,str2,copy_each_stack):

    newElement = []
    key = tupleMaker(str1,str2)
    newElement.append('CLEAR' + "(" + key[0] + ")")
    newElement.append('TABLE' + "(" + key[0] + ")")
    copy_each_stack.append('CLEAR' + "(" + key[1] + ")")
    copy_each_stack.remove("ON" + "(" + key[1] + "," + key[0] + ")")
    copy_each_stack.remove('CLEAR' + "(" + key[0] + ")")

    return newElement,copy_each_stack

def remove(mainList,delElement):

    for each_element in mainList:
        if sorted(each_element) == sorted(delElement):
            mainList.remove(each_element)
    return mainList

def takeAction(cStateList):

    trajectory = {}
    i = 0
    trajectory['putDown(s0)'] = cStateList
    while optimalConditionCheck(cStateList) == False:
        i = i +1
        mainCopy = deepcopy(cStateList)
        anotherresultDict = fetchClrNTabBlocks(mainCopy)
        keys =list(anotherresultDict.keys())
        keyasValue  = keys[int(random() * len(keys))]
        copykeyasValue = deepcopy(keyasValue)
        keyToDict = anotherresultDict[copykeyasValue]
        op = modifyState1(keyToDict[0],keyToDict[1],list(copykeyasValue))
        remove(mainCopy,list(copykeyasValue)); mainCopy.append(op[0]);mainCopy.append(op[1])
        cStateList = mainCopy
        if optimalConditionCheck(cStateList) == False:
            trajectory['putDown'+'(s'+str(i)+')'+keyToDict[0]] = cStateList
        else:
            trajectory['noop'+'(s'+str(i)+')'] = cStateList

    return trajectory

def listdictReader(listDict):

    i = 0
    posCounter = 0; negCounter= 0
    facts = [];positive = [];negative = []
    for each in listDict:
        for key, value in each.items():
            if key[0] == 'n':
                print()
                negative.append('putDown(s' + str(i) + ")")
                negCounter = negCounter + 1
            else:
                positive.append('putDown(s' + str(i) + ")")
                posCounter = posCounter + 1
            for eac in value:
                for e in eac:
                    facts.append(e.replace("(", "(" + 's' + str(i) + ",").replace(")", ")."))
            i = i + 1
    print ("posCounter",posCounter)
    print ("negCounter",negCounter)
    #writeFacts(facts);
    #writePosNeg(positive,negative)
    #return facts,positive,negative



def writeFacts(opText):

    with open("/Users/vigneshsureshbabu/Desktop/code/train/train_facts.txt", "a") as myfile:
        for i in range(len(opText)):
            myfile.write(opText[i]+'\n')


def writePosNeg(positiveList,negativeList):

    with open("/Users/vigneshsureshbabu/Desktop/code/train/train_pos.txt", "a") as myfile:
        for i in range(len(positiveList)):
            myfile.write(positiveList[i]+"."+'\n')

    with open("/Users/vigneshsureshbabu/Desktop/code/train/train_neg.txt", "a") as myfile:
        for i in range(len(negativeList)):
            myfile.write(negativeList[i]+"."+'\n')



def authority(cStateList):

    '''check if db results exists'''
    files = listdir(pathToResults)
    file = "results_putdown.db"
    if file in files:
        with open(file) as actionFile:
            
    else:
        if optimalConditionCheck(cStateList) == True:
            print("The configuration of the state is optimal! Hence Generating Facts without simulating!")
            trajectory = {}
            trajectory['noop(s0)']=cStateList
            #generateFactsif(cStateList)
            return trajectory
        else:
            trajectory = takeAction(cStateList)
            print (trajectory)
            print ("the length of the trajectory",len(trajectory))
            print("The configuration of the state is not optimal! Hence Generating Facts after simulating!")
            #generateFactselse(trajectory)
            return trajectory

if __name__ == "__main__":
    numberOfTrajectories = 5
    mainnumList = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19','20', '21', '22','23','24','25','26']
    trajectoryList = []
    mainBlockList = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o','p','q','r','s','t','u','v','w','x','y','z']
    rangeList = list(range(5, 16))
    #print(rangeList)



    for eachTrajectory in range(numberOfTrajectories):
    #blocksList = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        #training phase
        numofBlocks = rangeList[int(random() * len(rangeList))]

        #testing phase
        #numofBlocks = 25

        numberofStacksList = list(range(1,numofBlocks+1))
        print ("")
        print(numberofStacksList)
        print("the total number of blocks", numofBlocks)
        blocksList = mainBlockList[:numofBlocks]
        numberofStacks = numberofStacksList[int(random() * len(numberofStacksList))]
        numlistLimit = (numofBlocks - numberofStacks )+ 1
        numList = mainnumList[:numlistLimit]
        print (numList)
        print ("The number of Stacks in which the blocks will be arranged ",numberofStacks)
        trajectoryList.append(authority(configuration_generator(blocksList,numList,numberofStacks,len(blocksList))))# len(blocksList) = number of blocks
    print(" ")
    print("trajectoryList",trajectoryList)
    print("length", len(trajectoryList[1]))
    print ("length",len(trajectoryList))
    listdictReader(trajectoryList)




    # currstateConfiguration1 = [['ON(A,B)', 'ON(B,C)', 'ON(C,D)', 'TABLE(A)', 'CLEAR(D)'],
    # ['ON(E,F)', 'ON(F,G)', 'ON(G,H)', 'TABLE(E)', 'CLEAR(H)'],
    # ['ON(I,J)', 'ON(J,K)', 'TABLE(I)', 'CLEAR(K)'],
    # ['ON(L,M)', 'ON(M,N)', 'TABLE(L)', 'CLEAR(N)'], ['CLEAR(O)', 'TABLE(O)']]
    # currstateConfiguration2 = [['ON(A,B)', 'ON(B,C)', 'ON(C,D)', 'ON(D,E)', 'TABLE(A)', 'CLEAR(E)'],
    # ['ON(H,I)', 'ON(I,J)', 'ON(J,K)', 'ON(F,G)', 'ON(G,H)', 'TABLE(F)', 'CLEAR(K)'],
    # ['ON(L,M)', 'ON(M,N)', 'TABLE(L)', 'CLEAR(N)'],
    # ['CLEAR(O)','TABLE(O)']]
    # currstateConfiguration3 = [['TABLE(C)', 'ON(C,D)', 'ON(D,F)', 'ON(F,A)', 'ON(A,H)', 'ON(H,E)', 'ON(E,B)', 'CLEAR(B)'], ['TABLE(I)', 'CLEAR(I)'], ['TABLE(J)', 'CLEAR(J)'], ['TABLE(G)', 'CLEAR(G)']]

import json
import re 
import string
from queue import LifoQueue
from queue import Queue

### STACK FUNCTIONS ###
def top(list):
    elem=list.get()
    list.put(elem)
    return elem
################################################################
### STATE CLASS ###
class state:
    def __init__(self):
        self.dict={} 
        self.epsilon=[] 
        self.finishState=0
        self.startState=0
############################################################3
class dfa_state:
    def __init__(self):
        self.dict={}
        self.states=[] ##nfa states
###############################################################
### GLOBAL VARIABLES ###
nfa_size=0
nfa=[] # to keep track of states
stack =LifoQueue() #incremental states
endState=-1
start=-1 ##start state

dfa=[] ##final dfa states 
alphabets=[]
dfa_start_state=0


def isOperand(c): 
    regex="[a-zA-Z0-9]"
    if(re.match(regex,c)):
        return True
    else:
        return False ##a-zA-Z0-9


def get_all_values(nested_dictionary):
    for key, value in nested_dictionary.items():
        current=key
        if type(value) is dict:
            get_all_values(value)

            
        else:
            if key=='startingState': 
                 i= nested_dictionary[key]
                 slice = i[-1]
                 nfa[int(slice)].startState=1

            else:
                print(format(current)," this is key")
                
                print("key ",key, ":","value ", value)
           
def readFromJSON(data):
        global endState
        global start
        global alphabets

        for key,value in data.items(): ##filling nfa
            
            if type(value) is dict:

                if len(key)==2:
                    index=int(key[-1])
                else:
                    index=int(key[-2:])
                if (data[format(key)]["isTerminatingState"])==True: ## MABYDKHOLSH HENA 
                    
                    if len(key)==2:
                        endState=key[-1]
                        
                        nfa[int(endState)].finishState=1
                    else:
                        endState=key[-2:]
                        nfa[int(endState)].finishState=1

                
                else: ##isTerminatingState=false
                    for k,v in value.items():
                        
                        if(k=='Epsilon'):
                            
                            for x in range(len(v)):
                                if(len(value[k][x])==2):
                                    nfa[index].epsilon.append(format(v[x][-1])) 
                                else:
                                    nfa[index].epsilon.append(format(v[x][-2:]))

                              
                        elif (isOperand(format(k)) and k!='isTerminatingState'):
                            if format(k) not in alphabets:
                                alphabets.append(format(k))
                            nfa[index].dict[k]=v
            else:
                if(len(value)==2):

                    start=value[-1]
                    nfa[int(start)].startState=1
                else:
                    start=value[-2:]
                    nfa[int(start)].startState=1


def outTofile():
    global start
    global dfa
    global endState
    global dfa_start_state
    data={}
    data['startingState']='S'+str(dfa_start_state)

    transitions=[]
    transitions.append(dfa_start_state)
    
    while transitions:
        currentState= transitions.pop()
        name= 'S'+str(currentState)
        data[name]={}
        if(dfa[int(currentState)].finishState==1):
            data[name]['isTerminatingState']=True
        else:
            data[name]['isTerminatingState']=False

        for j,v in dfa[int(currentState)].dict.items():

            data[name][j]= 'S'+ str(v)
            
            if('S'+str(v) not in data):
                transitions.append(v)

    with open('./data.json', 'w') as outfile:
        json.dump(data, outfile,indent=2)



def printDFA():
    global stack 
    global dfa
    for i in range(0,len(dfa)):
        print(dfa[i].dict)

                
def printNFA():
    global stack 
    global nfa
    

    for i in range(0,len(nfa)):
        for k,v in nfa[i].dict.items():
            print("state",i,"on input",k,"going to state",nfa[i].dict.get(k))
        for k in range(len(nfa[i].epsilon)):
            print("state",i,"on epsilon goes to state",nfa[i].epsilon[k])

def exists(set,value):
    b=False
    for i in range(len(set)):
        if(set[i]==value):
            b= True 
    if b ==False:
        return False
    else:
        return True

def epsilonClosure(state,values):
    state = int(state)

    for i in range(len(nfa[state].epsilon)):
        if (int(nfa[state].epsilon[i]) not in values): 
            values.add(int(nfa[state].epsilon[i]))
            epsilonClosure(nfa[state].epsilon[i],values)
    return values


def new_state(alphabet,epsilon_list):
    temp= set()
    for i in epsilon_list:
        for k,v in nfa[i].dict.items():
            if format(k) == format(alphabet):
                for x in range(len(v)):
                    if(len(v[x])==2):
                        print("v",v[x][-1])
                        temp.add(int(v[x][-1]))
                    else: 
                        print("v",v[x][-2:])
                        temp.add(int(v[x][-2:]))
    return temp

def nfa_to_dfa(epsilon_set,que,start):
    set_key=[]
    int_val=[]

    counter=0
    idx=0

    epsilon_set.add(int(start))
    epsilonClosure(start,epsilon_set)

    if epsilon_set not in set_key:
        set_key.insert(idx,epsilon_set)
        counter=counter+1
        int_val.insert(idx,counter)
        idx=idx+1
        que.append(epsilon_set.copy())

    p=0
    f1=False
    while len(que) !=0:
        dfa.append(state()) 
        epsilon_set=que[0].copy()
        
        f1=False

        epsilon_list= list(epsilon_set)

        for i in range(len(epsilon_list)):
            if(nfa[epsilon_list[i]].finishState==1):
                f1=True

        dfa[p].finishState=f1
        
        for i in range(len(alphabets)):
            temp_set= new_state(alphabets[i],epsilon_list)
            epsilon_list= temp_set.copy()
            for k in temp_set:
                epsilonClosure(k,epsilon_list)
            if len(epsilon_list)!=0:
                if epsilon_list not in set_key:
                    set_key.append(epsilon_list.copy())
                    int_val.append(counter)
                    counter=counter+1
                    que.append(epsilon_list.copy())
                    dfa[p].dict[alphabets[i]] = counter-1

                else:
                    id= set_key.index(epsilon_list)
                    dfa[p].dict[alphabets[i]]=int_val[id]

            temp_set.clear()
            epsilon_list=que[0]

        que.pop(0)
        p=p+1


def main():
    global stack
    global nfa
    global endState
    global start

    epsilon_set=set()
    que=[]#list of sets
 
    regex="[a-zA-Z0-9]"
    myFile=open('./Test Cases/#1/nfa.json')
    data=json.load(myFile)

    for i in range(len(data)-1): ##initializing nfa with empty states
        nfa.append(state())

    readFromJSON(data)
    nfa_to_dfa(epsilon_set,que,start)

    outTofile()
    printDFA()
                   
if __name__=='__main__':
    main()
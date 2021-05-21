## assume we only deal with '(' and ')'
## assume our language includes only integers from 0-9 and small/capital alphabets
# The output file (The required one) is data.jsom
# the other file(draw.json) is for drawing the NFA only
import json
import re 
import string
from queue import LifoQueue
from PySimpleAutomata import automata_IO

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
    

###############################################################

nfa_size=0
nfa=[] # to keep track of states
final_state=0
start_state=0
stack =LifoQueue() #incremental states


###  VALIDATION FUNCTIONS ####
def match(open,close):
    if (open == '(' and close == ')'):
        return True

def balanacedParantheses(regex):
    stack = []
    for i in regex:
        if i=='(':
            stack.append(i)
        elif i==')':
            if ((len(stack) > 0) and
                (stack[len(stack)-1])=='('):
                stack.pop()
            else:
                return False
    if len(stack) == 0:
        return True
    else:
        return False

def validateRegex(regex):
    b=1
    for i in range(len(regex)):
        if regex[i]=='(':
            if regex[i+1]==')' or regex[i+1]=='|' or regex[i+1]=='*' : ## () or (| or (*
                b = 0
            else:
                b = 1
    if regex[0]=='*' or regex[0]=='|' or regex[0]==')': ##cannot start with '*' or ')' or '|'
        b=0
    if regex[len(regex)-1]=='|': ##cannot end with |
        b=0
    if b==1:
        return True
    else:
        return False
##########################################################################
def appendToConcatenate(regex):
    result=""
    for i in range(len(regex)):
        c=regex[i]
        if (i+1 < len(regex)):
            c2=regex[i+1]
            result+=c
            if(c!='(' and c2!=')' and c!='|'  and c2!='|' and c2!='*'):
                result+='.'
    result+=regex[len(regex)-1]
    return result ##must assume input doesnt implicitly have concatination symbol

def priority(c):
    if c== '*':
       return 3;
    if c==  '.': 
        return 2;
    if c==  '|': 
        return 1;
    else: 
        return 0;

def isOperand(c): 
    regex="[a-zA-Z0-9]"
    if(re.match(regex,c)):
        return True
    else:
        return False ##a-zA-Z0-9

def getPostfix(regex):
    postfix=""
    st=[]
    for i in range(len(regex)):
        if isOperand(regex[i]):
            postfix+=regex[i]
        elif regex[i]=='(':
            st.append(regex[i])
        elif regex[i]==')':
            while(st[-1]!='('):
                postfix+=st[-1]
                st.pop()
            st.pop()
        else:
            while(len(st)>0):
                c=st[-1]
                if(priority(c)>=priority(regex[i])):
                    postfix+=st[-1]
                    st.pop()
                else:
                    break
            st.append(regex[i])
    while(len(st)>0):
        postfix+=st[-1]
        st.pop()
    return postfix ## from regex to postfix

def cases(postfix):
    for i in range(len(postfix)):
        if isOperand(postfix[i]):
            c=postfix[i]
            go_to_operand(c)
        if postfix[i]=='|':
            go_to_UNION()
        if postfix[i]=='*':
            go_to_STAR()
        if postfix[i]=='.':
            go_to_CONC()

### COMPILATION CASES ###
def go_to_operand(c):
    global stack 
    global nfa
    global nfa_size

    nfa.append(state())
    nfa.append(state())
    nfa[nfa_size].dict[c]=nfa_size+1
    stack.put(nfa_size)
    nfa_size=nfa_size+1
    stack.put(nfa_size)
    nfa_size=nfa_size+1

def go_to_CONC():
    global stack 
    global nfa
    global nfa_size

    temp1=stack.get()
    temp2= stack.get()
    temp3= stack.get()
    temp4= stack.get()

    nfa[temp3].epsilon.append(temp2)
    stack.put(temp4)
    stack.put(temp1)


def  go_to_STAR():
    global stack 
    global nfa
    global nfa_size

    nfa.append(state())
    nfa.append(state())

    temp1=stack.get()
    temp2=stack.get()

    nfa[nfa_size].epsilon.append(temp2)
    nfa[nfa_size].epsilon.append(nfa_size+1)

    nfa[temp1].epsilon.append(nfa_size)
    nfa[temp1].epsilon.append(nfa_size+1)

    stack.put(nfa_size)
    nfa_size=nfa_size+1
    stack.put(nfa_size)
    nfa_size=nfa_size+1

def go_to_UNION():
    global stack 
    global nfa
    global nfa_size

    nfa.append(state())
    nfa.append(state())

    d=stack.get()
    c= stack.get()
    b= stack.get()
    a= stack.get()

    nfa[nfa_size].epsilon.append(a)
    nfa[nfa_size].epsilon.append(c)

    nfa[b].epsilon.append(nfa_size+1)
    nfa[d].epsilon.append(nfa_size+1)

    stack.put(nfa_size)
    nfa_size=nfa_size+1
    stack.put(nfa_size)
    nfa_size=nfa_size+1


def printNFA():
    global stack 
    global nfa
    global nfa_size

    for i in range(0,len(nfa)):
        for k in dict():
            if k != -1:
               print("state",i,"on input",k,"going to state",nfa[i].dict.get(k))
        for k in range(len(nfa[i].epsilon)):
            if(nfa[i].epsilon[k]!=-1):
                print("state",i,"on epsilon goes to state",nfa[i].epsilon[k])
                 
                                         
def outTofile():
    global final_state
    global start_state
    data={}
    drawing ={}
    data['startingState']='S'+str(start_state)

    transitions=[]
    drawing['alphabet']=[]
    drawing['states']=[]
    drawing['initial_states']=[]
    drawing['initial_states'].append('S'+str(start_state))
    drawing['accepting_states']=[]
    drawing['transitions']=[]
    transitions.append(start_state)
    
    while transitions:
        currentState= transitions.pop()
        name= 'S'+str(currentState)
        drawing['states'].append(name)
        data[name]={}
        if(nfa[currentState].finishState==1):
            data[name]['isTerminatingState']="true"
            drawing['accepting_states'].append(name)
        else:
            data[name]['isTerminatingState']="false"

        for j,v in nfa[currentState].dict.items():

            data[name][j]= 'S'+ str(v)
            
            if('S'+str(v) not in transitions):
                temp=[]
                transitions.append(v)
                temp.append(name)
                temp.append(str(j))
                temp.append('S'+ str(v))
                drawing['transitions'].append(temp)

            if (j not in drawing['alphabet']):
                drawing['alphabet'].append(j)

        if(len(nfa[currentState].epsilon)!= 0):
            data[name]['epsilon']=[]
            for k in range(len(nfa[currentState].epsilon)): 
                currTransition = 'S'+str(nfa[currentState].epsilon[k])  
                data[name]['epsilon'].append(
                        currTransition)
               
                temp=[]
                temp.append(name)
                temp.append('epsilon')
                temp.append(currTransition)
                drawing['transitions'].append(temp)

                if(currTransition not in data):
                    transitions.append(nfa[currentState].epsilon[k])

    with open('./data.json', 'w') as outfile:
        json.dump(data, outfile,indent=2)
    with open('./draw.json', 'w') as outfile:
        json.dump(drawing, outfile,indent=2)
    temp = automata_IO.nfa_json_importer("./draw.json")
    automata_IO.nfa_to_dot(temp, 'image', './')
        
def main():
    global final_state
    global start_state

    #****Test case 1*********
    #regex=format('(ab)*')

    #*****Test case 2*******
    #regex=format('01|23')

    #*****Test case 3********
    regex=format('0*1*011')

    print(regex)
    if (balanacedParantheses(regex) and validateRegex(regex)):
        print("valid")
        regex_concatenated=appendToConcatenate(regex)
        print(regex_concatenated)
        postfix=getPostfix(regex_concatenated)
        print(postfix)
        cases(postfix)

        final_state=stack.get();
        start_state=stack.get();
        nfa[start_state].startState=1;
        nfa[final_state].finishState=1;

        outTofile()
        printNFA()
    else:
        print("invalid")
    
if __name__=='__main__':
    main()

    



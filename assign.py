#!/usr/bin/python

def main():
	# Get the input Regular expression
	R =  raw_input("Enter the regular expression:")

	# Productions acceptable for R in CNF :
	# Productions of the form A -> a

	CNF = []
	charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	for i in range(52):
		CNF.append(('S',charset[i]))	# S -> all sigma (alphabets)
		
	CNF.append(('C','+'))		# C -> +
	CNF.append(('D','.'))		# D -> .
	CNF.append(('E','*'))		# E -> *
	CNF.append(('A','('))		# A -> (
	CNF.append(('B',')'))		# B -> )


	# Productions of the form A -> BC

	CNF1 = []
	CNF1.append(('S','P','Q'))	# S -> PQ
	CNF1.append(('S','P','T'))	# S -> PT	
	CNF1.append(('S','P','U'))	# S -> PU
	CNF1.append(('P','A','S'))	# P -> AS
	CNF1.append(('Q','C','R'))	# Q -> CR
	CNF1.append(('R','S','B'))	# R -> SB
	CNF1.append(('T','D','R'))	# T -> DR
	CNF1.append(('U','E','B'))	# U -> EB

	temp = check_reg(R,CNF,CNF1)	# temp = 1 if R is valid regular expression and 0 if not
	if temp == 0:
		print("Wrong Expression")
	else:
		# Get the input for number of names followed by the names
		N = int(raw_input("Enter the number of inputs:"))
		# Make a list of N strings and get input for them
		S = ["" for i in range(N)]
		for i in range(N):
			S[i] = raw_input()

		# NFA holds the Non deterministic Finite Automation corresponding to the regular expression R
		# NFA contains the transition information for each state as a list of lists
		# Each list corresponds to a state(index 0<=m<|States|) and within each list we have tuples (a,n)-
		# where a is some symbol over which state m goes to state n, there can be many such tuples for each m since its an NFA
		NFA = RegEx2NFA(R)
		for i in range(N):
			# For each name, call the loyal function and print 'Yes' if it returns 1 and 'No' if it returns 0
			if(check_loyal(NFA,S[i])==1):
				print("Yes")
			else:
				print("No")


def check_reg(R,CNF,CNF1):

	# Use CYK algorithm to check if the regular expression is valid
	# Create a 2D array where each entry is a list

	n =  len(R)
	T = [[ [] for i in range(n+1)] for i in range(n+1)]

	for i in range(n):
		# First fill the diagonals based on CNF entries
		# Append the non terminal to the entry list if the production exists
		# T[i][j] represents all the Non terminals starting with which the string between -
		# index i and j (i < j) can be derived

		for (x,y) in CNF:
			if y== R[i]:
				T[i][i+1].append(x)
				break

	# Fill the other entries by DP using the values of existing entries

	for m in range(2,n+1):

		for i in range(0,n-m+1):

			for j in range(i+1,i+m):

				for (x,y,z) in CNF1:

					# if y is a Non terminal in T[i][j] and z is a Non terminal in T[j][i+m] -
					# and if there exists a non terminal x such that x->yz in CNF1 then append -
					# x to T[i][i+m]

					if ( y in T[i][j] and z in T[j][i+m] ):
						T[i][i+m].append(x)

	# Checs if the start state S is present in T[0][n] i.e the list of Non terminals-
	# from which the string between indices 0 and n can be reached which is essentially the whole string

	if 'S' in T[0][n]:
		return 1
	else:
		return 0


# Runs the given string on the NFA and returns appropriately. Works on BFS.
def check_loyal(N,S):

	# We have constructed all our NFAs to have exactly one start and final state
	# The states are numbered from 0 to F-1 where F is the number of states
	# Perform a BFS to find whether on the input string we reach final state by some path

	F = len(N)
	# dest contains the current set of states
	dest = []
	# first we have to start from state 0
	dest.append(0)
	i=0


	# Repeat till i reaches the end of the string or if dest becomes empty
	while(i<len(S)):
		# temp holds the next set of states
		temp = []
		curr = []
		l=len(dest)
		if(l==0):
			break
			
		# The following while loop finds all possible epsilon transitions that is epsilon closure and stores them in curr
		while(len(dest)>0):
			l=len(dest)
			for j in range(l):
				k = dest[j]
				if(k not in curr):
					curr.append(k)
				for (x,y) in N[k]:
					if(x=='$'):
						if y not in temp:
							dest.append(y)
							temp.append(y)
							if y not in curr:
								curr.append(y)

			for m in range(l):
				dest.pop(0)

		l=len(curr)
		# ctr is a counter variable on how many states give a transition on the current input symbol S[i]
		ctr=0
		for j in range(l):
			k = curr[j]
			# k is now a state in dest
			for (x,y) in N[k]:
				# Do the following if either there is transition by symbol S[i]
				if(x==S[i]):
					dest.append(y)
					# Increment the counter if the transition is by S[i]
					ctr = ctr + 1
		if ctr > 0:
			# Increment i if ctr>0 means we've searched all states in curr and got atleast one transition by S[i] 
			i = i + 1


	# At this point dest contains the set of states obtained once the whole string has been covered by i
	# Now we have to check all possible epsilon transitions repetitively from dest to reach final state if possible
	# Or break if we can't get any more epsilon transitions

	while(len(dest)>0):
		if(F-1 in dest):
			break
		temp = []
		l=len(dest)
		for j in range(l):
			k = dest[j]
			for (x,y) in N[k]:
				if(x=='$'):
					if y not in temp:
						dest.append(y)
						temp.append(y)

		for m in range(l):
			dest.pop(0)

	# Return 1 if dest contains the final state (F-1) and 0 otherwise
	if F-1 in dest:
		return 1

	return 0

def symbol(a):

	# Creates and returns a NFA for a single symbol with one start state and one final state
	# Start state N[0] goes to final state N[1] on symbol a
	N = [ [] for i in range(2) ]
	N[0].append((a,1))

	return N

def union(N1,N2):

	# Given two NFA's, return a NFA that gives the union of both NFA's
	# l1 and l2 store the lengths of the NFA's i.e the number of states in them

	l1=len(N1)
	l2=len(N2)

	# Size of combined NFA will be l1+l2+2 
	# Create the combined NFA (the transition list)
	# '$' corresponds to the epsilon symbol

	N = [ [] for i in range (l1+l2+2)]

	# Add epsilon transitions from new start state to start states of N1 and N2
	N[0].append(('$',1))
	N[0].append(('$',1+l1))
	# Append transitions of N1 and N2 to N with the corresponding linear shifts
	for i in range(l1):
		for (x,y) in N1[i]:
			N[i+1].append((x,y+1))
	for i in range(l2):
		for (x,y) in N2[i]:
			N[i+1+l1].append((x,y+1+l1))

	# Add epsilon transitions from end states of N1 and N2 to the new end state
	N[l1].append(('$',l1+l2+1))
	N[l1+l2].append(('$',l1+l2+1))

	return N

def concat(N1,N2):
	# Given two NFA's return the concatenated NFA

	l1=len(N1)
	l2=len(N2)
	# The new NFA will be of size l1+l2
	N = [ [] for i in range (l1+l2)]
	# Append N1 and N2 to N with corresponding linear shifts
	# New start state will be start state of N1
	# New final state will be final state of N2
	for i in range(l1):
		for (x,y) in N1[i]:
			N[i].append((x,y))
	for i in range(l2):
		for (x,y) in N2[i]:
			N[i+l1].append((x,y+l1))

	# Add epsilon transition from end state of N1 to start state of N2
	N[l1-1].append(('$',l1))

	return N

def star(N1):
	# Given NFA, N1 return its asterate NFA

	l=len(N1)
	# Size of the new NFA will be l+2
	N = [ [] for i in range(l+2)]
	# Append N1 to N with linear shift of 1
	for i in range(l):
		for (x,y) in N1[i]:
			N[i+1].append((x,y+1))

	# Add epsilon transition from new start state to old start state and new final state
	# Add epsilon transition from old final state to old start state and new final state
	N[0].append(('$',1))
	N[0].append(('$',l+1))
	N[l].append(('$',1))
	N[l].append(('$',l+1))

	return N

def RegEx2NFA(R):

	# Returns the NFA corresponding to the given valid Regular expression R
	n=len(R)
	# Base Cases
	if(n==1):
		# R is of the form 'a' i.e a single symbol
		return symbol(R[0])
	if(n==4):
		# R is of the form (a*)
		return star(symbol(R[1]))
	if(n==5):
		# R is of the form (a+b) or (a.b)
		if(R[2] == '+'):
			return union(symbol(R[1]),symbol(R[3]))
		if(R[2] == '.'):
			return concat(symbol(R[1]),symbol(R[3]))

	# executes the below lines only if n>=6

	n=len(R)
	# Recursively find R1 and R2 which are also regular expressions and operate on them
	R1=[]
	R2=[]
	# count holds the no of '(' - no of ')' in R1
	count=0
	# R is always of the form (R1+R2) or (R1.R2) or (R1*)
	for i in range(1,n):
		if R[i]=='(':
			count = count + 1
		if R[i]==')':
			count = count - 1
		R1.append(R[i])
		if count == 0:
			# Indicates that we have reached the end of R1
			break

	# R[i+1] contains the symbol which operates on R1 and R2
	sym = R[i+1]

	# Store R2 from R correspondingly (if it exists)
	for j in range(i+2,n-1):
		R2.append(R[j])

	# Return the resultant NFA based on the operation performed recursively
	if(sym == '+'):
		return union(RegEx2NFA(R1),RegEx2NFA(R2))
	if(sym == '.'):
		return concat(RegEx2NFA(R1),RegEx2NFA(R2))
	if(sym == '*'):
		return star(RegEx2NFA(R1))

# Call the main function to execute the program
main()
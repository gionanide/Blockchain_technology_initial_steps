#!usr/bin/python

#A blockchain is a distributed database with a set of rules for verifying new additions to the database.
#We will start by tracking the acounts of two imaginary people A,B who will trade virtual money with each other.

#First we have to  create a transaction pool of incoming transactions , validate those transactions and
#make them into a block

import hashlib
import json
import sys
import random
import copy


#hash function to crate 'fingerprint' for each transaction(this function links our blocks to each other)
def hashFunction(block):
	passA = str(block[u'parentHash']) + str(block[u'blockNumber']) + str(block[u'chunkCount']) + str(block[u'chunk'])

	# {u'blockNumber':blockNumber,u'parentHash':parentHash,u'chunkCount':chunkCount,u'chunk':chunk}
	#passA= raw_input('Give me a password: ')
	#print ''
	password = passA 
	firstPass = hashlib.sha256(password.encode()).hexdigest()
	#print 'First sha256 pass: ' , firstPass , '\n'
	secondPass = hashlib.sha256(firstPass.encode()).hexdigest()
	#print 'Second sha256 pass: ' , secondPass , '\n'


	key = firstPass+secondPass
	print 'Hash value: ',key
	print ''
	return key

random.seed(0)
#we need to define a function to generate exchanges between A and B.
def makeTransaction(maxNumber):
	#arguments : maxNumebr,transactionSign,amount
	amount = random.randint(1,maxNumber)
	#if (amount > maxNumber):
		#print 'Not valid amount'
	#else:
	
	#this will create maxNumber valid transactions
	# transaction > 0 deposit , transaction < 0 withdrawal (because they give identity to the value)
	#we define that we mark the withdrawals with negative numbers
	#and the deposits with positive numbers
	#the transactions will be only between the two users(because the system has only those two users)
	transactionSign = int(random.getrandbits(1))*2 - 1#randomnly choose 1 or -1
	Apays = amount * transactionSign # the kind of the transaction and the amount
	Bpays = (-1) * Apays # the other user takes the reverse action of A
	return {u'A': Apays , u'B':Bpays}

def updateState(chunk,state):
	#this function does not validate the transaction it just updates the state
	state = state.copy()
	#as dictionaries are mutable, let's avoid any confusion by creating a working copy of the data
	for key in chunk:
		if key in state.keys():
			state[key] +=chunk[key]
		else:	
			state[key] = chunk[key]
	return state

#define a method for checking the validity of the transactions that we have pulled into the block of k transaction
#we will define two rules
# the sum of deposits and withdrawals must be 0
#a user's account must have enough funds to cover any withdrawal
#otherwise we cancel the transaction
def isValid(chunk,state):
	#check the sum
	if(sum(chunk.values()) is not 0):
		return False
		#print 'Rejected transaction'

	#check if the transaction does not cause an overdraft
	for key in chunk.keys():
		if key in state.keys():
			acctBalance = state[key]
		else:
			acctBalance = 0
		if((acctBalance + chunk[key]) < 0) :
			return False
	return True
		

#now we are going from Transaction to Blocks
	
def makeBlock(chunk,chain):
	parentBlock = chain[-1]
	parentHash = parentBlock[u'hash']
	blockNumber = parentBlock[u'contents'][u'blockNumber'] + 1
	chunkCount = len(chunk)

	blockContents = {u'blockNumber':blockNumber,u'parentHash':parentHash,u'chunkCount':chunkCount,u'chunk':chunk}
	blockHash = hashFunction( blockContents )
	block = {u'hash':blockHash,u'contents':blockContents}

	return block

#now we have to check that the new blocks are valid and that the whole chain is valid

#When we initially set up our node, we will download the full blockchain history. After downloading the chain,
# we would need to run through the blockchain to compute the state of the system. To protect against somebody 
#inserting invalid transactions in the initial chain, we need to check the validity of the entire chain in this 
#initial download.
#Once our node is synced with the network (has an up-to-date copy of the blockchain and a representation of system 
#state) it will need to check the validity of new blocks that are broadcast to the network.


#check if the block contents match the hash
def checkBlockHash(block):
	expectedHash = hashFunction(block['contents'])
	if (block['hash']!=expectedHash):
		raise Excpetion ('Hash does not match contents of block %s ' %block['contents']['blockNumber'])


#Check tha validiity of the block , given it's parents and the current system state
def checkBlockValidity(block,parent,state):
	parentNumber = parent['contents']['blockNumber']
	parentHash = parent['hash']
	blockNumber = block['contents']['blockNumber']

	#check the transaction validiity , if false throw an error
	for chunk in block['contents']['chunk']:
		if isValid(chunk,state):
			state = updateState(chunk,state)
		else:
			raise Exception ('Invalid  transaction in block %s:%s'(blockNumber,chunk))
	
	checkBlockHash(block)

	if (blockNumber!=(parentNumber+1)):
		raise Exception ('Hash does not match contents of block %s'%blockNumber)
	
	if (block['contents']['parentHash']!=parentHash):
		raise Exception ('Parent hash not accurate at block %s'%blockNumber)

	return state

def checkChain(chain):
	#walk through the starting block to the chain
	#checking that all the transactions are valid
	#that we do not have an overdraft
	#and that the blocks are linked by their hashes

	#make sure that the chain is a list of dicts
	if(type(chain)==str):
		try:
			chain = json.loads(chain)
			assert(type(chain)==list)
		except:#with this we catch all the exceptions
			return False
	elif (type(chain)!=list):#if it is not a list
		return False

	state = {}
	#check the starting block
	#we want to check that all of the transactions are valid updates to the system state
	# block hash is valid for the block contents

	for chunk in chain[0]['contents']['chunk']:
		state = updateState(chunk,state)
	checkBlockHash(chain[0])
	parent = chain[0]

	#checking subsequent blocks , so as we need to check the reference to the parent's block hash
	#and the validity of the block number
	for block in chain[1:]:
		state = checkBlockValidity(block,parent,state)
		parent = block

	return state
	

def main():
	#make one chunk of transactions
	chunkBuffer = [makeTransaction(10) for i in range(30)]
	#print 'Transaction block: ',chunkBuffer
	

	#example
	#define the initial state
	state = {u'A':5000,u'B':5000}
	#state1 = {u'A':-5,u'B':3}
	#print state1print isValid(state1,startingState)

	#we are making the first element from which everything else will be linked
	startingBlockChunk = [state]
	startingBlockContents = {u'blockNumber':0,u'parentHash':None,u'chunkCount':1,u'chunk':startingBlockChunk}
	#print str(startingBlockContents[u'parentHash'])	
	startingHash = hashFunction(startingBlockContents)
	startingBlock = {u'hash':startingHash,u'contents':startingBlockContents}
	startingBlockStr = json.dumps(startingBlock , sort_keys = True)

	chain = [startingBlock]

	#print str(chain[0][u'parentHash'])
	#for each block we want to collect a set of transaction , create a header , hash it , and add it to the chain
	
	blockSizeLimit = 5 #number of transactions per block(can vary between blocks)

	while (len(chunkBuffer)>0):
		bufferStartSize = len(chunkBuffer)

		#gather a set of valid transactions for inclusion
		chunkList = []
		while( (len(chunkBuffer)>0) and (len(chunkList)<blockSizeLimit) ):
			newChunk = chunkBuffer.pop()
			validChunk = isValid(newChunk,state)#check if it is valid
			
			if (validChunk):
				chunkList.append(newChunk)
				state = updateState(newChunk,state)
			else:
				print 'Rejected transaction'
				continue # move on

		myBlock = makeBlock(chunkList,chain)
		chain.append(myBlock)

	#As expected, the genesis block includes an invalid transaction which initiates account balances
	# (creating tokens out of thin air). The hash of the parent block is referenced in the child block, 
	#which contains a set of new transactions which affect system state. We can now see the state of the 
	#system, updated to include the transactions
	#print chain
	
	nodeChain = copy.copy(chain)
	nodeChunk = [makeTransaction(10000) for i in range(5)]
	newBlock = makeBlock(nodeChunk,nodeChain)

	print ('Blockchain on Node A is currently %s blocks long' %len(chain))

	try:
		print ('New Block Recieved : checking validity...')
		state = checkBlockValidity(newBlock,chain[-1],state)
		#this will throw an error if the block is invalid
		chain.append(newBlock)

	except:
		print('Invalid block, waiting for the next block...')

	print ('Blockchain on Node A is now %s blocks long'%len(chain))

	
main()

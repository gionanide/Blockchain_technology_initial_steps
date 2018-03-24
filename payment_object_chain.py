#!usr/bin/python
import hashlib as hasher
import datetime as date

class Block:
	def __init__(self,number,timestampNumber,dataNumber,previousHash):
		self.number = number
		self.timestampNumber = timestampNumber
		self.dataNumber  = dataNumber
		self.previousHash = previousHash
		self.hash = self.hashFunction()

	def hashFunction(self):
		sha = hasher.sha256()
		sha.update(str(self.number) + str(self.timestampNumber) + str(self.dataNumber) + str(self.previousHash))
		return sha.hexdigest()

	def createInitialBlock():
		return Block(0,date.datetime.now(),'Initial Block','0')

	def nextBlock(lastBlock):
		thisNumber = lastBlock.number + 1
		thisTimestampNumber = date.datetime.now()
		thisDataNumber = str(thisNumber)
		thisHash = lastBlock.hash
		return Block(thisNumber,thisTimestampNumber,thisDataNumber,thisHash)

def main():
	block = Block(0,date.datetime.now(),'Initial Block','0')
	blockChain = [block]
	previousBlock = blockChain[0]

	#how many blocks to add
	maxNumber = 20

	for i in range(0,maxNumber):
		blockToAdd = block.nextBlock(previousBlock)
		blockChain.append(blockToAdd)
		previousBlock = blockToAdd
		print 'Block ',blockToAdd.number,'has been added to the chain'
		print 'Hash ',blockToAdd.hash

main()



import sys
from random import randrange

from Common.config import *
from Common.HashAlgo import generateHash
from MerkleTreeHandling.MerkleTree import MerkleTree


# NOTE: Base Class
class Block:
    def __init__(self, prevBlockPtr, txnList):
        self.prevBlockPtr = prevBlockPtr
        self.prevBlockHash = prevBlockPtr.getBlockHash() if prevBlockPtr else ""
        self.txnList = txnList
        self.noOfTxn = len(txnList)
        self.merkleTree = MerkleTree(txnList)
        self._nonce = randrange(0, 2**sizeOfNonce)
        self._blockHash = generateHash(
            self.prevBlockHash
            + str(self._nonce)
            + str(self.noOfTxn)
            + self.merkleTree.treeHash
        )
        self._blockSize = self.calculateBlockSize()  # So that it only calculates once

    # NOTE: GETTERS
    def getBlockHash(self):
        return self._blockHash

    def getBlockSize(self):
        return self._blockSize

    def getBlockMerkleTreeRoot(self):
        return self.merkleTree.treeRoot

    def getNonce(self):
        return self._nonce

    def calculateBlockSize(self):
        totalSize = 0
        totalSize += sys.getsizeof(self.prevBlockPtr)
        totalSize += sys.getsizeof(self._nonce)
        totalSize += sys.getsizeof(self._blockHash)

        # Transaction Sizes
        for txn in self.txnList:
            totalSize += txn.getTxnSize()

        # Get merkle tree system size
        totalSize += self.merkleTree.getMerkleTreeSystemSize()
        return totalSize

    def __str__(self):
        return f"Block( BlockHash = {self._blockHash} NoOfTxn = {self.noOfTxn} BlockSize = {self._blockSize})"

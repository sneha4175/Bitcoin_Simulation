import sys

from Common.config import *
from Common.LoggingSetup import *
from MerkleTreeHandling.MerkleTreeNode import MerkleTreeNode
from MerkleTreeHandling.MerkleTreeNodeInfo import MerkleTreeNodeInfo


class MerkleTree:
    """
    Structure holds the merkle tree's implementation, by using the MerkleTreeNode and MerkleTreeNodeInfo
    txnList: The transactions which needs to be part of the merkle tree to be created
    """

    def __init__(self, txnList):
        self.txnList = txnList
        self.treeRoot = self.generateMerkleTree()
        self.treeHash = self.treeRoot.treeNodeHash
        self.treeNodeCount = self.calculateTreeNodeCount()
        self._treeSize = self.treeNodeCount * sys.getsizeof(self.treeHash)

    def generateMerkleTree(self):
        nodesQueue = []

        # NOTE : Store all the txn in unique Merkle Tree Node
        # NOTE : Well Merkle Tree Node structure have a field called isLeafNode
        # NOTE : Rule of thumb : if node is leaf -> It contains a transaction but it doesn't contain Merkle Tree Node childs
        # NOTE : All non-leaf node contains child Merkle Tree Nodes as children
        for transaction in self.txnList:
            tree_node = MerkleTreeNodeInfo(
                MerkleTreeNode([], txn=transaction, isLeafNode=True), 0
            )
            nodesQueue.append(tree_node)

        # NOTE : Store all the leaf nodes in queues
        # NOTE : Then in groups of arity number , we will group the leaf nodes and create parent node
        # NOTE : Once we got few parent node, the same process is repeated to get grand parents node
        # NOTE : Until in the end single node remains that will be the root, will have references to all the nodes
        while len(nodesQueue) > 1:
            currentLevel = nodesQueue[0].level
            nodesForParentLevel = []

            for i in range(arity):
                if len(nodesQueue) > 0 and nodesQueue[0].level == currentLevel:
                    nodesForParentLevel.append(
                        nodesQueue[0].node
                    )  # YOU ONLY APPEND THE NODE DETAILS not the level info
                    nodesQueue.remove(nodesQueue[0])
            nodesQueue.append(
                MerkleTreeNodeInfo(
                    MerkleTreeNode(nodesForParentLevel, isLeafNode=False),
                    currentLevel + 1,
                )
            )
        return nodesQueue[0].node

    def calculateTreeNodeCount(self):
        # NOTE : Right now, we are using an upper limit on number of nodes in the merkle tree to be 15
        # NOTE : This is due to the fact that this project was made for analysis purposes not execution purpose
        # NOTE : So that number of nodes can act as hyper parameter and anyone can run it
        # NOTE : But if you want to see the real behaviour, you can set the maxMerkleTreeLeafNode = None in config file, in Common folder
        if maxMerkleTreeLeafNode is None:
            numOfNodes = len(self.txnList)
        else:
            numOfNodes = maxMerkleTreeLeafNode

        n = numOfNodes
        while n > 1:
            numOfNodes += (n + arity - 1) // arity
            n = (n + arity - 1) // arity
        return numOfNodes

    def getMerkleTreeSystemSize(self):
        return self._treeSize

    def __str__(self):
        printValue = "MerkleTree("
        printValue += " TreeHash : " + str(self.treeHash) + ","
        printValue += " TreeNodeCount: " + str(self.treeNodeCount)
        printValue += ")"
        return printValue

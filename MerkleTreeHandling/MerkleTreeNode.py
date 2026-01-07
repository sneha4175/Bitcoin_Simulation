from Common.config import *
from Common.HashAlgo import *


class MerkleTreeNode:
    """
    Represents the structure of a Merkle Tree Node
    childrenTreeNodes : Non leaf nodes in merkle tree , have other merkle tree node as children, this represents a list of children nodes which needs to be contained under to be created node
    txn : Leaf nodes , doesn't have any children nodes, but they have transaction stored in them
    isLeafNode: Now we can use the flag isLeafNode, to query if a merkle node is either leaf o

    """

    def __init__(self, childrenTreeNodes, txn=None, isLeafNode=False):
        self.txn = txn
        self.isLeafNode = isLeafNode
        self.childrenTreeNodes = childrenTreeNodes
        self.treeNodeHash = (
            self.txn.getTransactionHash()
            if self.isLeafNode
            else self.calculateTreeNodeHash()
        )

    # NOTE: This function main job is to calculate the nodeHash of a non leaf node
    def calculateTreeNodeHash(self):
        localTreeNodeHash = ""
        for childTreeNode in self.childrenTreeNodes:
            localTreeNodeHash += childTreeNode.treeNodeHash

        # If the num of child is less than arity,
        # Then add the last child hash as pad value
        # NOTE: Merkle tree rules suggests that if there are
        diffInArity = arity - len(self.childrenTreeNodes)
        if diffInArity > 0:
            lastIndexTreeNodeHash = self.childrenTreeNodes[-1]
            localTreeNodeHash += lastIndexTreeNodeHash.treeNodeHash * diffInArity

        localTreeNodeHash = generateHash(localTreeNodeHash)
        return localTreeNodeHash

    def __str__(self):
        printString = "MerkleTree( leafNode = " + str(self.isLeafNode)
        if self.isLeafNode is True:
            printString += ", txn = " + str(self.txn.getTransactionHash())
        else:
            printString += ", countChildrenNode = " + str(len(self.childrenTreeNodes))
        printString += ")"
        return printString

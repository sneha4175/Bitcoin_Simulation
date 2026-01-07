class MerkleTreeNodeInfo:
    def __init__(self, node, level):
        self.node = node
        self.level = level

    def __str__(self):
        return (
            f"MerkleTreeNodeInfo(Node = {str(self.node)} , level = {str(self.level)})"
        )

class ReceiverHashes:
    """
    lockedTxnHash : This object contains the output's enteries amount + hashed public key, why called locked txn because which ever txn takes this particular txn as input, need to unlock it by validating by generating the same hash
    receiverPublicKeyHash: This object contains the double hashed version of receiver's public key in hexdigest format
    """

    def __init__(self, lockedTxnHash, receiverPublicKeyHash):
        self.lockedTxnHash = lockedTxnHash
        self.receiverPublicKeyHash = receiverPublicKeyHash

    def __str__(self):
        return f"ReceiverHashes(lockedTxnHash = {self.lockedTxnHash.hexdigest()} , Receiver Pub Key Hash = {self.receiverPublicKeyHash})"

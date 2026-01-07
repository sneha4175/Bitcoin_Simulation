class InputEntry:
    """
    outputEntryIndex : The index helps in recognizing the exact output entry in transaction which credits the amount to the sender ( of the to be created txn, or the receiver of previous txn)
    prevTxn: Transaction here represents, the previous txns which sender received from previous sender. The above index, the represents the outputEntry which has the amount details sent to the sender of the , txn being created.
    senderHashes: This object contain the public key , hashed and sender's signature, which will be helpful in transaction verification
    """

    def __init__(self, previousTxn, outputEntryIndex, senderHashes):
        self._transaction = previousTxn
        self._outputEntryIndex = outputEntryIndex
        self._senderHashes = senderHashes

    def getTransaction(self):
        return self._transaction

    def getOutputEntryIndex(self):
        return self._outputEntryIndex

    def getSenderHashes(self):
        return self._senderHashes

    def __str__(self):
        printValue = "InputEntry("
        printValue += " Txn = " + str(self._transaction.getTransactionHash()) + ","
        printValue += " Index = " + str(self.getOutputEntryIndex())
        printValue += ")"
        return printValue

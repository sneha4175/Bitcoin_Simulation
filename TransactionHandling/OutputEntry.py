class OutputEntry:
    """
    amount: Represents the bitcoin which needs to be sent to the receiver
    receiverHashes: This object contains the hashed public key and the transaction hash for validation of txn
    """

    def __init__(self, amount, receiverHashes):
        self._amount = amount
        self._receiverHashes = receiverHashes

    def getAmount(self):
        return self._amount

    def getReceiverHashes(self):
        return self._receiverHashes

    def __str__(self):
        printValue = "OutputEntry("
        printValue += " Amt = " + str(self._amount) + ","
        printValue += " ReceiverHashes = " + str(self._receiverHashes)
        printValue += " )"
        return printValue

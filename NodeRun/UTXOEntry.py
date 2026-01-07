from NodeRun.TransactionHandling.Transaction import Transaction


class UTXOEntry:
    def __init__(self, transaction: Transaction, outputEntryIndex: int):
        self._transaction = transaction
        self._outputEntryIndex = outputEntryIndex

    def getTransaction(self):
        return self._transaction

    def getOutputEntryIndex(self):
        return self._outputEntryIndex

    def __str__(self):
        return f"UTXOEntry(TxnHash = {str(self._transaction.getTransactionHash())}  Idx = {str(self._outputEntryIndex)})"

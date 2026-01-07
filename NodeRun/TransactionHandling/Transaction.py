from Common.BitcoinScripts import *
from Common.HashAlgo import *
from Common.LoggingSetup import *
from Common.ReceiverHashes import ReceiverHashes
from NodeRun.TransactionHandling.InputEntry import InputEntry
from NodeRun.TransactionHandling.OutputEntry import OutputEntry


class Transaction:
    """
    prevTxn:  A list of UTXOEntry objects contained within a list
    senderHashesList : This parameteres represents the sender node based hashes added by the sender per inputEntry
    amount : The amount for which the transaction is being created
    receiverHashes : Contains the hashes required to find the receiver
    genesisBlockTxn: If the provided transaction is a genesisBlockTxn
    """

    def __init__(
        self,
        prevTxns,
        senderHashesList,
        amount,
        receiverHashes,
        genesisBlockTxn=False,
    ):
        logger.info("Transaction creation instantiated ")
        self._txnHash = ""
        self.validTransaction = True
        self.input = self.processInput(prevTxns, senderHashesList)
        self.output = self.processOutput(amount, receiverHashes, genesisBlockTxn)
        self._txnSize = self.calculateTxnSize()
        # TODO : Validation check need not be done by the Transaction creator class
        # Or idk , have to think from the bit coin based logic
        # Where do you wanna keep it

    def getTransactionHash(self):
        return self._txnHash

    def processInput(self, prevTxns, senderHashesList):
        inputEntryList = []
        inputHash = ""

        # NOTE : Prev Txn contains the UTXOEntry objects
        for i in range(len(prevTxns)):
            prevTxn = prevTxns[i]
            senderHashes = senderHashesList[i]
            inputHash += prevTxn.getTransaction().getTransactionHash() + str(
                prevTxn.getOutputEntryIndex()
            )
            inputEntry = InputEntry(
                prevTxn.getTransaction(), prevTxn.getOutputEntryIndex(), senderHashes
            )
            logger.info("Input Entry Added : " + str(inputEntry))
            inputEntryList.append(inputEntry)
        self._txnHash += inputHash
        return inputEntryList

    # NOTE: Processing the output
    def processOutput(
        self,
        amount,
        receiverHashes,
        genesisBlockTxn=False,
    ):
        outputEntryList = []

        if genesisBlockTxn:
            outputEntry = OutputEntry(
                amount, ReceiverHashes(receiverHashes, receiverHashes.hexdigest())
            )
            outputEntryList.append(outputEntry)
        else:
            senderBalance = self.validateTransaction(amount)
            logger.info(
                "Sender balance after validating the transaction" + str(senderBalance)
            )

            if senderBalance == -1:
                self._txnHash = generateHash(self._txnHash)
                self.validTransaction = False
                return []

            outputEntryList.append(
                OutputEntry(
                    amount,
                    ReceiverHashes(receiverHashes, receiverHashes.hexdigest()),
                )
            )

            if senderBalance > amount:
                for inputEntry in self.input:
                    inputEntryAmount = (
                        inputEntry.getTransaction()
                        .output[inputEntry.getOutputEntryIndex()]
                        .getAmount()
                    )

                    paidAmount = 0

                    if amount > 0:
                        paidAmount = min(inputEntryAmount, amount)

                        inputEntryAmount -= paidAmount
                        amount -= paidAmount

                    if inputEntryAmount > 0:
                        # Double Hashed sender public key
                        # Of the current node which is processing this transaction
                        senderPubKeyHash = SHA256.new(
                            hashlib.sha256(inputEntry.getSenderHashes().senderPublicKey)
                            .hexdigest()
                            .encode()
                        )

                        outputEntryList.append(
                            OutputEntry(
                                inputEntryAmount,
                                ReceiverHashes(
                                    senderPubKeyHash, senderPubKeyHash.hexdigest()
                                ),
                            )
                        )

        for outputEntry in outputEntryList:
            self._txnHash += (
                str(outputEntry.getAmount())
                + outputEntry.getReceiverHashes().lockedTxnHash.hexdigest()
            )
            logger.info("Output Entry added to Transaction : " + str(outputEntry))
        self._txnHash = generateHash(self._txnHash)

        for outputEntry in outputEntryList:
            outputEntry.getReceiverHashes().lockedTxnHash.update(self._txnHash.encode())
        return outputEntryList

    def validateTransaction(self, amount):

        senderBalance = 0

        for ip_entry in self.input:
            index = ip_entry.getOutputEntryIndex()
            txnHash = ip_entry.getTransaction().getTransactionHash()
            senderNodeHashes = ip_entry.getSenderHashes()

            # NOTE: The transactions output has lot of entry
            # Index tells you which entry you need to choose

            lastTxnRecvHashes = (
                ip_entry.getTransaction().output[index].getReceiverHashes()
            )

            # Validate the scripts
            if validateTxnHash(senderNodeHashes, lastTxnRecvHashes, txnHash) == False:
                senderBalance = -1
                break

            senderBalance += ip_entry.getTransaction().output[index].getAmount()

        # NOTE: validAmount = total credit received from the previous txns
        # amount: Sender's node request to spend the provided amount

        if senderBalance < amount:
            logger.info("Sender doesn't have enough balance , invalid transaction")
            senderBalance = -1

        logger.info("Validate Transaction, " + str(senderBalance))
        return senderBalance

    def calculateTxnSize(self):
        totalSize = 0
        totalSize += sys.getsizeof(self._txnHash)
        totalSize += sys.getsizeof(self.input)
        totalSize += sys.getsizeof(self.output)
        return totalSize

    def getTxnSize(self):
        return self._txnSize

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False
        return (
            self.input,
            self.output,
            self.getTxnSize(),
            self.getTransactionHash(),
        ) == (other.input, other.output, other.getTxnSize(), other.getTransactionHash())

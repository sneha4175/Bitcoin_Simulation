import hashlib
import time
from random import random, randrange

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from prettytable import PrettyTable

from Common.config import *
from Common.LoggingSetup import *
from Common.SenderHashes import SenderHashes
from NodeRun.Block import Block
from NodeRun.BlockChain import BlockChain
from NodeRun.TransactionHandling.Transaction import Transaction
from NodeRun.UTXOEntry import UTXOEntry
from NodeRun.Wallet import Wallet


class Node:
    listOfNodes = []
    txnFlag = True
    txnNodes = []
    allTxnPerformedLog = PrettyTable()
    allTxnPerformedLog.field_names = ["Sender ", "Receiver ", "Amount ", "Valid"]
    walletsPublicKeyMap = {}
    nodeIdCounter = 0

    def __init__(self):
        self.nodeId = Node.nodeIdCounter
        self.wallets = []
        self.blockChain = BlockChain()
        self.nodeTxns = []
        self.localUTXO = {}
        self.start = 0
        self.lastCreatedBlockHashVal = None  # NOTE: Also notice that this is assigned even if the node doesn't win POW
        self.incentive = 0
        Node.nodeIdCounter += 1
        self.createWallets()

    def createWallets(self):
        Wallet.walletIdCounter = 0
        for i in range(walletCountPerNode):
            newWallet = Wallet()
            self.wallets.append(newWallet)
            Node.walletsPublicKeyMap[newWallet.getWalletPublicKeyHash().hexdigest()] = (
                str(self.nodeId) + " . " + str(newWallet.getWalletId())
            )
            logger.info("Wallet Created : " + str(newWallet))

    def getRandomWalletPublicKeyHash(self):
        randomWalletIdx = randrange(0, walletCountPerNode)
        logger.info("Generated wallet random id : " + str(randomWalletIdx))
        walletSelected = self.wallets[randomWalletIdx]
        return walletSelected.getWalletPublicKeyHash()

    def getNodeConsensus(self, block):
        logger.info("Get Node Consensus Called")
        if self.blockChain.latestBlock != block.prevBlockPtr:
            return False
        else:
            for txn in block.txnList:
                if txn.validTransaction is False:
                    return False

                for inputEntry in txn.input:
                    getSenderPubKey = inputEntry.getSenderHashes().senderPublicKey
                    senderPubKeyHash = SHA256.new(
                        hashlib.sha256(getSenderPubKey).hexdigest().encode()
                    )
                    txn = inputEntry.getTransaction()
                    try:
                        searchFlag = False
                        utxoEntryList = self.localUTXO[senderPubKeyHash.hexdigest()]
                        for utxoEntry in utxoEntryList:
                            if utxoEntry.getTransaction() == txn:
                                searchFlag = True
                                break
                        return searchFlag
                    except KeyError:
                        return False
        return True

    def processTransaction(self, txn):
        logger.info("Process Transaction Called")
        logger.info(
            "Process Transaction : Txn Validity Check " + str(txn.validTransaction)
        )
        if txn.validTransaction:
            self.nodeTxns.append(txn)

    def processBlock(self, block):
        logger.info("Process Block called")
        if self.blockChain.rootBlock is None:
            self.blockChain.rootBlock = block

        self.blockChain.latestBlock = block
        tempUTXO = {}
        for txn in block.txnList:
            # NOTE: Process input of a txn
            for inputEntry in txn.input:
                index = inputEntry.getOutputEntryIndex()
                receiverPublicKeyHash = (  # NOTE: This extracts the receiverPublicKeyHash from the previous txn
                    inputEntry.getTransaction()
                    .output[index]
                    .getReceiverHashes()
                    .receiverPublicKeyHash
                )
                try:
                    self.localUTXO[receiverPublicKeyHash] = []
                except KeyError:
                    continue

            index = 0

            # NOTE: Process output of a txn
            for outputEntry in txn.output:
                receiverPublicKeyHash = (  # NOTE: This extracts the receiverPublicKeyHash from the current txn
                    outputEntry.getReceiverHashes().receiverPublicKeyHash
                )
                utxoEntry = UTXOEntry(txn, index)
                try:
                    tempUTXO[receiverPublicKeyHash].append(utxoEntry)
                except KeyError:
                    tempUTXO[receiverPublicKeyHash] = [utxoEntry]

                index += 1
            try:
                self.nodeTxns.remove(txn)
            except ValueError:
                continue

        for recvPubKeyHash in tempUTXO:
            value = tempUTXO[recvPubKeyHash]  # Value : (txn , index)
            for entry in value:
                try:
                    # For the given receiver key, append the transaction
                    self.localUTXO[recvPubKeyHash].append(entry)
                except KeyError:
                    self.localUTXO[recvPubKeyHash] = [entry]

        self.start = time.time()

    def createGenesisBlock(self):
        logger.info("Create Genesis Block Called")
        bitCoinVal = genesisBlockBitCoin
        for _ in range(nodeCount):
            randomNode = randrange(0, nodeCount)
            node = Node.listOfNodes[randomNode]
            recvPubKeyHash = node.getRandomWalletPublicKeyHash()
            t1 = Transaction([], [], bitCoinVal, recvPubKeyHash, True)
            logger.info("Genesis Transaction Created : " + str(t1))
            self.nodeTxns.append(t1)
        copyOfTxnList = self.nodeTxns.copy()
        blk = Block(None, copyOfTxnList)

        for node in Node.listOfNodes:
            node.processBlock(blk)
        # Once the nodes have processed the txns, this basically removes the transactions related to genesis transactions from the list
        self.nodeTxns = []

    def createBlock(self):
        logger.info("Create Block Called")
        start_time = time.time()
        copyOfTxnList = self.nodeTxns.copy()
        blk = Block(self.blockChain.latestBlock, copyOfTxnList)
        return blk  # Returns the block

    def proofOfWork(self):
        logger.info("Proof Of Work Called")
        # NOTE: Basically pow defines which node gets to create block
        # If the current node has the least , last created block hash; wins the pow
        for node in Node.listOfNodes:
            if (
                node.lastCreatedBlockHashVal is not None
                and self.lastCreatedBlockHashVal > node.lastCreatedBlockHashVal
            ):
                logger.info(" POW : The last created block is not the least")
                return False

            # NOTE: This is a tie breaker condition
            # if two nodes have the same last created block hash the one with lesser id wins
            if (
                self.nodeId != node.nodeId
                and self.lastCreatedBlockHashVal == node.lastCreatedBlockHashVal
                and self.nodeId > node.nodeId
            ):
                logger.info(
                    " POW : in case of same block hash, the nodeid is not the least"
                )
                return False
                return False
        return True

    # NOTE: BOOKMARK ... you're here , start here
    def printTxn(self, txnList):
        logger.info("Print Txn is called")
        txnsExecuted = PrettyTable()
        txnsExecuted.field_names = ["ID", "IN/OUT", "Wallet ID", "Amount"]
        txnIdx = 0
        for txn in txnList:
            for inputEntry in txn.input:
                index = inputEntry.getOutputEntryIndex()
                walletAmt = inputEntry.getTransaction().output[index].getAmount()
                senderPubKeyHash = SHA256.new(
                    hashlib.sha256(inputEntry.getSenderHashes().senderPublicKey)
                    .hexdigest()
                    .encode()
                )
                txnsExecuted.add_row(
                    [
                        txnIdx,
                        "IN",
                        Node.walletsPublicKeyMap[senderPubKeyHash.hexdigest()],
                        walletAmt,
                    ]
                )

            for outputEntry in txn.output:
                walletAmt = outputEntry.getAmount()
                recvPubKeyHash = outputEntry.getReceiverHashes().receiverPublicKeyHash
                txnsExecuted.add_row(
                    [txnIdx, "OUT", Node.walletsPublicKeyMap[recvPubKeyHash], walletAmt]
                )
            txnIdx += 1
        print(txnsExecuted)

    def printUTXO(self):
        logger.info("Print UTXO is called")
        x = PrettyTable()
        columns = ["Node ID"]
        for i in range(walletCountPerNode):
            columns.append("Wallet " + str(i))

        x.field_names = columns

        for node in Node.listOfNodes:
            row = [node.nodeId]
            for i in range(walletCountPerNode):
                walletPubKeyHash = node.wallets[i].getWalletPublicKeyHash()
                balance = 0
                try:
                    val = self.localUTXO[walletPubKeyHash.hexdigest()]
                    for entry in val:
                        balance += (
                            entry.getTransaction()
                            .output[entry.getOutputEntryIndex()]
                            .getAmount()
                        )
                except KeyError:
                    balance += 0
                row.append(balance)
            x.add_row(row)
        print(x)
        print(
            "--------------------------------------------------------------------------------"
        )

    def run(self):
        logger.info("Starting the thread")
        self.start = time.time()

        while True:
            logger.info("Starting another iteration of while loop")
            end = time.time()
            if end - self.start > 15:
                if len(self.nodeTxns) > 0:
                    timer = time.time()

                    block = self.createBlock()
                    logger.info("Block Creation Completed " + str(block))
                    self.lastCreatedBlockHashVal = block.getBlockHash()

                    pow = self.proofOfWork()
                    logger.info("Proof of work completed " + str(pow))
                    if pow:
                        Node.txnFlag = False
                        flag = True

                        for node in Node.listOfNodes:
                            if node.getNodeConsensus(block) is False:
                                flag = False
                                break
                        logger.info("Inside POW block")
                        if flag:
                            print(
                                "--------Before Performing the Transaction final state of the Nodes---------"
                            )
                            self.printUTXO()
                            print(
                                " -------------------------------------------------------------------------- "
                            )

                            print(
                                "---------------------- Transactions Performed --------------------------"
                            )
                            print(Node.allTxnPerformedLog)
                            Node.allTxnPerformedLog.clear_rows()

                            print(
                                " -------------------------------------------------------------------------- "
                            )

                            for node in Node.listOfNodes:
                                node.processBlock(block)

                            logger.info("Completed the processBlock for all the nodes")
                            print(
                                "--------After Performing the Transaction final state of the Nodes---------"
                            )

                            self.printUTXO()

                            print(
                                "------------------------ Transactions Executed----------------------------"
                            )
                            self.printTxn(block.txnList)

                            print(
                                " -------------------------------------------------------------------------- "
                            )

                            Node.txnFlag = True
                            Node.txnNodes = []
                            self.incentive += incentiveAmount

                            randomWalletPubKeyHash = self.getRandomWalletPublicKeyHash()
                            txn = Transaction(
                                [], [], incentiveAmount, randomWalletPubKeyHash, True
                            )
                            logger.info("Incentive Transaction Created " + str(txn))
                            for node in Node.listOfNodes:
                                node.processTransaction(txn)
                        else:
                            self.nodeTxns = []
                            Node.txnFlag = True
                            Node.txnNodes = []
                    else:
                        self.start = time.time()
            dotxn = random()
            logger.info(
                "Starting Transaction Creator , dotxn number = "
                + str(dotxn)
                + " Node.txnFlag "
                + str(Node.txnFlag)
                + " Node.txnNodes : "
                + str(Node.txnNodes)
            )
            if dotxn <= 0.2 and Node.txnFlag and self.nodeId not in Node.txnNodes:
                logger.info("Inside the create random transaction block")
                # NOTE: Prepare sender information
                previousTxnsList = []
                senderHashesList = []

                for wallet in self.wallets:
                    senderPubKey = wallet.getWalletPublicKey()
                    senderPvtKey = wallet.getWalletPrivateKey()
                    try:
                        senderPubKeyHashTemp = wallet.getWalletPublicKeyHash()
                        senderInputTxnList = self.localUTXO[
                            senderPubKeyHashTemp.hexdigest()
                        ]
                        for utxoEntry in senderInputTxnList:
                            logger.info("Checking the UTXO Entry " + str(utxoEntry))
                            senderPubKeyHash = wallet.getWalletPublicKeyHash()
                            senderPubKeyHash.update(
                                utxoEntry.getTransaction().getTransactionHash().encode()
                            )
                            genSigner = PKCS115_SigScheme(RSA.importKey(senderPvtKey))
                            genSenderSignature = genSigner.sign(senderPubKeyHash)
                            previousTxnsList.append(utxoEntry)
                            senderHashesList.append(
                                SenderHashes(genSenderSignature, senderPubKey)
                            )
                    except KeyError:
                        continue
                logger.info("Sender Hashes and Previous Txn List processing over")

                # NOTE: Prepare receiver based information
                # NOTE: Start with generating
                randomNodeIdx = randrange(0, nodeCount)
                while str(randomNodeIdx) == str(self.nodeId):
                    randomNodeIdx = randrange(0, nodeCount)

                randomNode = Node.listOfNodes[randomNodeIdx]
                randomNodePubKeyHash = randomNode.getRandomWalletPublicKeyHash()
                logger.info("Line 372 , getRandomWalletPublicKeyHash()")
                randomNodePubKeyStrHash = randomNodePubKeyHash.hexdigest()
                logger.info(
                    "Receiver Node Selected "
                    + str(Node.walletsPublicKeyMap[randomNodePubKeyStrHash])
                )

                randomBitCoinVal = randrange(10, 201)
                newTxn = Transaction(
                    previousTxnsList,
                    senderHashesList,
                    randomBitCoinVal,
                    randomNodePubKeyHash,
                )
                logger.info("New Transaction Created " + str(newTxn))

                Node.allTxnPerformedLog.add_row(
                    [
                        self.nodeId,
                        Node.walletsPublicKeyMap[randomNodePubKeyStrHash],
                        randomBitCoinVal,
                        newTxn.validTransaction,
                    ]
                )

                if newTxn.validTransaction:
                    Node.txnNodes.append(self.nodeId)

                for node in Node.listOfNodes:
                    node.processTransaction(newTxn)
            time.sleep(1)

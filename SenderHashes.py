class SenderHashes:
    """
    senderSignature: Sender's sent signature generated on the txn.hash + sender's public key
    senderPublicKey: Sender's public key
    """

    def __init__(self, senderSignature, senderPublicKey):
        self.senderSignature = senderSignature
        self.senderPublicKey = senderPublicKey

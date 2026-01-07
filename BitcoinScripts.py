import hashlib

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme


def validateTxnHash(senderHashesObj, receiverHashesObj, txnHash):
    """
    This function basically validates given a transaction's receiver and its spender ( usually the same person/node). Their identification holds true or not
    senderHashObj: SenderHashes -> In real this is the spender's hash which include the spender's public key and signature
    receiverHashesObj: ReceiverHashes -> In real this contains the previous txn's output hash , in the sense the locked money which spender need to validate
    txnHash: The previous transaction hash from which the amount needs to be spent from
    """
    senderSignature = senderHashesObj.senderSignature
    senderPublicKey = senderHashesObj.senderPublicKey
    receiverLockedTxnHash = receiverHashesObj.lockedTxnHash
    genSenderUnlockingHash = SHA256.new(
        hashlib.sha256(senderPublicKey).hexdigest().encode()
    )
    genSenderUnlockingHash.update(txnHash.encode())
    if genSenderUnlockingHash.hexdigest() != receiverLockedTxnHash.hexdigest():
        return False  # NOTE: Basically means the receiver is not the right receiver
    verifier = PKCS115_SigScheme(RSA.importKey(senderPublicKey))
    try:
        verifier.verify(receiverLockedTxnHash, senderSignature)
    except:
        return False
    return True

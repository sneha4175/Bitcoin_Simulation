import hashlib

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA


class Wallet:
    walletIdCounter = 0

    def __init__(self):
        self._walletId = Wallet.walletIdCounter
        self._walletPubKey = None
        self._walletPvtKey = None

        # NOTE: Extra functions to be called
        self.createWalletPubPvtKey()
        Wallet.walletIdCounter += 1

    def getWalletId(self):
        return self._walletId

    def createWalletPubPvtKey(self):
        key = RSA.generate(2048)
        self._walletPubKey = key.publickey().exportKey("PEM")
        self._walletPvtKey = key.exportKey("PEM")

    def getWalletPublicKey(self):
        return self._walletPubKey

    # FIXME : In real life, pvt key has better restrictions
    def getWalletPrivateKey(self):
        return self._walletPvtKey

    # NOTE: We are not storing this in a local object
    def getWalletPublicKeyHash(self):
        return SHA256.new(hashlib.sha256(self._walletPubKey).hexdigest().encode())

    def __str__(self):
        return f"Wallet( Id = {str(self.getWalletId())} , PubKeyHash = {self.getWalletPublicKeyHash().hexdigest()})"

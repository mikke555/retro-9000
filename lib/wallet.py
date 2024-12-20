from eth_account import Account
from eth_account.messages import encode_defunct

from lib.http import HttpClient


class Wallet(HttpClient):
    def __init__(self, private_key: str, counter: str = None, proxy: str = None):
        super().__init__(proxy=proxy)
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        self.label = f"{counter} {self.address} | "

    def __str__(self) -> str:
        return f"Wallet(address={self.address})"

    def sign_message(self, message: str) -> str:
        message_encoded = encode_defunct(text=message)
        signed_message = self.account.sign_message(message_encoded)

        return "0x" + signed_message.signature.hex()

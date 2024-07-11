from substrateinterface import Keypair, KeypairType


def sign_message(keypair: Keypair, message: str):
    """
    Sign a message with a keypair.
    :param keypair: Keypair object
    :param message: The message to sign
    :return: Tuple containing signature and public key in hex format
    """
    signature = keypair.sign(message.encode('utf-8'))
    return signature.hex(), keypair.public_key.hex()


def verify_message(public_key_hex: str, message: str, received_signature_hex: str):
    """
    Verify a signed message with a public key and signature.
    :param public_key_hex: Public key in hex format
    :param message: The original message
    :param received_signature_hex: The signature in hex format
    :return: Boolean indicating whether the signature is valid
    """
    public_key = bytes.fromhex(public_key_hex)
    received_signature = bytes.fromhex(received_signature_hex)
    verifier_keypair = Keypair(public_key=public_key, crypto_type=KeypairType.SR25519)
    is_valid = verifier_keypair.verify(message.encode('utf-8'), received_signature)
    return is_valid


"""
Example usage
import json
from substrateinterface import Keypair, KeypairType

# Generate a key pair (or use an existing one)
keypair = Keypair.create_from_uri('//Alice', crypto_type=KeypairType.SR25519)

# JSON data to be signed
data = {
    "name": "Alice",
    "age": 30,
    "city": "Wonderland"
}

# Convert JSON data to string
data_str = json.dumps(data)

# Sign the data
signed_data = sign_message(keypair, data_str)
signature_hex = signed_data["signature"]
public_key_hex = signed_data["public_key"]

print("Signature (hex):", signature_hex)
print("Public Key (hex):", public_key_hex)

# Verify the signature
is_valid = verify_message(public_key_hex, data_str, signature_hex)
print("Is the signature valid?", is_valid)
"""
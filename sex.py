import hashlib
import binascii
import ecdsa
import random
import multiprocessing

def pubkey_to_hash160(public_key_bytes):
    sha256 = hashlib.sha256(public_key_bytes).digest()
    hash160 = hashlib.new('ripemd160')
    hash160.update(sha256)
    return hash160.digest()

def find_private_key(args):
    start_number, end_number, target_hash160 = args
    curve = ecdsa.SECP256k1

    for number in range(start_number, end_number):
        private_key = ecdsa.SigningKey.from_secret_exponent(number, curve)
        public_key = private_key.get_verifying_key().to_string("compressed")
        current_hash160 = pubkey_to_hash160(public_key)

        if current_hash160 == target_hash160:
            return number

    return None

if __name__ == "__main__":
    start_number = 73714918700800278528
    end_number = 73786976294838206463 - 1  # The maximum possible value for a private key in an elliptic curve.
    target_hash160 = bytes.fromhex("20d45a6a762535700ce9e0b216e31994335db8a5")

    # Compute number of vCPUs
    num_vCPUs = multiprocessing.cpu_count()

    # Create equally spaced intervals for each vCPU
    intervals = [(i*(end_number-start_number)//num_vCPUs+start_number, (i+1)*(end_number-start_number)//num_vCPUs+start_number, target_hash160) for i in range(num_vCPUs)]
    
    with multiprocessing.Pool(num_vCPUs) as pool:
        results = pool.map(find_private_key, intervals)
        
    # Filter out any None results (where no key was found)
    results = [result for result in results if result is not None]

    if results:
        for found_private_key in results:
            print(f"Private key found: {found_private_key}")
            print(f"Private key found: {hex(found_private_key)[2:]}")
    else:
        print("No private key found in the specified range.")

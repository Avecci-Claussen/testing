import hashlib
import binascii
import ecdsa
import random
import multiprocessing
from Crypto.Hash import RIPEMD160

def pubkey_to_hash160(public_key_bytes):
    sha256 = hashlib.sha256(public_key_bytes).digest()
    hash160 = RIPEMD160.new(sha256)
    return hash160.hexdigest()

def find_private_key(input_tuple):
    start_number, end_number, target_hash160, max_attempts = input_tuple
    curve = ecdsa.SECP256k1
    searched_values = set()

    for _ in range(max_attempts):
        number = random.randint(start_number, end_number)
        print(f"Scanning private key (decimal): {number}")

        if number in searched_values:
            continue
        searched_values.add(number)

        private_key = ecdsa.SigningKey.from_secret_exponent(number, curve)
        public_key = private_key.get_verifying_key().to_string("compressed")
        current_hash160 = pubkey_to_hash160(public_key)

        if current_hash160 == target_hash160:
            return number

    return None
def parallel_private_key_search(start_number, end_number, target_hash160, num_cores, max_attempts=1000000):
    pool = multiprocessing.Pool(processes=num_cores)
    input_tuples = [(start_number, end_number, target_hash160, max_attempts) for _ in range(num_cores)]

    results = pool.map(find_private_key, input_tuples)
    pool.close()
    pool.join()

    for result in results:
        if result is not None:
            return result

    return None

if __name__ == "__main__":
    start_number = 2**29
    end_number = 2**30 - 1
    target_hash160 = "d39c4704664e1deb76c9331e637564c257d68a08"
    max_attempts = 10000000
    num_cores = 74  # Set the number of CPU cores you want to use.

    found_private_key = parallel_private_key_search(start_number, end_number, target_hash160, num_cores, max_attempts)
    if found_private_key:
        print(f"Private key found:{found_private_key}")
        print(f"Private key found:{ hex(found_private_key) [2:]  }")
    else:
        print("No private key found in the specified range.")
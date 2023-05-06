import hashlib
import binascii
import ecdsa
import random
import multiprocessing

def pubkey_to_hash160(public_key_bytes):
    sha256 = hashlib.sha256(public_key_bytes).digest()
    hash160 = hashlib.new('ripemd160')
    hash160.update(sha256)
    return hash160.hexdigest()

def find_private_key(input_tuple):
    start_number, end_number, target_hash160, max_attempts = input_tuple
    curve = ecdsa.SECP256k1

    for number in range(start_number, end_number + 1)
    print(f"Scanning private key (decimal): {number}"):

        private_key = ecdsa.SigningKey.from_secret_exponent(number, curve)
        public_key = private_key.get_verifying_key().to_string("compressed")
        current_hash160 = pubkey_to_hash160(public_key)

        if current_hash160 == target_hash160:
            return number

    return None

def parallel_private_key_search(start_number, end_number, target_hash160, num_cores):
    segment_size = (end_number - start_number) // num_cores
    input_tuples = [(start_number + i * segment_size, start_number + (i + 1) * segment_size, target_hash160, segment_size) for i in range(num_cores)]

    # Fix the end number for the last tuple
    last_start, _, _, _ = input_tuples[-1]
    input_tuples[-1] = (last_start, end_number, target_hash160, segment_size)

    pool = multiprocessing.Pool(processes=num_cores)
    results = pool.map(find_private_key, input_tuples)
    pool.close()
    pool.join()

    for result in results:
        if result is not None:
            return result

    return None

if __name__ == "__main__":
    start_number = 36893488147419103232
    end_number = 73786976294838206463
    target_hash160 = "20d45a6a762535700ce9e0b216e31994335db8a5"
    num_cores = 78  # Set the number of CPU cores you want to use.

    found_private_key = parallel_private_key_search(start_number, end_number, target_hash160, num_cores)
    if found_private_key:
        print(f"Private key found:{found_private_key}")
        print(f"Private key found:{ hex(found_private_key) [2:]  }")
    else:
        print("No private key found in the specified range.")

import hashlib
import binascii
import ecdsa
import random
import multiprocessing
import time
import threading

def pubkey_to_hash160(public_key_bytes):
    sha256 = hashlib.sha256(public_key_bytes).digest()
    hash160 = hashlib.new('ripemd160')
    hash160.update(sha256)
    return hash160.hexdigest()

def find_private_key(input_tuple, progress_counter):
    start_number, end_number, target_hash160, max_attempts = input_tuple
    curve = ecdsa.SECP256k1

    for number in range(start_number, end_number + 1):
        with progress_counter.get_lock():
            progress_counter.value += 1

        private_key = ecdsa.SigningKey.from_secret_exponent(number, curve)
        public_key = private_key.get_verifying_key().to_string("compressed")
        current_hash160 = pubkey_to_hash160(public_key)

        if current_hash160 == target_hash160:
            return number

    return None

def report_progress(progress_counter):
    while True:
        time.sleep(10)
        with progress_counter.get_lock():
            keys_scanned = progress_counter.value
            print(f"{keys_scanned} keys scanned so far.")
            progress_counter.value = 0

def parallel_private_key_search(start_number, end_number, target_hash160, num_cores):
    segment_size = (end_number - start_number) // num_cores
    input_tuples = [(start_number + i * segment_size, start_number + (i + 1) * segment_size, target_hash160, segment_size) for i in range(num_cores)]

    # Fix the end number for the last tuple
    last_start, _, _, _ = input_tuples[-1]
    input_tuples[-1] = (last_start, end_number, target_hash160, segment_size)

    progress_counter = multiprocessing.Value('L', 0)
    progress_thread = threading.Thread(target=report_progress, args=(progress_counter,))
    progress_thread.start()

    with multiprocessing.Pool(processes=num_cores) as pool:
        results = [pool.apply_async(find_private_key, args=(t, progress_counter)) for t in input_tuples]
        results = [res.get() for res in results]

    progress_thread.join()

    for result in results:
        if result is not None:
            return result

    return None

if __name__ == "__main__":
    start_number = 2**29
    end_number = 2**30
    target_hash160 = "d39c4704664e1deb76c9331e637564c257d68a08"
    num_cores = 78  # Set the number of CPU cores you want to use.

    found_private_key = parallel_private_key_search(start_number, end_number, target_hash160, num_cores)
    if found_private_key:
        print(f"Private key found:{found_private_key}")
        print(f"Private key found:{ hex(found_private_key) [2:]  }")
    else:
        print("No private key found in the specified range.")

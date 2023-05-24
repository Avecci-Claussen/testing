import hashlib
import binascii
import ecdsa
import random
import multiprocessing
import time

def pubkey_to_hash160(public_key_bytes):
    sha256 = hashlib.sha256(public_key_bytes).digest()
    hash160 = hashlib.new('ripemd160')
    hash160.update(sha256)
    return hash160.hexdigest()

def find_private_key(start_number, end_number, target_hash160, shared_dict):
    curve = ecdsa.SECP256k1

    for number in range(start_number, end_number+1):
        with shared_dict.get_lock():
            shared_dict['keys_scanned'] += 1

        private_key = ecdsa.SigningKey.from_secret_exponent(number, curve)
        public_key = private_key.get_verifying_key().to_string("compressed")
        current_hash160 = pubkey_to_hash160(public_key)

        if current_hash160 == target_hash160:
            return number

    return None

def monitor(shared_dict):
    start_time = time.time()

    while True:
        time.sleep(10)  # wait for 10 seconds
        with shared_dict.get_lock():
            keys_scanned = shared_dict['keys_scanned']
            shared_dict['keys_scanned'] = 0  # reset the counter

        print(f"Speed: {keys_scanned / (time.time() - start_time)} keys/s")

def worker(args):
    return find_private_key(*args)

if __name__ == "__main__":
    start_number = 73714918700800278528
    end_number = 73786976294838206463 - 1  
    target_hash160 = "20d45a6a762535700ce9e0b216e31994335db8a5"
    vcpus = 56

    # A shared dictionary
    manager = multiprocessing.Manager()
    shared_dict = manager.dict()
    shared_dict['keys_scanned'] = 0

    # Start the monitor process
    monitor_process = multiprocessing.Process(target=monitor, args=(shared_dict,))
    monitor_process.start()

    # Divide the work among the available CPUs
    pool = multiprocessing.Pool(vcpus)
    ranges = [(start_number + i * (end_number - start_number) // vcpus, 
               start_number + (i+1) * (end_number - start_number) // vcpus, 
               target_hash160, shared_dict) for i in range(vcpus)]

    results = pool.map(worker, ranges)

    # Check for a valid result
    for result in results:
        if result is not None:
            print(f"Private key found:{result}")
            print(f"Private key found:{ hex(result) [2:]  }")
            pool.terminate()  # Stop all worker processes
            monitor_process.terminate()  # Stop the monitor process
            break
    else:
        print("No private key found in the specified range.")

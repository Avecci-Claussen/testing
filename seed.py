import random
import concurrent.futures
import os

def read_known_outputs(file_name):
    with open(file_name, 'r') as file:
        return [int(line.strip()) for line in file]

def generate_mt_outputs(seed, count=65):
    random.seed(seed)
    return [random.getrandbits(32) for _ in range(count)]

def hamming_distance(n1, n2):
    return bin(n1 ^ n2).count('1')

def brute_force_seed_range(start, end, known_outputs, similarity_threshold=5):
    similar_seeds = []

    for potential_seed in range(start, end):
        generated_outputs = generate_mt_outputs(potential_seed)
        total_similarity = sum(hamming_distance(generated, known) for generated, known in zip(generated_outputs, known_outputs))

        if total_similarity <= similarity_threshold:
            similar_seeds.append(potential_seed)
            with open('pos.txt', 'a') as file:  # append to file in real-time
                file.write(str(potential_seed) + '\n')
            print(f"Found a potential seed with similarity: {potential_seed}")

    return similar_seeds

def parallel_brute_force(known_outputs, max_seed=2**32, num_processes=None):
    chunk_size = max_seed // num_processes
    all_similar_seeds = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = [executor.submit(brute_force_seed_range, i * chunk_size, (i+1) * chunk_size, known_outputs) for i in range(num_processes)]
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                all_similar_seeds.extend(result)

    return all_similar_seeds

if __name__ == "__main__":
    known_outputs = read_known_outputs('dec.txt')

    if len(known_outputs) != 65:
        print("The file 'dec.txt' should contain exactly 65 known outputs.")
        exit()

    num_cpus = os.cpu_count()
    print(f"Detected {num_cpus} CPUs, initiating parallel brute force...")

    similar_seeds = parallel_brute_force(known_outputs, num_processes=num_cpus)

    if similar_seeds:
        print(f"Finished. Found {len(similar_seeds)} potential seeds with similar outputs. Check 'pos.txt' for the seeds.")
    else:
        print("No similar seeds found in the tested range.")

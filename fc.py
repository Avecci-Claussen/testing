import argparse
import multiprocessing

def find_solutions_for_chunk(args):
    start, end, index = args
    solutions = []
    for privkey in range(start, end + 1):
        mod_value = 2 ** index - privkey
        if mod_value >= 0 and mod_value < privkey and 2 ** index == privkey + mod_value:
            solutions.append((privkey, mod_value))
    return solutions

def find_solutions(index):
    num_processes = multiprocessing.cpu_count()  # Number of available CPUs
    chunk_size = (int(2 ** (index - 0.10)) - max(2 * index, 2 ** (index - 1))) // num_processes

    args_list = [
        (max(2 * index, 2 ** (index - 1)) + chunk_size * i, 
         max(2 * index, 2 ** (index - 1)) + chunk_size * (i + 1) - 1,  # Subtracted 1 to make the end exclusive
         index) 
        for i in range(num_processes)
    ]

    with multiprocessing.Pool(num_processes) as pool:
        all_solutions = pool.map(find_solutions_for_chunk, args_list)

    # Flattening the list of lists
    return [solution for sublist in all_solutions for solution in sublist]

def main():
    parser = argparse.ArgumentParser(description="Find solutions for the equation 2^index = privkey + mod_value")
    parser.add_argument("-n", type=int, help="The index value")
    args = parser.parse_args()

    if args.n is not None:
        solutions = find_solutions(args.n)
        
        if solutions:
            print(f"Solutions for index {args.n}:")
            for idx, (privkey, mod_value) in enumerate(solutions, start=1):
                print(f"# {idx}: puzz_num: {args.n}, privkey: {privkey}, mod: {mod_value}")
        else:
            print(f"No solutions found for index {args.n}")
    else:
        print("Please provide the -n argument.")

if __name__ == "__main__":
    main()

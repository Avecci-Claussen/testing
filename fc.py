import argparse

def find_solutions(index):
    solutions = []
    for privkey in range(max(2 * index, 2 ** (index - 1)), int(2 ** (index - 0.10)) + 1):
        mod_value = 2 ** index - privkey
        if mod_value >= 0 and mod_value < privkey and 2 ** index == privkey + mod_value:
            solutions.append((privkey, mod_value))
    return solutions

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
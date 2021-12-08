import random
import time
from rubik import solve
from rubik.cube import Cube
from rubik.solve import Solver
from rubik.optimize import optimize_moves

SOLVED_CUBE_STR = """
    OOO
    OOO
    OOO
GGG WWW BBB YYY
GGG WWW BBB YYY
GGG WWW BBB YYY
    RRR
    RRR
    RRR
"""
#SOLVED_CUBE_STR = "OOOOOOOOOYYYWWWGGGBBBYYYWWWGGGBBBYYYWWWGGGBBBRRRRRRRRR"
#SOLVED_CUBE_STR = "YGOYORYOWBBBRWOYGWOBGOYYWWWGGOGBYYBRWWRGYORBBGRBORRWRG"
MOVES = ["L", "R", "U", "D", "F", "B", "M", "E", "S"]


def random_cube():
    """
    :return: A new scrambled Cube
    """
    scramble_moves = " ".join(random.choices(MOVES, k=200))
    print ("scramble = ", scramble_moves)
    a = Cube(SOLVED_CUBE_STR)
    print("unscrampled cube: ", a)
    a.sequence(scramble_moves)
    return a


def run():
    successes = 0
    failures = 0

    avg_opt_moves = 0.0
    avg_moves = 0.0
    avg_time = 0.0
    count = 0
    while True:

        C = random_cube()
        C1 = Cube(C)
        assert C == C1
        print("\n\n",C)
        C.orientToFront()
        C1.orientToFront()

        #C.orientToFront()
        #print("\n\n", C)
        
        solver = Solver(C)

        start = time.time()
        solver.solve()
        duration = time.time() - start

        C1.sequence(" ".join(solver.moves))
        print ("C1 = ", C1)
        print(" ".join(solver.moves))
        assert C == C1

        if C.is_solved():
            opt_moves = optimize_moves(solver.moves)
            successes += 1
            avg_moves = (avg_moves * (successes - 1) + len(solver.moves)) / float(successes)
            avg_time = (avg_time * (successes - 1) + duration) / float(successes)
            avg_opt_moves = (avg_opt_moves * (successes - 1) + len(opt_moves)) / float(successes)
        else:
            failures += 1
            print(f"Failed ({successes + failures}): {C.flat_str()}")

        total = successes + failures
        if total == 1 or total % 100 == 0:
            pass_percentage = 100 * successes / total
            print(f"{total}: {successes} successes ({pass_percentage:0.3f}% passing)"
                  f" avg_moves={avg_moves:0.3f} avg_opt_moves={avg_opt_moves:0.3f}"
                  f" avg_time={avg_time:0.3f}s")


if __name__ == '__main__':
    solve.DEBUG = True
    run()

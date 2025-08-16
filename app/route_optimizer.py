def ga_optimize_route(start, disposal, required=None, population_size=30, generations=40, mutation_rate=0.2):
    # Build all possible nodes
    nodes = list(NETWORK.keys())
    nodes.remove(start)
    nodes.remove(disposal)
    if required and required in nodes:
        nodes.remove(required)
    # Initial population: random permutations with required node in the middle if needed
    population = []
    for _ in range(population_size):
        middle = [required] if required else []
        rest = nodes.copy()
        random.shuffle(rest)
        route = [start] + middle + rest + [disposal]
        # Remove unreachable nodes from route
        filtered = [start]
        for n in route[1:]:
            if n in NETWORK[filtered[-1]]:
                filtered.append(n)
        if filtered[-1] != disposal:
            filtered.append(disposal)
        population.append(filtered)

    def fitness(route):
        # Penalize if required node is missing
        penalty = 1000 if required and required not in route else 0
        return get_distance(route) + penalty

    for _ in range(generations):
        # Evaluate fitness
        population = sorted(population, key=fitness)
        # Selection: keep top 50%
        survivors = population[:population_size//2]
        # Crossover
        children = []
        while len(children) < population_size//2:
            p1, p2 = random.sample(survivors, 2)
            cut = random.randint(1, len(p1)-2)
            child = p1[:cut] + [n for n in p2 if n not in p1[:cut]]
            # Ensure start and disposal
            if child[0] != start:
                child = [start] + child
            if child[-1] != disposal:
                child = child + [disposal]
            children.append(child)
        # Mutation
        for child in children:
            if random.random() < mutation_rate and len(child) > 3:
                i, j = random.sample(range(1, len(child)-1), 2)
                child[i], child[j] = child[j], child[i]
        population = survivors + children
    # Return best route
    best = min(population, key=fitness)
    return best, get_distance(best)

from distance_matrix import get_distance
import random

NETWORK = {
    "Source": ["Inspection A", "Inspection B", "Inspection C", "Node W"],
    "Inspection A": ["Node X"],
    "Inspection B": ["Node Y"],
    "Inspection C": ["Node Z"],
    "Node X": ["Disposal A"],
    "Node Y": ["Disposal B"],
    "Node Z": ["Disposal C"],
    "Node W": ["Disposal A", "Disposal B", "Disposal C"],
    "Disposal A": [], "Disposal B": [], "Disposal C": []
}

def find_all_routes(graph, start, end, path=None):
    if path is None:
        path = []
    path = path + [start]
    if start == end:
        return [path]
    if start not in graph:
        return []
    routes = []
    for node in graph[start]:
        if node not in path:
            newroutes = find_all_routes(graph, node, end, path)
            for nr in newroutes:
                routes.append(nr)
    return routes

def optimize_route(waste_type):
    """
    Uses a true genetic algorithm to find the best route from Source to the correct Disposal node.
    """
    if waste_type == "Flammable":
        required = "Inspection A"
        disposal = "Disposal A"
    elif waste_type == "Corrosive":
        required = "Inspection B"
        disposal = "Disposal B"
    elif waste_type == "Toxic":
        required = "Inspection C"
        disposal = "Disposal C"
    else:
        required = None
        disposal = "Disposal A"
    best_route, cost = ga_optimize_route("Source", disposal, required)
    return best_route, cost
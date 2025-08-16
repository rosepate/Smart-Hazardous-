# distance_matrix.py
# Simple mock distance matrix for 6 nodes

# Nodes: Source, Inspection A, Inspection B, Inspection C, Node X, Node Y, Node Z, Node W, Disposal

distances = {
    ("Source", "Inspection A"): 5,
    ("Source", "Inspection B"): 6,
    ("Source", "Inspection C"): 7,
    ("Inspection A", "Node X"): 8,
    ("Inspection B", "Node Y"): 9,
    ("Inspection C", "Node Z"): 10,
    ("Node X", "Disposal"): 11,
    ("Node Y", "Disposal"): 12,
    ("Node Z", "Disposal"): 13,
    ("Source", "Node W"): 4,
    ("Node W", "Disposal"): 14
}

def get_distance(route):
    total = 0
    for i in range(len(route)-1):
        total += distances.get((route[i], route[i+1]), 0)
    return total

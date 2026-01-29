"""
Example: Multi-segment image segmentation using gco.cut_general_graph()

This example demonstrates the CORRECT way to use pyGCO for multi-segment
segmentation, addressing a common confusion about unary costs.

KEY CONCEPT: The GCO library MINIMIZES total energy, so:
- Unary costs: LOWER values = pixel is MORE LIKELY to belong to that label
- If you have probabilities/scores where HIGHER is better, NEGATE them first

Common mistake: Using one-hot encoded labels (1 where pixel belongs, 0 elsewhere)
directly as unary costs. This is WRONG because GCO will interpret 1 as high cost
(pixel should NOT have that label).

Correct approach: Either:
1. Use negative log-probabilities as costs: cost = -log(probability)
2. Negate scores/probabilities: cost = -score
3. Use distance/error measures directly as costs (already lower is better)
"""

import numpy as np
import gco


def get_uniform_grid_edges(height, width):
    """Create edges for a uniform 2D grid graph."""
    E = (height - 1) * width + height * (width - 1)
    edges = np.empty((E, 2), dtype=np.int32)
    edge_weights = np.ones(E, dtype=np.float32)
    idx = 0
    
    # horizontal edges
    for row in range(height):
        edges[idx:idx+width-1, 0] = np.arange(width-1) + row * width
        edges[idx:idx+width-1, 1] = np.arange(width-1) + row * width + 1
        idx += width-1
    
    # vertical edges
    for col in range(width):
        edges[idx:idx+height-1, 0] = np.arange(0, (height-1)*width, width) + col
        edges[idx:idx+height-1, 1] = np.arange(width, height*width, width) + col
        idx += height-1
    
    return edges, edge_weights


def example_with_one_hot_labels():
    """Example showing the WRONG and RIGHT way to use one-hot encoded labels."""
    print("=" * 70)
    print("Example 1: Using one-hot encoded labels")
    print("=" * 70)
    
    # Create a simple 3x3 grid with 3 segments
    height, width = 3, 3
    num_labels = 3
    
    # Simulate one-hot encoded "ground truth" (e.g., from k-means)
    # This represents: "pixel i belongs to label j with confidence 1.0"
    one_hot_labels = np.zeros((height * width, num_labels))
    one_hot_labels[0:3, 0] = 1.0  # First row belongs to label 0
    one_hot_labels[3:6, 1] = 1.0  # Second row belongs to label 1
    one_hot_labels[6:9, 2] = 1.0  # Third row belongs to label 2
    
    print("\nOne-hot encoded labels (higher value = pixel belongs to that label):")
    print(one_hot_labels.reshape(height, width, num_labels))
    print("\nExpected segmentation (argmax):")
    print(np.argmax(one_hot_labels, axis=1).reshape(height, width))
    
    # Create grid edges with zero pairwise costs (no smoothness)
    edges, edge_weights = get_uniform_grid_edges(height, width)
    pairwise = np.zeros((num_labels, num_labels))
    
    # WRONG: Use one-hot directly as unary costs
    print("\n" + "=" * 70)
    print("WRONG APPROACH: Using one-hot directly as costs")
    print("=" * 70)
    wrong_labels = gco.cut_general_graph(
        edges, edge_weights, one_hot_labels, pairwise, algorithm='swap'
    )
    print("Result (WRONG - mostly label 0):")
    print(wrong_labels.reshape(height, width))
    print("Why wrong? GCO minimizes cost. High one-hot values (1.0) are interpreted")
    print("as HIGH COST, so GCO avoids those labels!")
    
    # RIGHT: Negate one-hot to convert to costs
    print("\n" + "=" * 70)
    print("CORRECT APPROACH: Negate one-hot to convert probabilities to costs")
    print("=" * 70)
    unary_cost = -one_hot_labels  # Now: lower cost where pixel belongs
    correct_labels = gco.cut_general_graph(
        edges, edge_weights, unary_cost, pairwise, algorithm='swap'
    )
    print("Result (CORRECT - matches expected):")
    print(correct_labels.reshape(height, width))
    print("Why correct? After negation, label with value 1.0 becomes cost -1.0,")
    print("which is the LOWEST cost, so GCO prefers it!")


def example_with_probabilities():
    """Example showing how to use classifier probabilities."""
    print("\n\n" + "=" * 70)
    print("Example 2: Using classifier probabilities")
    print("=" * 70)
    
    # Create a simple 2x2 grid with 2 labels
    height, width = 2, 2
    num_labels = 2
    
    # Simulate classifier probabilities (e.g., from a neural network)
    # probabilities[i, j] = P(pixel i has label j)
    probabilities = np.array([
        [0.9, 0.1],  # pixel 0: 90% label 0, 10% label 1
        [0.8, 0.2],  # pixel 1: 80% label 0, 20% label 1
        [0.3, 0.7],  # pixel 2: 30% label 0, 70% label 1
        [0.2, 0.8],  # pixel 3: 20% label 0, 80% label 1
    ])
    
    print("\nClassifier probabilities:")
    print(probabilities)
    print("\nExpected segmentation (argmax):")
    print(np.argmax(probabilities, axis=1).reshape(height, width))
    
    # Create grid edges
    edges, edge_weights = get_uniform_grid_edges(height, width)
    pairwise = (1 - np.eye(num_labels)) * 0.1  # Small smoothness penalty
    
    # Convert probabilities to costs using negative log-likelihood
    # This is a common and theoretically sound approach
    epsilon = 1e-10  # Avoid log(0)
    unary_cost = -np.log(probabilities + epsilon)
    
    print("\n" + "=" * 70)
    print("Using negative log-probabilities as costs")
    print("=" * 70)
    print("Unary cost = -log(probability):")
    print(unary_cost)
    
    labels = gco.cut_general_graph(
        edges, edge_weights, unary_cost, pairwise, algorithm='expansion'
    )
    print("\nResult:")
    print(labels.reshape(height, width))


def example_with_distances():
    """Example showing how to use distance/error measures."""
    print("\n\n" + "=" * 70)
    print("Example 3: Using pixel-to-centroid distances")
    print("=" * 70)
    
    # Create a simple 3x3 grid with 3 labels
    height, width = 3, 3
    num_labels = 3
    
    # Simulate pixel features (e.g., RGB values)
    np.random.seed(42)
    pixel_features = np.random.rand(height * width, 3)
    
    # Cluster centroids
    centroids = np.array([
        [0.2, 0.3, 0.4],  # label 0 centroid
        [0.5, 0.6, 0.7],  # label 1 centroid
        [0.8, 0.9, 1.0],  # label 2 centroid
    ])
    
    # Compute distances from each pixel to each centroid
    # Distance is already a cost (lower = more similar = more likely)
    unary_cost = np.zeros((height * width, num_labels))
    for i in range(height * width):
        for j in range(num_labels):
            unary_cost[i, j] = np.linalg.norm(pixel_features[i] - centroids[j])
    
    print("\nUnary costs (pixel-to-centroid Euclidean distances):")
    print(unary_cost[:5])  # Show first 5 pixels
    print("\nExpected segmentation (argmin of distances):")
    print(np.argmin(unary_cost, axis=1).reshape(height, width))
    
    # Create grid edges
    edges, edge_weights = get_uniform_grid_edges(height, width)
    pairwise = (1 - np.eye(num_labels)) * 0.5
    
    labels = gco.cut_general_graph(
        edges, edge_weights, unary_cost, pairwise, algorithm='expansion'
    )
    print("\nResult (with smoothness):")
    print(labels.reshape(height, width))
    print("\nNote: Distances are already costs (lower = better), so use them directly!")


if __name__ == "__main__":
    example_with_one_hot_labels()
    example_with_probabilities()
    example_with_distances()
    
    print("\n\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("✓ GCO MINIMIZES energy, so use COSTS (lower = better)")
    print("✓ If you have scores/probabilities (higher = better), NEGATE them")
    print("✓ Common conversions:")
    print("  - Probabilities: cost = -log(probability)")
    print("  - Scores: cost = -score")
    print("  - Distances: cost = distance (already lower is better)")
    print("=" * 70)

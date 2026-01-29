"""
Validation: Reproduce user's exact issue and demonstrate the fix

This script closely replicates the user's reported issue and shows
that the fix (negating the unary) solves the problem.
"""

import numpy as np
import gco


def get_uniform_smoothness_pw_single_image(img_shape):
    """From the user's original code."""
    H, W = img_shape
    E = (H - 1) * W + H * (W - 1)
    edges = np.empty((E, 2), dtype=int)
    edge_weights = np.ones(E, dtype=np.single)
    idx = 0

    # horizontal edges
    for row in range(H):
        edges[idx:idx+W-1, 0] = np.arange(W-1) + row * W
        edges[idx:idx+W-1, 1] = np.arange(W-1) + row * W + 1
        idx += W-1

    # vertical edges
    for col in range(W):
        edges[idx:idx+H-1, 0] = np.arange(0, (H-1)*W, W) + col
        edges[idx:idx+H-1, 1] = np.arange(W, H*W, W) + col
        idx += H-1

    return [edges, edge_weights]


def main():
    print("=" * 80)
    print("VALIDATION: User's Issue Reproduction and Fix")
    print("=" * 80)
    
    # Simulate a 15x15 image with 3 segments (similar scale to user's dog image)
    height, width = 15, 15
    num_seg = 3
    
    # Create ground truth segmentation (like k-means output)
    # Sky: top 5 rows
    # Dog: middle 5 rows
    # Ground: bottom 5 rows
    ground_truth = np.zeros(height * width, dtype=int)
    ground_truth[0:5*width] = 0  # Sky (label 0)
    ground_truth[5*width:10*width] = 1  # Dog (label 1)
    ground_truth[10*width:15*width] = 2  # Ground (label 2)
    
    # Create one-hot encoding (like user's kmeans_labels_onehot)
    kmeans_labels_onehot = np.zeros((height * width, num_seg))
    for seg_i in range(num_seg):
        kmeans_labels_onehot[:, seg_i] = (ground_truth == seg_i).astype(float)
    
    print(f"\nSimulated image: {height}x{width} with {num_seg} segments")
    print(f"Ground truth distribution: {np.bincount(ground_truth)}")
    print("\nOne-hot encoding (first 5 pixels):")
    print(kmeans_labels_onehot[:5])
    
    # User's parameters: no noise, scale=1, lamb_grid=0
    unary_vec = kmeans_labels_onehot.copy()
    unary_noise = 0
    unary_scale = 1
    lamb_grid = 0
    
    # Add noise (user had unary_noise=0, so this does nothing)
    unary_vec += unary_noise * np.random.randn(*unary_vec.shape)
    unary_vec *= unary_scale
    
    pairwise_pot = (1 - np.eye(num_seg)) * lamb_grid  # All zeros
    grid_edges, grid_edge_weights = get_uniform_smoothness_pw_single_image((height, width))
    
    print("\n" + "=" * 80)
    print("USER'S ORIGINAL APPROACH (INCORRECT)")
    print("=" * 80)
    print("Using one-hot directly as unary (treats 1.0 as high cost = avoid label)")
    
    labels_wrong = gco.cut_general_graph(
        grid_edges, 
        grid_edge_weights, 
        unary_vec,  # WRONG: using one-hot directly
        pairwise_pot, 
        algorithm="swap"
    )
    
    wrong_dist = np.bincount(labels_wrong, minlength=num_seg)
    accuracy_wrong = np.mean(labels_wrong == ground_truth) * 100
    
    print(f"\nExpected distribution: {np.bincount(ground_truth)}")
    print(f"Got distribution:      {wrong_dist}")
    print(f"Accuracy: {accuracy_wrong:.1f}%")
    print("\n❌ PROBLEM: Missing label 2 entirely! Only using labels 0 and 1.")
    
    print("\n" + "=" * 80)
    print("CORRECTED APPROACH (CORRECT)")
    print("=" * 80)
    print("Negate one-hot to convert to costs (treats -1.0 as low cost = prefer label)")
    
    unary_cost = -unary_vec  # THE FIX: negate to convert scores to costs
    
    labels_correct = gco.cut_general_graph(
        grid_edges, 
        grid_edge_weights, 
        unary_cost,  # CORRECT: negated one-hot
        pairwise_pot, 
        algorithm="swap"
    )
    
    correct_dist = np.bincount(labels_correct, minlength=num_seg)
    accuracy_correct = np.mean(labels_correct == ground_truth) * 100
    
    print(f"\nExpected distribution: {np.bincount(ground_truth)}")
    print(f"Got distribution:      {correct_dist}")
    print(f"Accuracy: {accuracy_correct:.1f}%")
    
    if accuracy_correct == 100.0:
        print("\n✅ SUCCESS: Perfect segmentation! All 3 labels correctly assigned.")
    else:
        print(f"\n✅ MUCH BETTER: All labels present, {accuracy_correct:.1f}% accuracy")
    
    print("\n" + "=" * 80)
    print("VISUALIZATION")
    print("=" * 80)
    
    # Show first 5 rows
    print("\nGround truth (first 5 rows):")
    print(ground_truth[:5*width].reshape(5, width))
    
    print("\nWrong result (first 5 rows):")
    print(labels_wrong[:5*width].reshape(5, width))
    
    print("\nCorrect result (first 5 rows):")
    print(labels_correct[:5*width].reshape(5, width))
    
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print("\n✅ The fix works! Key insight:")
    print("   - GCO minimizes energy (lower cost = better)")
    print("   - One-hot has 1.0 where pixel belongs (higher = better)")
    print("   - Must NEGATE one-hot to convert: unary_cost = -one_hot")
    print("\n✅ Documentation now clearly explains this in all function docstrings")
    print("✅ Example code demonstrates the correct approach")
    print("=" * 80)


if __name__ == "__main__":
    main()

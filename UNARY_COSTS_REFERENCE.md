# Quick Reference: Unary Costs in pyGCO

## ⚡ Quick Answer

**GCO minimizes energy**, so:
- ✅ **Lower** unary cost = pixel **should** have this label
- ❌ **Higher** unary cost = pixel **should not** have this label

## 🔄 Common Conversions

### From Probabilities/Scores (higher = better)
```python
# If your values represent "confidence" or "probability"
# where 1.0 means "definitely this label"
unary_cost = -scores
```

### From Classifier Probabilities
```python
# More principled: negative log-likelihood
epsilon = 1e-10  # Avoid log(0)
unary_cost = -np.log(probabilities + epsilon)
```

### From One-Hot Encoding (k-means, etc.)
```python
# One-hot: 1.0 where pixel belongs, 0.0 elsewhere
kmeans_labels_onehot = ...  # shape: (n_pixels, n_labels)

# WRONG: Using directly
# labels = gco.cut_general_graph(edges, weights, kmeans_labels_onehot, pairwise)

# CORRECT: Negate first
unary_cost = -kmeans_labels_onehot
labels = gco.cut_general_graph(edges, weights, unary_cost, pairwise)
```

### From Distance/Error Measures
```python
# Distances are already costs (lower = more similar)
# Use directly, no conversion needed!
unary_cost = distances  # e.g., L2 distance to cluster centers
```

## 📊 Example

```python
import numpy as np
import gco

# Simulate 3-class segmentation
n_pixels = 100
n_labels = 3

# You have scores from a classifier (higher = more confident)
scores = np.random.rand(n_pixels, n_labels)

# Convert to costs (lower = more confident)
unary_cost = -scores

# Setup graph
edges = np.array([[i, i+1] for i in range(n_pixels-1)])
edge_weights = np.ones(len(edges))
pairwise = (1 - np.eye(n_labels)) * 0.5

# Run optimization
labels = gco.cut_general_graph(edges, edge_weights, unary_cost, pairwise)
```

## 🚫 Common Mistake

```python
# ❌ WRONG: Using scores directly
labels = gco.cut_general_graph(edges, weights, scores, pairwise)

# ✅ CORRECT: Negate scores first
labels = gco.cut_general_graph(edges, weights, -scores, pairwise)
```

## 📚 More Information

- See `examples/multisegment_example.py` for detailed examples
- See `FIX_SUMMARY.md` for technical details
- See function docstrings for parameter descriptions

## 🔍 Debugging

If you're getting unexpected results:

1. Check if your unary values make sense:
   ```python
   print("Unary shape:", unary_cost.shape)
   print("Unary range:", unary_cost.min(), "to", unary_cost.max())
   print("Expected labels (argmin):", np.argmin(unary_cost, axis=1)[:10])
   ```

2. With zero pairwise costs, result should match argmin:
   ```python
   pairwise = np.zeros((n_labels, n_labels))
   labels = gco.cut_general_graph(edges, weights, unary_cost, pairwise)
   expected = np.argmin(unary_cost, axis=1)
   print("Match?", np.array_equal(labels, expected))
   ```

3. If not matching, your unary interpretation is likely inverted:
   ```python
   # Try negating
   labels = gco.cut_general_graph(edges, weights, -unary_cost, pairwise)
   ```

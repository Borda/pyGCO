# Multi-segment Segmentation Example

This example demonstrates the correct way to use pyGCO for multi-segment image segmentation, particularly when working with probabilities, scores, or one-hot encoded labels.

## The Problem

A common mistake when using graph cut optimization is to provide unary values that represent **probabilities** or **scores** (where higher is better) directly as costs to the GCO library. This leads to incorrect segmentation because:

**The GCO library MINIMIZES total energy**, which means:
- **Lower** unary cost = pixel is **MORE likely** to take that label
- **Higher** unary cost = pixel is **LESS likely** to take that label

## The Solution

If your unary values represent probabilities, scores, or confidences (where higher means the pixel belongs to that label), you must **convert them to costs** first.

### Common Conversions

1. **One-hot encoded labels or confidence scores**:
   ```python
   unary_cost = -scores  # Negate to convert to costs
   ```

2. **Probabilities**:
   ```python
   epsilon = 1e-10  # Avoid log(0)
   unary_cost = -np.log(probabilities + epsilon)
   ```

3. **Distances/errors** (already costs):
   ```python
   unary_cost = distances  # Use directly, no conversion needed
   ```

## Running the Example

```bash
python multisegment_example.py
```

This will show three examples:
1. **One-hot encoded labels**: Demonstrates the WRONG vs. RIGHT approach
2. **Classifier probabilities**: Shows how to convert probabilities to costs
3. **Distance measures**: Shows that distances are already costs

## Key Takeaways

✓ **Always remember**: GCO minimizes energy, so use COSTS (lower = better)  
✓ **If you have scores/probabilities** (higher = better), NEGATE them  
✓ **If you have distances/errors** (already lower = better), use them directly  

## Related Issue

This example addresses the issue: "Can't segment multisegment image using `gco.cut_general_graph()`"

The problem was not a bug in the library, but a common misunderstanding about how unary costs should be interpreted.

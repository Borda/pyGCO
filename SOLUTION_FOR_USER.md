# Solution: Multi-segment Image Segmentation Issue

## For the Original Issue Reporter

Your code was almost correct! You just needed **one simple change**: negate the unary values.

### The Problem

Your code:
```python
unary_vec = kmeans_labels_onehot  # 1.0 where pixel belongs, 0.0 elsewhere
unary_vec += unary_noise * np.random.randn(*unary_vec.shape)
unary_vec *= unary_scale

labels = gco.cut_general_graph(grid_edges, grid_edge_weights, 
                                unary_vec,  # ❌ WRONG
                                pairwise_pot, algorithm="swap")
```

The issue: GCO minimizes energy, so it interprets:
- High values (1.0) = HIGH COST = avoid this label ❌
- Low values (0.0) = LOW COST = prefer this label ❌

This is **opposite** to your one-hot encoding where 1.0 means "pixel belongs here"!

### The Fix

Add **ONE LINE** to negate the unary:

```python
unary_vec = kmeans_labels_onehot
unary_vec += unary_noise * np.random.randn(*unary_vec.shape)
unary_vec *= unary_scale

unary_vec = -unary_vec  # 🔥 ADD THIS LINE

labels = gco.cut_general_graph(grid_edges, grid_edge_weights, 
                                unary_vec,  # ✅ CORRECT
                                pairwise_pot, algorithm="swap")
```

Now:
- High one-hot (1.0) → Low cost (-1.0) = prefer this label ✅
- Low one-hot (0.0) → High cost (0.0) = avoid this label ✅

### Your Complete Fixed Function

```python
def graph_segment(img, num_seg = 2, lamb_grid = 2, unary_noise = 0.1, unary_scale = 3):
    pairwise_pot = (1 - np.eye(num_seg)) * lamb_grid
    grid_edges, grid_edge_weights = get_uniform_smoothness_pw_single_image((img.shape[0], img.shape[1]))
    
    # run kmeans on img to get unaries
    kmeans = KMeans(n_clusters=num_seg, random_state=0).fit(img.reshape(-1, 3))
    kmeans_labels = kmeans.labels_
    
    # create one hot encoding
    kmeans_labels_onehot = np.zeros((len(kmeans_labels), num_seg))
    for seg_i in range(num_seg):
        kmeans_labels_onehot[:, seg_i] = (kmeans_labels.astype(int) == seg_i).flatten()
    
    # Use onehot as unary
    unary_vec = kmeans_labels_onehot
    
    # Add noise to unary    
    unary_vec += unary_noise * np.random.randn(*unary_vec.shape)
    unary_vec *= unary_scale
    
    # 🔥 THE FIX: Negate to convert probabilities/scores to costs
    unary_vec = -unary_vec
    
    # display unaries
    fig, axarr = plt.subplots(1, num_seg, figsize=(2 * num_seg, 2))
    for i in range(num_seg):    
        unary_i = unary_vec[:, i].reshape(*img.shape[:2])
        axarr[i].imshow(unary_i)
        axarr[i].set_title("Unary term #%i" % i)
    plt.show()

    labels = gco.cut_general_graph(grid_edges, 
                               grid_edge_weights, 
                               unary_vec,  # Now correct!
                               pairwise_pot, 
                               algorithm="swap")

    return labels.reshape(*img.shape[:2])
```

### Why This Works

GCO library **minimizes** total energy:
```
E_total = E_unary + E_pairwise
```

By negating your one-hot encoding:
- Pixel that SHOULD be label 0: one-hot [1, 0, 0] → cost [-1, 0, 0] → GCO picks label 0 (lowest cost) ✅
- Pixel that SHOULD be label 1: one-hot [0, 1, 0] → cost [0, -1, 0] → GCO picks label 1 (lowest cost) ✅
- Pixel that SHOULD be label 2: one-hot [0, 0, 1] → cost [0, 0, -1] → GCO picks label 2 (lowest cost) ✅

### Alternative: Use Negative Log-Likelihood

If your one-hot represents probabilities, this is more principled:

```python
# After creating one-hot
epsilon = 1e-10  # Avoid log(0)
unary_vec = -np.log(kmeans_labels_onehot + epsilon)

# Then add noise and scale as before
unary_vec += unary_noise * np.random.randn(*unary_vec.shape)
unary_vec *= unary_scale
```

### Additional Changes in This PR

Beyond fixing your issue, we also:

1. **Fixed a bug**: `pairwise_cost=None` now works correctly
2. **Improved docs**: All function docstrings now clearly explain that unary = costs (lower = better)
3. **Added examples**: See `examples/multisegment_example.py` for detailed examples
4. **Added tests**: New tests ensure this works correctly going forward

### Try It Now

```python
# Your call with the fix:
seg = graph_segment(img, num_seg=3, lamb_grid=0, unary_noise=0, unary_scale=1)
plt.imshow(seg, interpolation="nearest")
plt.title("Partition")
plt.show()
```

You should now see **all 3 segments** correctly identified! 🎉

### Need Help?

- See `UNARY_COSTS_REFERENCE.md` for quick reference
- See `examples/multisegment_example.py` for detailed examples
- See `FIX_SUMMARY.md` for technical details

### Questions?

If you're still having issues, please provide:
1. The shape of your unary array
2. The range of values (min/max)
3. What `np.argmin(unary, axis=1)` gives (should match expected labels)

# catalog-knowledge-graph

A miniature of the two problems every product catalog has: the same product listed five different ways, and attributes missing exactly where shoppers filter on them.

## Problem

Merchants describe the same product differently — word order, abbreviations, sizes and colors in the title, brand present in one feed and absent in another. Until those listings are resolved into one product, search counts them as five products, quality metrics are meaningless, and shoppers see duplicates.

## Approach

`catalog_graph.py` works on 8 synthetic listings and does three things:

1. **Entity resolution** — tokenizes titles, scores pairs with Jaccard similarity, and clusters listings that refer to the same product (single-linkage, threshold 0.45).
2. **Attribute inference** — fills missing brand and color from title tokens against known vocabularies.
3. **Quality queries** — reports which clusters still lack a brand after inference: the work queue for catalog quality, in priority order.

## What the code shows

The pipeline shape matters more than the toy data: resolve first (you cannot measure quality per-product until listings are products), infer second (cheap recall from text), and let the leftover gaps — not raw listing counts — drive the quality roadmap.

## Run

```bash
python3 catalog_graph.py
```

Standard library only. All data is synthetic.

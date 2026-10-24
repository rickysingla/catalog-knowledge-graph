"""Entity resolution and attribute inference over a messy catalog.

Takes synthetic product listings the way they actually arrive from
merchants — the same product listed three ways, attributes missing,
brands buried in titles — and:

  1. resolves duplicates into product clusters (entity resolution),
  2. infers missing attributes (brand, color) from title tokens,
  3. answers graph-style queries (which clusters lack a brand,
     which listings merged into which cluster).

Pure standard library. Run:  python3 catalog_graph.py
"""

import re
from collections import defaultdict

LISTINGS = [
    {"id": 1, "title": "Nike Air Zoom Pegasus 40 Running Shoes - Black, Size 10", "brand": "Nike", "color": None},
    {"id": 2, "title": "Nike Air Zoom Pegasus 40 - Black/Anthracite - US 10", "brand": None, "color": "Black"},
    {"id": 3, "title": "Air Zoom Pegasus 40 Men's Running Shoe Black 10", "brand": None, "color": None},
    {"id": 4, "title": "Adidas Ultraboost Light Running Shoes White Size 9", "brand": "Adidas", "color": "White"},
    {"id": 5, "title": "Ultraboost Light - White - Men's 9", "brand": None, "color": None},
    {"id": 6, "title": "Instant Pot Duo 7-in-1 Pressure Cooker 6 Quart", "brand": "Instant Pot", "color": None},
    {"id": 7, "title": "Instant Pot Duo 6Qt 7-in-1 Electric Pressure Cooker", "brand": None, "color": None},
    {"id": 8, "title": "Generic Yoga Mat 6mm Non-Slip Purple", "brand": None, "color": "Purple"},
]

STOPWORDS = {"the", "a", "in", "for", "men", "mens", "size", "us", "new"}
KNOWN_BRANDS = ["Nike", "Adidas", "Instant Pot"]
KNOWN_COLORS = ["Black", "White", "Purple", "Red", "Blue", "Anthracite"]


def tokens(title: str) -> set[str]:
    cleaned = title.lower().replace("'s", "").replace("'", "")
    words = re.findall(r"[a-z0-9]+", cleaned)
    return {w for w in words if w not in STOPWORDS}


def similarity(a: set[str], b: set[str]) -> float:
    return len(a & b) / max(1, len(a | b))


def resolve_clusters(listings: list[dict], threshold: float = 0.45) -> list[list[dict]]:
    """Greedy clustering: a listing joins a cluster if it is similar
    enough to any member (single-linkage on token Jaccard)."""
    clusters: list[list[dict]] = []
    for item in listings:
        toks = tokens(item["title"])
        placed = False
        for cluster in clusters:
            if any(similarity(toks, tokens(m["title"])) >= threshold for m in cluster):
                cluster.append(item)
                placed = True
                break
        if not placed:
            clusters.append([item])
    return clusters


def infer_attributes(item: dict) -> dict:
    """Fill brand/color from the title when the feed left them blank."""
    out = dict(item)
    title = item["title"]
    if not out["brand"]:
        out["brand"] = next((b for b in KNOWN_BRANDS if b.lower() in title.lower()), None)
    if not out["color"]:
        out["color"] = next((c for c in KNOWN_COLORS if c.lower() in title.lower()), None)
    return out


def main() -> None:
    clusters = resolve_clusters(LISTINGS)
    print(f"{len(LISTINGS)} listings -> {len(clusters)} product clusters\n")
    missing = []
    for i, cluster in enumerate(clusters, 1):
        enriched = [infer_attributes(m) for m in cluster]
        brand = next((m["brand"] for m in enriched if m["brand"]), None)
        if brand is None:
            missing.append(i)
        print(f"Cluster {i}: listings {[m['id'] for m in cluster]} | brand: {brand or 'UNKNOWN'}")
    print(f"\nClusters still missing a brand after inference: {missing or 'none'}")
    print("These are the listings a catalog-quality queue should look at first.")


if __name__ == "__main__":
    main()

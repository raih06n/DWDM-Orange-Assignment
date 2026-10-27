"""Classic Apriori (level-wise candidate generation + pruning) on the Titanic
dataset, used to cross-check the rules produced by Orange's Association
Rules widget (which uses FP-Growth internally).

Usage:  python apriori.py titanic_items.csv 0.10 0.70
"""
import csv, sys
from itertools import combinations

path = sys.argv[1] if len(sys.argv) > 1 else "titanic_items.csv"
MIN_SUP = float(sys.argv[2]) if len(sys.argv) > 2 else 0.10
MIN_CONF = float(sys.argv[3]) if len(sys.argv) > 3 else 0.70

with open(path) as f:
    rows = list(csv.reader(f))
header, data = rows[0], rows[1:]
transactions = [frozenset(f"{h}={v}" for h, v in zip(header, r)) for r in data]
N = len(transactions)

def support(itemset):
    return sum(1 for t in transactions if itemset <= t) / N

# L1: frequent 1-itemsets
items = sorted({i for t in transactions for i in t})
L = [{frozenset([i]) for i in items if support(frozenset([i])) >= MIN_SUP}]
freq = {s: support(s) for s in L[0]}

# Level-wise: join L(k-1) with itself, prune candidates with an infrequent subset
k = 2
while L[-1]:
    prev = L[-1]
    candidates = {a | b for a in prev for b in prev if len(a | b) == k}
    candidates = {c for c in candidates
                  if all(frozenset(s) in prev for s in combinations(c, k - 1))}
    Lk = set()
    for c in candidates:
        s = support(c)
        if s >= MIN_SUP:
            Lk.add(c); freq[c] = s
    L.append(Lk); k += 1

print(f"Transactions: {N}   min_support={MIN_SUP:.0%}   min_confidence={MIN_CONF:.0%}\n")
for level, Lk in enumerate(L[:-1], start=1):
    print(f"Frequent {level}-itemsets: {len(Lk)}")
print(f"Total frequent itemsets: {len(freq)}\n")

rules = []
for itemset, sup in freq.items():
    if len(itemset) < 2:
        continue
    for r in range(1, len(itemset)):
        for ante in map(frozenset, combinations(itemset, r)):
            conf = sup / freq[ante]
            if conf >= MIN_CONF:
                lift = conf / freq[itemset - ante]
                rules.append((ante, itemset - ante, sup, conf, lift))

rules.sort(key=lambda x: (-x[4], -x[3]))
print(f"Association rules: {len(rules)}\n")
print(f"{'Antecedent':<38} {'Consequent':<28} {'Supp':>6} {'Conf':>6} {'Lift':>6}")
for a, c, s, cf, lf in rules:
    print(f"{', '.join(sorted(a)):<38} {', '.join(sorted(c)):<28} {s:6.3f} {cf:6.3f} {lf:6.3f}")

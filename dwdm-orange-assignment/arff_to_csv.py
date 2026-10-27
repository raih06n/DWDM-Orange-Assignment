"""Orange's File widget cannot read Weka .arff files directly.
This script converts iris.arff to a CSV that Orange opens, keeping
the 'class' column marked as the target (Orange header flag 'cD#').

Usage:  python arff_to_csv.py iris.arff iris_from_arff.csv
"""
import sys, csv
from scipy.io import arff

src = sys.argv[1] if len(sys.argv) > 1 else "iris.arff"
dst = sys.argv[2] if len(sys.argv) > 2 else "iris_from_arff.csv"

data, meta = arff.loadarff(src)
names = meta.names()
header = [("cD#" + n) if meta[n][0] == "nominal" and n == names[-1] else n for n in names]

with open(dst, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(header)
    for row in data:
        w.writerow([v.decode() if isinstance(v, bytes) else v for v in row])

print(f"Converted {len(data)} rows, attributes: {names} -> {dst}")

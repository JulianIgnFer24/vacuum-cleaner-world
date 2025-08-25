# tools/plot_results.py
import csv, pathlib
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"
CSV_PATH = RESULTS_DIR / "vacuum_experiments.csv"

def load_rows():
    rows = []
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            r["dirt_rate"] = float(r["dirt_rate"])
            r["seed"] = int(r["seed"])
            r["repetition"] = int(r["repetition"])
            r["initial_dirt"] = int(r["initial_dirt"])
            r["final_dirt"] = int(r["final_dirt"])
            r["cells_cleaned"] = int(r["cells_cleaned"])
            r["actions_taken"] = int(r["actions_taken"])
            r["performance"] = float(r["performance"])
            r["success"] = (r["success"].lower() == "true")
            r["runtime_sec"] = float(r["runtime_sec"])
            rows.append(r)
    return rows

def success_rate_by_size_and_dirt(rows):
    # Aggregation: mean(success) for each (size, dirt_rate)
    table = defaultdict(list)
    for r in rows:
        key = (r["size"], r["dirt_rate"])
        table[key].append(1.0 if r["success"] else 0.0)

    sizes = sorted({k[0] for k in table.keys()}, key=lambda s: int(s.split("x")[0]))
    rates = sorted({k[1] for k in table.keys()})

    Z = np.zeros((len(sizes), len(rates)))
    for i, s in enumerate(sizes):
        for j, d in enumerate(rates):
            vals = table.get((s, d), [])
            Z[i, j] = np.mean(vals) if vals else 0.0

    fig = plt.figure()
    plt.imshow(Z, aspect="auto", origin="lower")
    plt.xticks(range(len(rates)), [str(r) for r in rates])
    plt.yticks(range(len(sizes)), sizes)
    plt.xlabel("Dirt rate")
    plt.ylabel("Grid size")
    plt.title("Success rate heatmap")
    plt.colorbar()
    out = RESULTS_DIR / "success_rate_heatmap.png"
    plt.savefig(out, bbox_inches="tight", dpi=150)

def actions_vs_dirt(rows, size_filter="10x10"):
    # Line: average actions per dirt_rate for one grid size
    by_rate = defaultdict(list)
    for r in rows:
        if r["size"] == size_filter:
            by_rate[r["dirt_rate"]].append(r["actions_taken"])

    rates = sorted(by_rate.keys())
    means = [np.mean(by_rate[d]) for d in rates]

    fig = plt.figure()
    plt.plot(rates, means, marker="o")
    plt.xlabel("Dirt rate")
    plt.ylabel("Actions taken (avg)")
    plt.title(f"Actions vs Dirt rate (size={size_filter})")
    out = RESULTS_DIR / f"actions_vs_dirt_{size_filter.replace('x','x')}.png"
    plt.savefig(out, bbox_inches="tight", dpi=150)

def performance_vs_dirt(rows, size_filter="10x10"):
    by_rate = defaultdict(list)
    for r in rows:
        if r["size"] == size_filter:
            by_rate[r["dirt_rate"]].append(r["performance"])

    rates = sorted(by_rate.keys())
    means = [np.mean(by_rate[d]) for d in rates]

    fig = plt.figure()
    plt.plot(rates, means, marker="s")
    plt.xlabel("Dirt rate")
    plt.ylabel("Performance (avg)")
    plt.title(f"Performance vs Dirt rate (size={size_filter})")
    out = RESULTS_DIR / f"performance_vs_dirt_{size_filter.replace('x','x')}.png"
    plt.savefig(out, bbox_inches="tight", dpi=150)

def runtime_boxplot(rows, size_filter="10x10"):
    by_rate = defaultdict(list)
    for r in rows:
        if r["size"] == size_filter:
            by_rate[r["dirt_rate"]].append(r["runtime_sec"])

    rates = sorted(by_rate.keys())
    data = [by_rate[d] for d in rates]

    fig = plt.figure()
    plt.boxplot(data, labels=[str(r) for r in rates], showmeans=True)
    plt.xlabel("Dirt rate")
    plt.ylabel("Runtime (s)")
    plt.title(f"Runtime by Dirt rate (size={size_filter})")
    out = RESULTS_DIR / f"runtime_boxplot_{size_filter.replace('x','x')}.png"
    plt.savefig(out, bbox_inches="tight", dpi=150)

def main():
    rows = load_rows()
    success_rate_by_size_and_dirt(rows)
    # Pick any size present in CSV (update if you changed SIZES)
    for sz in ["6x6","8x8","10x10","12x12"]:
        actions_vs_dirt(rows, size_filter=sz)
        performance_vs_dirt(rows, size_filter=sz)
        runtime_boxplot(rows, size_filter=sz)
    print(f"Plots saved to {RESULTS_DIR}")

if __name__ == "__main__":
    main()

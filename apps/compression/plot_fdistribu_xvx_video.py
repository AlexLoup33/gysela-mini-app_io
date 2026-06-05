#!/usr/bin/env python3
"""Plot x–vx slices from GYSELALIBXX_*.h5 and save one PNG per snapshot."""

import argparse
import glob
import os
import re

import h5py
import matplotlib.pyplot as plt
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", nargs="?", default=".")
    parser.add_argument("-o", "--output-dir", default=".")
    return parser.parse_args()


def list_h5_files(data_dir):
    files = []
    for path in glob.glob(os.path.join(data_dir, "GYSELALIBXX_*.h5")):
        if "initstate" not in os.path.basename(path):
            files.append(path)
    files.sort(key=lambda p: int(re.search(r"(\d+)\.h5$", p).group(1)))
    if not files:
        raise FileNotFoundError(f"No GYSELALIBXX_*.h5 in {data_dir}")
    return files


def xvx_slice(f):
    """fdistribu[sp, x, y, vx, vy] -> f[x, vx] (sum over y and vy)."""
    return np.sum(f[0, ...], axis=(1, 3))


def main():
    args = parse_args()
    data_dir = os.path.abspath(args.data_dir)
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    files = list_h5_files(data_dir)

    init_file = os.path.join(data_dir, "GYSELALIBXX_initstate.h5")
    mesh_file = init_file if os.path.isfile(init_file) else files[0]
    with h5py.File(mesh_file, "r") as h5:
        x = h5["MeshX"][:]
        vx = h5["MeshVx"][:]

    for filepath in files:
        idx = int(re.search(r"(\d+)\.h5$", filepath).group(1))
        with h5py.File(filepath, "r") as h5:
            f_xvx = xvx_slice(h5["fdistribu"][...])
            t = float(h5["time_saved"][()]) if "time_saved" in h5 else np.nan

        fig, ax = plt.subplots(figsize=(7, 5))
        im = ax.imshow(
            f_xvx,
            origin="lower",
            aspect="auto",
            extent=[vx[0], vx[-1], x[0], x[-1]],
            cmap="viridis",
        )
        fig.colorbar(im, ax=ax, label="f(x, vx)")
        ax.set_xlabel("vx")
        ax.set_ylabel("x")
        ax.set_title(f"t = {t:.3g}" if np.isfinite(t) else f"frame {idx:03d}")

        out = os.path.join(output_dir, f"fdist_x_vx_{idx:03d}.png")
        fig.savefig(out, dpi=120, bbox_inches="tight")
        plt.close(fig)
        print(out)


if __name__ == "__main__":
    main()

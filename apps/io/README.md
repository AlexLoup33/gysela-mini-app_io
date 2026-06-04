# GYSELA I/O Mini App

A minimal application demonstrating GYSELA I/O operations and testing the cpu performance scaling for 5D particle distribution functions.

## Overview

This mini application:

- Initialises a 5D particle distribution function (species × toroidal coordinates × velocity space)
- Writes the distribution function and mesh coordinates to HDF5 files
- Computes fluid moments (density, mean velocity, temperature) via C++ integration or in-situ Python computation
- Measures and saves CPU timing statistics

## Usage

```bash
mpirun -n <nprocs> ./gys_io [config.yaml] [pdi_config.yml]
```

- `config.yaml`: Input configuration file (default: uses built-in defaults)
- `pdi_config.yml`: PDI configuration file (default: uses `pdi_default.yml.hpp`)

### Example

```bash
mpirun -n 4 ./gys_io gys_io.yaml
```
Do not forget to set the the `PYTHONPATH` if you are using PyCall:

```bash
export PYTHONPATH=/path/to/your/gysela-mini-app_io/src/python:$PYTHONPATH
```

## Usage with Deisa-dask

### Installation

To use deisa-dask, you need to create the environment of the miniapp with additional dependencies.

```bash
cp apps/io/spack_deisa-dask.yaml external/gyselalibxx/toolchains/<MACHINE>/gyselalibxx-env-1.1.0.yaml
./external/gyselalibxx/toolchains/cpu.spack.gyselalibxx_env/prepare.sh
```
Then insert the correct <MACHINE> toolchain path in the `gysela-mini-app_io/apps/io/env-miniapp-io.sh`

### Basic run

```bash
./deisa-dask_launch_script.sh <nsimu_procs> <nworker_proc>
```

- `nsimu_procs`: number of MPI ranks for the simulation
- `nworkers`: number of Dask workers to use for the analytics

### Run with OAR

```bash
./oar_deisa-dask_launch_script.sh <nsimu_procs> <nworker_proc>
```

## Configuration

Edit `gys_io.yaml` to configure:

- **Mesh**: Grid sizes and ranges for toroidal coordinates (Tor1, Tor2, Tor3) and velocity space (Vpar, Mu)
- **Species**: Number of species, charges, masses
- **Application version**: `"gpu2cpu"`, `"mpi_transpose"`, or `"in-situ-diagnostic"` (the latter enables Python-based fluid moments computation)

## Output Files

- **`fdistribu_5D_output.h5`**: Distribution function and mesh coordinates
- **`cpu_time_stats.h5`**: CPU timing statistics (initialisation, transpose, GPU↔CPU transfer, I/O)
- **`fluid_moments.h5`**: Fluid moments (density, mean velocity, temperature)

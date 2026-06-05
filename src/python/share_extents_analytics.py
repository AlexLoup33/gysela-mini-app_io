import os
import sys
import dask
import h5py
import json
import yaml
import time
import logging
import xarray as xr
import dask.array as da
from fluid_moments import FluidMoments
from deisa.dask import Deisa
from distributed import Variable, Queue, get_client

#logging.basicConfig(level=logging.DEBUG)

deisa = Deisa()


@deisa.register("partial_density", 
        "partial_velocity", 
        "partial_temperature")
def sum_moments(partial_density, partial_velocity, partial_temperature):
    density = partial_density[0].sum(dim=("vpar", "mu")).compute() 
    velocity = partial_velocity[0].sum(dim=("vpar", "mu")).compute() 
    temperature = partial_temperature[0].sum(dim=("vpar", "mu")).compute() 

    if density[0].t == nb_iter-1:
        with h5py.File("deisa_fluid_moments.h5", 'w') as f:
            f.create_dataset("density", data=density)
            f.create_dataset("mean_velocity", data=velocity)
            f.create_dataset("temperature", data=temperature)


@deisa.register("fdistribu_raw",
                "tor1_raw",
                "tor2_raw",
                "tor3_raw",
                "vpar_raw",
                "mu_raw")
def compute_moments(fdistribu_raw, 
        tor1_raw, tor2_raw, tor3_raw, 
        vpar_raw, mu_raw):
    fdistribu = xr.DataArray(
            fdistribu_raw[0],
            dims=( 'species', 'tor1', 'tor2', 'tor3', 'vpar', 'mu'),
            coords= {'tor1': tor1_raw, 'tor2': tor2_raw, 'tor3': tor3_raw, 'vpar': vpar_raw, 'mu': mu_raw},
    )

    fm = FluidMoments(vpar_vals, mu_vals)

    density = fm.compute_density(fdistribu)
    velocity = fm.compute_velocity(fdistribu, density)
    temperature = fm.compute_temperature(fdistribu, density, velocity)


    with h5py.File("deisa_fluid_moments.h5", 'w') as f:
        f.create_dataset("density", data=density)
        f.create_dataset("mean_velocity", data=velocity)
        f.create_dataset("temperature", data=temperature)

deisa.execute_callbacks()


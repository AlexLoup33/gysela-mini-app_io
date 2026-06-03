#!/bin/bash

SIMU_NODES=${1:-1}
DASK_WORKERS=${2:-1}
DASK_THREADS_PER_WORKER=${3:-2}

#DASK_WORKER_MEMORY=8589934592
#DASK_WORKER_MEMORY="8GiB"
#DASK_WORKER_MEMORY=4294967296
#DASK_WORKER_MEMORY=3221225472
DASK_WORKER_MEMORY=2147483648
#DASK_WORKER_MEMORY=1610612736
#DASK_WORKER_MEMORY=1073741824
#DASK_WORKER_MEMORY=536870912

SCHEFILE=~/gysela-mini-app_io/scheduler.json

. ~/env-miniapp-gysela.sh

#export DASK_DISTRIBUTED__WORKER__MULTIPROCESSING_METHOD=forkserver
export DASK_DISTRIBUTED__WORKER__MEMORY__SPILL=False
export DASK_DISTRIBUTED__WORKER__MEMORY__TARGET=False
export DASK_DISTRIBUTED__WORKER__MEMORY__TERMINATE=False

NODES=($(sort -u $OAR_NODEFILE))
WORKER_NODES=(${NODES[@]:0:${DASK_WORKERS}})
MPI_NODES=(${NODES[@]:${DASK_WORKERS}:${SIMU_NODES}})
MPI_NODEFILE=$(mktemp)
printf "%s\n" "${MPI_NODES[@]}" > $MPI_NODEFILE

cd ~/gysela-mini-app_io
rm -f $SCHEFILE
rm -rf gysela_plots/[dhn]*/*

echo "Launch scheduler"
dask scheduler --scheduler-file=$SCHEFILE &
dask_sch_pid=$!
while ! [ -f $SCHEFILE ]; do
    sleep 1
    echo -n .
done

export DEISA_DASK_SCHEDULER_ADDRESS=$(jq -r '.["address"]' $SCHEFILE)

echo "Launch workers"
dask_worker_pids=()
for NODE in "${WORKER_NODES[@]}"; do
    oarsh ${NODE} ". ~/env-miniapp-gysela.sh && dask worker \
        --nworkers 1 \
        --nthreads ${DASK_THREADS_PER_WORKER} \
        --local-directory /tmp \
        --memory-limit ${DASK_WORKER_MEMORY} \
        --scheduler-file=${SCHEFILE}" &
    dask_worker_pids+=($!)
done
sleep 10

echo "Launch analytics"
python3 python/analytics.py apps/gys_io.yaml &
analytics_pid=$!

echo "Launch simulation"
mpirun -machinefile $MPI_NODEFILE \
	--prefix $(dirname $(dirname $(which mpirun))) \
	-x PATH \
	-x LD_LIBRARY_PATH \
	-x PYTHONPATH \
	-x PDI_PLUGIN_PATH \
	-x DEISA_DASK_SCHEDULER_ADDRESS \
	-n $SIMU_NODES build/apps/gys_io apps/gys_io.yaml apps/pdi_default.yaml &
simu_pid=$!

wait ${analytics_pid}
echo "Analytics over"

wait ${simu_pid}
echo "Simulation over"

rm -f $MPI_NODEFILE

for NODE in "${WORKER_NODES[@]}"; do
    oarsh ${NODE} "pkill -9 -f 'dask worker'" &
done

kill -9 ${dask_sch_pid}

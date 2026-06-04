#!/bin/bash

SIMU_NODES=${1:-1}
DASK_WORKERS=${2:-1}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd $SCRIPT_DIR/../.. && pwd)"

. $SCRIPT_DIR/env-miniapp-io.sh

SCHEFILE="$BASE_DIR/scheduler.json"
rm -f $SCHEFILE

cd $BASE_DIR

echo "Launch scheduler"
dask scheduler --scheduler-file=$SCHEFILE &
dask_sch_pid=$!

while ! [ -f $SCHEFILE ]; do
	sleep 1
	echo -n .
done

export DEISA_DASK_SCHEDULER_ADDRESS=$(jq -r '.["address"]' $SCHEFILE)

echo "Launch workers"
dask worker \
	--nworkers ${DASK_WORKERS} \
	--local-directory /tmp \
	--scheduler-file=${SCHEFILE} &
dask_worker_pid=$!

sleep 10

echo "Launch analytics"
python3 python/analytics.py apps/io/gys_io.yaml &
analytics_pid=$!

echo "Launch simu"
mpirun -n $SIMU_NODES build/apps/io/gys_io apps/io/gys_io.yaml apps/io/pdi_deisa.yaml & 
simu_pid=$!

wait ${analytics_pid}
echo "Analytics over"
wait ${simu_pid}
echo "Simulation over"

kill -9 ${dask_worker_pid} ${dask_sch_pid}

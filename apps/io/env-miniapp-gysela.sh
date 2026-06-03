SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd $SCRIPT_DIR/../.. && pwd)"

source $BASE_DIR/external/gyselalibxx/toolchains/cpu.spack.gyselalibxx_env/environment.sh

export PYTHONPATH=$BASE_DIR/python:$PYTHONPATH

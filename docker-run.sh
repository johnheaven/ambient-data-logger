AMB_DAT_DATA_DIR=$1
AMB_DAT_CACHE_DIR=$2

docker run -d --rm --name ambient-data-logger --mount type=bind,src=${AMB_DAT_DATA_DIR},dst=/usr/src/data --mount type=bind,src=${AMB_DAT_CACHE_DIR},dst=/usr/src/cache ambient-data-logger

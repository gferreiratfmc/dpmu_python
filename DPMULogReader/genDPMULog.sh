#!/bin/bash

DPMU_LOG_READER=/home/gferreira/DPMULogReader/read_dpmu_log
DPMU_LOG_DIR=/mnt/c/DPMU_LOG


for LOG_FILE in ${DPMU_LOG_DIR}/DPMU_CAN_LOG_*.hex
do
	${DPMU_LOG_READER}  ${LOG_FILE}
done

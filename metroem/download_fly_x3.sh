#!/bin/bash
Z_START=200
SECTION_NUMBER=6600
NAME=fly_full_x4_bigtest

for x in 10240 #112000
do
    for y in 0 #40000
    do
        python3 downloader.py \
            --z_start ${Z_START} --z_end $((${Z_START} + ${SECTION_NUMBER})) \
            --dst_folder  /usr/people/popovych/metro_datasets/${NAME}/ \
            --x_offset ${x} \
            --y_offset ${y} \
            --mips 7 --patch_sizes 1792 \
            --cv_path 'gs://corgie_package/fly/raw_x2_scaled/img/img_normalized'

    done
done


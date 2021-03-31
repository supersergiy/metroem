#!/bin/bash
Z_START=200
SECTION_NUMBER=6600
NAME=fly_full_x1

for x in 64000 #112000
do
    for y in 0 #40000
    do
        python3 downloader.py \
            --z_start ${Z_START} --z_end $((${Z_START} + ${SECTION_NUMBER})) \
            --dst_folder  /usr/people/popovych/metro_datasets/${NAME}/ \
            --x_offset ${x} \
            --y_offset ${y} \
            --mips 7 --patch_sizes 1280 \
            --cv_path 'gs://manuel_fafb_test/fafb_mainland_norm_with_masks/img/unaligned_normalized_fixed'

    done
done


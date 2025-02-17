#!/bin/bash
SECTION_NUMBER=500
Z_START=1000
NAME=fly_x0

for x in 112000
do
    for y in 40000
    do
        python3 downloader.py \
            --z_start ${Z_START} --z_end $((${Z_START} + ${SECTION_NUMBER})) \
            --dst_folder  ./${NAME}/ \
            --x_offset ${x} \
            --y_offset ${y} \
            --mips 4 --patch_sizes 3072 3072\
            --cv_path 'gs://manuel_fafb_test/fafb_mainland_norm_with_masks/img/unaligned_normalized'

    done
done


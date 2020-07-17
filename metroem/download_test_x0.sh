#!/bin/bash
SECTION_NUMBER=250
Z_START=17500
NAME=large_test_x1

for x in 147456
do
    for y in 147456
    do
        python3 downloader.py \
            --z_start ${Z_START} --z_end $((${Z_START} + ${SECTION_NUMBER})) \
            --dst_folder  ./${NAME}/ \
            --x_offset ${x} \
            --y_offset ${y} \
            --mips 5 6 --patch_sizes 2048 2048 \
            --cv_path 'gs://corgie_package/minie/test_x1/img/unaligned_normalized_defects' \
            --cv_path_defects 'gs://corgie_package/minie/test_x1/mask/fold_lengths'

    done
done


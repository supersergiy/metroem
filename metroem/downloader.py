import time
import h5py
import json
import sys
import os
import six
import copy
import argparse

import cloudvolume as cv
import numpy as np

from pathlib import Path
from tqdm import tqdm


def make_dset(dst_path, data_kind,
              num_samples, patch_size, chunk_size=512,
              dtype=None):

    if chunk_size is None:
        chunk_size = patch_size
    if dtype is None:
        dtype = np.float32

    df = h5py.File(dst_path, 'a')

    if data_kind in ['img', 'defects']:
        data_shape = [patch_size, patch_size]
        chunk_shape = [chunk_size, chunk_size]
    elif data_kind == 'field':
        data_shape = [patch_size, patch_size, 2]
        chunk_shape = [chunk_size, chunk_size, 2]
    else:
        raise Exception("Unkonw data kind {}".format(data_kind))

    dset_shape = (num_samples, 2, *data_shape)
    chunk_dim = (1, 1, *data_shape)

    if data_kind in df:
        del df[data_kind]

    dset = df.create_dataset(data_kind, dset_shape, dtype=dtype,
            chunks=chunk_dim)

    return dset

def download_dataset(meta, dst_folder, z_start, z_end,
                     mip, x_offset=0, y_offset=0, patch_size=None,
                     suffix=None):
    assert x_offset % 2**mip == 0
    assert y_offset % 2**mip == 0

    src_cvs = {}
    tgt_cvs = {}
    dsets = {}

    section_ids = range(z_start, z_end)
    num_sections = len(section_ids)

    if suffix is not None:
        suffix = '_' + suffix
    else:
        suffix = ''

    dset_name = "x{}_y{}_z{}{}_MIP{}.h5".format(x_offset,
            y_offset, z_start, suffix, mip)

    x_offset //= 2**mip
    y_offset //= 2**mip
    dst_path = os.path.join(dst_folder, dset_name)
    for data_kind in ['img', 'defects', 'field']:
        if data_kind in meta['src'] and \
                meta['src'][data_kind] is not None:
            dsets[data_kind] = make_dset(dst_path,
                    data_kind,
                    num_sections,
                    patch_size)

            src_cvs[data_kind] = cv.CloudVolume(
                meta['src'][data_kind],
                mip=mip,
                fill_missing=True,
                bounded=False, progress=False, parallel=16)

        if data_kind in meta['tgt'] and \
                meta['tgt'][data_kind] is not None:
            tgt_cvs[data_kind] = cv.CloudVolume(
                    meta['tgt'][data_kind],
                    mip=mip,
                    fill_missing=True,
                    bounded=False, progress=False, parallel=16)


    for i, z in tqdm(enumerate(section_ids)):
        src_x_offset = x_offset
        src_y_offset = y_offset
        tgt_x_offset = x_offset
        tgt_y_offset = y_offset

        for data_kind in ['field', 'img', 'defects']:
            if data_kind in src_cvs:
                src_cv_data = src_cvs[data_kind][
                    src_x_offset:src_x_offset + patch_size,
                    src_y_offset:src_y_offset + patch_size,
                    z:z+1]

                if data_kind in tgt_cvs:
                    tgt_cv_data = tgt_cvs[data_kind][
                        tgt_x_offset:tgt_x_offset + patch_size,
                        tgt_y_offset:tgt_y_offset + patch_size,
                        z-1:z]
                else:
                    tgt_cv_data = np.zeros_like(src_cv_data)

                src_data = np.array(src_cv_data).squeeze()
                tgt_data = np.array(tgt_cv_data).squeeze()
                if (src_data != 0).sum() == 0:
                    print ('empty slice')

                if data_kind == 'field':
                    tgt_field_offset = profile_field(tgt_data)
                    assert (tgt_data != 0).sum() == 0
                    src_field_offset = profile_field(src_data)

                dsets[data_kind][i, 0] = src_data
                dsets[data_kind][i, 1] = tgt_data


def profile_field(field):
    return 0, 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Do Sergiys work instead of Sergiy.')
    parser.add_argument('--mips', type=int, nargs='+')
    parser.add_argument('--patch_sizes', type=int, nargs='+')
    parser.add_argument('--x_offset',  type=int, default=0)
    parser.add_argument('--y_offset',  type=int, default=0)
    parser.add_argument('--section_ids_filename', type=str, default=None)
    parser.add_argument('--z_start', type=int, default=None)
    parser.add_argument('--z_end', type=int, default=None)
    parser.add_argument('--cv_path', type=str, default=None)
    parser.add_argument('--cv_path_defects', type=str, default=None)
    parser.add_argument('--suffix', type=str, default=None)
    parser.add_argument('--dst_folder', type=str, default='./dataset01')

    args = parser.parse_args()

    section_ids_filename = args.section_ids_filename
    mips = args.mips
    patch_sizes = args.patch_sizes
    z_start = args.z_start
    z_end = args.z_end
    x_offset = args.x_offset
    y_offset = args.y_offset

    src_spec = {
        'img': args.cv_path,
        'defects': args.cv_path_defects
    }
    tgt_spec = src_spec
    meta = {
        'src': src_spec,
        'tgt': tgt_spec
    }

    dst_folder = args.dst_folder
    Path(dst_folder).mkdir(parents=True, exist_ok=True)

    for mip, patch_size in zip(mips, patch_sizes):

        download_dataset(
                meta, dst_folder,
                z_start, z_end, mip=mip,
                x_offset=x_offset,
                y_offset=y_offset,
                patch_size=patch_size,
                suffix=None)

#!/usr/bin/env python

import argparse
import sys
import os
import shutil


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Run this command in the job directory of the topaz pick job.'
    )
    parser.add_argument('--coords_star_dir', type=str, required=True, help='Directory name within which the topaz picking star files exist.')
    parser.add_argument('--coords_suffix_file', type=str, default='./coords_suffix_topazpicks.star')
    parser.add_argument('--coords_suffix', type=str, default='_topazpicks.star')
    parser.add_argument('--relion_project_dir', type=str, default='../..')
    args = parser.parse_args()

    print('##### Command #####\n\t' + ' '.join(sys.argv))
    args_print_str = '##### Input parameters #####\n'
    for opt, val in vars(args).items():
        args_print_str += '\t{} : {}\n'.format(opt, val)
    print(args_print_str)
    return args


def main(coords_star_dir, coords_suffix_file, coords_suffix, relion_project_dir):
    with open(coords_suffix_file) as f:
        lines = f.readlines()
    assert len(lines) == 1

    mic_star_file = os.path.join(relion_project_dir, lines[0])

    with open(mic_star_file) as f:
        for line in f:
            if 'data_micrographs' in line:
                break

        for line in f:
            if 'loop_' in line:
                break

        idx_rlnMicrographName = None
        for line in f:
            if not '_rln' in line:
                break
            words = line.strip().split()
            if words[0] == '_rlnMicrographName':
                idx_rlnMicrographName = int(words[1].replace('#', '')) - 1
        assert idx_rlnMicrographName is not None

        lines = [line]
        for line in f:
            if len(line.strip()) == 0:
                break
            lines.append(line)
        for line in lines:
            words = line.strip().split()
            if len(words) == 0:
                break
            mic_name = words[idx_rlnMicrographName]
            assert os.path.exists(os.path.join(relion_project_dir, mic_name))
            mic_basename = os.path.splitext(os.path.basename(mic_name))[0]
            # Remove the job directory name from the directory path
            mic_dirname = '/'.join(os.path.dirname(mic_name).split('/')[2:])
            coord_name = os.path.join(coords_star_dir, mic_basename + coords_suffix)
            # Copy the coord star file into the correct path
            if os.path.exists(coord_name):
                if not os.path.isdir(mic_dirname):
                    os.makedirs(mic_dirname)
                shutil.copy2(coord_name, mic_dirname)

if __name__ == '__main__':
    args = parse_args()
    main(args.coords_star_dir, args.coords_suffix_file, args.coords_suffix, args.relion_project_dir)

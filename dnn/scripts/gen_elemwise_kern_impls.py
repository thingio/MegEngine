#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import itertools
from gen_elemwise_utils import ARITIES, DTYPES, MODES

def main():
    parser = argparse.ArgumentParser(
        description='generate elemwise impl files',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--type', type=str, choices=['cuda',
                                                     'cpp'],
                        default='cpp', help='generate cuda/hip kernel file')
    parser.add_argument('output', help='output directory')
    args = parser.parse_args()

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    if args.type == 'cuda':
        cpp_ext = 'cu'
    else:
        assert args.type == 'cpp'
        cpp_ext = 'cpp'

    for anum, ctype in itertools.product(ARITIES.keys(), DTYPES.keys()):
        for mode in MODES[(anum, DTYPES[ctype][1])]:
            formode = 'MEGDNN_ELEMWISE_MODE_ENABLE({}, cb)'.format(mode)
            fname = '{}_{}.{}'.format(mode, ctype, cpp_ext)
            fname = os.path.join(args.output, fname)
            with open(fname, 'w') as fout:
                w = lambda s: print(s, file=fout)
                w('// generated by gen_elemwise_kern_impls.py')

                if ctype == 'dt_float16':
                    w('#if !MEGDNN_DISABLE_FLOAT16')

                w('#define KERN_IMPL_MODE(cb) {}'.format(formode))
                w('#define KERN_IMPL_ARITY {}'.format(anum))
                w('#define KERN_IMPL_CTYPE {}'.format(ctype))
                w('#include "../kern_impl.inl"')

                if ctype == 'dt_float16':
                    w('#endif')

            print('generated {}'.format(fname))

    os.utime(args.output)

if __name__ == '__main__':
    main()
# -*- coding: utf-8 -*-

"""Trimmomatic"""

from __future__ import absolute_import
from __future__ import division
from __future__ import generators
from __future__ import nested_scopes
from __future__ import print_function
from __future__ import with_statement

from kakapo.shell import call


def trimmomatic_se(trimmomatic, adapters, in_file, out_file, stats_file,
                   threads, minlen):  # noqa

    cmd = ['java', '-jar', trimmomatic, 'SE', '-threads', str(threads),
           '-phred33',
           '-summary', stats_file, in_file, out_file,
           'ILLUMINACLIP:' + adapters + ':2:30:10',
           'SLIDINGWINDOW:4:20',
           'LEADING:20',
           'TRAILING:20',
           'MINLEN:' + str(minlen)]

    call(cmd)


def trimmomatic_pe(trimmomatic, adapters, in_file_1, in_file_2,
                   out_file_paired_1, out_file_unpaired_1,
                   out_file_paired_2, out_file_unpaired_2,
                   stats_file, threads, minlen):  # noqa

    cmd = ['java', '-jar', trimmomatic, 'PE', '-threads', str(threads),
           '-phred33',
           '-summary', stats_file,
           in_file_1, in_file_2,
           out_file_paired_1, out_file_unpaired_1,
           out_file_paired_2, out_file_unpaired_2,
           'ILLUMINACLIP:' + adapters + ':2:30:10',
           'SLIDINGWINDOW:4:20',
           'LEADING:20',
           'TRAILING:20',
           'MINLEN:' + str(minlen)]

    call(cmd)

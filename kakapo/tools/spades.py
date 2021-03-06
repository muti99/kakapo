"""SPAdes."""

from kakapo.utils.subp import run
from kakapo.utils.subp import which


PY3 = which('python3')


def run_spades_se(spades, out_dir, input_file, threads, memory, rna):

    memory = str(memory).split('.')[0]

    cmd = [spades,
           '-o', out_dir,
           '-s', input_file,
           '--only-assembler',
           '--threads', str(threads),
           '--memory', memory,
           '--phred-offset', '33']

    if rna:
        cmd.append('--rna')

    cmd = [PY3] + cmd

    run(cmd, do_not_raise=True)


def run_spades_pe(spades, out_dir, input_files, threads, memory, rna):

    memory = str(memory).split('.')[0]

    cmd = [spades,
           '-o', out_dir,
           '--pe1-1', input_files[0],  # paired_1.fastq
           '--pe1-2', input_files[1],  # paired_2.fastq
           '--s1', input_files[2],     # unpaired_1.fastq
           '--s2', input_files[3],     # unpaired_2.fastq
           '--only-assembler',
           '--threads', str(threads),
           '--memory', memory,
           '--phred-offset', '33']

    if rna:
        cmd.append('--rna')

    cmd = [PY3] + cmd

    run(cmd, do_not_raise=True)

"""Miscellaneous."""

import fileinput
import gzip
import hashlib
import re
import sys
from collections import defaultdict
from collections import OrderedDict
from datetime import datetime
from ftplib import FTP
from itertools import zip_longest
from operator import itemgetter
from os import listdir
from os import makedirs
from os import popen
from os import remove
from os import sysconf
from os.path import abspath
from os.path import exists as ope
from os.path import expanduser
from os.path import isdir
from os.path import isfile
from os.path import join as opj
from os.path import splitext
from shutil import move
from urllib.parse import urlparse

from kakapo.utils.http import download_file as download_file_http


def python_version():
    """Determine Python version."""
    py_v_hex = sys.hexversion

    py_v_1 = sys.version_info[0]
    py_v_2 = sys.version_info[1]
    py_v_3 = sys.version_info[2]

    py_v_str = '{v0}.{v1}.{v2}'.format(v0=py_v_1, v1=py_v_2, v2=py_v_3)

    return py_v_hex, py_v_str


def sys_ram(os_id):
    try:
        page_size = sysconf('SC_PAGE_SIZE')
        page_count = sysconf('SC_PHYS_PAGES')
        if page_size < 0 or page_count < 0:
            raise SystemError
        ram_b = sysconf('SC_PAGE_SIZE') * sysconf('SC_PHYS_PAGES')

    except ValueError:

        if os_id == 'mac':
            ram_b = int(
                float(popen("sysctl hw.memsize").readlines()[0].split()[1]))
        elif os_id == 'linux':
            ram_b = int(float(popen("free").readlines()[1].split()[1]) * 1024)
        else:
            raise NotImplementedError

    ram_g = ram_b / (1024 ** 3)
    return ram_g


def make_dirs(path):
    path = abspath(expanduser(path))
    if not ope(path):
        makedirs(path)
    return path


def list_of_items_at_path(path):
    path = abspath(expanduser(path))
    li, e = None, None
    if isfile(path):
        e = 'Item at path "{}" is not a directory.'.format(path)
    else:
        try:
            li = [opj(path, x) for x in listdir(path)]
        except FileNotFoundError:
            e = 'Directory "{}" does not exist.'.format(path)
    return li, e


def list_of_dirs_at_path(path):
    li, e = list_of_items_at_path(path)
    ld = li
    if li is not None:
        ld = [x for x in li if isdir(x)]
    return ld, e


def list_of_files_at_path(path):
    li, e = list_of_items_at_path(path)
    lf = li
    if li is not None:
        lf = [x for x in li if isfile(x)]
    return lf, e


def download_file(url, local_path, protocol='http'):
    assert protocol in ('http', 'ftp')
    if protocol == 'http':
        download_file_http(url, local_path)
    elif protocol == 'ftp':
        url_parsed = urlparse(url)
        netloc = url_parsed.netloc
        path = url_parsed.path

        with FTP(netloc) as ftp:
            ftp.login()
            with open(local_path, 'wb') as f:
                ftp.retrbinary(cmd='RETR ' + path,
                               callback=lambda x: f.write(x),
                               blocksize=8192 * 32)


def replace_line_in_file(file_path, line_str, replace_str):
    line_str = re.escape(line_str.strip())
    replace_str = replace_str.strip()
    for line in fileinput.input(file_path, inplace=1):
        r = re.findall('^(\\s*)(' + line_str + ')(\\s*)$', line)
        if len(r) != 0 and len(r[0]) == 3:
            print(r[0][0] + replace_str)
        else:
            print(line.rstrip())


def invert_dict(d):
    """Will only work if the values in the provided dict are hashable."""
    d_type = type(d)
    d_inv = defaultdict(list)
    for k, v in d.items():
        d_inv[v].append(k)
    for k in d_inv:
        d_inv[k] = tuple(d_inv[k])
    d_inv = d_type(d_inv)
    if d_type is OrderedDict:
        d_inv = OrderedDict(sorted(d_inv.items(), key=lambda x: x[0]))
    return d_inv


##############################################################################


def generate_md5_hash_for_file(file_path):
    with open(file_path, 'rb') as f:
        return_value = hashlib.md5(f.read()).hexdigest()
    return return_value


def extract_md5_hash(file_path):
    with open(file_path, 'r') as f_md5:
        line = f_md5.readline()
        md5_reported = line.split(' ')[0]
    return md5_reported


def unique_lines_in_file(path):
    with open(path, 'r') as f:
        x = f.readlines()
    x = list(set(x))
    x.sort()
    return x


def keep_unique_lines_in_file(path):
    x = unique_lines_in_file(path)
    with open(path, 'w') as f:
        f.write(''.join(x))


def combine_text_files(paths, out_path):
    ret = ''
    for p in paths:
        with open(p, 'r') as f:
            x = f.read()
            ret = ret + x

    with open(out_path, 'w') as f:
        f.write(ret)


def time_stamp():
    return datetime.now().strftime('%Y%m%d%H%M%S')


def overlap(a, b):
    a = sorted(a)
    b = sorted(b)
    ab = tuple(sorted((a, b), key=itemgetter(0)))
    if ab[0][1] <= ab[1][0]:
        overlap = 0
    else:
        overlap = ab[0][1] - ab[1][0]
        if ab[1][1] < ab[0][1]:
            overlap -= ab[0][1] - ab[1][1]
    return overlap


def splitext_gz(path):
    """
    Split extension for files that may have a double extension: x.y.(gz|gzip).

    :param path: A path-like string.
    :type path: str

    :returns: ('x', '.y', '.gz|.gzip')
    :rtype: tuple
    """
    ext = splitext(path)
    ext_gz = None

    if ext[1] in ('.gz', '.gzip'):
        ext_gz = ext[1]
        ext = splitext(ext[0])

    ext1 = ext[1]
    base = ext[0]

    return base, ext1, ext_gz


def _gzip_open(filename, mode='rt', compresslevel=5, encoding=None,
               errors=None, newline=None):
    return gzip.open(filename, mode, compresslevel, encoding, errors, newline)


def plain_or_gzip(in_file):
    read_mode = 'r'
    write_mode = 'w'
    append_mode = 'a'
    fqopen = open
    ext = ''

    ext_info = splitext_gz(in_file)
    if ext_info[2] is not None:
        read_mode = 'rt'
        write_mode = 'wt'
        append_mode = 'at'
        fqopen = _gzip_open
        ext = ext_info[2]

    return read_mode, write_mode, append_mode, fqopen, ext


def grouper(iterable, n, fillvalue=None):
    """
    Break the data into fixed-length chunks or blocks.

    Allows parsing of a (FASTQ) file n (4) lines at a time.

    Edited from "Transcriptome workshop at Botany 2018"
    Ya Yang and Stephen A. Smith, which was modified from the code in:
    FilterUncorrectabledPEfastq.py file by Adam H. Freedman:
    https://github.com/harvardinformatics/TranscriptomeAssemblyTools
    """
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def split_mixed_fq(in_file, out_file_1, out_file_2):
    r_mode, w_mode, a_mode, fqopen, ext = plain_or_gzip(in_file)

    with fqopen(in_file, r_mode) as in_f, \
            fqopen(out_file_1, w_mode) as out_f_1, \
            fqopen(out_file_2, w_mode) as out_f_2:
        entries = grouper(in_f, 4)
        for entry in entries:
            head, seq, plhld, qual = [i.strip() for i in entry]
            entry_str = '\n'.join([head, seq, plhld, qual])
            if ' 1:N:' in head:
                out_f_1.write('{}\n'.format(entry_str))
            elif ' 2:N:' in head:
                out_f_2.write('{}\n'.format(entry_str))


def rename_fq_seqs(in_file, prefix, suffix):
    r_mode, w_mode, a_mode, fqopen, ext = plain_or_gzip(in_file)

    out_file_temp = in_file + '.temp'

    with fqopen(in_file, r_mode) as in_f, \
            fqopen(out_file_temp, w_mode) as out_f:
        entries = grouper(in_f, 4)
        for i, entry in enumerate(entries):
            head, seq, plhld, qual = [x.strip() for x in entry]
            head = '@' + prefix + '.' + str(i + 1) + ' ' + suffix
            plhld = '+'
            entry_str = '\n'.join([head, seq, plhld, qual])
            out_f.write('{}\n'.format(entry_str))

    remove(in_file)
    move(out_file_temp, in_file)


def avg_read_len_fq(in_file):
    r_mode, w_mode, a_mode, fqopen, ext = plain_or_gzip(in_file)

    num_reads = 0
    tot_seq_len = 0

    with fqopen(in_file, r_mode) as in_f:
        entries = grouper(in_f, 4)
        for i, entry in enumerate(entries):
            _, seq, _, _ = [x.strip() for x in entry]
            tot_seq_len += len(seq)
            num_reads = i
        num_reads += 1

    return tot_seq_len / num_reads


def approx_avg_read_len_fq(in_file):
    r_mode, w_mode, a_mode, fqopen, ext = plain_or_gzip(in_file)

    head, _, plhld, qual = None, None, None, None

    num_reads = 0
    file_size = 0

    with fqopen(in_file, r_mode) as in_f:
        entries = grouper(in_f, 4)
        for i, entry in enumerate(entries):
            head, _, plhld, qual = [x.strip() for x in entry]
            break

        for _ in in_f:
            num_reads += 1
        num_reads = num_reads / 4

        file_size = in_f.seek(0, 2)

    rec_size_no_seq = len(head + plhld + qual) + 4
    recs_size_no_seq = rec_size_no_seq * num_reads

    return (file_size - recs_size_no_seq) / num_reads


def split_seq_defn_for_printing(defn):
    defn_split = defn.split(' ')
    defn_a = defn_split[0]
    defn_b = ' '.join(defn_split[1:]).split('|')[0]
    defn_b = defn_b.replace('_', ' ').replace('-', ' ')
    defn_b = defn_b[0].upper() + defn_b[1:]
    defn_b = defn_b.split('; RevComp')[0]
    return defn_a, defn_b

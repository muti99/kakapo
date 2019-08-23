#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""kakapo"""

from __future__ import absolute_import
from __future__ import division
from __future__ import generators
from __future__ import nested_scopes
from __future__ import print_function
from __future__ import with_statement

import inspect
import os
import sys

##############################################################################
SCRIPT_FILE_PATH = inspect.getfile(inspect.currentframe())
SCRIPT_DIR_PATH = os.path.dirname(os.path.abspath(SCRIPT_FILE_PATH))
KAKAPO_DIR_PATH = os.path.sep.join(SCRIPT_DIR_PATH.split(os.path.sep)[0:-1])
sys.path.insert(0, KAKAPO_DIR_PATH)
##############################################################################

import argparse

from os.path import basename
from os.path import exists as ope
from os.path import join as opj
from os.path import splitext
from shutil import rmtree
from sys import exit

from ncbi_taxonomy_local import taxonomy

from kakapo import __version__, __script_name__
from kakapo import dependencies as deps
from kakapo.config import CONYELL, CONSDFL
from kakapo.config import DIR_CFG, DIR_DEP, DIR_TAX
from kakapo.config import THREADS, RAM
from kakapo.config import SCRIPT_INFO
from kakapo.config_file_parse import config_file_parse
from kakapo.helpers import make_dir
from kakapo.helpers import time_stamp
from kakapo.logging_k import prepare_logger
from kakapo.py_v_diffs import StringIO
from kakapo.translation_tables import TranslationTable
from kakapo.workflow import combine_aa_fasta
from kakapo.workflow import descending_tax_ids
from kakapo.workflow import dnld_cds_for_ncbi_prot_acc
from kakapo.workflow import dnld_pfam_uniprot_seqs
from kakapo.workflow import dnld_prot_seqs
from kakapo.workflow import dnld_sra_fastq_files
from kakapo.workflow import dnld_sra_info
from kakapo.workflow import filter_queries
from kakapo.workflow import find_orfs_translate
from kakapo.workflow import gff_from_json
from kakapo.workflow import makeblastdb_assemblies
from kakapo.workflow import makeblastdb_fq
from kakapo.workflow import min_accept_read_len
from kakapo.workflow import pfam_uniprot_accessions
from kakapo.workflow import prepare_output_directories
from kakapo.workflow import run_inter_pro_scan
from kakapo.workflow import run_spades
from kakapo.workflow import run_tblastn_on_assemblies
from kakapo.workflow import run_tblastn_on_reads
from kakapo.workflow import run_trimmomatic
from kakapo.workflow import run_vsearch_on_reads
from kakapo.workflow import trimmed_fq_to_fa
from kakapo.workflow import user_aa_fasta
from kakapo.workflow import user_fastq_files
from kakapo.workflow import user_protein_accessions

# Command line arguments -----------------------------------------------------
USAGE = '{} --cfg path/to/configuration_file.ini'.format(__script_name__)

PARSER = argparse.ArgumentParser(
    prog=__script_name__,
    formatter_class=argparse.RawTextHelpFormatter,
    usage=USAGE,
    description=None,
    epilog=None,
    prefix_chars='-',
    add_help=False)

PARSER.add_argument(
    '--cfg',
    type=str,
    required=False,
    metavar='path',
    dest='CONFIG_FILE_PATH',
    help='Path to a {} project configuration file.'.format(__script_name__))

PARSER.add_argument(
    '--force-deps',
    action='store_true',
    required=False,
    dest='CLEAN_CONFIG_DIR',
    help='Force the use of {}-installed dependencies,\neven if they are '
         'already available on the system.'.format(__script_name__))

PARSER.add_argument(
    '--clean-config-dir',
    action='store_true',
    required=False,
    dest='CLEAN_CONFIG_DIR',
    help='Remove all downloaded software dependencies and\n'
         'NCBI taxonomy data.')

PARSER.add_argument(
    '-v', '--version',
    action='store_true',
    required=False,
    dest='PRINT_VERSION',
    help='Print {} version.'.format(__script_name__))

PARSER.add_argument(
    '-h', '--help',
    action='store_true',
    required=False,
    dest='PRINT_HELP',
    help='Print {} help information.'.format(__script_name__))

ARGS = PARSER.parse_args()

CLEAN_CONFIG_DIR = ARGS.CLEAN_CONFIG_DIR
CONFIG_FILE_PATH = ARGS.CONFIG_FILE_PATH
PRINT_VERSION = ARGS.PRINT_VERSION
PRINT_HELP = ARGS.PRINT_HELP

if PRINT_HELP is True:
    print(SCRIPT_INFO)
    PARSER.print_help()
    exit(0)

if PRINT_VERSION is True:
    print(__script_name__ + ' v' + __version__)
    exit(0)

if CLEAN_CONFIG_DIR is True and ope(DIR_CFG):
    print('Removing configuration directory: ' + DIR_CFG)
    rmtree(DIR_CFG)
    exit(0)
elif CLEAN_CONFIG_DIR is True:
    print('Configuration directory does not exist. Nothing to do.')
    exit(0)

if CLEAN_CONFIG_DIR is False and CONFIG_FILE_PATH is not None:
    if not ope(CONFIG_FILE_PATH):
        print('Configuration file ' + CONFIG_FILE_PATH + ' does not exist.')
        exit(0)
else:
    print(SCRIPT_INFO)
    print(CONYELL +
          'Configuration file was not provided. Nothing to do.' +
          CONSDFL)
    print()
    print('-' * 80)
    PARSER.print_help()
    print('-' * 80)
    print()
    exit(0)

print(SCRIPT_INFO)

# ----------------------------------------------------------------------------


def main():
    """Run the script."""
    # Prepare initial logger (before we know the log file path) --------------
    prj_log_file_suffix = time_stamp() + '.log'
    log_stream = StringIO()
    log, stream_log_handler = prepare_logger(console=True, stream=log_stream)
    linfo = log.info

    # Prepare configuration directory ----------------------------------------
    if ope(DIR_CFG):
        linfo('Found configuration directory: ' + DIR_CFG)
    else:
        linfo('Creating configuration directory: ' + DIR_CFG)
        make_dir(DIR_CFG)

    # Initialize NCBI taxonomy database --------------------------------------
    linfo('Loading NCBI taxonomy data')
    tax = taxonomy(DIR_TAX)

    # Parse configuration file -----------------------------------------------
    __ = config_file_parse(CONFIG_FILE_PATH, tax)

    prj_name = __['project_name']
    email = __['email']
    dir_out = __['output_directory']
    inter_pro_scan = __['inter_pro_scan']
    prepend_assmbl = __['prepend_assmbl']
    min_target_orf_len = __['min_target_orf_len']
    max_target_orf_len = __['max_target_orf_len']
    allow_non_aug = __['allow_non_aug']
    allow_no_strt_cod = __['allow_no_strt_cod']
    allow_no_stop_cod = __['allow_no_stop_cod']
    sras = __['sras']
    fq_pe = __['fq_pe']
    fq_se = __['fq_se']
    user_assemblies = __['assmbl']
    min_query_length = __['min_query_length']
    max_query_length = __['max_query_length']
    user_queries = __['user_queries']
    blast_1_culling_limit = __['blast_1_culling_limit']
    blast_1_evalue = __['blast_1_evalue']
    blast_1_max_target_seqs = __['blast_1_max_target_seqs']
    blast_1_qcov_hsp_perc = __['blast_1_qcov_hsp_perc']
    blast_2_culling_limit = __['blast_2_culling_limit']
    blast_2_evalue = __['blast_2_evalue']
    blast_2_max_target_seqs = __['blast_2_max_target_seqs']
    blast_2_qcov_hsp_perc = __['blast_2_qcov_hsp_perc']
    tax_group = __['tax_group']
    tax_group_name = __['tax_group_name']
    tax_ids_user = __['tax_ids']
    pfam_acc = __['pfam_acc']
    prot_acc_user = __['prot_acc']

    # Create output directory with all the subdirectories --------------------
    if dir_out is not None:
        if ope(dir_out):
            linfo('Found output directory: ' + dir_out)
        else:
            linfo('Creating output directory: ' + dir_out)
            make_dir(dir_out)

    __ = prepare_output_directories(dir_out, prj_name)

    dir_temp = __['dir_temp']
    dir_cache_pfam_acc = __['dir_cache_pfam_acc']
    dir_cache_fq_minlen = __['dir_cache_fq_minlen']
    dir_cache_prj = __['dir_cache_prj']
    dir_prj_logs = __['dir_prj_logs']
    dir_prj_queries = __['dir_prj_queries']
    dir_fq_data = __['dir_fq_data']
    dir_fq_trim_data = __['dir_fq_trim_data']
    dir_fa_trim_data = __['dir_fa_trim_data']
    dir_blast_fa_trim = __['dir_blast_fa_trim']
    dir_prj_blast_results_fa_trim = __['dir_prj_blast_results_fa_trim']
    dir_prj_vsearch_results_fa_trim = __['dir_prj_vsearch_results_fa_trim']
    dir_prj_spades_assemblies = __['dir_prj_spades_assemblies']
    dir_prj_blast_assmbl = __['dir_prj_blast_assmbl']
    dir_prj_assmbl_blast_results = __['dir_prj_assmbl_blast_results']
    dir_prj_transcripts = __['dir_prj_transcripts']
    dir_prj_ips = __['dir_prj_ips']
    dir_prj_transcripts_combined = __['dir_prj_transcripts_combined']

    # Prepare logger ---------------------------------------------------------
    prj_log_file = opj(dir_prj_logs, prj_name + '_' + prj_log_file_suffix)
    with open(prj_log_file, 'w') as f:
        f.write(SCRIPT_INFO.strip() + '\n\n' + log_stream.getvalue())
    log, _ = prepare_logger(console=True, stream=None, file=prj_log_file)
    linfo = log.info

    # Check for dependencies -------------------------------------------------
    linfo('Checking for dependencies')
    make_dir(DIR_DEP)
    seqtk = deps.dep_check_seqtk(linfo)
    trimmomatic, adapters = deps.dep_check_trimmomatic(linfo)
    fasterq_dump = deps.dep_check_sra_toolkit(linfo)
    makeblastdb, __, tblastn = deps.dep_check_blast(linfo)
    vsearch = deps.dep_check_vsearch(linfo)
    spades = deps.dep_check_spades(linfo)

    # Genetic code information and translation tables ------------------------

    linfo('Loading genetic code information and translation tables for ' +
          tax_group_name)

    gc_id = tax.genetic_code_for_taxid(tax_group)
    gc_tt = TranslationTable(gc_id)

    # Housekeeping done. Start the analyses. ---------------------------------

    # Resolve descending taxonomy nodes --------------------------------------
    tax_ids = descending_tax_ids(tax_ids_user, tax, linfo)

    # Pfam uniprot accessions ------------------------------------------------
    pfam_uniprot_acc = pfam_uniprot_accessions(pfam_acc, tax_ids,
                                               dir_cache_pfam_acc, linfo)

    # Download Pfam uniprot sequences if needed ------------------------------
    aa_uniprot_file = opj(dir_prj_queries, 'aa_uniprot.fasta')
    dnld_pfam_uniprot_seqs(pfam_uniprot_acc, aa_uniprot_file, dir_cache_prj,
                           linfo)

    # User provided protein accessions ---------------------------------------
    prot_acc_user = user_protein_accessions(prot_acc_user, linfo)

    # Download from NCBI if needed -------------------------------------------
    aa_prot_ncbi_file = opj(dir_prj_queries, 'aa_prot_ncbi.fasta')
    dnld_prot_seqs(prot_acc_user, aa_prot_ncbi_file, dir_cache_prj, linfo)

    # User provided protein sequences ----------------------------------------
    aa_prot_user_file = opj(dir_prj_queries, 'aa_prot_user.fasta')
    user_aa_fasta(user_queries, aa_prot_user_file, linfo)

    # Combine all AA queries -------------------------------------------------
    aa_queries_file = opj(dir_prj_queries, 'aa_all.fasta')
    combine_aa_fasta([aa_uniprot_file,
                      aa_prot_ncbi_file,
                      aa_prot_user_file], aa_queries_file, linfo)

    # Filter AA queries ------------------------------------------------------
    filter_queries(aa_queries_file, min_query_length, max_query_length, linfo)

    # Download SRA run metadata if needed ------------------------------------
    sra_runs_info, sras_acceptable = dnld_sra_info(sras, dir_cache_prj, linfo)

    # Download SRA run FASTQ files if needed ---------------------------------
    x, y, z = dnld_sra_fastq_files(sras_acceptable, sra_runs_info, dir_fq_data,
                                   fasterq_dump, THREADS, dir_temp, linfo)

    se_fastq_files_sra = x
    pe_fastq_files_sra = y
    sra_runs_info = z

    # User provided FASTQ files ----------------------------------------------
    se_fastq_files_usr, pe_fastq_files_usr = user_fastq_files(fq_se, fq_pe,
                                                              linfo)

    # Collate FASTQ file info ------------------------------------------------
    se_fastq_files = se_fastq_files_sra.copy()
    se_fastq_files.update(se_fastq_files_usr)
    pe_fastq_files = pe_fastq_files_sra.copy()
    pe_fastq_files.update(pe_fastq_files_usr)

    # Minimum acceptable read length -----------------------------------------
    min_accept_read_len(se_fastq_files, pe_fastq_files, dir_temp,
                        dir_cache_fq_minlen, vsearch, linfo)

    # File name patterns -----------------------------------------------------

    pe_trim_pair_1_sfx = '_paired_1'
    pe_trim_pair_2_sfx = '_paired_2'
    pe_trim_unpr_1_sfx = '_unpaired_1'
    pe_trim_unpr_2_sfx = '_unpaired_2'

    pe_trim_suffixes = [pe_trim_pair_1_sfx, pe_trim_pair_2_sfx,
                        pe_trim_unpr_1_sfx, pe_trim_unpr_2_sfx]

    pe_file_pattern = opj('@D@', '@N@')

    pe_trim_fq_file_patterns = list(
        zip([pe_file_pattern] * 4, pe_trim_suffixes, ['.fastq'] * 4))
    pe_trim_fq_file_patterns = [''.join(x) for x in pe_trim_fq_file_patterns]

    pe_trim_fa_file_patterns = [x.replace('.fastq', '.fasta') for x in
                                pe_trim_fq_file_patterns]

    pe_blast_db_file_patterns = list(
        zip([pe_file_pattern] * 4, pe_trim_suffixes))
    pe_blast_db_file_patterns = [''.join(x) for x in pe_blast_db_file_patterns]

    pe_blast_results_file_patterns = [x.replace('.fastq', '.txt') for x in
                                      pe_trim_fq_file_patterns]

    pe_vsearch_results_file_patterns = pe_blast_results_file_patterns

    # Run Trimmomatic --------------------------------------------------------
    run_trimmomatic(se_fastq_files, pe_fastq_files, dir_fq_trim_data,
                    trimmomatic, adapters, pe_trim_fq_file_patterns, THREADS,
                    linfo)

    # Convert trimmed FASTQ files to FASTA -----------------------------------
    trimmed_fq_to_fa(se_fastq_files, pe_fastq_files, dir_fa_trim_data, seqtk,
                     pe_trim_fa_file_patterns, linfo)

    # Run makeblastdb on reads -----------------------------------------------
    makeblastdb_fq(se_fastq_files, pe_fastq_files, dir_blast_fa_trim,
                   makeblastdb, pe_blast_db_file_patterns, linfo)

    # Run tblastn on reads ---------------------------------------------------
    run_tblastn_on_reads(se_fastq_files, pe_fastq_files, aa_queries_file,
                         tblastn, blast_1_evalue, blast_1_max_target_seqs,
                         blast_1_culling_limit, blast_1_qcov_hsp_perc,
                         dir_prj_blast_results_fa_trim,
                         pe_blast_results_file_patterns, THREADS, gc_id, seqtk,
                         vsearch, linfo)

    # Run vsearch on reads ---------------------------------------------------
    run_vsearch_on_reads(se_fastq_files, pe_fastq_files, vsearch,
                         dir_prj_vsearch_results_fa_trim,
                         pe_vsearch_results_file_patterns, seqtk, linfo)

    # Run SPAdes -------------------------------------------------------------
    run_spades(se_fastq_files, pe_fastq_files, dir_prj_spades_assemblies,
               spades, dir_temp, THREADS, RAM, linfo)

    # Collate SPAdes and user provided assemblies ----------------------------
    assemblies = []

    for se in se_fastq_files:
        a_path = se_fastq_files[se]['spades_assembly']
        if a_path is None:
            continue
        a = {}
        a['path'] = a_path
        a['name'] = se
        a['tax_id'] = se_fastq_files[se]['tax_id']
        assemblies.append(a)

    for pe in pe_fastq_files:
        a_path = pe_fastq_files[pe]['spades_assembly']
        if a_path is None:
            continue
        a = {}
        a['path'] = a_path
        a['name'] = pe
        a['tax_id'] = pe_fastq_files[pe]['tax_id']
        assemblies.append(a)

    for us in user_assemblies:
        a_path = us
        a = {}
        a['path'] = a_path
        a['name'] = splitext(basename(a_path))[0]
        a['tax_id'] = None
        assemblies.append(a)

    # Run makeblastdb on assemblies  -----------------------------------------
    makeblastdb_assemblies(assemblies, dir_prj_blast_assmbl, makeblastdb,
                           linfo)

    # Run tblastn on assemblies ----------------------------------------------
    run_tblastn_on_assemblies(assemblies, aa_queries_file, tblastn,
                              dir_prj_assmbl_blast_results, blast_2_evalue,
                              blast_2_max_target_seqs, blast_2_culling_limit,
                              blast_2_qcov_hsp_perc, THREADS, gc_id, linfo)

    # Prepare BLAST hits for analysis: find ORFs, translate ------------------
    find_orfs_translate(assemblies, dir_prj_transcripts, gc_tt, seqtk,
                        dir_temp, prepend_assmbl, min_target_orf_len,
                        max_target_orf_len, allow_non_aug, allow_no_strt_cod,
                        allow_no_stop_cod, tax, tax_group, tax_ids_user, linfo)

    # Download CDS for NCBI protein queries ----------------------------------
    nt_prot_ncbi_file = opj(dir_prj_transcripts_combined, prj_name +
                            '_ncbi_query_cds.fasta')
    if len(prot_acc_user) > 0:
        dnld_cds_for_ncbi_prot_acc(prot_acc_user, nt_prot_ncbi_file, tax,
                                   linfo)

    # GFF3 files from kakapo results JSON files ------------------------------
    gff_from_json(assemblies, dir_prj_ips, dir_prj_transcripts_combined,
                  prj_name, linfo)

    # Run InterProScan 5 -----------------------------------------------------
    if inter_pro_scan is True:
        run_inter_pro_scan(assemblies, email, dir_prj_ips, dir_cache_prj,
                           linfo)

    # GFF3 files from kakapo and InterProScan 5 results JSON files -----------
    if inter_pro_scan is True:
        gff_from_json(assemblies, dir_prj_ips, dir_prj_transcripts_combined,
                      prj_name, linfo)

##############################################################################

    rmtree(dir_temp)

##############################################################################


if __name__ == '__main__':
    main()

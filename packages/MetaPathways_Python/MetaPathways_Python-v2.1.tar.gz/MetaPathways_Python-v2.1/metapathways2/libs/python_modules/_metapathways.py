#!/usr/bin/python

__author__ = "Kishori M Konwar"
__copyright__ = "Copyright 2013, MetaPathways"
__credits__ = ["r"]
__version__ = "1.0"
__maintainer__ = "Kishori M Konwar"
__status__ = "Release"


try:
   from optparse import make_option
   from os import makedirs,  path, listdir, remove, rename, _exit
   import os, sys, errno, shutil, re
   from glob import glob
   from datetime import date
   #from metapaths_utils  import pars[s._command_line_parameters

   from libs.python_modules.utils.sysutil import getstatusoutput, pathDelim
   #from libs.python_modules.utils.utils import *, hasInput, createFolderIfNotFound
   from libs.python_modules.utils.utils import *
   from libs.python_modules.parsers.parse  import parse_metapaths_parameters
   from libs.python_modules.pipeline.metapathways_pipeline import print_commands, call_commands_serially, execute_tasks
   from libs.python_modules.pipeline.MetaPathways_gather_run_stats import MetaPathways_gather_run_stats
   from libs.python_modules.utils.metapathways_utils import fprintf, printf, eprintf, remove_existing_pgdb, exit_process, WorkflowLogger, generate_log_fp

   from libs.python_modules.pipeline.sampledata import *
   from libs.python_modules.pipeline.jobscreator import *
   from libs.python_modules.pipeline.commands import *
   import libs.python_scripts


except:
     print """ Could not load some user defined  module functions"""
     print """ Make sure your typed \"source MetaPathwaysrc\""""
     print """ """
     sys.exit(3)



PATHDELIM = pathDelim()


def copyFile(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise

def dry_run_status( commands ):
    for command in commands:
        printf("%s", command[0])
        if command[4] == True:
           printf("%s", " Required")
        else:
           printf("%s", " Not Required")
    printf("\n")


def get_refdb_name( dbstring ):
    dbstring = dbstring.rstrip()
    dbstring = dbstring.lstrip()
    dbstring = dbstring.lower() 
    return dbstring



def format_db(formatdb_executable, seqType, raw_sequence_file, formatted_db,  algorithm):
     _temp_formatted_db  =  formatted_db+ "__temp__"

     """ format with 4GB file size """
     if algorithm=='BLAST':
         cmd='%s -dbtype %s --max_file_sz 4294967296  -in %s -out %s' %(formatdb_executable, seqType, raw_sequence_file, _temp_formatted_db)

     if algorithm=='LAST':
         # dirname = os.path.dirname(raw_sequence_file)    
         cmd='%s -s 4G -p -c %s  %s' %(formatdb_executable, _temp_formatted_db, raw_sequence_file)

     result= getstatusoutput(cmd)
     temp_fileList = glob(_temp_formatted_db + '*') 
     try:
        for tempFile in temp_fileList:
           file = re.sub('__temp__','', tempFile)
           rename( tempFile, file);

     except:
        return False

     if result[0]==0:
        return True
     else:
        return False


def create_quality_check_cmd(min_length, type,  log, contig_lengths_file, input, output, mapping, config_settings):
    cmd = "%s  --min_length %d --log_file %s  -i %s -o  %s -M %s -t %s -L %s" %((config_settings['METAPATHWAYS_PATH'] + config_settings['PREPROCESS_FASTA']), min_length, log, input,  output,  mapping, type,   contig_lengths_file) 
    #cmd = "%s  --min_length %d --log_file %s  -i %s -o  %s -M %s" %((config_settings['METAPATHWAYS_PATH'] + config_settings['PREPROCESS_FASTA']), min_length, log, input,  output, mapping) 
    return cmd


def create_orf_prediction_cmd(options, log, input, output, config_settings):
    cmd = "%s %s -i %s -o %s" %((config_settings['METAPATHWAYS_PATH'] + config_settings['ORF_PREDICTION']), options, input, output) 
    return cmd

# convert an input gbk file to fna faa and gff file
def  convert_gbk_to_fna_faa_gff(input_gbk, output_fna, output_faa, output_gff, config_settings):
    cmd = "%s  -g %s --output-fna %s --output-faa %s --output-gff %s" %((config_settings['METAPATHWAYS_PATH'] \
                 + config_settings['GBK_TO_FNA_FAA_GFF']), input_gbk, output_fna, output_faa, output_gff) 
    return cmd

# convert an input gff file to fna faa and gff file
def  convert_gff_to_fna_faa_gff(inputs, outputs,  config_settings):
    cmd = "%s " %(config_settings['METAPATHWAYS_PATH']+ config_settings['GFF_TO_FNA_FAA_GFF'])
    for  source, target in zip(inputs, outputs):
       cmd += ' --source ' + source + ' --target ' + target
    return cmd


#converts the orfs into 
#def create_orf_converter_cmd(options, input, output, config_settings):
#    cmd = "%s  %s  %s" %((config_settings['METAPATHWAYS_PATH'] + config_settings['ORF_CONVERTER']), options,  input) 
#    return cmd

def create_aa_orf_sequences_cmd(input_gff, input_fasta, output_fna, output_faa, output_gff,config_settings):
    cmd = "%s -g  %s  -n %s --output_nuc %s --output_amino %s --output_gff %s" %((config_settings['METAPATHWAYS_PATH'] + config_settings['GFF_TO_FASTA']), input_gff, input_fasta, output_fna, output_faa, output_gff) 
    return cmd

# create genbank files
def create_genebank_file_cmd(output, input_orf, input_fas, sample_name, config_settings) :
    cmd = "%s  --out %s --orphelia %s --fasta %s  --sample-name %s"\
           %((config_settings['METAPATHWAYS_PATH'] + config_settings['CREATE_GENBANK']), output, input_orf, input_fas, sample_name) 
    return cmd

# extract from the genbank files a fasta file
def create_genebank_2_fasta_cmd(options, input, output, config_settings):
    cmd = "%s %s --o %s %s" %((config_settings['METAPATHWAYS_PATH'] + config_settings['GENBANK_TO_FASTA']), options, output, input) 
    return cmd

def create_create_filtered_amino_acid_sequences_cmd(input, type, output, orf_lengths_file,  logfile, min_length, config_settings):
    cmd = "%s  --min_length %d --log_file %s  -i %s -o  %s -L %s -t %s" %((config_settings['METAPATHWAYS_PATH'] + config_settings['PREPROCESS_FASTA']), min_length, logfile, input,  output, orf_lengths_file, type) 
    return cmd 

#compute refscores
def create_refscores_compute_cmd(input, output, config_settings, algorithm):
    if algorithm == 'BLAST':
       cmd = "%s  -F %s -B %s -o %s -i %s -a  %s" %((config_settings['METAPATHWAYS_PATH'] + config_settings['COMPUTE_REFSCORE']), \
             (config_settings['METAPATHWAYS_PATH'] + config_settings['FORMATDB_EXECUTABLE']), \
             (config_settings['METAPATHWAYS_PATH'] + config_settings['BLASTP_EXECUTABLE']), \
              output, input, algorithm) 

    elif algorithm == 'LAST':
       cmd = "%s  -F %s -B %s -o %s -i %s -a %s" %((config_settings['METAPATHWAYS_PATH'] + config_settings['COMPUTE_REFSCORE']), \
             (config_settings['METAPATHWAYS_PATH'] + config_settings['LASTDB_EXECUTABLE']), \
             (config_settings['METAPATHWAYS_PATH'] + config_settings['LAST_EXECUTABLE']), \
              output, input, algorithm) 
    else:
        eprintf("Unknown choice for annotation algorithm : " + "\"" + algorithm + "\"" + "\n Please check your parameter file\n")
        exit_process("Unknown choice for annotation algorithm : " + "\"" + algorithm + "\"" + "\n Please check your parameter file\n")

    return cmd

def formatted_db_exists(dbname, suffixes):
    for suffix in suffixes:
       allfileList = glob(dbname + '*.' + suffix) 
       fileList = []
       tempFilePattern = re.compile(r''+ dbname + '\d*.' + suffix +'$');

       for aFile in allfileList:
           searchResult =  tempFilePattern.search(aFile)
           if searchResult:
             fileList.append(aFile)

       if len(fileList)==0 :
          eprintf("ERROR :  if formatted correctely then expected the files with pattern %s\n", dbname + suffix)
          return False

    return True

def check_if_raw_sequences_exist(filename):
    return path.exists(filename)


# Makes.re that the ref database is formatted for blasting 
def check_an_format_refdb(dbname, seqType,  config_settings, params, globallogger = None): 



    algorithm=  get_parameter( params,'annotation','algorithm').upper()
    
    suffixes=[]
    
    # we do not use LAST for searchingin the taxonomic databas. e.g., greengenes, silva, etc
    # if the db formatting request is done with nucl and LAST, we switch to BLAST-based formatting
    if algorithm == 'LAST' and seqType == 'nucl':
       algorithm = 'BLAST'
    
    if algorithm == 'LAST' and seqType == 'prot':
        suffixes = [ 'des', 'sds', 'suf', 'bck', 'prj', 'ssp', 'tis' ]
    
    if algorithm == 'BLAST':
      if seqType=='prot':
        suffixes = ['phr', 'psq', 'pin']
    
      if seqType=='nucl':
        suffixes = ['nhr', 'nsq', 'nin']
        
    # formatted DB directories
    taxonomic_formatted = config_settings['REFDBS'] + PATHDELIM + 'taxonomic' + PATHDELIM + 'formatted'
    functional_formatted = config_settings['REFDBS'] + PATHDELIM + 'functional' + PATHDELIM + 'formatted'
    # check if formatted folder exis. if not create it
    for d in [taxonomic_formatted, functional_formatted]:
        if not createFolderIfNotFound(d):
            eprintf("WARNING : Creating formatted subdirectory in blastDB folder.\n")
    
    # formatted database output paths
    if seqType == 'nucl':
       seqPath= config_settings['REFDBS'] + PATHDELIM + 'taxonomic' + PATHDELIM +  dbname
       formattedDBPath = taxonomic_formatted + PATHDELIM +  dbname
    elif seqType == 'prot':
       seqPath = config_settings['REFDBS'] + PATHDELIM + 'functional' + PATHDELIM +  dbname
       formattedDBPath = functional_formatted + PATHDELIM +  dbname
    else:
       eprintf("ERROR : Undefined sequnce type for %s!\n", dbname) 
       if globallogger!=None:
          globallogger.write("ERROR \t Undefined sequnce type for %s!\n" %( dbname) )
       exit_process()
    
    # database formatting executables paths
    if algorithm == 'LAST' and seqType =='prot':
      executable  = config_settings['METAPATHWAYS_PATH'] + PATHDELIM + config_settings['LASTDB_EXECUTABLE']
    else: # algorithm == 'BLAST':
      executable  = config_settings['METAPATHWAYS_PATH'] + PATHDELIM + config_settings['FORMATDB_EXECUTABLE']

    if not (formatted_db_exists(formattedDBPath,  suffixes) ):
        eprintf("WARNING : You do not seem to have Database %s formatted!\n", dbname)
        if globallogger!=None:
          globallogger.write("WARNING\t You do not seem to have Database %s formatted!\n" %(dbname) )
        if check_if_raw_sequences_exist(seqPath):
            eprintf("          Found raw sequences for  Database %s in folder %s!\n", dbname, seqPath)
            eprintf("          Trying to format on the fly .... for %s!\n", algorithm )
            if globallogger!=None:
               globallogger.write("ERROR\t Found raw sequences for  Database %s in folder %s!\n" %(dbname, seqPath) )
               globallogger.write("Trying to format on the fly .... for %s!\n" %(algorithm ) )

            result =format_db(executable, seqType, seqPath, formattedDBPath, algorithm)
            if result ==True:
                eprintf("          Formatting successful!\n")
                return 
            else:
                eprintf("          Formatting failed! Please consider formatting manually or do not try to annotate with this database!\n")
                if globallogger!=None:
                  globallogger.write("ERROR\tFormatting failed! Please consider formatting manually or do not try to annotate with this database!\n")
                exit_process()

        eprintf("ERROR : You do not even have the raw sequence for Database %s to format!\n", dbname)
        eprintf("        in the folder %s\n", seqPath)
        eprintf("        Please put the appropriate files in folder \"blastDB\"\n")
        if globallogger!=None:
            globallogger.write("ERROR \t You do not even have the raw sequence for Database %s to format!\n" %( dbname) )
            globallogger.write("in the folder %s\n" %(seqPath))
            globallogger.write("Please put the appropriate files in folder \"blastDB\"\n")
        exit_process()
  

#    fullRefDbMapName = config_settings['METAPATHWAYS_PATH'] + PATHDELIM + config_settings['REFDBS'] +PATHDELIM + dbname + '-names.txt'
#    if not doFilesExist( [fullRefDbMapName ] ):
#        s.exit(0)


def  make_sure_map_file_exists(config_settings, dbname, globallogger = None):
    dbmapFile = config_settings['REFDBS'] + PATHDELIM + 'functional' + PATHDELIM + 'formatted' + PATHDELIM + dbname + "-names.txt"
    seqFilePath = config_settings['REFDBS'] + PATHDELIM + 'functional' + PATHDELIM + dbname
    if not doFilesExist( [dbmapFile ] ):
         eprintf("WARNING: Trying to create database map file for %s\n", dbname)
         if globallogger!= None:
            globallogger.write("WARNING: Trying to create database map file for %s\n" %( dbname) )

         if not doFilesExist( [seqFilePath] ):
            eprintf("ERROR : You do not even have the raw sequence for Database  %s to format!\n", dbname)
            eprintf("      : Make sure you have the file %s\n", seqFilePath)

            if globallogger!= None:
               globallogger.write("ERROR \t You do not even have the raw sequence for Database  %s to format!\n" %( dbname))
               globallogger.write("Make sure you have the file %s\n" %( seqFilePath))

            exit_process()

         mapfile = open(dbmapFile,'w')
         seqFile = open(seqFilePath,'r')
         for line in seqFile:
             if re.match(r'>', line):
                 fprintf(mapfile, "%s\n",line.strip())
         seqFile.close()
         mapfile.close()

    return dbmapFile

# creates the command to blast the sample orf sequences against the reference databas.for the 
# purpose of annotation
def create_blastp_against_refdb_cmd(input, output, output_dir, sample_name,
        dbfilename, config_settings, params,  run_command, algorithm, db_type, globallogger = None): 
    max_evalue = float(get_parameter(params, 'annotation', 'max_evalue', default=0.000001))
    system =    get_parameter(params,  'metapaths_steps', 'BLAST_REFDB', default='yes')
    max_hits =    get_parameter(params,  'annotation', 'max_hits', default=5)


    dbname = get_refdb_name(dbfilename);
    if run_command:
         check_an_format_refdb(dbfilename, 'prot',  config_settings, params, globallogger = globallogger)

    if system=='grid':
       batch_size = get_parameter(params,  'grid_engine', 'batch_size', default=500)
       max_concurrent_batches = get_parameter(params,  'grid_engine', 'max_concurrent_batches', default=500)
       user = get_parameter(params,  'grid_engine', 'user', default='')
       server = get_parameter(params,  'grid_engine', 'server', default='')

       mem = get_parameter(params,  'grid_engine', 'RAM', default='10gb')
       walltime= get_parameter(params,  'grid_engine', 'walltime', default='10:10:10')

       cmd = {'sample_name':output_dir,  'dbnames':[dbname], 'database_files':[dbfilename],\
               'run_type':'overlay', 'batch_size':batch_size,'max_parallel_jobs':max_concurrent_batches,\
               'mem':mem, 'walltime':walltime,\
               'user':user, 'server':server, 'algorithm': algorithm } 
    else:
       if algorithm == 'BLAST':
          cmd="%s -num_threads 16  -max_target_seqs %s  -outfmt 6  -db %s -query  %s -evalue  %f  -out %s"\
            %((config_settings['METAPATHWAYS_PATH'] + config_settings['BLASTP_EXECUTABLE']), max_hits,\
             config_settings['REFDBS'] + PATHDELIM + db_type + PATHDELIM + 'formatted' + PATHDELIM + dbfilename, input, max_evalue, output) 
       if algorithm == 'LAST':
          cmd="%s -o %s -f 0 %s %s"\
            %((config_settings['METAPATHWAYS_PATH'] + config_settings['LAST_EXECUTABLE']), \
              output, config_settings['REFDBS'] + PATHDELIM + db_type + PATHDELIM + 'formatted' + PATHDELIM + dbfilename, input) 
    return cmd


# Command for pars[s.ng the blast flie snd create the parse blast files
#     input -- blastoutput
#     output -- parseed files
#     refscorefile   -- refscore file
#     min_bsr   -- minimum bsr ratio for accepting into annotation
#     max_evalue  -- max evalue
#     min_score   -- min score
#     min_length  -- min_length in amino acids, typcically 100 amino acids.ould be minimum
#     dbmane      -- name of the refrence databases
def create_parse_blast_cmd(input, refscorefile, dbname, dbmapfile,  config_settings, params, algorithm): 
    min_bsr = float(get_parameter(params, 'annotation', 'min_bsr', default=0.4))
    min_score = float(get_parameter(params, 'annotation', 'min_score', default=0.0))
    min_length = float(get_parameter(params, 'annotation', 'min_length', default=100))
    max_evalue = float(get_parameter(params, 'annotation', 'max_evalue', default=1000))

    cmd="%s -d %s  -b %s -m %s  -r  %s  --min_bsr %f  --min_score %f --min_length %f --max_evalue %f"\
         %((config_settings['METAPATHWAYS_PATH'] + config_settings['PARSE_BLAST']), dbname, input, dbmapfile,  refscorefile, min_bsr, min_score, min_length, max_evalue);

    if algorithm == 'LAST':
       cmd = cmd + ' --algorithm LAST'

    if algorithm == 'BLAST':
       cmd = cmd + ' --algorithm BLAST'

    return cmd

# this function creates the command that is required to make the annotated genbank file
def create_annotate_genebank_cmd(sample_name, mapping_txt, input_unannotated_gff, output_annotated_gff,\
           blast_results_dir,  options, refdbs, output_comparative_annotation,\
           config_settings, algorithm):
    cmd="%s --input_gff  %s -o %s  %s --output-comparative-annotation %s \
            --algorithm %s" %((config_settings['METAPATHWAYS_PATH'] +
                config_settings['ANNOTATE']),input_unannotated_gff,\
                output_annotated_gff,  options, output_comparative_annotation,\
                algorithm)

    for refdb in refdbs:
        if algorithm == "LAST":
            cmd = cmd + " -b " + blast_results_dir + PATHDELIM + sample_name + "." + refdb+ "." + algorithm + "out.parsed.txt -d " + refdb + " -w 1 "
        else:
            cmd = cmd + " -b " + blast_results_dir + PATHDELIM + sample_name + "." + refdb+ "." + algorithm + "out.parsed.txt -d " + refdb + " -w 1 "

    cmd = cmd + " -m " +  mapping_txt
    return cmd

def create_genbank_ptinput_sequin_cmd(input_annotated_gff, nucleotide_fasta, amino_fasta, outputs, config_settings, ncbi_params_file, ncbi_sequin_sbt):
    cmd="%s -g %s -n %s -p %s " %((config_settings['METAPATHWAYS_PATH'] + config_settings['GENBANK_FILE']), input_annotated_gff, nucleotide_fasta, amino_fasta) ; 

    if 'gbk' in outputs:
       cmd += ' --out-gbk ' + outputs['gbk']

    if ncbi_params_file and  'sequin' in outputs:
       cmd += ' --out-sequin ' + outputs['sequin']
       cmd += ' --sequin-params-file ' + ncbi_params_file
       cmd += ' --ncbi-sbt-file ' +  ncbi_sequin_sbt

    if 'ptinput' in outputs:
       cmd += ' --out-ptinput ' + outputs['ptinput']


    return cmd

def  create_report_files_cmd(dbs, input_dir, input_annotated_gff,  sample_name, output_dir, config_settings, algorithm, verbose):
    db_argument_string = ''
    for db in dbs:
        dbname = get_refdb_name(db)
        db_argument_string += ' -d ' + dbname
        db_argument_string += ' -b ' + input_dir + sample_name +'.' + dbname
        if algorithm == "LAST":
            db_argument_string += '.' + algorithm + 'out.parsed.txt'
        else:
            db_argument_string += '.' + algorithm + 'out.parsed.txt'
    basefun = config_settings['REFDBS'] + PATHDELIM + 'functional_categories' + PATHDELIM
    basencbi = config_settings['REFDBS'] + PATHDELIM + 'ncbi_tree' + PATHDELIM
    # construct command        
    #cmd="%s %s --input-annotated-gff %s  --input-kegg-maps  %s  --input-cog-maps %s --output-dir %s --ncbi-taxonomy-map %s --seed2ncbi-file %s"\
    cmd="%s %s --input-annotated-gff %s  --input-kegg-maps  %s  --input-cog-maps %s --input-seed-maps %s --output-dir %s --ncbi-taxonomy-map %s "\
           %((config_settings['METAPATHWAYS_PATH'] + config_settings['CREATE_REPORT_FILES']),\
              db_argument_string, input_annotated_gff,\
              basefun + 'KO_classification.txt', basefun + 'COG_categories.txt',  basefun + 'SEED_subsystems.txt',  output_dir,\
               basencbi + 'ncbi_taxonomy_tree.txt')
    if verbose:
       cmd += " -v"
    return cmd


def create_genbank_2_sequin_cmd(input_gbk_file, output_sequin_file, config_settings):
    cmd="%s -i %s -o %s" %((config_settings['METAPATHWAYS_PATH'] + config_settings['GENBANK_2_SEQUIN']),input_gbk_file, output_sequin_file); 
    return cmd


def create_reduce_genebank_cmd(input_gbk_file, output_reduced_gbk_file, config_settings):
    cmd="%s -i %s -o %s" %((config_settings['METAPATHWAYS_PATH'] + config_settings['REDUCE_ANNOTATED_FILE']),input_gbk_file, output_reduced_gbk_file ); 
    return cmd

#creates the fasta and the pf files to be processed by pathologic and  a subsequent step will 
# create the PGDB
def create_fasta_and_pf_files_cmd(sample_name, input_reduced_annotated_gbk_file_pat, output_fasta_pf_dir, config_settings):
    cmd="%s -s %s -p %s -a %s" %((config_settings['METAPATHWAYS_PATH'] + config_settings['PATHOLOGIC_INPUT']), sample_name, output_fasta_pf_dir, input_reduced_annotated_gbk_file_pat)
    return cmd

def create_create_genetic_elements_cmd(output_fasta_pf_dir, config_settings):
    cmd="%s -p %s" %((config_settings['METAPATHWAYS_PATH'] + config_settings['CREATE_GENETIC_ELEMENTS']),output_fasta_pf_dir)
    return cmd

# this function creates an organism file for pathway tools
def create_create_organism_params_cmd(yaml_file, output_fasta_pf_dir, pgdb_ID, config_settings):
    cmd="%s --yaml-file %s --ptools-dir %s %s" %((config_settings['METAPATHWAYS_PATH'] + config_settings['CREATE_ORGANISM_PARAM']), yaml_file, output_fasta_pf_dir, pgdb_ID)
    return cmd

# this is where the command for PGDB creation is called, by using 
def create_pgdb_using_pathway_tools_cmd(output_fasta_pf_dir, taxonomic_pruning_flag, config_settings):
    cmd="%s -patho %s"  %(config_settings['PATHOLOGIC_EXECUTABLE'], output_fasta_pf_dir +  PATHDELIM)
    if taxonomic_pruning_flag=='no':
        cmd= cmd + " -no-taxonomic-pruning "
        #cmd= cmd + " -no-taxonomic-pruning -no-cel-overview -no-web-cel-ov"
    cmd= cmd + " -no-web-cel-overview"
    return cmd
 

def create_scan_rRNA_seqs_cmd(input_fasta, output_blast, refdb, config_settings,params, command_Status, db_type, globallogger = None):

    if command_Status:
       check_an_format_refdb(refdb, 'nucl',  config_settings, params, globallogger = globallogger)
    else:
       s.exit(0)


    cmd="%s -outfmt 6 -num_threads 16  -query %s -out %s -db %s -max_target_seqs 5"%((config_settings['METAPATHWAYS_PATH'] + config_settings['BLASTN_EXECUTABLE']),input_fasta,output_blast, config_settings['REFDBS'] + PATHDELIM + db_type + PATHDELIM + 'formatted' + PATHDELIM + refdb)
    return cmd


# create the command to do rRNA scan statististics
def create_rRNA_scan_statistics(blastoutput, refdbname, bscore_cutoff, eval_cutoff, identity_cutoff, config_settings, rRNA_stat_results):
    cmd= "%s -o %s -b %s -e %s -s %s"  %((config_settings['METAPATHWAYS_PATH'] + config_settings['SCAN_rRNA']), rRNA_stat_results, bscore_cutoff, eval_cutoff, identity_cutoff)

    cmd =  cmd +  " -i "  + blastoutput + " -d " + config_settings['REFDBS'] + "/taxonomic/" +  refdbname 

    return cmd

# create the command to do tRNA scan statististics
def create_tRNA_scan_statistics(in_file,stat_file, fasta_file,  config_settings):
    cmd= "%s -o %s -F %s  -i %s -T %s  -D %s"  %((config_settings['METAPATHWAYS_PATH'] + config_settings['SCAN_tRNA']) ,\
           stat_file, fasta_file, in_file,\
          (config_settings['METAPATHWAYS_PATH'] + config_settings['RESOURCES_DIR'])+ PATHDELIM + 'TPCsignal',\
          (config_settings['METAPATHWAYS_PATH'] + config_settings['RESOURCES_DIR'])+ PATHDELIM + 'Dsignal')
    return cmd

# create the command to make the MLTreeMap Images
def create_MLTreeMap_Imagemaker(mltreemap_image_output, mltreemap_final_outputs, config_settings):
    executable_path = config_settings['MLTREEMAP_IMAGEMAKER']
    if not path.isfile( executable_path):
        executable_path = config_settings['METAPATHWAYS_PATH'] + executable_path
    cmd= "%s -i %s -o %s -m a"  %(executable_path, mltreemap_final_outputs, mltreemap_image_output) 
    return cmd

# create the command to do mltreemap calculations
def create_MLTreeMap_Calculations(mltreemap_input_file, mltreemap_output_dir, config_settings):
    executable_path = config_settings['MLTREEMAP_CALCULATION']
    if not path.isfile( executable_path):
        executable_path = config_settings['METAPATHWAYS_PATH'] + executable_path
    cmd= "%s -i %s -o %s -e %s"  %(executable_path, mltreemap_input_file, mltreemap_output_dir, config_settings['EXECUTABLES_DIR'] ) 
    return cmd

# gather mltreemap calculations 
def create_MLTreeMap_Hits(mltreemap_output_dir, output_folder, config_settings):
    cmd= "%s -i %s -o %s"  %(config_settings['METAPATHWAYS_PATH'] + config_settings['MLTREEMAP_HITS'], mltreemap_output_dir, output_folder +PATHDELIM + 'sequence_to_cog_hits.txt') 
    return cmd


#gets the parameter value from a category as.ecified in the 
# parameter file
def get_parameter(params, category, field, default = None):
    if params == None:
      return default

    if category in params:
        if field in params[category]:
            return params[category][field]
        else:
            return default
    return default


# parameter file
def get_make_parameter(params,category, field, default = False):
    if category in params:
        if field in params[category]:
            return params[category][field]
        else:
            return default
    return default

def get_pipeline_steps(steps_log_file):
    try:
       logfile = open(steps_log_file, 'r')
    except IOError:
       eprintf("Did not find %s!\n", logfile) 
       eprintf("Try running in \'complete\' run-type\n")
    else:
       lines = logfile.readlines()

    pipeline_steps = None
    return pipeline_steps


def write_run_parameters_file(fileName, parameters):
    try:
       paramFile = open(fileName, 'w')
    except IOError:
       eprintf("Cannot write run parameters to file %s!\n", fileName)
       exit_process("Cannot write run parameters to file %s" %(fileName) )

#       16s_rRNA      {'min_identity': '40', 'max_evalue': '0.000001', 'min_bitscore': '06', 'refdbs': 'silva_104_rep_set,greengenes_db_DW'}
    paramFile.write("\nRun Date : " + str(date.today()) + " \n")

    paramFile.write("\n\nNucleotide Quality Control parameters[s.n")
    paramFile.write( "  min length" + "\t" + str(parameters['quality_control']['min_length']) + "\n")

    paramFile.write("\n\nORF prediction parameters[s.n")
    paramFile.write( "  min length" + "\t" + str(parameters['orf_prediction']['min_length']) + "\n")
    paramFile.write( "  algorithm" + "\t" + str(parameters['orf_prediction']['algorithm']) + "\n")


    paramFile.write("\n\nAmino acid quality control and annotation parameters[s.n")
    paramFile.write( "  min bit score" + "\t" + str(parameters['annotation']['min_score']) + "\n")
    paramFile.write( "  min seq length" + "\t" + str(parameters['annotation']['min_length']) + "\n")
    paramFile.write( "  annotation reference dbs" + "\t" + str(parameters['annotation']['dbs']) + "\n")
    paramFile.write( "  min BSR" + "\t" + str(parameters['annotation']['min_bsr']) + "\n")
    paramFile.write( "  max evalue" + "\t" + str(parameters['annotation']['max_evalue']) + "\n")

    paramFile.write("\n\nPathway Tools parameters[s.n")
    paramFile.write( "  taxonomic pruning " + "\t" + str(parameters['ptools_settings']['taxonomic_pruning']) + "\n")

    paramFile.write("\n\nrRNA search/match parameters[s.n")
    paramFile.write( "  min identity" + "\t" + str(parameters['rRNA']['min_identity']) + "\n")
    paramFile.write( "  max evalue" + "\t" + str(parameters['rRNA']['max_evalue']) + "\n")
    paramFile.write( "  rRNA reference dbs" + "\t" + str(parameters['rRNA']['refdbs']) + "\n")

    paramFile.close()


# checks if the necessary files, directories  and executables really exis.or not
def check_config_settings(config_settings, file, globalerrorlogger = None):
   essentialItems= ['METAPATHWAYS_PATH', 'EXECUTABLES_DIR', 'RESOURCES_DIR']
   missingItems = []

   for key, value in  config_settings.items():
      # make sure  MetaPathways directory is present
      if key in ['METAPATHWAYS_PATH' ]:
         if not path.isdir( config_settings[key]) :
            eprintf("ERROR: Path for \"%s\" is NOT set properly in configuration file \"%s\"\n", key, file)  
            eprintf("ERROR: Currently it is.t to \"%s\"\n",  config_settings[key] )  

            if globalerrorlogger!=None:
               globalerrorlogger.write("ERROR\tPath for \"%s\" is NOT set properly in configuration file \"%s\"\n"  %(key, file))  
               globalerrorlogger.write("       Currently it is.t to \"%s\"\n" %(config_settings[key] )  )
            missingItems.append(key) 
         continue


      # make sure  REFDB directories are present
      if key in [ 'REFDBS' ]:
         if not path.isdir( config_settings[key]) :
            eprintf("ERROR: Path for \"%s\" is NOT set properly in configuration file \"%s\"\n", key, file)  
            eprintf("ERROR: Currently it is.t to \"%s\"\n", config_settings[key] )  
            if globalerrorlogger!=None:
                globalerrorlogger.write("ERROR\tPath for \"%s\" is NOT set properly in configuration file \"%s\"\n" %(key,file))
                globalerrorlogger.write("Currently it is.t to \"%s\"\n" %( config_settings[key]) )  
            missingItems.append(key) 
         continue

      # make sure EXECUTABLES_DIR directories are present
      if key in [ 'EXECUTABLES_DIR']:
         if not path.isdir( config_settings['METAPATHWAYS_PATH'] + PATHDELIM + config_settings[key]) :
            eprintf("ERROR: Path for \"%s\" is NOT set properly in configuration file \"%s\"\n", key, file)  
            eprintf("ERROR: Currently it is.t to \"%s\"\n", config_settings[key] )  
            if globalerrorlogger!=None:
               globalerrorlogger.write("ERROR\tPath for \"%s\" is NOT set properly in configuration file \"%s\"\n" %(key, file))  
               globalerrorlogger.write("Currently it is.t to \"%s\"\n" %( config_settings[key] )) 
            missingItems.append(key) 
         continue

      # make sure RESOURCES_DIR directories are present
      if key in [ 'RESOURCES_DIR']:
         if not path.isdir( config_settings['METAPATHWAYS_PATH'] + PATHDELIM + config_settings[key]) :
            eprintf("ERROR: Path for \"%s\" is NOT set properly in configuration file \"%s\"\n", key, file)  
            eprintf("ERROR: Currently it is.t to \"%s\"\n",  config_settings['METAPATHWAYS_PATH'] + PATHDELIM + config_settings[key] )  
            print  config_settings['METAPATHWAYS_PATH'], config_settings[key] 
            if globalerrorlogger!=None:
               globalerrorlogger.write("ERROR\tPath for \"%s\" is NOT set properly in configuration file \"%s\"\n" %(key, file))
               globalerrorlogger.write("Currently it is.t to \"%s\"\n" %( config_settings[key]))  
            missingItems.append(key) 
         continue

      # make sure  MetaPaths directory is present
      if key in ['PERL_EXECUTABLE',  'PYTHON_EXECUTABLE' , 'PATHOLOGIC_EXECUTABLE' ]:
         if not path.isfile( config_settings[key]) :
            eprintf("ERROR: Path for \"%s\" is NOT set properly in configuration file \"%s\"\n", key, file)  
            eprintf("ERROR: Currently it is.t to \"%s\"\n", config_settings[key] )  
            if globalerrorlogger!=None:
               globalerrorlogger.write("ERROR\tPath for \"%s\" is NOT set properly in configuration file \"%s\"\n" %(key, file)) 
               globalerrorlogger.write("Currently it is.t to \"%s\"\n" %( config_settings[key] ) )
            missingItems.append(key) 
         continue

      
      # check if the desired file exis. if not, then print a message
      if not path.isfile( config_settings['METAPATHWAYS_PATH'] +  value ) :
          if not path.isfile( value ) :
              eprintf("ERROR:Path for \"%s\" is NOT set properly in configuration file \"%s\"\n", key, file)  
              eprintf("Currently it is.t to \"%s\"\n", config_settings['METAPATHWAYS_PATH'] + value ) 
              if globalerrorlogger!=None:
                 globalerrorlogger.write("ERROR\tPath for \"%s\" is NOT set properly in configuration file \"%s\"\n" %(key, file) )
                 globalerrorlogger.write("Currently it is.t to \"%s\"\n" %(config_settings['METAPATHWAYS_PATH'] + value)) 
              missingItems.append(key) 
          continue
     
   stop_execution = False
   for item in missingItems:
      if item in essentialItems:
         eprintf("ERROR\t Essential field in setting %s is missing in configuration file!\n", item)
         if globalerrorlogger!=None:
            globalerrorlogger.write("ERROR\tEssential field in setting %s is missing in configuration file!\n" %(item))
         stop_execution = True

   if stop_execution ==True:
      eprintf("ERROR: Terminating execution due to missing essential  fields in configuration file!\n")
      if globalerrorlogger!=None:
         globalerrorlogger.write("ERROR\tTerminating execution due to missing essential  fields in configuration file!\n")
      exit_process()

   

# This function reads the pipeline configuration file and sets the 
# paths to differenc scripts and executables the pipeline call
def read_pipeline_configuration( file, globallogger ):
    patternKEYVALUE = re.compile(r'^([^\t\s]+)[\t\s]+\'(.*)\'')
    try:
       configfile = open(file, 'r')
    except IOError:
       eprintf("ERROR :Did not find pipeline config %s!\n", file) 
       globalerrorlogger.write("ERROR\tDid not find pipeline config %s!\n" %(file)) 
    else:
       lines = configfile.readlines()

    config_settings = {}
    for line in lines:
        if not re.match("#",line) and len(line.strip()) > 0 :
           line = line.strip()
           result = patternKEYVALUE.search(line)
           
           try:
              if len(result.groups()) == 2:
                 fields = result.groups()
              else:
                 eprintf("     The following line in your config settings files is.t set up yet\n")
                 eprintf("     Please rerun the pipeline after setting up this line\n")
                 eprintf("     Error in line : %s\n", line)
                 globalerrorlogger(
                      "WARNING\t\n"+\
                      "     The following line in your config settings files is.t set up yet\n"+\
                      "     Please rerun the pipeline after setting up this line\n"+\
                      "     Error in line : %s\n" %(line))

                 exit_process()
           except:
                 eprintf("     The following line in your config settings files is.t set up yet\n")
                 eprintf("     Please rerun the pipeline after setting up this line\n")
                 eprintf("     Error ine line : %s\n", line)
                 globalerrorlogger(
                      "WARNING\t\n"+\
                      "     The following line in your config settings files is.t set up yet\n"+\
                      "     Please rerun the pipeline after setting up this line\n"+\
                      "     Error in line : %s\n" %(line))
                 exit_process()
              
           if PATHDELIM=='\\':
              config_settings[fields[0]] = re.sub(r'/',r'\\',fields[1])   
           else:
              config_settings[fields[0]] = re.sub(r'\\','/',fields[1])   

           
    config_settings['METAPATHWAYS_PATH'] = config_settings['METAPATHWAYS_PATH'] + PATHDELIM
    config_settings['REFDBS'] = config_settings['REFDBS'] + PATHDELIM
    
    check_config_settings(config_settings, file, globallogger);
    config_settings['configuration_file'] = file

    return config_settings

#check for empty values in parameter settings 
def  checkMissingParam_values(params, choices, logger = None):
     reqdCategoryParams = { 
                            'annotation': {'dbs': False}, 
                            'orf_prediction':{}, 
                            'rRNA':{},
                            'metapaths_steps':{}
                         }

     success  = True
     for category in choices:
       for parameter in choices[category]:
         if (not params[category][parameter]) and\
            ( (category in reqdCategoryParams) and\
               (parameter in reqdCategoryParams[category]) and   reqdCategoryParams[category][parameter]) :
            print category, parameter
            print reqdCategoryParams
            print reqdCategoryParams[category]
            eprintf('ERROR: Empty parameter %s of type %s\n'  %(parameter, category))
            eprintf('Please select at least one database for %s\n'  %(category))
            if logger!=None:
               logger.write('ERROR\tEmpty parameter %s of type %s\n'  %(parameter, category))
               logger.write('Please select at least one database for %s\n'  %(category))
            success = False

     return success

# check if all of the metapaths_steps have 
# settings from the valid list [ yes, skip stop, redo]

def  checkParam_values(allcategorychoices, parameters, runlogger = None):
     for category in allcategorychoices:
        for choice in allcategorychoices[category]:
           if choice in parameters: 

             if not parameters[choice] in allcategorychoices[category][choice]:
                 logger.write('ERROR\tIncorrect setting in your parameter file')
                 logger.write('for step %s as %s' %(choice, parameters[choices]))
                 eprintf("ERROR: Incorrect setting in your parameter file" +\
                         "       for step %s as %s", choice, parameters[choices])
                 exit_process()

def checkMetapathsteps(params, runlogger = None):
     choices = { 'metapaths_steps':{}, 'annotation':{}, 'INPUT':{} }

     choices['INPUT']['format']  = ['fasta', 'gbk_unannotated', 'gbk_annotated', 'gff_unannotated', 'gff_annotated']

     choices['annotation']['algorithm'] =  ['last', 'blast'] 

     choices['metapaths_steps']['PREPROCESS_FASTA']   = ['yes', 'skip', 'stop', 'redo']
     choices['metapaths_steps']['ORF_PREDICTION']  = ['yes', 'skip', 'stop', 'redo']
     choices['metapaths_steps']['GFF_TO_AMINO']    = ['yes', 'skip', 'stop', 'redo']
     choices['metapaths_steps']['FILTERED_FASTA']  = ['yes', 'skip', 'stop', 'redo']
     choices['metapaths_steps']['COMPUTE_REFSCORE']    = ['yes', 'skip', 'stop', 'redo']
     choices['metapaths_steps']['BLAST_REFDB'] = ['yes', 'skip', 'stop', 'redo', 'grid']
     choices['metapaths_steps']['PARSE._BLAST'] = ['yes', 'skip', 'stop', 'redo']
     choices['metapaths_steps']['SCAN_rRNA']   = ['yes', 'skip', 'stop', 'redo']
     choices['metapaths_steps']['STATS_rRNA']  = ['yes', 'skip', 'stop', 'redo']
     choices['metapaths_steps']['ANNOTATE']    = ['yes', 'skip', 'stop', 'redo']
     choices['metapaths_steps']['PATHOLOGIC_INPUT']    = ['yes', 'skip', 'stop', 'redo']
     choices['metapaths_steps']['GENBANK_FILE']    = ['yes', 'skip', 'stop', 'redo']
     choices['metapaths_steps']['CREATE_SEQUIN_FILE']  = ['yes', 'skip', 'stop', 'redo']
     choices['metapaths_steps']['CREATE_REPORT_FILES']  = ['yes', 'skip', 'stop', 'redo']
     choices['metapaths_steps']['SCAN_tRNA']   = ['yes', 'skip', 'stop', 'redo']
     choices['metapaths_steps']['MLTREEMAP_CALCULATION']   = ['yes', 'skip', 'stop', 'redo']
     choices['metapaths_steps']['MLTREEMAP_IMAGEMAKER']    = ['yes', 'skip', 'stop', 'redo']
     choices['metapaths_steps']['PATHOLOGIC']  = ['yes', 'skip', 'stop', 'redo']


     if params['metapaths_steps']:
        checkParam_values(choices, params['metapaths_steps'], runlogger)

     checkparams = {}
     checkparams['annotation'] = []
     checkparams['annotation'].append('dbs') 

     if not checkMissingParam_values(params, checkparams, runlogger):
        exit_process("Missing parameters")


def  copy_fna_faa_gff_orf_prediction( source_files, target_files, config_settings) :

     for source, target in zip(source_files, target_files):  

         sourcefile = open(source, 'r')
         targetfile = open(target, 'w')
         sourcelines = sourcefile.readlines()
         for line in sourcelines:
            fprintf(targetfile, "%s\n", line.strip())

         sourcefile.close()
         targetfile.close()


#################################################################################
########################### BEFORE BLAST ########################################
#################################################################################
def run_metapathways_before_BLAST(s, input_fp, output_dir, all_samples_output_dir, globallogger,  command_handler, command_line_params, params, metapaths_config, status_update_callback, config_file, run_type, config_settings = None):

    
    jobcreator = JobCreator(params, config_settings)
    jobcreator.addJobs(s)
    execute_tasks(s, verbose = command_line_params['verbose'])    

    _exit(0)

    ####################  IMPORTANT VARIABLES ########################
    checkMetapathsteps(params, globallogger)

#----------------------- path variables -----------------------------------------------


#-----------------------------------------------------------------------
    
#this is the part before BLAST PART1    


    commands= [] 

    # IF the format is gff then copy the gff, fna and faa to the orf_prediction folder
    if params['INPUT']['format'] in ['gff-annotated', 'gff-unannotated' ]:
       input_gff = re.sub('[.][a-zA-Z]*$','',input_fp) + ".gff"
       input_fasta = re.sub('[.][a-zA-Z]*$','',input_fp) + ".fasta"
       input_faa = re.sub('[.][a-zA-Z]*$','',input_fp) + ".faa"

       output_fasta = s.preprocessed_dir + s.sample_name + ".fasta"
       output_faa = s.orf_prediction_dir + s.sample_name + ".faa"
       if params['INPUT']['format'] in ['gff-unannotated' ]:
             output_gff = s.orf_prediction_dir + s.sample_name + ".unannot.gff"
       if params['INPUT']['format'] in ['gff-annotated' ]:
             output_gff = s.genbank_dir + s.sample_name + ".annot.gff"

       command_Status =  get_parameter( params,'metapaths_steps','PREPROCESS_FASTA')
       removeFileOnRedo(command_Status, output_fasta)
       removeFileOnRedo(command_Status, output_faa)
       removeFileOnRedo(command_Status, output_gff)

       enable_flag = shouldRunStep(run_type, output_fna) or shouldRunStep(run_type, output_faa)  or shouldRunStep(run_type, output_gff)  

       input_gff_to_fasta_faa_gff_cmd=convert_gff_to_fna_faa_gff([input_gff, input_fasta, input_faa], [ output_gff, output_fasta, output_faa], config_settings) 
       commands.append(["\n" + '*** ' + s.sample_name + ' ***\n' + "1. Converting gff file to fna, faa and gff files ....", input_gff_to_fasta_faa_gff_cmd,\
                       'PREPROCESS_FASTA', command_Status, enable_flag])



    #################################
    
    # IF the format is gbk then convert them  to gff faa and fna files
    if params['INPUT']['format'] in ['gbk-annotated', 'gbk-unannotated' ]:
       input_gbk = re.sub('[.][a-zA-Z]*$','',input_fp) + ".gbk"
       output_fna = s.preprocessed_dir + s.sample_name + ".fasta"
       output_faa = s.orf_prediction_dir + s.sample_name + ".faa"

       if params['INPUT']['format'] in ['gbk-unannotated' ]:
             output_gff = s.orf_prediction_dir + s.sample_name + ".unannot.gff"
       if params['INPUT']['format'] in ['gbk-annotated' ]:
             output_gff = s.genbank_dir + s.sample_name + ".annot.gff"

       genbank_to_fna_faa_gff_cmd = convert_gbk_to_fna_faa_gff(input_gbk, output_fna, output_faa, output_gff, config_settings) 
    
       command_Status =  get_parameter( params,'metapaths_steps','PREPROCESS_FASTA')
       removeFileOnRedo(command_Status, output_fna)
       removeFileOnRedo(command_Status, output_faa)
       removeFileOnRedo(command_Status, output_gff)
       enable_flag = shouldRunStep(run_type, output_fna) or shouldRunStep(run_type, output_faa)  or shouldRunStep(run_type, output_gff)  

       message = "\n" + '*** ' + s.sample_name + ' ***\n' +"\n1. Converting genbank file to fna, faa and gff files ...."
       commands.append([message, genbank_to_fna_faa_gff_cmd, 'PREPROCESS_FASTA', command_Status, enable_flag])

    #################################
    if params['INPUT']['format'] in ['fasta']:
         output_fas = s.preprocessed_dir + PATHDELIM + s.sample_name + ".fasta" 
         print "writring ", s.output_run_statistics_dir 
         write_run_parameters_file(s.output_run_statistics_dir + PATHDELIM + "run_parameters.txt", params)
         nuc_stats_file = s.output_run_statistics_dir + PATHDELIM + s.sample_name + ".nuc.stats" 
         contig_lengths_file = s.output_run_statistics_dir + PATHDELIM + s.sample_name + ".contig.lengths.txt" 
     
         min_length = float(get_parameter(params, 'quality_control', 'min_length', default=300))
         
         input_file = input_fp 
         mapping_txt =  s.preprocessed_dir + PATHDELIM + s.sample_name + ".mapping.txt" 

         quality_check_cmd = create_quality_check_cmd(min_length, 'nucleotide', nuc_stats_file, contig_lengths_file, input_file, output_fas, mapping_txt, config_settings) 
     
     
         command_Status =  get_parameter( params,'metapaths_steps','PREPROCESS_FASTA')
         removeFileOnRedo(command_Status, output_fas)
         removeFileOnRedo(command_Status, nuc_stats_file)
         removeFileOnRedo(command_Status, contig_lengths_file)
         # Niels - changed from shouldRunStep1() to shouldRunStep()
         enable_flag = shouldRunStep(run_type, output_fas) or shouldRunStep(run_type, nuc_stats_file ) or shouldRunStep(run_type, contig_lengths_file)

         message = "\n" + '*** ' + s.sample_name + ' ***\n' +"\n1. Running Quality Check ...."
         commands.append( [message, quality_check_cmd, 'PREPROCESS_FASTA', command_Status, enable_flag])
     
         #################################
     
         # ORF PREDICTION STEP
         #s.orf_prediction_dir =  output_dir + "/orf_prediction/"
         input_file = output_fas
         output_gff = s.orf_prediction_dir + s.sample_name + ".gff"
         orf_prediction_cmd = create_orf_prediction_cmd(" -m -p meta -f gff", "log_file",  input_file, output_gff,config_settings) 
     
          # make folder for orf prediction procesing
         command_Status=  get_parameter( params,'metapaths_steps','ORF_PREDICTION')
         removeFileOnRedo(command_Status, output_gff)
         enable_flag = shouldRunStep(run_type,  output_gff) 
        
         #add command
         message = "\n" + '*** ' + s.sample_name + ' ***\n' +"\n2. Running ORF Prediction ...."
         commands.append([message, orf_prediction_cmd, 'ORF_PREDICTION',command_Status, enable_flag])
         #################################


         # GFF to Fasta
         input_gff = output_gff
         input_fasta= output_fas
         output_faa = s.orf_prediction_dir + PATHDELIM +  s.sample_name + ".faa"   
         output_fna = s.orf_prediction_dir + PATHDELIM +  s.sample_name + ".fna"   
         output_gff = s.orf_prediction_dir + PATHDELIM +  s.sample_name + ".unannot.gff"   
         command_Status= get_parameter( params,'metapaths_steps','GFF_TO_AMINO')
         removeFileOnRedo(command_Status, output_faa)
         enable_flag=shouldRunStep1(run_type, s.orf_prediction_dir,  [ s.sample_name + '.unannot.gff',  s.sample_name + '.faa' , s.sample_name + '.fna'] )  

         create_aa_sequences_cmd = create_aa_orf_sequences_cmd(input_gff, input_fasta, output_fna, output_faa, output_gff, config_settings) 

         commands.append(["\n" + '*** ' + s.sample_name + ' ***\n' +"\n3. Creating the Amino Acid sequences ....", create_aa_sequences_cmd, 'GFF_TO_AMINO',command_Status, enable_flag])
    #################################

    
    #------ COMPUTE THE STATISTICS OF THE AMINO ACID SEQUENCES
    output_faa = s.orf_prediction_dir + PATHDELIM +  s.sample_name + ".faa"   

    input_gbk_faa = output_faa
    output_filtered_faa = s.orf_prediction_dir + PATHDELIM +  s.sample_name + ".qced.faa"   
    amino_stats_file = s.output_run_statistics_dir + PATHDELIM + s.sample_name + ".amino.stats"
    orf_lengths_file = s.output_run_statistics_dir + PATHDELIM + s.sample_name + ".orf.lengths.txt"

    min_length = float(get_parameter(params, 'orf_prediction', 'min_length', default=100))

    create_filtered_amino_acid_sequences_cmd = create_create_filtered_amino_acid_sequences_cmd(\
                                               input_gbk_faa, 'amino', output_filtered_faa,\
                                               orf_lengths_file, amino_stats_file, min_length,\
                                               config_settings)

    command_Status=  get_parameter(params,'metapaths_steps','FILTERED_FASTA')
    removeFileOnRedo(command_Status, output_filtered_faa)
    removeFileOnRedo(command_Status, amino_stats_file)
    removeFileOnRedo(command_Status, orf_lengths_file)
    enable_flag=shouldRunStep(run_type, output_filtered_faa)  or shouldRunStep(run_type, amino_stats_file)  or shouldRunStep(run_type, orf_lengths_file)


    #add command

    commands.append( ["\n" + '*** ' + s.sample_name + ' ***\n' +"\n4. Creating the filtered fasta sequences ....", create_filtered_amino_acid_sequences_cmd, 'FILTERED_FASTA', command_Status, enable_flag])
    #################################


    # COMPUTE THE REFSCORES FROM THE FASTA FILE OF AMINO ACID SEQUENCES
    #s.blast_results_dir =  output_dir + "/blast_results"
    input_faa =  output_filtered_faa 
      
    output_refscores =  s.blast_results_dir + PATHDELIM + s.sample_name + ".refscores" + "." + s.algorithm 
    if params['INPUT']['format'] in ['fasta', 'gbk-unannotated', 'gff-unannotated' ]:
       #algorithm=  get_parameter( params,'annotation','algorithm')
       refscores_compute_cmd = create_refscores_compute_cmd(input_faa, output_refscores, config_settings, s.algorithm) 
       command_Status=  get_parameter( params,'metapaths_steps','COMPUTE_REFSCORE')

       removeFileOnRedo(command_Status, output_refscores)
       enable_flag=shouldRunStep(run_type, output_refscores)  


       # add command
       commands.append( ["\n" + '*** ' + s.sample_name + ' ***\n' +"\n5. Computing refscores for the ORFs ....", refscores_compute_cmd,'COMPUTE_REFSCORE', command_Status, enable_flag])
    #################################

#   Now call the commands
    command_handler(commands, status_update_callback, s.runlogger, s.stepslogger, s.errorlogger, s.runstatslogger, command_line_params)

#################################################################################
###########################  BLAST ##############################################
#################################################################################
def run_metapathways_at_BLAST(s, input_fp, output_dir, all_samples_output_dir, globallogger, command_handler, command_line_params, params, metapaths_config, status_update_callback, config_file, run_type, config_settings = None):

    

    # BLAST THE ORFs AGAINST THE REFERENCE DATABAs. FOR FUNCTIONAL ANNOTATION
    commands = []
    dbstring = get_parameter(params, 'annotation', 'dbs', default=None)
    # all these dbs are under functional
    dbs= [x.strip() for x in dbstring.split(",") ]

    output_filtered_faa = s.orf_prediction_dir + PATHDELIM +  s.sample_name + ".qced.faa"   
    input_faa =  output_filtered_faa 

    db_type = 'functional'

    if params['INPUT']['format'] in ['fasta', 'gbk-unannotated', 'gff-unannotated' ]:
       command_Status=  get_parameter( params,'metapaths_steps','BLAST_REFDB')
       message = "\n" + '*** ' + s.sample_name + ' ***\n' + "\n6. " + s.algorithm.upper() + "ing ORFs against reference database - "
       for db in dbs:
             dbname = get_refdb_name(db);
             blastoutput = s.blast_results_dir + PATHDELIM + s.sample_name + "." + dbname    # append "algorithout"
             blastoutput += "."+s.algorithm + "out"

             removeFileOnRedo(command_Status, blastoutput)
             enable_flag=shouldRunStep(run_type, blastoutput)  

              
             blast_against_refdb_cmd=create_blastp_against_refdb_cmd(input_faa, blastoutput,\
                                       output_dir,  s.sample_name, db,\
                                      config_settings, params, \
                                      enable_flag, s.algorithm, db_type, globallogger =globallogger)
   
             commands.append([message + db + " ....", blast_against_refdb_cmd, 'BLAST_REFDB_' + dbname, command_Status, enable_flag])
             message = "\n                                               "
    #################################
#   Now call the commands
    command_handler(commands, status_update_callback, s.runlogger, s.stepslogger, s.errorlogger, s.runstatslogger,  command_line_params)



#################################################################################
########################### AFTER BLAST #########################################
#################################################################################
#This is the part after BLAST PART3
def run_metapathways_after_BLAST(s, input_fp, output_dir, all_samples_output_dir, globallogger,  command_handler, command_line_params, params, metapaths_config, status_update_callback, config_file,  run_type, config_settings = None):
    
    #algorithm = get_parameter(params, 'annotation', 'algorithm', default='BLAST').upper()
    #globallogger = WorkflowLogger(generate_log_fp(all_samples_output_dir, basefile_name= 'global_errors[s.warnings'), open_mode='a')

    # the importatn variables
    commands = []
    dbstring = get_parameter(params, 'annotation', 'dbs', default=None)
    dbs= [x.strip() for x in dbstring.split(",") ]

    output_filtered_faa = s.orf_prediction_dir + PATHDELIM +  s.sample_name + ".qced.faa"   
    # PArs[s. THE BLAST RESULTS 
    #input_gbk_faa =  output_gbk_faa 
    message = "\n" + '*** ' + s.sample_name + ' ***\n' +"\n7. Parsing blast outputs for reference database - "
    if params['INPUT']['format'] in ['fasta', 'gbk-unannotated', 'gff-unannotated' ]:
       for db in dbs:
          dbname = get_refdb_name(db);
   
          input_db_blastout = s.blast_results_dir + PATHDELIM + s.sample_name + "." + dbname 
          refscorefile = s.blast_results_dir + PATHDELIM + s.sample_name + ".refscores"
          output_db_blast_parse = s.blast_results_dir + PATHDELIM + s.sample_name + "." + dbname 

          if s.algorithm == 'BLAST':
            output_db_blast_parse += "." + s.algorithm + "out.parsed.txt"
            input_db_blastout += "." + s.algorithm + "out"
          if s.algorithm == 'LAST':
            output_db_blast_parse += "." + s.algorithm + "out.parsed.txt"
            input_db_blastout += "." + s.algorithm + "out"
    
          command_Status=  get_parameter( params,'metapaths_steps','PARSE_BLAST')
          removeFileOnRedo(command_Status, output_db_blast_parse)
          enable_flag=shouldRunStep(run_type, output_db_blast_parse)  

   
          dbmapfile = make_sure_map_file_exists(config_settings, db, globallogger = globallogger)
   
          parse_blast_cmd = create_parse_blast_cmd(input_db_blastout, refscorefile,  dbname, dbmapfile,  config_settings, params, s.algorithm)
          #add command
       
          commands.append( [message  + dbname + " ....",\
              parse_blast_cmd, 'PARSE_BLAST_'+ dbname, get_parameter(params,'metapaths_steps','PARSE_BLAST'), enable_flag])
          message = "\n                                                  "
    #################################


    
    # BLAST AGAINST rRNA REFERENCE DATABAs.- are all under REFDBS/taxonomic
    input_fasta = s.preprocessed_dir +  PATHDELIM + s.sample_name + ".fasta" 
    db_type = 'taxonomic'
    refdbstring = get_parameter(params, 'rRNA', 'refdbs', default=None)
    refdbnames= [ x.strip() for x in refdbstring.split(',') if len(x.strip()) ]


    message = "\n" + '*** ' + s.sample_name + ' ***\n' +"\n8. Scan for rRNA sequences in reference database - "
    for refdbname in refdbnames:

       rRNA_blastout= s.blast_results_dir + PATHDELIM + s.sample_name + ".rRNA." + get_refdb_name(refdbname) + ".BLASTout"

       command_Status=  get_parameter( params,'metapaths_steps','SCAN_rRNA')

       enable_flag=shouldRunStep(run_type, rRNA_blastout)  


    #   commands.append( [message + refdbname + "...." , scan_rRNA_seqs_cmd, 'SCAN_rRNA_' + refdbname, command_Status, enable_flag])
       message = "\n                                                   "
    #################################

    
    # COMPUTE rRNA STATISTICS 
    bscore_cutoff = get_parameter(params,'rRNA', 'min_bitscore', default=27)
    eval_cutoff = get_parameter(params, 'rRNA', 'max_evalue', default=6)
    identity_cutoff = get_parameter(params, 'rRNA', 'min_identity', default=40)

    message = "\n" + '*** ' + s.sample_name + ' ***\n' +"\n9. Scanning for rRNA genes .... "

    for refdbname in refdbnames:
        rRNA_stat_results= s.output_results_rRNA_dir + s.sample_name + "." + get_refdb_name(refdbname) + ".rRNA.stats.txt"
        rRNA_blastout= s.blast_results_dir + PATHDELIM + s.sample_name + ".rRNA." + get_refdb_name(refdbname) + ".BLASTout"
        removeFileOnRedo(command_Status, rRNA_blastout)

        scan_rRNA_seqs_cmd = create_scan_rRNA_seqs_cmd(input_fasta, rRNA_blastout, refdbname, config_settings, params, command_Status, db_type, globallogger = globallogger)
        rRNA_stats_cmd = create_rRNA_scan_statistics(rRNA_blastout, refdbname, bscore_cutoff, eval_cutoff, identity_cutoff, config_settings, rRNA_stat_results)

        command_Status=  get_parameter( params,'metapaths_steps','SCAN_rRNA')
        removeFileOnRedo(command_Status, rRNA_stat_results)
        enable_flag=shouldRunStep(run_type, rRNA_stat_results)  


        #add command
        commands.append( [message + get_refdb_name(refdbname), (rRNA_stats_cmd, scan_rRNA_seqs_cmd),  'STATS_' + refdbname, command_Status, enable_flag])
        message = "\n                             "
    #################################
    
    #SCAN FOR tRNA genes
    tRNA_stats_output = s.output_results_tRNA_dir + PATHDELIM + s.sample_name +  ".tRNA.stats.txt"
    tRNA_fasta_output = s.output_results_tRNA_dir + PATHDELIM + s.sample_name +  ".tRNA.fasta"
    input_fasta = s.preprocessed_dir + PATHDELIM + s.sample_name + ".fasta" 

    scan_tRNA_seqs_cmd = create_tRNA_scan_statistics(input_fasta, tRNA_stats_output, tRNA_fasta_output,  config_settings)

    command_Status=  get_parameter( params,'metapaths_steps','SCAN_tRNA')
    removeFileOnRedo(command_Status, tRNA_stats_output)
    removeFileOnRedo(command_Status, tRNA_fasta_output)
    enable_flag=shouldRunStep1(run_type, s.output_results_tRNA_dir, [s.sample_name + ".tRNA.stats.txt", s.sample_name + ".tRNA.fasta"] )

    #add command
    commands.append( ["\n" + '*** ' + s.sample_name + ' ***\n' +"\n10. Scanning for tRNA using tRNAscan 1.4 ... ", scan_tRNA_seqs_cmd, 'SCAN_tRNA', command_Status, enable_flag])
    #################################

    # ANNOTATION STEP 
    input_unannotated_gff = s.orf_prediction_dir +PATHDELIM + s.sample_name+".unannot.gff"
    output_annotated_gff  = s.genbank_dir +PATHDELIM + s.sample_name+".annot.gff"
    output_comparative_annotation  =  s.output_results_annotation_table_dir + PATHDELIM + s.sample_name
    mapping_txt =  s.preprocessed_dir + PATHDELIM + s.sample_name + ".mapping.txt" 

    if params['INPUT']['format'] in ['fasta', 'gbk-unannotated', 'gff-unannotated' ]:
        parse_blast= [] 
        options =''
        for db in dbs:
            parse_blast.append( get_refdb_name(db) );
         
    
        rRNArefdbstring = get_parameter(params, 'rRNA', 'refdbs', default=None)
        rRNArefdbs=[ x.strip() for x in rRNArefdbstring.split(',') ]

        for rRNArefdb in rRNArefdbs:
            rRNA_stat_results= s.output_results_rRNA_dir + s.sample_name + '.' + get_refdb_name(rRNArefdb) + '.rRNA.stats.txt' 
            isrRNA_stat_available=  hasResults(rRNA_stat_results)  
            if  isrRNA_stat_available:
                options += " --rRNA_16S " +  rRNA_stat_results 
    
        tRNA_stat_results= s.output_results_tRNA_dir + PATHDELIM + s.sample_name + '.tRNA.stats.txt' 
        istRNA_stat_available=  hasResults(tRNA_stat_results)  
        if  istRNA_stat_available:
           options += " --tRNA " +  tRNA_stat_results 
    
        # create the command
        annotate_gbk_cmd = create_annotate_genebank_cmd(s.sample_name, mapping_txt,  input_unannotated_gff,\
                             output_annotated_gff,  s.blast_results_dir, options,\
                              parse_blast,  output_comparative_annotation,\
                              config_settings, s.algorithm)
    
        command_Status=  get_parameter( params,'metapaths_steps','ANNOTATE')
        removeFileOnRedo(command_Status, output_annotated_gff)
        enable_flag=shouldRunStep(run_type, output_annotated_gff)  

    
        commands.append( ["\n" + '*** ' + s.sample_name + ' ***\n' +"\n11. Annotate gff files    ....", annotate_gbk_cmd,'ANNOTATE',command_Status, enable_flag])
    #################################
 
    
    # CREATE A GENBANK FILE, PTOOLS INPUT and SEQUIN FILE
    input_annot_gff =  output_annotated_gff
    input_nucleotide_fasta = s.preprocessed_dir + PATHDELIM + s.sample_name + ".fasta" 
    input_amino_acid_fasta = output_filtered_faa

    output_annot_gbk= s.genbank_dir + PATHDELIM + s.sample_name +  '.gbk'
    gbk_command_Status=  get_parameter(params,'metapaths_steps','GENBANK_FILE')
    removeFileOnRedo(gbk_command_Status, output_annot_gbk)
    enable_gbk_flag=shouldRunStep(run_type, output_annot_gbk)  

    outputs = {}
    if enable_gbk_flag:
       outputs['gbk'] = output_annot_gbk

    output_annot_sequin= s.output_results_sequin_dir + PATHDELIM + s.sample_name +  '.tbl'
    sequin_command_Status=  get_parameter(params,'metapaths_steps','CREATE_SEQUIN_FILE')
    removeFileOnRedo(sequin_command_Status, output_annot_sequin)
    #set this back when sequin id added enable_sequin_flag=shouldRunStep(run_type, output_annot_sequin)  
    enable_sequin_flag=False
    if enable_sequin_flag:
       outputs['sequin'] = output_annot_sequin


    files = [ '0.pf', '0.fasta', 'genetic-elements.dat', 'organism-params.dat']
    ptinput_command_Status=  get_parameter( params,'metapaths_steps','PATHOLOGIC_INPUT')
    removeDirOnRedo(ptinput_command_Status, s.output_fasta_pf_dir)
    enable_ptinput_flag=shouldRunStep1(run_type, s.output_fasta_pf_dir, files)

    # Niels - Issue #12 removed some strange output appearing to standard out
    
    if enable_ptinput_flag:
        outputs['ptinput'] = s.output_fasta_pf_dir

    
    if enable_ptinput_flag or enable_gbk_flag or enable_sequin_flag:
       enable_flag = True
    else:
       enable_flag = False


    if ptinput_command_Status in ['redo', 'yes' ] or gbk_command_Status in ['redo', 'yes'] or sequin_command_Status in ['redo', 'yes']:
       if 'redo' in [ptinput_command_Status, gbk_command_Status,  sequin_command_Status]:
          command_Status = 'redo'
       else:
          command_Status = 'yes'
    else: 
       command_Status = 'skip'
    

    genbank_annotation_table_cmd = create_genbank_ptinput_sequin_cmd(input_annot_gff, input_nucleotide_fasta, input_amino_acid_fasta, outputs, config_settings, ncbi_sequin_params, ncbi_sequin_sbt)
    #add command
    message = "\n" + '*** ' + s.sample_name + ' ***\n' +"\n12. Create reports/genbank/tools command ...."
    commands.append( [message, genbank_annotation_table_cmd,'GENBANK_FILE', command_Status, enable_flag])
    #################################
 
    
    # CREATE A REPORT TABLES WITH FUNCTION AND TAXONOMY
    input_annotated_gff = output_annotated_gff
    output_annot_table = s.output_results_annotation_table_dir +  PATHDELIM + 'functional_and_taxonomic_table.txt'
    if params['INPUT']['format'] in ['fasta', 'gbk-unannotated', 'gff-unannotated' ]:
       command_Status=  get_parameter(params,'metapaths_steps','CREATE_REPORT_FILES')
       removeFileOnRedo(command_Status, output_annot_table)
       enable_flag=shouldRunStep(run_type, output_annot_table)  

       message = "\n" + '*** ' + s.sample_name + ' ***\n' +"\n13. Creating KEGG and COG hits table and LCA based taxonomy table...."
       input_dir = s.blast_results_dir + PATHDELIM # D+ s.sample_name + "." + dbname + ".blastout.pars[s.d"
       create_report_cmd = create_report_files_cmd(dbs, input_dir, input_annotated_gff, s.sample_name, 
                                                   s.output_results_annotation_table_dir, config_settings, 
                                                   s.algorithm, command_line_params['verbose'] )
       commands.append([message, create_report_cmd, 'CREATE_REPORT_FILES', command_Status, enable_flag])

    #################################

    # IS REFSEQ BLAST OUTPUT PRESENT?
    # Niels - Issue #12: change this to detect if RefSeq is.heduled or not rather than just 
    # having the results here.
    # refseqblastoutput = s.blast_results_dir + PATHDELIM + s.sample_name + "." + 'refseq' + ".blastout"
    blast_dbs = (get_parameter( params,'annotation','dbs'))
    
    # if not  (path.exis.refseqblastoutput) :
    if not (re.search(".*refseq.*",blast_dbs, re.IGNORECASE)):
        eprintf("\nWARNING: Refseq annotation is not scheduled!\n")
        eprintf("         Taxonomic information will not be found in the annotation table.\n")


    #MLTreeMap Calculations 
    mltreemap_input_file = s.preprocessed_dir +  PATHDELIM + s.sample_name + ".fasta" 

    command_Status=  get_parameter( params,'metapaths_steps','MLTREEMAP_CALCULATION')

    removeDirOnRedo(command_Status, s.output_mltreemap_calculations_dir+ PATHDELIM + 'various_outputs')
    removeDirOnRedo(command_Status, s.output_mltreemap_calculations_dir+ PATHDELIM + 'final_outputs')
    removeDirOnRedo(command_Status, s.output_mltreemap_calculations_dir+ PATHDELIM + 'final_RAxML_outputs')
    cleanDirOnRedo(command_Status, s.output_mltreemap_calculations_dir)
    enable_flag=shouldRunStepOnDirectory(run_type, s.output_mltreemap_calculations_dir)

    mltreemap_calculation_cmd = create_MLTreeMap_Calculations(mltreemap_input_file, s.output_mltreemap_calculations_dir, config_settings)
    message = "\n" + '*** ' + s.sample_name + ' ***\n' +"\n16. MLTreeMap Calculations  ...."
    commands.append( [message, mltreemap_calculation_cmd, 'MLTREEMAP_CALCULATION', command_Status, enable_flag])


    #MLTreeMap Image Creating 
    mltreemap_final_outputs = s.output_mltreemap_calculations_dir + PATHDELIM + "final_outputs" + PATHDELIM 

    mltreemap_imagemaker_cmd = create_MLTreeMap_Imagemaker(s.mltreemap_image_output, mltreemap_final_outputs, config_settings)
    command_Status=  get_parameter( params,'metapaths_steps','MLTREEMAP_IMAGEMAKER')
    removeDirOnRedo(command_Status, s.mltreemap_image_output)
    enable_flag=shouldRunStep(run_type, s.mltreemap_image_output)

   # mltreemap_gather_hits_cmd=create_MLTreeMap_Hits.output_mltreemap_calculations_dir+ PATHDELIM + 'various_outputs', s.mltreemap_image_output, config_settings)

    #add command
    message = "\n" + '*** ' + s.sample_name + ' ***\n' +"\n17. Making MLTreeMap Images  ...."
    commands.append( [message, "", 'MLTREEMAP_IMAGEMAKER', command_Status, enable_flag])
   # commands.append( ["\n17a. Gather MLTreeMap Hits  ....", mltreemap_gather_hits_cmd, 'MLTREEMAP_CALCULATION', command_Status, enable_flag])
    #################################


    # GENERATE PGDB using pathologic
    # note "redo" is a forceful way of recomputing the pgdb 
    command_Status=  get_parameter( params,'metapaths_steps','PATHOLOGIC')

    enable_flag = False
    if (run_type in ['overwrite', 'overlay'])  and  (command_Status in ['redo', 'yes']):
       enable_flag = True
       #remove the pathologic dir for the pgdb with the same sample name since a new pgdb is requested
       remove_existing_pgdb( s.sample_name, config_settings['PATHOLOGIC_EXECUTABLE'])


    taxonomic_pruning_flag = get_parameter(params,'ptools.ttings', 'taxonomic_pruning')
    create_pgdb_cmd = create_pgdb_using_pathway_tools_cmd(s.output_fasta_pf_dir, taxonomic_pruning_flag, config_settings)

    message = "\n" + '*** ' + s.sample_name + ' ***\n' +"\n18. Create PGDB  ...."
    commands.append( ["\n" + '*** ' + s.sample_name + ' ***\n' +"\n18. Create PGDB  ....", create_pgdb_cmd, 'PATHOLOGIC', command_Status, enable_flag])
    #################################

    create_pgdb_table_cmd = create_pgdb_using_pathway_tools_cmd(s.output_fasta_pf_dir, taxonomic_pruning_flag, config_settings)
    #commands.append( ["\n18. Create PGDB (creating pathways table)  ....", create_pgdb_table_cmd, 'PATHOLOGIC', command_Status, enable_flag])

#    print """  """
#    print """  ********************************************************** """
#    print """  **************** Running  MetaPathways ******************* """
#    print """  ********************************************************** """
#    print """              """  +  input_fp + """                       """
#    print """  ********************************************************** """

    command_handler(commands, status_update_callback, s.runlogger, s.stepslogger, s.errorlogger, s.runstatslogger,  command_line_params)






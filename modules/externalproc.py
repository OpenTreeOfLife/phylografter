#!/usr/env python
import logging
import os
import sys
import subprocess
_EXTERNAL_PROC_PARENT = None
_CONF_OBJ_DICT = {}

def get_conf(request):
    global _CONF_OBJ_DICT
    app_name = request.application
    c = _CONF_OBJ_DICT.get(app_name)
    if c is None:
        from ConfigParser import SafeConfigParser
        c = SafeConfigParser({})
        lcp = "applications/%s/private/localconfig" % app_name
        if os.path.isfile(lcp):
            c.read(lcp)
        else:
            c.read("applications/%s/private/config" % app_name)
        _CONF_OBJ_DICT[app_name] = c
    return c

def get_logging_level(request):
    '''
    Converts a config files logging section, level attribute to a logging modules' 
    value (default is logging.INFO)
    '''
    conf = get_conf(request)
    try:
        level_str = conf.get("logging", "level").upper()
        if level_str == "NOTSET":
            return logging.NOTSET
        elif level_str == "DEBUG":
            return logging.DEBUG
        elif level_str == "INFO":
            return logging.INFO
        elif level_str == "WARNING":
            return logging.WARNING
        elif level_str == "ERROR":
            return logging.ERROR
        elif level_str == "CRITICAL":
            return logging.CRITICAL
        else:
            return logging.NOTSET
    except:
        return logging.INFO
    
def get_logger(request, name):
    '''
    Returns a logger object with the level set based on the config file
    '''
    logger = logging.getLogger(name)
    if not hasattr(logger, 'is_configured'):
        logger.is_configured = False
    if not logger.is_configured:
        level = get_logging_level(request)
        logging_formatter = logging.Formatter("%(levelname) 8s: %(message)s")
        logging_formatter.datefmt='%H:%M:%S'
        logger.setLevel(level)
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(logging_formatter)
        logger.addHandler(ch)
        logger.is_configured = True
    return logger



def get_external_proc_parent(request):
    '''
    Returns the absolute path to the directory that will be the parent of all 
    of the directories used to hold files from external processes.
    
    This will be read from the config file (dir setting in external) or default
        to a tempdir.mkdtemp directory.
    '''
    global _EXTERNAL_PROC_PARENT
    if _EXTERNAL_PROC_PARENT is None:
        conf = get_conf(request)
        try:
            _EXTERNAL_PROC_PARENT = conf.get('external', 'dir')
            _EXTERNAL_PROC_PARENT = os.path.abspath(_EXTERNAL_PROC_PARENT)
            _LOG = get_logger(request, 'externalproc')
            if not os.path.exists(_EXTERNAL_PROC_PARENT):
                try:
                    os.makedirs(_EXTERNAL_PROC_PARENT)
                    _LOG.info('Created dir "%s"' % _EXTERNAL_PROC_PARENT)
                except:
                    _LOG.warn('Could not make the configuration-file-specified external dir "%s"\n' % _EXTERNAL_PROC_PARENT)
                    raise
        except:
            import tempfile
            _EXTERNAL_PROC_PARENT = tempfile.mkdtemp()
            _EXTERNAL_PROC_PARENT = os.path.abspath(_EXTERNAL_PROC_PARENT)
            _LOG = get_logger(request, 'externalproc')
            _LOG.warn('The configuration file does not contain a "dir" setting in a "external" section...\n    Using a tempdir "%s"\n' % _EXTERNAL_PROC_PARENT)
    return _EXTERNAL_PROC_PARENT
            


def get_external_proc_dir_for_upload(request, db, upload_file):
    '''
    Returns the absolute path to a directory that is can serve as the parent
    directory for external processes that pertain to particular uploaded_file.
    
    The goal is to return a filepath that will always correspond to the same 
        uploaded file. This will facilitate:
            1. asynchronous queries without triggering repeated spawning of the
                same process (the subsequent calls will be able to detect that 
                the directory has already been created), and
            2. caching of the results of external process. Their output files 
                will be present so repeated calls can just read the output again.
    
    This assumes that the study_file.file will be unique and will match upload_file
    
    Returns `None` if there is no match for upload_file
    
    Raises a ValueError if there are multiple matches (this should not occur).
    
    The file-specific portion of the path will be composed of:
        studyid_fileid_uploadedtimestamp
    The parent of that directory will be read from the config file (or default to
        /tmp)
    
    '''
    # @Schema-dependent code: assumes study_file.file will match upload_file and that the match will have id (int), study (int), and uploaded (datetime)
    match_list =  db(db.study_file.file == upload_file).select()
    if len(match_list) == 0:
        return None
    if len(match_list) > 1:
        raise ValueError('More than one match was found for the study_file.file field!')
    match = match_list[0]
    s, i, d = str(match.study), str(match.id), match.uploaded
    pref_subdir = s[-2:].rjust(2, '0')
    field_sep = '.'
    ds = '-'.join(d.isoformat(field_sep).split(':'))
    upload_subdir = field_sep.join([s, i, ds])
    par = get_external_proc_parent(request)
    fp = os.path.join(par, pref_subdir, upload_subdir)
    if not os.path.exists(fp):
        os.makedirs(fp)
        _LOG = get_logger(request, 'externalproc')
        _LOG.info('Created dir "%s"' % fp)        
    return fp


class ExternalProcStatus:
    NOT_FOUND, RUNNING, FAILED, COMPLETED = range(4)

#@TEMPORARY These must be kept synced with constants in modules/joblauncher.py
_METADATA_DIR = ".process_metadata"
_RETURNCODE_FILE = "returncode"

def invoc_status(request,
                 par_dir):
    '''
    Returns a ExternalProcStatus based on the .process_metadata dir created 
    by the joblauncher.py
    '''
    proc_dir = os.path.join(par_dir, _METADATA_DIR)
    if not os.path.exists(proc_dir):
        return ExternalProcStatus.NOT_FOUND
    rc_file = os.path.join(proc_dir, _RETURNCODE_FILE)
    if not os.path.exists(rc_file):
        return ExternalProcStatus.RUNNING
    rc = open(rc_file, 'rU').read().strip()
    if rc == '0':
        return ExternalProcStatus.COMPLETED
    return ExternalProcStatus.FAILED
    

def write_input_files(request,
                      par_dir,
                      inp_file_path_list):
    '''
    Iterates through inp_file_path_list. 
    Expects (filename, content) tuples.
    For each tuple the file of the appropriate name will be created in par_dir
    and filled with content (first trying the read() method and falling back 
    to writing content as a string.
    '''
    for fn, content in inp_file_path_list:
        full_path = os.path.join(par_dir, fn)
        if not os.path.exists(full_path):
            fo = open(full_path, 'w')
            try:
                try:
                    fo.write(content.read())
                except:
                    fo.write(content)
            finally:
                fo.close()
        
            
def do_ext_proc_launch(request,
                       par_dir,
                       invocation,
                       stdout_path,
                       stderr_path,
                       inp_file_path_list,
                       wait):
    '''
    Uses modules/joblauncher.py to launch an external process.
    
    Launches the command contained in the list `invocation` from the par_dir
    directory
    `inp_file_path_list` should be a list of tuples of (filename, content)
        which need to be written to the par_dir before the invocation.
    '''
    write_input_files(request, par_dir, inp_file_path_list)
    app_name = request.application
    job_launcher = os.path.abspath("applications/%s/modules/joblauncher.py" % app_name)
    if not os.path.exists(job_launcher):
        raise RuntimeError('Could not find joblauncher script')
    stdin_path = ''
    wrapped_invoc = [sys.executable,
                     job_launcher,
                     par_dir,
                     stdin_path,
                     stdout_path,
                     stderr_path] + invocation
    p = subprocess.Popen(wrapped_invoc)
    _LOG = get_logger(request, 'externalproc')
    if wait:
        p.wait()
    

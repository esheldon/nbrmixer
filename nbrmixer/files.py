from __future__ import print_function
import os, sys

BASE_DIR_KEY='NBRMIXER_OUTPUT_DIR'
#FILE_FRONT='nbrmixer'
INDEX_FMT='%06d'

def get_basedir():
    """
    The base directory

    Runs are held under bad/run
    """
    if BASE_DIR_KEY not in os.environ:
        raise ValueError("$%s environment variable is not set" % BASE_DIR_KEY)

    return os.environ[BASE_DIR_KEY]

def get_generic_basename(run, index=None, type=None, ext='fits'):
    """
    basic file names are
        {front}-{run}.{ext}
        or
        {front}-{run}-{index}.{ext}
        or
        {front}-{run}-{index}-{type}.{ext}
    """
    #fname = [FILE_FRONT,run]
    fname = [run]
    
    if index is not None:
        fname += [INDEX_FMT % index]

    if type is not None:
        fname += [type]

    fname = '-'.join(fname)

    if ext is not None:
        fname += '.' + ext

    return fname

#
# directories
#

def get_run_dir(run):
    """
    The run directory
    """
    bdir=get_basedir()
    return os.path.join(bdir, run)

def get_script_dir(run, index):
    """
    dir holding the processing script
    """
    return get_output_dir(run, index)

def get_output_dir(run, index):
    """
    Directory holding the output file
    """
    bdir=get_basedir()

    idir = INDEX_FMT % index
    return os.path.join(bdir, run, 'output', idir)

def get_collated_dir(run):
    """
    The script directory BASE_DIR/{run}/collated
    """
    bdir=get_basedir()
    return os.path.join(bdir, run, 'collated')

#
# files
#

def get_script_file(run, index):
    """
    get the script file path
    """

    dir=get_script_dir(run, index)
    basename = get_generic_basename(run, index=index, ext='sh')
    return os.path.join(dir, basename)

def get_output_file(run, index):
    """
    get the output file path
    """

    dir=get_output_dir(run, index)
    basename = get_generic_basename(run, index=index, ext='fits')
    return os.path.join(dir, basename)

def get_log_file(run, index):
    """
    location of the log file
    """

    dir=get_output_dir(run, index)
    basename = get_generic_basename(run, index=index, ext='log')

    return os.path.join(dir, basename)


def get_collated_file(run):
    """
    get the output file path
    """

    dir=get_collated_dir(run)
    basename = get_generic_basename(run, ext='fits')
    return os.path.join(dir, basename)

def get_fof_file(run, index):
    """
    get the fof output file path
    """

    dir=get_output_dir(run, index)
    basename = get_generic_basename(run, index=index, type='fof', ext='fits')
    return os.path.join(dir, basename)

def get_nbrs_file(run, index):
    """
    get the nbrs output file path
    """

    dir=get_output_dir(run, index)
    basename = get_generic_basename(run, index=index, type='nbrs', ext='fits')
    return os.path.join(dir, basename)

def get_nbrs_script_file(run, index):
    """
    get the script file path
    """

    dir=get_script_dir(run, index)
    basename = get_generic_basename(run, index=index, type='nbrs', ext='sh')
    return os.path.join(dir, basename)


def get_nbrs_log_file(run, index):
    """
    location of the log file
    """

    dir=get_output_dir(run, index)
    basename = get_generic_basename(run, index=index, type='nbrs', ext='log')

    return os.path.join(dir, basename)

def get_summer_script_file(run, select, index):
    """
    get the script file path
    """

    dir=get_script_dir(run, index)
    type = 'sum-%s' % select
    basename = get_generic_basename(run, index=index, type=type, ext='sh')
    return os.path.join(dir, basename)

def get_summer_log_file(run, select, index):
    """
    location of the log file
    """

    dir=get_output_dir(run, index)
    type = 'sum-%s' % select
    basename = get_generic_basename(run, index=index, type=type, ext='log')

    return os.path.join(dir, basename)


#
# submission scripts

def get_wq_dir(run):
    """
    We don't want wq stuff on gpfs
    """
    bdir = os.environ['TMPDIR']
    return os.path.join(bdir, 'nbrmixer', run, 'scripts')

def get_lsf_dir(run):
    """
    We don't want wq stuff on gpfs
    """
    return get_wq_dir(run)

def get_lsf_file(run, index):
    """
    get the yaml file path
    """
    dir=get_lsf_dir(run)
    basename = get_generic_basename(run, index=index, ext='lsf')
    return os.path.join(dir, basename)

def get_nbrs_lsf_file(run, index):
    """
    get the yaml file path
    """
    dir=get_lsf_dir(run)
    basename = get_generic_basename(run, index=index, type='nbrs', ext='lsf')
    return os.path.join(dir, basename)

def get_summer_lsf_file(run, select, index):
    """
    get the yaml file path
    """
    dir=get_lsf_dir(run)
    type = 'sum-%s' % select
    basename = get_generic_basename(run, index=index, type=type, ext='lsf')
    return os.path.join(dir, basename)



#
# config
#

def get_config_dir():
    """
    directory holding installed config files
    """
    d=sys.exec_prefix
    return os.path.join(d,'share','nbrmixer-config')

def get_config_file(identifier):
    """
    installed config file location
    """
    d=get_config_dir()
    name='%s.yaml' % identifier
    return os.path.join(d, name)

def read_config(identifier):
    """
    read an installed config file
    """
    import yaml
    f=get_config_file(identifier)

    with open(f) as fobj:
        c=yaml.load(fobj)

    if 'sim' in c:
        # this is a run configuration
        c['run'] = identifier

    return c


#
# sums and fitting
#

def get_means_dir(run):
    dir=get_run_dir(run)
    return os.path.join(dir, 'fit-m-c')

def get_plot_dir(run):
    dir=get_run_dir(run)
    return os.path.join(dir, 'plots')


def get_means_file(run, extra=None):
    dir=get_means_dir(run)

    type = ['means']
    if extra is not None:
        type += [extra]

    type='-'.join(type)
    basename = get_generic_basename(run, type=type, ext='fits')
    return os.path.join(dir, basename)

def get_sums_file(run, index=None, extra=None):
    dir=get_means_dir(run)

    type = ['sums']
    if extra is not None:
        type += [extra]

    if index is not None:
        type += ['%06d' % index]

    type='-'.join(type)
    basename = get_generic_basename(run, type=type, ext='fits')
    return os.path.join(dir, basename)

def get_plot_file(run, extra=None):
    dir=get_means_dir(run)

    basename = get_generic_basename(run, type=extra, ext='eps')
    return os.path.join(dir, basename)


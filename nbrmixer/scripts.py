from __future__ import print_function
try:
    xrange
except:
    xrange=range
import os

import fitsio
import nbrsim
from . import files

class ScriptWriter(dict):
    """
    class to write scripts and queue submission scripts

    parameters
    ----------
    run: string
        run identifier
    system: string
        Queue system.  Currently supports wq.
    extra_commands: string
        Extra shell commands to run, e.g. for setting up
        your environment
    """

    def __init__(self, run, system, missing=False, extra_commands=''):
        self['run'] = run
        self['extra_commands'] = extra_commands
        self['system'] = system
        
        self.missing=missing

        self._load_configs()

        self['njobs']=self.nbrsim_conf['output']['nfiles']

        self._makedirs()

    def write_scripts(self):
        """
        write the basic bash scripts and queue submission scripts
        """
        for i in xrange(self['njobs']):
            if self['system']=='wq':
                self._write_wq(i)
            else:
                raise RuntimeError("bad system: '%s'" % self['system'])

            self._write_script(i)

    def _write_script(self, index):
        """
        write the basic bash script
        """

        self['meds_file'] = nbrsim.files.get_meds_file(
            self.conf['nbrsim_run'],
            index,
        )
        self['start']=0
        self['end']=1000000000

        self['output_file'] = files.get_output_file(self['run'], index)
        
        
        text=_script_template % self

        script_fname=files.get_script_file(self['run'], index)
        print("writing:",script_fname)
        with open(script_fname, 'w') as fobj:
            fobj.write(text)


    def _write_wq(self, index):
        """
        write the wq submission script
        """

        wq_dir = files.get_wq_dir(self['run'])
        if not os.path.exists(wq_dir):
            os.makedirs(wq_dir)

        wq_fname=files.get_wq_file(self['run'], index)

        if self.missing:
            wq_fname = wq_fname.replace('.yaml','-missing.yaml')

            output_file = files.get_output_file(self['run'], index)
            if os.path.exists(output_file):
                if os.path.exists(wq_fname):
                    os.remove(wq_fname)
                return

        job_name = os.path.basename(wq_fname)
        job_name = job_name.replace('.yaml','')

        self['job_name'] = job_name
        self['logfile']  = files.get_log_file(self['run'], index)
        self['script']   = files.get_script_file(self['run'], index)

        text = _wq_template  % self

        print("writing:",wq_fname)
        with open(wq_fname,'w') as fobj:
            fobj.write(text)


    def _makedirs(self):
        """
        make all the directories needed
        """

        dirs=[]

        for i in xrange(self['njobs']):
            output_dir = files.get_output_dir(self['run'],i)
            script_dir = files.get_script_dir(self['run'],i)

            dirs += [output_dir]

            if script_dir != output_dir:
                dirs += [script_dir]

        for d in dirs:
            if not os.path.exists(d):
                try:
                    print("making dir:",d)
                    os.makedirs(d)
                except:
                    pass

    def _load_configs(self):
        """
        load the galsim config and do some checks
        """
        self['config_file']=files.get_config_file(self['run'])

        self.conf = files.read_config(self['run'])

        self.nbrsim_conf = nbrsim.files.read_config(self.conf['nbrsim_run'])

#
# MEDS making
#

_script_template = r"""#!/bin/bash
# set up environment before running this script

config_file="%(config_file)s"
meds_file="%(meds_file)s"
output_file="%(output_file)s"

start=%(start)d
end=%(end)d

python -u $(which ngmixit)    \
    --work-dir=$TMPDIR        \
    --fof-range=$start,$end   \
    $config_file              \
    $output_file              \
    $meds_file
"""

_wq_template = """#!/bin/bash
command: |
    %(extra_commands)s

    logfile="%(logfile)s"
    tmp_logfile="$(basename $logfile)"
    tmp_logfile="$TMPDIR/$tmp_logfile"
    bash %(script)s &> "$tmp_logfile"

    mv -vf "$tmp_logfile" "$logfile"

job_name: "%(job_name)s"
"""



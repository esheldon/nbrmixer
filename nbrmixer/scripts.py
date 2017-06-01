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
            if self['system'] == 'wq':
                self._write_wq(i)

            elif self['system'] == 'lsf':
                self._write_lsf(i)

            else:
                raise RuntimeError("bad system: '%s'" % self['system'])

            self._write_script(i)

    def _write_script(self, index):
        if self.conf['model_nbrs']:
            self._write_nbrs_script(index)
        self._write_main_script(index)

    def _write_nbrs_script(self, index):
        """
        write the nbrs bash script
        """

        self['meds_file'] = nbrsim.files.get_meds_file(
            self.conf['nbrsim_run'],
            index,
        )

        self['fof_file'] = files.get_fof_file(self['run'], index)
        self['nbrs_file'] = files.get_nbrs_file(self['run'], index)
        
        
        text=_nbrs_script_template % self

        script_fname=files.get_nbrs_script_file(self['run'], index)
        #print("writing:",script_fname)
        with open(script_fname, 'w') as fobj:
            fobj.write(text)


    def _write_main_script(self, index):
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
        
        if self.conf['model_nbrs']:
            self['fof_file'] = files.get_fof_file(self['run'], index)
            self['nbrs_file'] = files.get_nbrs_file(self['run'], index)
            text=_mof_script_template % self
        elif 'correct_meds' in self.conf:
            self['mof_file'] = files.get_output_file(
                self.conf['correct_meds']['mof_run'],
                index,
            )
            text=_mofsub_script_template % self
        else:
            text=_script_template % self

        script_fname=files.get_script_file(self['run'], index)
        #print("writing:",script_fname)
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

    def _write_lsf(self, index):
        if self.conf['model_nbrs']:
            self._write_nbrs_lsf(index)

        self._write_main_lsf(index)

    def _write_nbrs_lsf(self, index):
        """
        write the nbrs lsf submission script
        """

        lsf_dir = files.get_lsf_dir(self['run'])
        if not os.path.exists(lsf_dir):
            os.makedirs(lsf_dir)

        lsf_fname=files.get_nbrs_lsf_file(self['run'], index)

        if self.missing:
            lsf_fname = lsf_fname.replace('.lsf','-missing.lsf')

            nbrs_file = files.get_nbrs_file(self['run'], index)
            fof_file = files.get_fof_file(self['run'], index)
            if os.path.exists(nbrs_file) and os.path.exists(fof_file):
                if os.path.exists(lsf_fname):
                    os.remove(lsf_fname)
                return

        job_name = os.path.basename(lsf_fname)
        job_name = job_name.replace('.lsf','')

        self['job_name'] = job_name
        self['logfile']  = files.get_nbrs_log_file(self['run'], index)
        self['script']   = files.get_nbrs_script_file(self['run'], index)

        text = _lsf_template  % self

        print("writing:",lsf_fname)
        with open(lsf_fname,'w') as fobj:
            fobj.write(text)

    def _write_main_lsf(self, index):
        """
        write the lsf submission script
        """

        lsf_dir = files.get_lsf_dir(self['run'])
        if not os.path.exists(lsf_dir):
            os.makedirs(lsf_dir)

        lsf_fname=files.get_lsf_file(self['run'], index)

        if self.missing:
            lsf_fname = lsf_fname.replace('.lsf','-missing.lsf')

            output_file = files.get_output_file(self['run'], index)
            if os.path.exists(output_file):
                if os.path.exists(lsf_fname):
                    os.remove(lsf_fname)
                return

        job_name = os.path.basename(lsf_fname)
        job_name = job_name.replace('.lsf','')

        self['job_name'] = job_name
        self['logfile']  = files.get_log_file(self['run'], index)
        self['script']   = files.get_script_file(self['run'], index)

        text = _lsf_template  % self

        print("writing:",lsf_fname)
        with open(lsf_fname,'w') as fobj:
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
        self.conf['model_nbrs'] = self.conf.get('model_nbrs',False)

        self.nbrsim_conf = nbrsim.files.read_config(self.conf['nbrsim_run'])

class SummerScriptWriter(ScriptWriter):
    def __init__(self, run, system, select_conf, nchunks,
                 missing=False, extra_commands=''):

        super(SummerScriptWriter,self).__init__(
            run,
            system,
            missing=missing,
            extra_commands=extra_commands,
        )

        self['nchunks'] = nchunks
        self.select_conf=select_conf
        if select_conf is not None:
            self['select_string'] = '--select="%s"' % select_conf
        else:
            self['select_string'] = ''

    def write_scripts(self):
        """
        write the basic bash scripts and queue submission scripts
        """

        chunker = Chunker(self['njobs'], self['nchunks'])
        for i,chunkdef in enumerate(Chunker(self['njobs'], self['nchunks'])):
            if self['system'] == 'wq':
                self._write_wq(i)

            elif self['system'] == 'lsf':
                self._write_lsf(i,chunkdef)

            else:
                raise RuntimeError("bad system: '%s'" % self['system'])

            self._write_script(i, chunkdef)

    def _write_script(self, index, chunkdef):

        start,end=chunkdef

        self['start'] = start
        self['end'] = end

        text=_summer_script_template % self

        script_fname=files.get_summer_script_file(
            self['run'],
            self.select_conf,
            index,
        )
        with open(script_fname, 'w') as fobj:
            fobj.write(text)

    def _write_lsf(self, index, chunkdef):
        """
        write the lsf submission script
        """

        start,end=chunkdef

        lsf_dir = files.get_lsf_dir(self['run'])
        if not os.path.exists(lsf_dir):
            os.makedirs(lsf_dir)

        lsf_fname=files.get_summer_lsf_file(
            self['run'],
            self.select_conf,
            index,
        )
        submitted_fname = lsf_fname.replace('.lsf','.lsf.submitted')

        if os.path.exists(lsf_fname):
            os.remove(lsf_fname)
        if os.path.exists(submitted_fname):
            os.remove(submitted_fname)


        if self.missing:
            self['force']=''
            all_ok=True
            lsf_fname = lsf_fname.replace('.lsf','-missing.lsf')
            submitted_fname = lsf_fname.replace('.lsf','.lsf.submitted')


            if os.path.exists(submitted_fname):
                os.remove(submitted_fname)
            if os.path.exists(lsf_fname):
                os.remove(lsf_fname)

            for i in xrange(start,end+1):
                sums_file = files.get_sums_file(
                    self['run'],
                    extra=self.select_conf,
                    index=i,
                )

                if not os.path.exists(sums_file):
                    all_ok=False
        else:
            self['force']='--force'
            all_ok=False



        if all_ok:
            return



        job_name = os.path.basename(lsf_fname)
        job_name = job_name.replace('.lsf','')

        self['job_name'] = job_name
        self['logfile']  = files.get_summer_log_file(
            self['run'],
            self.select_conf,
            index,
        )
        self['script']   = files.get_summer_script_file(
            self['run'],
            self.select_conf,
            index,
        )

        text = _lsf_template  % self

        print("writing:",lsf_fname)
        with open(lsf_fname,'w') as fobj:
            fobj.write(text)

    def _makedirs(self):
        """
        make all the directories needed
        """
        pass


def Chunker(num, nchunks):

    nper = num//nchunks
   
    current = 0
    while current < nchunks:

        start = current*nper
        if current == nchunks-1:
            end = num-1
        else:
            end = (current+1)*nper-1

        yield (start,end)

        current += 1

class ChunkerOld(object):
    def __init__(self, num, nchunks):

        self.nchunks = nchunks
        self.nper = num//nchunks

    def __iter__(self):
        return self

    def next(self): # Python 3: def __next__(self)
        if self.current > self.high:
            raise StopIteration
        else:
            self.current += 1
            return self.current - 1

    def __call__(self, index):
        start = index*self.nper
        if index == self.nchunks-1:
            end = self.num-1
        else:
            end = (index+1)*self.nper

        return (start,end)




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

_summer_script_template = r"""#!/bin/bash
# set up environment before running this script

start=%(start)d
end=%(end)d

for index in $(seq $start $end); do
    nbrmixer-fit-m-c          \
            %(run)s           \
            %(select_string)s \
            --index=$index %(force)s
done
"""



_mofsub_script_template = r"""#!/bin/bash
# set up environment before running this script

config_file="%(config_file)s"
meds_file="%(meds_file)s"
mof_file="%(mof_file)s"
output_file="%(output_file)s"

meds_base=$(basename $meds_file)
meds_local="$TMPDIR/$meds_base"

/bin/cp -fv "$meds_file" "$meds_local"

python -u $(which ngmixit)    \
    --work-dir=$TMPDIR        \
    --mof-file="$mof_file"    \
    $config_file              \
    $output_file              \
    $meds_local

rm -v "$meds_local"


"""


_mof_script_template = r"""#!/bin/bash
# set up environment before running this script

config_file="%(config_file)s"
meds_file="%(meds_file)s"
fof_file="%(fof_file)s"
nbrs_file="%(nbrs_file)s"
output_file="%(output_file)s"

meds_base=$(basename $meds_file)
meds_local="$TMPDIR/$meds_base"

/bin/cp -fv "$meds_file" "$meds_local"

python -u $(which ngmixit)    \
    --work-dir=$TMPDIR        \
    --fof-file="$fof_file"    \
    --nbrs-file="$nbrs_file"  \
    $config_file              \
    $output_file              \
    $meds_local

rm -v "$meds_local"

"""


_nbrs_script_template = r"""#!/bin/bash
# set up environment before running this script

config_file="%(config_file)s"
meds_file="%(meds_file)s"
fof_file="%(fof_file)s"
nbrs_file="%(nbrs_file)s"

ngmixer-meds-make-nbrs-data    \
    --fof-file="$fof_file"     \
    --nbrs-file="$nbrs_file"   \
    "$config_file"             \
    "$meds_file"
"""


_lsf_template = """#!/bin/bash
#BSUB -J %(job_name)s
#BSUB -n 1
#BSUB -oo ./%(job_name)s.oe
#BSUB -W 12:00
#BSUB -R "linux64 && rhel60 && scratch > 2"

echo "working on host: $(hostname)"
uptime

export tmpdir="/scratch/esheldon/${LSB_JOBID}"
export TMPDIR="$tmpdir"

mkdir -p ${tmpdir}
echo "cd $tmpdir"
cd $tmpdir

logfile="%(logfile)s"
tmp_logfile="$(basename $logfile)"
tmp_logfile="$tmpdir/$tmp_logfile"

/usr/bin/time bash %(script)s &> "$tmp_logfile"

mv -vf "$tmp_logfile" "$logfile"

rm -r $tmpdir
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



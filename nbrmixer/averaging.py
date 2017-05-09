from __future__ import print_function
try:
    xrange
except:
    xrange=range

import os
import shutil
import nsim
import nbrsim

from . import files


class NbrmixerSummer(nsim.averaging_new.Summer):
    def _load_config(self):
        args=self.args
        if 'runs' in args.runs:
            # this is a runs config file
            data=files.read_config(args.runs)
            self.runs=data['runs']

        else:
            self.runs=[args.runs]

        conf = files.read_config(self.runs[0])

        conf['simc'] = nbrsim.files.read_config(conf['nbrsim_run'])

        conf['simc']['do_ring'] = False
        
        #shear_conf = conf['simc']['bright_gal']['shear']
        #g1 = shear_conf['g1']
        #g2 = shear_conf['g2']
        #conf['simc']['shear'] = [g1,g2]

        self.update(conf)

        self.step = self['metacal_pars'].get('step',0.01)

    def get_run_output(self, run):
        """
        collated file
        """

        fname = files.get_collated_file(run)
        if self.args.cache:
            origname=fname
            bname = os.path.basename(origname)
            fname=os.path.join('$TMPDIR', bname)
            fname=os.path.expandvars(fname)
            if not os.path.exists(fname):
                print("copying to cache: %s -> %s" % (origname,fname))
                shutil.copy(origname, fname)

        return fname

    def _get_means_file(self):

        extra=self._get_fname_extra()
        fname=files.get_means_file(self.args.runs, extra=extra)
        return fname

    def _get_sums_file(self, run):

        extra=self._get_fname_extra(run=run)
        fname=files.get_sums_file(run, extra=extra)
        return fname


    def _get_fit_plot_file(self):
        extra=self._get_fname_extra(last='fit-m-c')
        fname=files.get_plot_file(self.args.runs[0], extra=extra)
        return fname

    def _get_resid_hist_file(self):
        extra=self._get_fname_extra(last='resid-hist')
        fname=files.get_plot_file(self.args.runs[0], extra=extra)
        return fname




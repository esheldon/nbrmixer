from __future__ import print_function
try:
    xrange
except:
    xrange=range

import os
import shutil
import numpy
import nsim
import nbrsim

from . import files
from . import util


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

        self.update(conf)
        self._set_step()

    def _preselect(self, data):
        """
        sub-classes might make a pre-selection, e.g. of some flags
        """
        
        data = super(NbrmixerSummer,self)._preselect(data)
        w,=numpy.where(data['shear_index'] >= -1) 
        data=data[w]
        data['shear_index'] = 0
        return data



    def get_run_output(self, run):
        """
        collated file
        """

        if self.args.index is None:
            fname = files.get_collated_file(run)
        else:
            fname = files.get_output_file(run, self.args.index)

        if self.args.cache:
            origname=fname
            bname = os.path.basename(origname)
            fname=os.path.join('$TMPDIR', bname)
            fname=os.path.expandvars(fname)
            if not os.path.exists(fname):
                print("copying to cache: %s -> %s" % (origname,fname))
                shutil.copy(origname, fname)

        return fname

    def _add_true_shear(self, data):
        data = util.add_true_shear(
            data,
            self['nbrsim_run'],
            self.args.index,
        )

        return data

    def _get_means_file(self):

        extra=self._get_fname_extra()
        fname=files.get_means_file(self.args.runs, extra=extra)
        return fname

    def _get_sums_file(self, run, use_select_string=False):

        extra=self._get_fname_extra(
            run=run,
            use_select_string=use_select_string,
        )
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


    def _set_select(self):
        self.select=None
        self.do_selection=False

        if self.args.select is not None:
            self.do_selection=True

            d = files.read_config(self.args.select)
            self.select = d['select'].strip()

        elif self.args.weighted:
            self.do_selection=True



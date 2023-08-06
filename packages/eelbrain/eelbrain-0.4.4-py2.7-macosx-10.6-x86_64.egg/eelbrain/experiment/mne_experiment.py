# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
'''
MneExperiment is a base class for managing an mne experiment.


Epochs
------

Epochs are defined as dictionaries containing the following entries
(**mandatory**/optional):

sel_epoch : str
    Name of the epoch providing primary events (e.g. whose trial rejection
    file should be used).
sel : str
    Expression which evaluates in the events Dataset to the index of the
    events included in this Epoch specification.
**tmin** : scalar
    Start of the epoch.
**tmax** : scalar
    End of the epoch.
reject_tmin : scalar
    Alternate start time for rejection (amplitude and eye-tracker).
reject_tmax : scalar
    Alternate end time for rejection (amplitude and eye-tracker).
decim : int
    Decimate the data by this factor (i.e., only keep every ``decim``'th
    sample)
pad : scalar
    Pad epochs with this this amount of data (in seconds) not included in
    rejection.
tag : str
    Optional tag to identify epochs that differ in ways not captured by the
    above.


Epochs can be
specified in the :attr:`MneExperiment.epochs` dictionary. All keys in this
dictionary have to be of type :class:`str`, values have to be :class:`dict`s
containing the epoch specification. If an epoch is specified in
:attr:`MneExperiment.epochs`, its name (key) can be used in the epochs
argument to various methods. Example::

    # in MneExperiment subclass definition
    class experiment(MneExperiment):
        epochs = {'adjbl': dict(sel="stim=='adj'", tstart=-0.1, tstop=0)}
        ...

The :meth:`MneExperiment.get_epoch_str` method produces A label for each
epoch specification, which is used for filenames. Data which is excluded from
artifact rejection is parenthesized. For example, ``"noun[(-100)0,500]"``
designates data form -100 to 500 ms relative to the stimulus 'noun', with only
the interval form 0 to 500 ms used for rejection.

'''

from collections import defaultdict
import datetime
import inspect
from itertools import izip
import os
from Queue import Queue
import re
import shutil
import socket
import subprocess
from threading import Thread
import time
from warnings import warn

import numpy as np

import mne
from mne.baseline import rescale
from mne.minimum_norm import (make_inverse_operator, apply_inverse,
                              apply_inverse_epochs)
try:
    from mne import Evoked as _mne_Evoked
    from mne.io import Raw as _mne_Raw
except ImportError:
    from mne.fiff import Evoked as _mne_Evoked
    from mne.fiff import Raw as _mne_Raw

from .. import fmtxt, __version__
from ..fmtxt import FMText
from ..data import load
from ..data import plot
from ..data import save
from ..data import table
from ..data import test as _test
from ..data import testnd
from ..data import Dataset, Factor, Var, NDVar, combine, source_induced_power
from ..data.data_obj import isdatalist, UTS, DimensionMismatchError
from ..fmtxt import List, Report
from .. import ui
from ..utils import keydefaultdict
from ..utils import subp
from ..utils.mne_utils import fix_annot_names, is_fake_mri
from .experiment import FileTree


__all__ = ['MneExperiment']


class PickleCache(dict):
    def __getitem__(self, path):
        if path in self:
            return dict.__getitem__(self, path)
        else:
            item = load.unpickle(path)
            dict.__setitem__(self, path, item)
            return item

    def __setitem__(self, path, item):
        save.pickle(item, path)
        dict.__setitem__(self, path, item)


temp = {
        # basic dir
        'meg-sdir': os.path.join('{root}', 'meg'),  # contains subject-name folders for MEG data
        'meg-dir': os.path.join('{meg-sdir}', '{subject}'),
        'mri-sdir': os.path.join('{root}', 'mri'),  # contains subject-name folders for MRI data
        'mri-dir': os.path.join('{mri-sdir}', '{mrisubject}'),
        'bem-dir': os.path.join('{mri-dir}', 'bem'),
        'raw-dir': os.path.join('{meg-dir}', 'raw'),

        # raw
        'experiment': '???',
        # use iir with "l-h" labels, "hp..." labels are legacy
        'raw': ('clm', '0-40', '1-40'),
        # key necessary for identifying raw file info (used for bad channels):
        'raw-key': '{subject}',
        'raw-base': os.path.join('{raw-dir}', '{subject}_{experiment}_{raw}'),
        'raw-file': '{raw-base}-raw.fif',
        'raw-evt-file': '{raw-base}-evts.pickled',
        'trans-file': os.path.join('{raw-dir}', '{mrisubject}-trans.fif'),  # mne p. 196

        # log-files (eye-tracker etc.)
        'log-dir': os.path.join('{meg-dir}', 'logs'),
        'log-rnd': '{log-dir}/rand_seq.mat',
        'log-data-file': '{log-dir}/data.txt',
        'log-file': '{log-dir}/log.txt',
        'edf-file': os.path.join('{log-dir}', '*.edf'),

        # mne secondary/forward modeling
        'cov': 'bl',
        'proj-file': '{raw-base}_{proj}-proj.fif',
        'proj-plot': '{raw-base}_{proj}-proj.pdf',
        'cov-file': '{raw-base}_{cov}-{cov-rej}-{proj}-cov.fif',
        'mri-file': os.path.join('{mri-dir}', 'mri', 'orig.mgz'),
        'bem-file': os.path.join('{bem-dir}', '{mrisubject}-*-bem.fif'),
        'bem-sol-file': os.path.join('{bem-dir}', '{mrisubject}-*-bem-sol.fif'),
        'src-file': os.path.join('{bem-dir}', '{mrisubject}-{src}-src.fif'),
        'fwd-file': '{raw-base}_{mrisubject}-{src}-fwd.fif',

        # epochs
        'rej-dir': os.path.join('{meg-dir}', 'epoch selection'),
        'rej-file': os.path.join('{rej-dir}', '{experiment}_{raw}_'
                                 '{epoch}-{rej}.pickled'),

        'common_brain': 'fsaverage',

        # evoked
        'equalize_evoked_count': ('', 'eq'),
        'evoked-dir': os.path.join('{meg-dir}', 'evoked'),
        'evoked-file': os.path.join('{evoked-dir}', '{experiment} {sns-kind} '
                                    '{epoch} {model} {evoked-kind}.pickled'),

        # Labels
        'hemi': ('lh', 'rh'),
        'label-dir': os.path.join('{mri-dir}', 'label'),
        'annot-file': os.path.join('{label-dir}', '{hemi}.{parc}.annot'),
        # pickled list of labels
        'label-file': os.path.join('{label-dir}', '{parc}.pickled'),

        # compound properties
        'src-kind': '{sns-kind} {cov} {inv}',

        # (method) plots
        'plot-dir': os.path.join('{root}', 'plots'),
        'plot-file': os.path.join('{plot-dir}', '{analysis}', '{name}.{ext}'),

        # general analysis parameters
        'analysis': '',  # analysis parameters (sns-kind, src-kind, ...)

        # test files (2nd level, cache only TFCE distributions)
        # test-options should be test + bl_repr + pmin_repr + tw_repr
        'test-dir': os.path.join('{root}', 'test', '{analysis} {group}'),
        'data_parc': 'unmasked',
        'test-file': os.path.join('{test-dir}', '{epoch} {test} '
                                  '{test_options} {data_parc}.pickled'),

        # result output files
        # data processing parameters
        #    > group
        #        > kind of test
        #    > single-subject
        #        > kind of test
        #            > subject
        'folder': '',  # intermediate folder for deep files
        'resname': '',  # analysis name (GA-movie, max plot, ...)
        'ext': 'pickled',  # file extension
        'res-dir': os.path.join('{root}', 'results'),
        'res-file': os.path.join('{res-dir}', '{analysis}', '{resname}.{ext}'),
        'res-deep-file': os.path.join('{res-dir}', '{analysis}', '{folder}',
                                      '{resname}.{ext}'),
        'res-g-file': os.path.join('{res-dir}', '{analysis} {group}',
                                   '{resname}.{ext}'),
        'res-g-deep-file': os.path.join('{res-dir}', '{analysis} {group}',
                                        '{folder}', '{resname}.{ext}'),
        'res-s-file': os.path.join('{res-dir}', '{analysis} subjects',
                                    '{resname}', '{subject}.{ext}'),

        # besa
        'besa-root': os.path.join('{root}', 'besa'),
        'besa-trig': os.path.join('{besa-root}', '{subject}', '{subject}_'
                                  '{experiment}_{epoch}_triggers.txt'),
        'besa-evt': os.path.join('{besa-root}', '{subject}', '{subject}_'
                                 '{experiment}_{epoch}[{rej}].evt'),
         }


class MneExperiment(FileTree):
    """Class for managing data for an experiment

    """
    # Experiment Constants
    # ====================

    # Bad channels dictionary: (sub, exp) -> list of str
    bad_channels = defaultdict(list)

    # Default values for epoch definitions
    epoch_default = {'tmin':-0.1, 'tmax': 0.6, 'decim': 5}

    # named epochs
    epochs = {'epoch': dict(sel="stim=='target'"),
              'bl': dict(sel_epoch='epoch', tmin=-0.1, tmax=0)}
    # Rejection
    # =========
    # eog_sns: The sensors to plot separately in the rejection GUI. The default
    # is the two MEG sensors closest to the eyes for Abu Dhabi KIT data. For NY
    # KIT data set _eog_sns = ['MEG 143', 'MEG 151']
    _eog_sns = ['MEG 087', 'MEG 130']
    #
    # epoch_rejection dict:
    #
    # kind : 'auto', 'manual', 'make'
    #     How the rejection is derived; 'auto': use the parameters to do the
    #     selection on the fly; 'manual': manually create a rejection file (use
    #     the selection GUI .make_rej()); 'make' a rejection file
    #     is created by the user
    # cov-rej : str
    #     rej setting to use for cov under this setting.
    #
    # For manual rejection
    # ^^^^^^^^^^^^^^^^^^^^
    # decim : int
    #     Decim factor for the rejection GUI (default is 5).
    #
    # For automatic rejection
    # ^^^^^^^^^^^^^^^^^^^^^^^
    # threshod : None | dict
    #     the reject argument when loading epochs:
    # edf : list of str
    #     How to use eye tracker information in rejection. True
    #     causes edf files to be loaded but not used
    #     automatically.
    _epoch_rejection = {'': {'kind': None},
                        'man': {'kind': 'manual',
                                'decim': 5,
                                },
                        'et': {'kind': 'auto',
                               'threshold': dict(mag=3e-12),
                               'edf': ['EBLINK'],
                               },
                        'threshold': {'kind': 'auto',
                                      'threshold': dict(mag=3e-12)}
                        }
    epoch_rejection = {}

    exclude = {}  # field_values to exclude (e.g. subjects)

    groups = {}

    # whether to look for and load eye tracker data when loading raw files
    has_edf = defaultdict(lambda: False)

    # projection definition:
    # "base": 'raw' for raw file, or epoch name
    # "rej": rejection setting to use (only applies for epoch projs)
    # r.g. {'ironcross': {'base': 'adj', 'rej': 'man'}}
    projs = {}

    # Pattern for subject names
    subject_re = re.compile('R\d{4}$')

    # state variables that are always shown in self.__repr__():
    _repr_kwargs = ('subject', 'rej')

    # Where to search for subjects (defined as a template name). If the
    # experiment searches for subjects automatically, it scans this directory
    # for subfolders matching subject_re.
    _subject_loc = 'meg-sdir'

    # basic templates to use. Can be a string referring to a templates
    # dictionary in the module level _temp dictionary, or a templates
    # dictionary
    _templates = temp
    # specify additional templates
    _values = {}
    # specify defaults for specific fields (e.g. specify the initial subject
    # name)
    _defaults = {
                 'experiment': 'experiment_name',
                 # this should be a key in the epochs class attribute (see
                 # above)
                 'epoch': 'epoch'}

    # model order: list of factors in the order in which models should be built
    # (default for factors not in this list is alphabetic)
    _model_order = []

    # Tests
    # -----
    # specify tests as (test_type, model, test_parameter) tuple. For example,
    # ("anova", "condition", "condition*subject")
    # ("t_contrast_rel", "ref%loc", "+min(ref|left>nref|*, ref|right>nref|*)")
    # Make sure dictionary keys (test names) are appropriate for filenames.
    # tests imply a model which is set automatically
    tests = {}
    cluster_criteria = {'mintime': 0.025, 'minsensor': 4, 'minsource': 10}

    def __init__(self, root=None, **state):
        """
        Parameters
        ----------
        root : str | None
            the root directory for the experiment (usually the directory
            containing the 'meg' and 'mri' directories)
        """
        # create attributes (overwrite class attributes)
        self.groups = self.groups.copy()
        self.projs = self.projs.copy()
        self.tests = self.tests.copy()
        self.cluster_criteria = self.cluster_criteria.copy()
        self._mri_subjects = keydefaultdict(lambda k: k)
        self._label_cache = PickleCache()
        self._templates = self._templates.copy()
        for cls in reversed(inspect.getmro(self.__class__)):
            if hasattr(cls, '_values'):
                self._templates.update(cls._values)
        # epochs
        epochs = {}
        for name in self.epochs:
            # expand epoch dict
            epoch = self.epoch_default.copy()
            epoch.update(self.epochs[name])
            epoch['name'] = name

            # process secondary attributes
            pad = epoch.get('pad', None)
            if pad:
                if not 'reject_tmin' in epoch:
                    epoch['reject_tmin'] = epoch['tmin']
                epoch['tmin'] -= pad
                if not 'reject_tmax' in epoch:
                    epoch['reject_tmax'] = epoch['tmax']
                epoch['tmax'] += pad

            epochs[name] = epoch
        self.epochs = epochs


        # store epoch rejection settings
        epoch_rejection = self._epoch_rejection.copy()
        epoch_rejection.update(self.epoch_rejection)
        self.epoch_rejection = epoch_rejection

        FileTree.__init__(self, **state)
        self.set_root(root, state.pop('find_subjects', True))

        # register variables with complex behavior
        self._register_field('rej', self.epoch_rejection.keys(),
                             post_set_handler=self._post_set_rej)
        self._register_field('group', self.groups.keys() + ['all'], 'all',
                             eval_handler=self._eval_group)
        self._register_field('epoch', self.epochs.keys(),
                             eval_handler=self._eval_epoch)
        self._register_value('inv', 'free-3-dSPM',
                             set_handler=self._set_inv_as_str)
        self._register_value('model', '', eval_handler=self._eval_model)
        if self.tests:
            self._register_field('test', self.tests.keys(),
                                 post_set_handler=self._post_set_test)
        self._register_field('parc', default='aparc',
                             eval_handler=self._eval_parc)
        self._register_field('proj', [''] + self.projs.keys())
        self._register_field('src', ('ico-4', 'vol-10', 'vol-7', 'vol-5'))

        # compounds
        self._register_compound('sns-kind', ('raw', 'proj'))
        self._register_compound('evoked-kind', ('rej', 'equalize_evoked_count'))

        # Define make handlers
        self._bind_make('evoked-file', self.make_evoked)
        self._bind_make('raw-file', self.make_raw)
        self._bind_make('cov-file', self.make_cov)
        self._bind_make('src-file', self.make_src)
        self._bind_make('fwd-file', self.make_fwd)
        self._bind_make('label-file', self.make_labels)

        # set initial values
        self.store_state()
        self.brain = None

    def __iter__(self):
        "Iterate state through subjects and yield each subject name."
        for subject in self.iter():
            yield subject

    def _annot_exists(self):
        for _ in self.iter('hemi'):
            fpath = self.get('annot-file')
            if not os.path.exists(fpath):
                return False
        return True

    @property
    def _epoch_state(self):
        epochs = self._params['epochs']
        if len(epochs) != 1:
            err = ("This function is only implemented for single epochs (got "
                   "%s)" % self.get('epoch'))
            raise NotImplementedError(err)
        return epochs[0]

    def _process_subject_arg(self, subject, kwargs):
        """Process subject arg for methods that work on groups and subjects

        Returns
        -------
        subject : None | str
            Subject name if the value specifies a subject, None otherwise.
        group : None | str
            Group name if the value specifies a group, None otherwise.
        """
        if subject is None:
            group = None
            subject_ = self.get('subject', **kwargs)
        elif subject in self.get_field_values('group'):
            group = subject
            subject_ = None
            self.set(group=group, **kwargs)
        else:
            group = None
            subject_ = subject
            self.set(subject=subject, **kwargs)

        return subject_, group

    def add_epochs_stc(self, ds, src='epochs', dst=None, ndvar=True,
                       baseline=None):
        """
        Transform epochs contained in ds into source space (adds a list of mne
        SourceEstimates to ds)

        Parameters
        ----------
        ds : Dataset
            The Dataset containing the mne Epochs for the desired trials.
        src : str
            Name of the source epochs in ds.
        dst : str
            Name of the source estimates to be created in ds. The default is
            'stc' for SourceEstimate, and 'src' for NDVar.
        ndvar : bool
            Add the source estimates as NDVar instead of a list of
            SourceEstimate objects.
        """
        subject = ds['subject']
        if len(subject.cells) != 1:
            err = ("ds must have a subject variable with exaclty one subject")
            raise ValueError(err)
        subject = subject.cells[0]
        self.set(subject=subject)

        epochs = ds[src]
        inv = self.load_inv(epochs)
        stc = apply_inverse_epochs(epochs, inv, **self._params['apply_inv_kw'])

        if ndvar:
            if dst is None:
                dst = 'src'

            subject = self.get('mrisubject')
            src = self.get('src')
            mri_sdir = self.get('mri-sdir')
            parc = self.get('parc') or None
            src = load.fiff.stc_ndvar(stc, subject, src, mri_sdir, dst,
                                      parc=parc)
            if baseline is not None:
                src -= src.summary(time=baseline)
            ds[dst] = src
        else:
            if dst is None:
                dst = 'stc'

            if baseline is not None:
                raise NotImplementedError("Baseline for SourceEstimate")
            ds[dst] = stc

    def add_evoked_stc(self, ds, ind_stc=False, ind_ndvar=False, morph_stc=False,
                       morph_ndvar=False, baseline=None):
        """
        Add source estimates to a dataset with evoked data.

        Parameters
        ----------
        ds : Dataset
            The Dataset containing the Evoked objects.
        ind_stc : bool
            Add source estimates on individual brains as list of
            :class:`mne.SourceEstimate`.
        ind_ndvar : bool
            Add source estimates on individual brain as :class:`NDVar` (only
            possible for datasets containing data of a single subject).
        morph_stc : bool
            Add source estimates morphed to the common brain as list of
            :class:`mne.SourceEstimate`.
        morph_ndvar : bool
            Add source estimates morphed to the common brain as :class:`NDVar`.
        baseline : None | str | tuple
            Baseline correction in source space.

        Notes
        -----
        Assumes that all Evoked of the same subject share the same inverse
        operator.
        """
        if not any((ind_stc, ind_ndvar, morph_stc, morph_ndvar)):
            err = ("Nothing to load, set at least one of (ind_stc, ind_ndvar, "
                   "morph_stc, morph_ndvar) to True")
            raise ValueError(err)

        if isinstance(baseline, str):
            raise NotImplementedError("Baseline form different epoch")

        # find from subjects
        common_brain = self.get('common_brain')
        meg_subjects = ds.eval('subject.cells')
        n_subjects = len(meg_subjects)
        if ind_ndvar and n_subjects > 1:
            err = ("Can't use ind_ndvar with data from more than one "
                   "subjects; an NDVar can only be created from stcs that are "
                   "estimated on the same brain. Use morph_ndvar=True "
                   "instead.")
            raise ValueError(err)
        from_subjects = {}  # from-subject for the purpose of morphing
        for subject in meg_subjects:
            if is_fake_mri(self.get('mri-dir', subject=subject)):
                subject_from = common_brain
            else:
                subject_from = self.get('mrisubject', subject=subject)
            from_subjects[subject] = subject_from

        morph_requested = (morph_stc or morph_ndvar)
        all_are_common_brain = all(v == common_brain for v in
                                   from_subjects.values())
        collect_morphed_stcs = morph_requested and not all_are_common_brain
        collect_ind_stcs = (ind_stc or ind_ndvar) or (morph_requested and
                                                      all_are_common_brain)

        # make sure annot files are available (needed only for NDVar)
        if (ind_ndvar and all_are_common_brain) or morph_ndvar:
            self.make_annot(mrisubject=common_brain)
        if ind_ndvar and not all_are_common_brain:
            self.make_annot(mrisubject=from_subjects[meg_subjects[0]])

        # find vars to work on
        do = []
        for name in ds:
            if isinstance(ds[name][0], _mne_Evoked):
                do.append(name)
        if len(do) == 0:
            raise RuntimeError("No Evoked found")

        # prepare data containers
        if collect_ind_stcs:
            stcs = defaultdict(list)
        if collect_morphed_stcs:
            mstcs = defaultdict(list)

        # convert evoked objects
        mri_sdir = self.get('mri-sdir')
        invs = {}
        mms = {}
        for i in xrange(ds.n_cases):
            subject = ds[i, 'subject']
            subject_from = from_subjects[subject]

            # create stcs from sns data
            for name in do:
                evoked = ds[i, name]

                # get inv
                if subject in invs:
                    inv = invs[subject]
                else:
                    inv = self.load_inv(evoked, subject=subject)
                    invs[subject] = inv

                # apply inv
                stc = apply_inverse(evoked, inv, **self._params['apply_inv_kw'])

                # baseline correction
                if baseline:
                    rescale(stc._data, stc.times, baseline, 'mean', copy=False)

                if collect_ind_stcs:
                    stcs[name].append(stc)

                if collect_morphed_stcs:
                    if subject_from != common_brain:
                        if subject_from in mms:
                            v_to, mm = mms[subject_from]
                        else:
                            mm, v_to = self.load_morph_matrix()
                            mms[subject_from] = (v_to, mm)
                        stc = mne.morph_data_precomputed(subject_from, subject,
                                                         stc, v_to, mm)
                    mstcs[name].append(stc)

        # add to Dataset
        if len(do) > 1:
            keys = ('%%s_%s' % d for d in do)
        else:
            keys = ('%s',)
        src = self.get('src')
        parc = self.get('parc') or None
        for name, key in izip(do, keys):
            if ind_stc:
                ds[key % 'stc'] = stcs[name]
            if ind_ndvar:
                subject = from_subjects[meg_subjects[0]]
                ndvar = load.fiff.stc_ndvar(stcs[name], subject, src, mri_sdir,
                                            parc=parc)
                ds[key % 'src'] = ndvar
            if morph_stc:
                if all_are_common_brain:
                    stcm = stcs[name]
                else:
                    stcm = mstcs[name]
                ds[key % 'stcm'] = stcm
            if morph_ndvar:
                if all_are_common_brain:
                    stcm = stcs[name]
                else:
                    stcm = mstcs[name]
                ndvar = load.fiff.stc_ndvar(stcm, common_brain, src, mri_sdir,
                                            parc=parc)
                ds[key % 'srcm'] = ndvar

    def add_stc_label(self, ds, label, src='stc'):
        """
        Extract the label time course from a list of SourceEstimates.

        Returns nothing.

        Parameters
        ----------
        ds : Dataset
            Dataset containing a list of SourceEstimates and a subject
            variabls.
        label :
            the label's name (e.g., 'fusiform_lh').
        src : str
            Name of the variable in ds containing the SourceEstimates.
        """
        x = []
        for case in ds.itercases():
            # find appropriate label
            subject = case['subject']
            label_ = self.load_label(label, subject=subject)

            # extract label
            stc = case[src]
            label_data = stc.in_label(label_).data
            label_avg = label_data.mean(0)
            x.append(label_avg)

        time = UTS(stc.tmin, stc.tstep, stc.shape[1])
        ds[label] = NDVar(np.array(x), dims=('case', time))

    def cache_events(self, redo=False):
        """Create the 'raw-evt-file'.

        This is done automatically the first time the events are loaded, but
        caching them will allow faster loading times form the beginning.
        """
        evt_file = self.get('raw-evt-file')
        exists = os.path.exists(evt_file)
        if exists and redo:
            os.remove(evt_file)
        elif exists:
            return

        self.load_events(add_proj=False)

    def get_field_values(self, field, exclude=True):
        """Find values for a field taking into account exclusion

        Parameters
        ----------
        field : str
            Field for which to find values.
        exclude : bool | list of values
            Exclude values. If True, exclude values based on ``self.exclude``.
            For 'mrisubject', exclusions are done on 'subject'. For 'group',
            no exclusions are done.
        """
        if field == 'mrisubject':
            subjects = self.get_field_values('subject', exclude=exclude)
            mrisubjects = sorted(self._mri_subjects[s] for s in subjects)
            common_brain = self.get('common_brain')
            if common_brain:
                mrisubjects.insert(0, common_brain)
            return mrisubjects
        elif field == 'group':
            values = ['all', 'all!']
            values.extend(self.groups.keys())
            return values
        else:
            return FileTree.get_field_values(self, field, exclude)

    def iter(self, fields='subject', group=None, **kwargs):
        """
        Cycle the experiment's state through all values on the given fields

        Parameters
        ----------
        fields : list | str
            Field(s) over which should be iterated.
        exclude : dict  {str: str, str: iterator over str, ...}
            Values to exclude from the iteration with {name: value} and/or
            {name: (sequence of values, )} entries.
        values : dict  {str: iterator over str}
            Fields with custom values to iterate over (instead of the
            corresponding field values) with {name: (sequence of values)}
            entries.
        group : None | str
            If iterating over subjects, use this group ('all' for all except
            excluded subjects, 'all!' for all including excluded subjects, or
            a name defined in experiment.groups).
        prog : bool | str
            Show a progress dialog; str for dialog title.
        mail : bool | str
            Send an email when iteration is finished. Can be True or an email
            address. If True, the notification is sent to :attr:`.owner`.
        others :
            Fields with constant values throughout the iteration.
        """
        if 'subject' in fields:
            if group is None:
                group = self.get('group')

            if group == 'all!':
                kwargs['exclude'] = False
            elif group != 'all':
                subjects = self.get_field_values('subject')
                group = self.groups[group]
                group_subjects = [s for s in subjects if s in group]
                kwargs.setdefault('values', {})['subject'] = group_subjects

        return FileTree.iter(self, fields, **kwargs)

    def iter_range(self, start=None, stop=None, field='subject'):
        """Iterate through a range on a field with ordered values.

        Parameters
        ----------
        start : None | str
            Start value (inclusive). With ``None``, begin at the first value.
        stop : None | str
            Stop value (inclusive). With ``None``, end with the last value.
        field : str
            Name of the field.

        Yields
        ------
        value : str
            Current field value.
        """
        values = self.get_field_values(field)
        if start is not None:
            start = values.index(start)
        if stop is not None:
            stop = values.index(stop) + 1
        idx = slice(start, stop)
        values = values[idx]

        self.store_state()
        for value in values:
            self.restore_state(discard_tip=False)
            self.set(**{field: value})
            yield value
        self.restore_state()

    def iter_vars(self, *args, **kwargs):
        """Deprecated. Use :attr:`.iter()`"""
        warn("MneExperiment.iter_vars() is deprecated. Use .iter()",
             DeprecationWarning)
        kwargs['mail'] = kwargs.get('notify', False)
        self.iter(*args, **kwargs)

    def label_events(self, ds, experiment, subject):
        """
        Adds T (time) and SOA (stimulus onset asynchrony) to the Dataset.

        Parameters
        ----------
        ds : Dataset
            A Dataset containing events (as returned by
            :func:`load.fiff.events`).
        experiment : str
            Name of the experiment.
        subject : str
            Name of the subject.

        Notes
        -----
        Subclass this method to specify events.
        """
        if 'raw' in ds.info:
            raw = ds.info['raw']
            sfreq = raw.info['sfreq']
            ds['T'] = ds['i_start'] / sfreq
            ds['SOA'] = Var(np.ediff1d(ds['T'].x, 0))

        # add subject label
        ds['subject'] = Factor([subject] * ds.n_cases, random=True)
        return ds

    def label_subjects(self, ds):
        """Label the subjects in ds based on .groups

        Parameters
        ----------
        ds : Dataset
            A Dataset with 'subject' entry.
        """
        subject = ds['subject']
        for name, subjects in self.groups.iteritems():
            ds[name] = Var(subject.isin(subjects))

    def load_annot(self, **state):
        self.make_annot(**state)
        parc = self.get('parc')
        subject = self.get('mrisubject')
        mri_sdir = self.get('mri-sdir')
        labels = mne.read_labels_from_annot(subject, parc, 'both', subjects_dir=mri_sdir)
        return labels

    def load_edf(self, **kwargs):
        """Load the edf file ("edf-file" template)"""
        kwargs['fmatch'] = False
        src = self.get('edf-file', **kwargs)
        edf = load.eyelink.Edf(src)
        return edf

    def load_epochs(self, subject=None, baseline=None, ndvar=False,
                    add_bads=True, reject=True, add_proj=True, cat=None,
                    decim=None, pad=0, **kwargs):
        """
        Load a Dataset with epochs for a given epoch definition

        Parameters
        ----------
        subject : str
            Subject(s) for which to load evoked files. Can be a group name
            such as 'all' or a single subject.
        baseline : None | (tmin, tmax)
            Baseline to apply to epochs.
        ndvar : bool | str
            Convert epochs to an NDVar with the given name (if True, 'meg' is
            uesed).
        add_bads : False | True | list
            Add bad channel information to the Raw. If True, bad channel
            information is retrieved from self.bad_channels. Alternatively,
            a list of bad channels can be sumbitted.
        reject : bool
            Whether to apply epoch rejection or not. The kind of rejection
            employed depends on the :attr:`.epoch_rejection` class attribute.
        add_proj : bool
            Add the projections to the Raw object.
        cat : sequence of cell-names
            Only load data for these cells (cells of model).
        decim : None | int
            override the epoch decim factor.
        pad : scalar
            Pad the epochs with this much time (in seconds; e.g. for spectral
            analysis).
        """
        subject, group = self._process_subject_arg(subject, kwargs)
        if group is not None:
            dss = []
            for _ in self.iter(group=group):
                ds = self.load_epochs(baseline=baseline, ndvar=False,
                                      add_bads=add_bads, reject=reject,
                                      cat=cat)
                dss.append(ds)

            ds = combine(dss)
        else:  # single subject
            ds = self.load_selected_events(add_bads=add_bads, reject=reject,
                                           add_proj=add_proj)
            if reject and self._params['rej']['kind'] == 'auto':
                reject_arg = self._params['rej'].get('threshold', None)
            else:
                reject_arg = None

            if cat:
                model = ds.eval(self.get('model'))
                idx = model.isin(cat)
                ds = ds.sub(idx)

            # load sensor space data
            epoch = self._epoch_state
            target = 'epochs'
            tmin = epoch['tmin']
            tmax = epoch['tmax']
            if pad:
                tmin -= pad
                tmax += pad
            decim = decim or epoch['decim']
            ds = load.fiff.add_mne_epochs(ds, tmin, tmax, baseline, decim=decim,
                                          target=target, reject=reject_arg)

        if ndvar:
            if ndvar is True:
                ndvar = 'meg'
            else:
                ndvar = str(ndvar)
            ds[ndvar] = load.fiff.epochs_ndvar(ds[target], ndvar)

        return ds

    def load_epochs_stc(self, subject=None, sns_baseline=None,
                        src_baseline=None, ndvar=False, cat=None):
        """Load a Dataset with stcs for single epochs

        Parameters
        ----------
        subject : str
            Subject(s) for which to load evoked files. Can be a group name
            such as 'all' or a single subject.
        """
        ds = self.load_epochs(subject, baseline=sns_baseline, ndvar=False,
                              cat=cat)
        self.add_epochs_stc(ds, ndvar=ndvar, baseline=src_baseline)
        return ds

    def load_events(self, subject=None, add_proj=True, add_bads=True,
                    edf=True, **kwargs):
        """
        Load events from a raw file.

        Loads events from the corresponding raw file, adds the raw to the info
        dict.

        Parameters
        ----------
        subject : str (state)
            Subject for which to load events.
        add_proj : bool
            Add the projections to the Raw object.
        add_bads : False | True | list
            Add bad channel information to the Raw. If True, bad channel
            information is retrieved from self.bad_channels. Alternatively,
            a list of bad channels can be sumbitted.
        edf : bool
            Loads edf and add it as ``ds.info['edf']``. Edf will only be added
            if ``bool(self.epoch_rejection['edf']) == True``.
        others :
            Update state.
        """
        raw = self.load_raw(add_proj=add_proj, add_bads=add_bads,
                            subject=subject, **kwargs)

        evt_file = self.get('raw-evt-file')
        if os.path.exists(evt_file):
            ds = load.unpickle(evt_file)
        else:
            ds = load.fiff.events(raw)

            subject = self.get('subject')
            if edf and self.has_edf[subject]:  # add edf
                edf = self.load_edf()
                edf.add_t_to(ds)
                ds.info['edf'] = edf

            # cache
            del ds.info['raw']
            if edf or not self.has_edf[subject]:
                save.pickle(ds, evt_file)

        ds.info['raw'] = raw

        subject = subject or self.get('subject')
        experiment = self.get('experiment')

        ds = self.label_events(ds, experiment, subject)
        return ds

    def load_evoked(self, subject=None, baseline=None, ndvar=True, cat=None,
                    **kwargs):
        """
        Load a Dataset with the evoked responses for each subject.

        Parameters
        ----------
        subject : str
            Subject(s) for which to load evoked files. Can be a group name
            such as 'all' or a single subject.
        baseline : None | (tmin, tmax)
            Baseline to apply to evoked response.
        ndvar : bool | str
            Convert the mne Evoked objects to an NDVar. If True, the target
            name is 'meg'.
        cat : sequence of cell-names
            Only load data for these cells (cells of model).
        model : str (state)
            Model according to which epochs are grouped into evoked responses.
        *others* : str
            State parameters.
        """
        subject, group = self._process_subject_arg(subject, kwargs)
        if group is not None:
            dss = []
            for _ in self.iter(group=group):
                ds = self.load_evoked(baseline=baseline, ndvar=False, cat=cat)
                dss.append(ds)

            ds = combine(dss)

            # check consistency
            for name in ds:
                if isinstance(ds[name][0], (_mne_Evoked, mne.SourceEstimate)):
                    lens = np.array([len(e.times) for e in ds[name]])
                    ulens = np.unique(lens)
                    if len(ulens) > 1:
                        err = ["Unequel time axis sampling (len):"]
                        subject = ds['subject']
                        for l in ulens:
                            idx = (lens == l)
                            err.append('%i: %r' % (l, subject[idx].cells))
                        raise DimensionMismatchError(os.linesep.join(err))

        else:  # single subject
            path = self.get('evoked-file', make=True)
            ds = load.unpickle(path)

            if cat:
                model = ds.eval(self.get('model'))
                idx = model.isin(cat)
                ds = ds.sub(idx)

            # baseline correction
            if isinstance(baseline, str):
                raise NotImplementedError
            elif baseline:
                if ds.info.get('evoked', ('evoked',)) != ('evoked',):
                    raise NotImplementedError
                for e in ds['evoked']:
                    rescale(e.data, e.times, baseline, 'mean', copy=False)

        # convert to NDVar
        if ndvar:
            if ndvar is True:
                ndvar = 'meg'

            keys = [k for k in ds if isdatalist(ds[k], _mne_Evoked, False)]
            for k in keys:
                if len(keys) > 1:
                    ndvar_key = '_'.join((k, ndvar))
                else:
                    ndvar_key = ndvar
                ds[ndvar_key] = load.fiff.evoked_ndvar(ds[k])

        return ds

    def load_evoked_freq(self, subject=None, sns_baseline=(None, 0),
                         label=None, frequencies='4:40', **kwargs):
        """Load frequency space evoked data

        Parameters
        ----------
        subject : str
            Subject or group.
        sns_baseline : tuple
            Baseline in sensor space.
        label : None | str | mne.Label
            Label in which to compute the induce power (average in label).
        """
        subject, group = self._process_subject_arg(subject, kwargs)
        model = self.get('model') or None
        if group is not None:
            dss = []
            for _ in self.iter(group=group):
                ds = self.load_evoked_freq(None, sns_baseline, label,
                                           frequencies)
                dss.append(ds)

            ds = combine(dss)
        else:
            if label is None:
                src = self.get('src')
            else:
                src = 'mean'
                if isinstance(label, basestring):
                    label = self.load_label(label)
            ds_epochs = self.load_epochs(None, sns_baseline, decim=10, pad=0.2)
            inv = self.load_inv(ds_epochs['epochs'])
            subjects_dir = self.get('mri-sdir')
            ds = source_induced_power('epochs', model, ds_epochs, src, label,
                                      None, inv, subjects_dir, frequencies,
                                      n_cycles=3,
                                      **self._params['apply_inv_kw'])
            ds['subject'] = Factor([subject], rep=ds.n_cases, random=True)
        return ds

    def load_evoked_stc(self, subject=None, sns_baseline=(None, 0),
                        src_baseline=None, sns_ndvar=False, ind_stc=False,
                        ind_ndvar=False, morph_stc=False, morph_ndvar=False,
                        cat=None, **kwargs):
        """Load evoked source estimates.

        Parameters
        ----------
        subject : str
            Subject(s) for which to load evoked files. Can be a group name
            such as 'all' or a single subject.
        sns_baseline : None | str | tuple
            Sensor space baseline correction.
        src_baseline : None | str | tuple
            Source space baseline correctoin.
        ind_stc : bool
            Add source estimates on individual brains as list of
            :class:`mne.SourceEstimate`.
        ind_ndvar : bool
            Add source estimates on individual brains as :class:`NDVar`.
        morph_stc : bool
            Add source estimates morphed to the common brain as list of
            :class:`mne.SourceEstimate`.
        morph_ndvar : bool
            Add source estimates morphed to the common brain as :class:`NDVar`.
        cat : sequence of cell-names
            Only load data for these cells (cells of model).
        *others* : str
            State parameters.
        """
        if not any((ind_stc, ind_ndvar, morph_stc, morph_ndvar)):
            err = ("Nothing to load, set at least one of (ind_stc, ind_ndvar, "
                   "morph_stc, morph_ndvar) to True")
            raise ValueError(err)

        ds = self.load_evoked(subject=subject, baseline=sns_baseline,
                              ndvar=sns_ndvar, cat=cat, **kwargs)
        self.add_evoked_stc(ds, ind_stc, ind_ndvar, morph_stc, morph_ndvar,
                            src_baseline)
        return ds

    def load_inv(self, fiff=None, **kwargs):
        """Load the inverse operator

        Parameters
        ----------
        fiff : Raw | Epochs | Evoked | ...
            Object for which to make the inverse operator (provides the mne
            info dictionary). By default, the current raw is used.
        others :
            State parameters.
        """
        self.set(**kwargs)

        if fiff is None:
            fiff = self.load_raw()

        fwd_file = self.get('fwd-file', make=True)
        fwd = mne.read_forward_solution(fwd_file, surf_ori=True)
        cov = mne.read_cov(self.get('cov-file', make=True))
        if self._params['reg_inv']:
            cov = mne.cov.regularize(cov, fiff.info)
        inv = make_inverse_operator(fiff.info, fwd, cov,
                                    **self._params['make_inv_kw'])
        return inv

    def load_label(self, label, **kwargs):
        """Retrieve a label as mne Label object

        Parameters
        ----------
        label : str
            Name of the label. If the label ends in '_bh', the combination of
            '*_lh' and '*_rh' will be returned.

        Notes
        -----
        Labels are processed in the following sequence:

        annot-file
            Some are provided by default, others are created. Each vertex is
            occupied by at most one label (limitation of *.annot files). Can be
            morphed from one subject to others. Labels are marked "*-?h".
        label-file
            File with pickled labels, based on an annot file but can add
            additional labels. Labels can be overlapping. Labels are marked
            "*_?h".
        """
        labels = self.load_labels(**kwargs)
        if label in labels:
            return labels[label]
        elif label.endswith('_bh'):
            region = label[:-3]
            label_lh = self.load_label(region + '_lh')
            label_rh = self.load_label(region + '_rh')
            label_bh = label_lh + label_rh
            labels[label] = label_bh
            return label_bh
        else:
            parc = self.get('parc')
            msg = ("Label %r could not be found in parc %r." % (label, parc))
            raise ValueError(msg)

    def load_labels(self, **kwargs):
        """Load labels from an annotation file."""
        fpath = self.get('label-file', make=True, **kwargs)
        labels = self._label_cache[fpath]
        return labels

    def load_morph_matrix(self, **state):
        """Load the morph matrix from mrisubject to common_brain

        Returns
        -------
        mm :
            Morph matrix.
        vertices_to : array
            Vertices of the morphed data.
        """
        subjects_dir = self.get('mri-sdir', **state)
        subject_to = self.get('common_brain')
        subject_from = self.get('mrisubject')

        src_to = self.load_src(mrisubject=subject_to, match=False)
        src_from = self.load_src(mrisubject=subject_from, match=False)

        vertices_to = [src_to[0]['vertno'], src_to[1]['vertno']]
        vertices_from = [src_from[0]['vertno'], src_from[1]['vertno']]

        mm = mne.compute_morph_matrix(subject_from, subject_to, vertices_from,
                                      vertices_to, None, subjects_dir)
        return mm, vertices_to

    def load_raw(self, add_proj=True, add_bads=True, preload=False, **kwargs):
        """
        Load a raw file as mne Raw object.

        Parameters
        ----------
        add_proj : bool
            Add the projections to the Raw object. This does *not* set the
            proj variable.
        add_bads : False | True | list
            Add bad channel information to the Raw. If True, bad channel
            information is retrieved from self.bad_channels. Alternatively,
            a list of bad channels can be sumbitted.
        preload : bool
            Mne Raw parameter.
        """
        self.set(**kwargs)

        if add_proj:
            proj = self.get('proj')
            if proj:
                proj = self.get('proj-file')
            else:
                proj = None
        else:
            proj = None

        raw_file = self.get('raw-file', make=True)
        raw = load.fiff.mne_raw(raw_file, proj, preload=preload)
        if add_bads:
            if add_bads is True:
                key = self.get('raw-key')
                bad_chs = self.bad_channels[key]
            else:
                bad_chs = add_bads

            raw.info['bads'].extend(bad_chs)

        return raw

    def load_selected_events(self, subject=None, reject=True, add_proj=True,
                             add_bads=True, index=True, **kwargs):
        """
        Load events and return a subset based on epoch and rejection

        Parameters
        ----------
        subject : str
            Subject(s) for which to load evoked files. Can be a group name
            such as 'all' or a single subject.
        reject : bool | 'keep'
            Reject bad trials. For True, bad trials are removed from the
            Dataset. For 'keep', the 'accept' variable is added to the Dataset
            and bad trials are kept.
        add_proj : bool
            Add the projections to the Raw object.
        add_bads : False | True | list
            Add bad channel information to the Raw. If True, bad channel
            information is retrieved from self.bad_channels. Alternatively,
            a list of bad channels can be sumbitted.
        index : bool | str
            Index the Dataset before rejection (provide index name as str).
        others :
            Update the experiment state.

        Warning
        -------
        For automatic rejection: Since no epochs are loaded, no rejection
        based on thresholding is performed.
        """
        # process arguments
        if reject not in (True, False, 'keep'):
            raise ValueError("Invalid reject value: %r" % reject)
        if index and not isinstance(index, str):
            index = 'index'

        # case of loading events for a group
        subject, group = self._process_subject_arg(subject, kwargs)
        if group is not None:
            dss = [self.load_selected_events(reject=reject, add_proj=add_proj,
                                             add_bads=add_bads, index=index)
                   for _ in self.iter(group=group)]
            ds = combine(dss)
            return ds

        # retrieve & check epoch parameters
        epoch = self._epoch_state
        sel = epoch.get('sel', None)
        sel_epoch = epoch.get('sel_epoch', None)
        rej_kind = self._params['rej']['kind']
        if rej_kind not in ('manual', 'make', 'auto'):
            raise ValueError("Unknown rej_kind value: %r" % rej_kind)

        # case 1: no rejection
        if not reject or rej_kind == '':
            ds = self.load_events(add_proj=add_proj, add_bads=add_bads)
            if sel is not None:
                ds = ds.sub(sel)
            if index:
                ds.index(index)
            return ds

        # case 2: rejection comes from a different epoch
        if sel_epoch is not None:
            self.store_state()
            ds = self.load_selected_events(None, 'keep', add_proj, add_bads,
                                           index, epoch=sel_epoch)
            self.restore_state()

            if sel is not None:
                ds = ds.sub(sel)
            if index:
                ds.index(index)

            if reject is True:
                ds = ds.sub('accept')

            return ds

        # case 3: proper rejection
        ds = self.load_events(add_proj=add_proj, add_bads=add_bads)
        if sel is not None:
            ds = ds.sub(sel)
        if index:
            ds.index(index)

        if rej_kind in ('manual', 'make'):
            path = self.get('rej-file')
            if not os.path.exists(path):
                err = ("The rejection file at %r does not exist. Run "
                       ".make_rej() first." % path)
                raise RuntimeError(err)

            ds_sel = load.unpickle(path)
            if not np.all(ds['trigger'] == ds_sel['trigger']):
                err = ("The epoch selection file contains different "
                       "events than the data. Something went wrong...")
                raise RuntimeError(err)

            if reject == 'keep':
                ds['accept'] = ds_sel['accept']
            elif reject == True:
                ds = ds.sub(ds_sel['accept'])
            else:
                err = ("reject parameter must be bool or 'keep', not "
                       "%r" % reject)
                raise ValueError(err)
        else:
            use = self._params['rej'].get('edf', False)
            if use:
                edf = ds.info['edf']
                tmin = epoch.get('reject_tmin', epoch['tmin'])
                tmax = epoch.get('reject_tmax', epoch['tmax'])
                if reject == 'keep':
                    edf.mark(ds, tstart=tmin, tstop=tmax, use=use)
                else:
                    ds = edf.filter(ds, tstart=tmin, tstop=tmax, use=use)

        return ds

    def load_src(self, add_geom=False, **state):
        "Load the current source space"
        fpath = self.get('src-file', make=True, **state)
        src = mne.read_source_spaces(fpath, add_geom)
        return src

    def load_test(self, tstart, tstop, pmin, parc=None, mask=None, samples=1000,
                  group='all', data='src', sns_baseline=(None, 0),
                  src_baseline=None, return_data=False, redo=False, **kwargs):
        """Load thrshold-free spatio-temporal cluster permutation test

        Parameters
        ----------
        tstart, tstop : None | scalar
            Time window for finding clusters.
        pmin : None | 'tfce'
            Kind of test.
        parc : None | str
            Parcellation for which to collect distribution.
        mask : None | str
            Mask whole brain.
        samples : int
            Number of samples used to determine cluster p values for spatio-
            temporal clusters.
        group : str
            Group for which to perform the test.
        data : 'sns' | 'src'
            Whether the analysis is in sensor or source space.
        sns_baseline : None | tuple
            Sensor space baseline interval.
        src_baseline : None | tuple
            Source space baseline interval.
        return_data : bool
            Return the data along with the test result (see below).
        redo : bool
            If the target file already exists, delete and recreate it (only
            applies for tests that are cached).

        Returns
        -------
        ds : Dataset (if return_data==True)
            Data that forms the basis of the test.
        res : TestResult
            Test result for the specified test.
        """
        self._set_test_options(data, sns_baseline, src_baseline, pmin, tstart,
                               tstop)

        # figure out what test to do
        test, model, contrast = self.tests[self.get('test', **kwargs)]
        self.set(model=model)

        # find cached file path
        if parc:
            if pmin == 'tfce':
                raise NotImplementedError("tfce analysis can't have parc")
            elif data == 'sns':
                raise NotImplementedError("sns analysis can't have parc")
            mask = True
            parc_ = parc
            parc_dim = 'source'
            data_parc = parc
        elif mask:
            if data == 'sns':
                raise NotImplementedError("sns analysis can't have mask")
            parc_ = mask
            if pmin is None:  # can as well collect dist for on parc
                parc_dim = 'source'
                data_parc = mask
            else:  # parc means disconnecting
                parc_dim = None
                data_parc = '%s-mask' % mask
        else:
            parc_ = 'aparc'
            parc_dim = None
            data_parc = 'unmasked'

        dst = self.get('test-file', mkdir=True, data_parc=data_parc,
                       parc=parc_)

        # try to load cached test
        if not redo and os.path.exists(dst):
            res = load.unpickle(dst)
            if res.samples >= samples:
                load_data = return_data
            else:
                res = None
                load_data = True
        else:
            res = None
            load_data = True

        # load data
        if load_data:
            if data == 'sns':
                ds = self.load_evoked(group, sns_baseline, ndvar=True)
            elif data == 'src':
                ds = self.load_evoked_stc(group, sns_baseline, src_baseline,
                                          morph_ndvar=True)
                if mask:
                    # reduce data to parc
                    y = ds['srcm']
                    idx = np.invert(y.source.parc.startswith('unknown'))
                    ds['srcm'] = y.sub(source=idx)
            else:
                raise ValueError(data)

        # perform the test if it was not cached
        if res is None:
            if data == 'sns':
                y = ds['meg']
            elif data == 'src':
                y = ds['srcm']

            res = self._make_test(y, ds, test, model, contrast, samples, pmin,
                                  tstart, tstop, None, parc_dim)
            # cache
            save.pickle(res, dst)

        if return_data:
            return ds, res
        else:
            return res

    def make_annot(self, redo=False, **state):
        self.set(**state)
        if not redo and self._annot_exists():
            return

        # variables
        parc = self.get('parc')
        mrisubject = self.get('mrisubject')
        common_brain = self.get('common_brain')

        if mrisubject == common_brain:
            labels = self._make_annot(parc, mrisubject)
            mri_sdir = self.get('mri-sdir')
            mne.write_labels_to_annot(labels, mrisubject, parc, True, mri_sdir)
        else:
            # make sure annot exists for common brain
            self.set(mrisubject=common_brain, match=False)
            self.make_annot()
            self.set(mrisubject=mrisubject, match=False)

            # copy or morph
            if is_fake_mri(self.get('mri-dir')):
                for _ in self.iter('hemi'):
                    self.make_copy('annot-file', 'mrisubject', common_brain,
                                   mrisubject)
            else:
                self.get('label-dir', make=True)
                for hemi in ('lh', 'rh'):
                    cmd = ["mri_surf2surf", "--srcsubject", common_brain,
                           "--trgsubject", mrisubject, "--sval-annot", parc,
                           "--tval", parc, "--hemi", hemi]
                    self.run_subp(cmd, 0)

                mri_sdir = self.get('mri-sdir')
                fix_annot_names(mrisubject, parc, common_brain,
                                subjects_dir=mri_sdir)

    def _make_annot(self, parc, subject):
        "Only called to make custom annotation files for the common_brain"
        msg = "Custom parcellations %r is not implemented." % parc
        raise NotImplementedError(msg)

    def make_besa_evt(self, redo=False, **state):
        """Make the trigger and event files needed for besa

        Parameters
        ----------
        redo : bool
            If besa files already exist, overwrite them.

        Notes
        -----
        Ignores the *decim* epoch parameter.

        Target files are saved relative to the *besa-root* location.
        """
        self.set(**state)
        epoch = self._epoch_state

        rej = self.get('rej')

        trig_dest = self.get('besa-trig', rej='', mkdir=True)
        evt_dest = self.get('besa-evt', rej=rej, mkdir=True)

        if not redo and os.path.exists(evt_dest) and os.path.exists(trig_dest):
            return

        # load events
        ds = self.load_selected_events(reject='keep')

        # save triggers
        if redo or not os.path.exists(trig_dest):
            save.meg160_triggers(ds, trig_dest, pad=1)
            if not redo and os.path.exists(evt_dest):
                return
        else:
            ds.index('besa_index', 1)

        # reject bad trials
        ds = ds.sub('accept')

        # save evt
        tmin = epoch['tmin']
        tmax = epoch['tmax']
        save.besa_evt(ds, tstart=tmin, tstop=tmax, dest=evt_dest)

    def make_copy(self, temp, field, src, dst, redo=False):
        """Make a copy of a file

        Parameters
        ----------
        temp : str
            Template of the file which to copy.
        field : str
            Field in which the source and target of the link are distinguished.
        src : str
            Value for field on the source file.
        dst : str
            Value for field on the destination filename.
        redo : bool
            If the target file already exists, overwrite it.
        """
        dst_path = self.get(temp, mkdir=True, **{field: dst})
        if not redo and os.path.exists(dst_path):
            return

        src_path = self.get(temp, **{field: src})
        if os.path.isdir(src_path):
            raise ValueError("Can only copy files, not directories.")
        shutil.copyfile(src_path, dst_path)

    def make_cov(self, redo=False):
        """Make a noise covariance (cov) file

        Parameters
        ----------
        redo : bool
            If the cov file already exists, overwrite it.
        cov : None | str
            The epoch used for estimating the covariance matrix (needs to be
            a name in .epochs). If None, the experiment state cov is used.
        """
        dest = self.get('cov-file')
        if (not redo) and os.path.exists(dest):
            return

        cov = self.get('cov')
        rej = self.get('cov-rej')
        ds = self.load_epochs(baseline=(None, 0), ndvar=False, decim=1,
                              epoch=cov, rej=rej)
        epochs = ds['epochs']
        cov = mne.cov.compute_covariance(epochs)
        cov.save(dest)

    def make_evoked(self, redo=False, **kwargs):
        """
        Creates datasets with evoked files for the current subject/experiment
        pair.

        Parameters
        ----------
        epoch : str
            Data epoch specification.
        model : str
            Model specifying cells for evoked.
        """
        dest = self.get('evoked-file', mkdir=True, **kwargs)
        if not redo and os.path.exists(dest):
            return

        epoch_names = [ep['name'] for ep in self._params['epochs']]
        equal_count = self.get('equalize_evoked_count') == 'eq'

        # load the epochs
        epoch = self.get('epoch')
        dss = [self.load_epochs(epoch=name) for name in epoch_names]
        self.set(epoch=epoch)

        # find the events common to all epochs
        idx = reduce(np.intersect1d, (ds['index'] for ds in dss))

        # reduce datasets to common events and aggregate
        model = self.get('model')
        drop = ('i_start', 't_edf', 'T', 'index')
        for i in xrange(len(dss)):
            ds = dss[i]
            index = ds['index']
            ds_idx = index.isin(idx)
            if ds_idx.sum() < len(ds_idx):
                ds = ds[ds_idx]

            dss[i] = ds.aggregate(model, drop_bad=True, drop=drop,
                                  equal_count=equal_count,
                                  never_drop=('epochs',))

        if len(dss) == 1:
            ds = dss[0]
            ds.rename('epochs', 'evoked')
            ds.info['evoked'] = ('evoked',)
        else:
            for name, ds in zip(epoch_names, dss):
                ds.rename('epochs', name)
            ds = combine(dss)
            ds.info['evoked'] = tuple(epoch_names)

        if 'raw' in ds.info:
            del ds.info['raw']

        save.pickle(ds, dest)

    def make_fwd(self, redo=False):
        """Make the forward model"""
        fname = self.get('fwd-file')
        if not redo and os.path.exists(fname):
            return

        info = self.get('raw-file', make=True)
        mri = self.get('trans-file')
        src = self.get('src-file', make=True)
        bem = self.get('bem-sol-file', fmatch=True)

        mne.make_forward_solution(info, mri, src, bem, fname, ignore_ref=True,
                                  overwrite=True)

    def make_labels(self, redo=False):
        dst = self.get('label-file')
        if not redo and os.path.exists(dst):
            return

        parc = self.get('parc')
        subject = self.get('mrisubject')
        mri_sdir = self.get('mri-sdir')
        labels = self._make_labels(parc, subject, redo, mri_sdir)
        label_dict = {label.name: label for label in labels}
        self._label_cache[dst] = label_dict

    def _make_labels(self, parc, subject, redo, mri_sdir):
        "Returns an iterator over labels for a given parc/subject combination"
        if redo:
            self.make_annot(redo)
        labels = self.load_annot()
        for label in labels:
            if label.name.endswith('-lh'):
                label.name = label.name[:-3] + '_lh'
            elif label.name.endswith('-rh'):
                label.name = label.name[:-3] + '_rh'
        return labels

    def make_link(self, temp, field, src, dst, redo=False):
        """Make a hard link at the file with the dst value on field, linking to
        the file with the src value of field

        Parameters
        ----------
        temp : str
            Template of the file for which to make a link.
        field : str
            Field in which the source and target of the link are distinguished.
        src : str
            Value for field on the source file.
        dst : str
            Value for field on the destination filename.
        redo : bool
            If the target file already exists, overwrite it.
        """
        dst_path = self.get(temp, **{field: dst})
        if not redo and os.path.exists(dst_path):
            return

        src_path = self.get(temp, **{field: src})
        os.link(src_path, dst_path)

    def make_mov_ga_dspm(self, subject=None, surf='inflated', fmin=2,
                         redo=False, **kwargs):
        """Make a grand average movie from dSPM values

        Parameters
        ----------
        subject : None | str
            Subject or group.
        surf : str
            Surface on which to plot data.
        fmin : scalar
            Minimum dSPM value to draw. fmax is 3 * fmin.
        redo : bool
            Make the movie even if the target file exists already.
        others :
            Experiment state parameters.
        """
        kwargs['model'] = ''
        subject, group = self._process_subject_arg(subject, kwargs)

        self.set(equalize_evoked_count='',
                 analysis='{src-kind} {evoked-kind}',
                 resname="GA dSPM %s %s" % (surf, fmin),
                 ext='mov')
        if group is not None:
            dst = self.get('res-g-file', mkdir=True)
            src = 'srcm'
        else:
            dst = self.get('res-s-file', mkdir=True)
            src = 'src'
        if not redo and os.path.exists(dst):
            return

        ds = self.load_evoked_stc(group, (None, 0),
                                  ind_ndvar=subject is not None,
                                  morph_ndvar=group is not None)

        brain = plot.brain.dspm(ds[src], fmin, fmin * 3, surf=surf)
        brain.save_movie(dst)
        brain.close()

    def make_mov_ga(self, subject=None, surf='smoothwm', p0=0.05, redo=False,
                    **kwargs):
        """Make a grand average movie for a subject or group

        In order to compare activation with baseline, data are not baseline
        corrected in sensor space but in source space.

        Parameters
        ----------
        subject : None | str
            Subject or group.
        surf : str
            Surface on which to plot data.
        p0 : scalar
            Minimum p value to draw.
        redo : bool
            Make the movie even if the target file exists already.
        others :
            Experiment state parameters.
        """
        subject, group = self._process_subject_arg(subject, kwargs)

        if p0 == 0.05:
            p1 = 0.01
        elif p0 == 0.01:
            p1 = 0.001
        else:
            raise ValueError("Unknown p0: %s" % p0)

        self.set(equalize_evoked_count='',
                 analysis='{src-kind} {evoked-kind}',
                 resname="GA %s %s" % (surf, p0),
                 ext='mov')
        if group is not None:
            dst = self.get('res-g-file', mkdir=True)
        else:
            dst = self.get('res-s-file', mkdir=True)
        if not redo and os.path.exists(dst):
            return

        inv = self.get('inv')
        if inv.startswith(('free', 'loose')):
            sns_baseline = None
            src_baseline = (None, 0)
        elif inv.startswith('fixed'):
            sns_baseline = (None, 0)
            src_baseline = None
        else:
            raise ValueError("Unknown inv kind: %r" % inv)

        self.set(model='')
        if group is not None:
            ds = self.load_evoked_stc(group, sns_baseline, src_baseline,
                                      morph_ndvar=True)
            src = 'srcm'
        else:
            ds = self.load_epochs_stc(group, sns_baseline, src_baseline,
                                      ndvar=True)
            src = 'src'

        res = testnd.ttest_1samp(src, match=None, ds=ds)
        brain = plot.brain.stat(res.p, res.t, p0=p0, p1=p1, surf=surf,
                                dtmin=0.01)
        brain.save_movie(dst)
        brain.close()

    def make_mov_ttest(self, x, c1, c0, subject=None, surf='inflated', p0=0.05,
                       redo=False, **kwargs):
        """Make a t-test movie

        Parameters
        ----------
        x : str
            Model on which the conditions c1 and c0 are defined.
        c1 : None | str | tuple
            Test condition (cell in model). If None, the grand average is
            used and c0 has to be a scalar.
        c0 : str | scalar
            Control condition (cell on model) or scalar against which to
            compare c1.
        subject : str (state)
            Group name, or subject name for single subject ttest.
        """
        subject, group = self._process_subject_arg(subject, kwargs)

        if p0 == 0.1:
            p1 = 0.05
        elif p0 == 0.05:
            p1 = 0.01
        elif p0 == 0.01:
            p1 = 0.001
        else:
            raise ValueError("Unknown p0: %s" % p0)

        self.set(analysis='{src-kind} {evoked-kind}',
                 resname="T-Test %s-%s %s %s" % (str(c1), str(c0), surf, p0),
                 ext='mov')
        if group is not None:
            dst = self.get('res-g-file', mkdir=True)
        else:
            dst = self.get('res-s-file', mkdir=True)
        if not redo and os.path.exists(dst):
            return

        sns_baseline = (None, 0)
        src_baseline = None

        if group is not None:
            ds = self.load_evoked_stc(group, sns_baseline, src_baseline,
                                      morph_ndvar=True, cat=(c1, c0), model=x)
            res = testnd.ttest_rel('srcm', x, c1, c0, match='subject', ds=ds)
        else:
            ds = self.load_epochs_stc(group, sns_baseline, src_baseline,
                                      ndvar=True, cat=(c1, c0), model=x)
            res = testnd.ttest_ind('src', x, c1, c0, ds=ds)

        brain = plot.brain.stat(res.p, res.t, p0=p0, p1=p1, surf=surf,
                                dtmin=0.01)
        brain.save_movie(dst)
        brain.close()

    def make_plot_annot(self, surf='inflated', redo=False, **state):
        mrisubject = self.get('mrisubject', **state)
        if is_fake_mri(self.get('mri-dir')):
            mrisubject = self.get('common_brain')
            self.set(mrisubject=mrisubject, match=False)

        analysis = 'Source Annot'
        resname = "{parc} {mrisubject} %s" % surf
        ext = 'png'
        dst = self.get('res-file', mkdir=True, analysis=analysis,
                       resname=resname, ext=ext)
        if not redo and os.path.exists(dst):
            return

        brain = self.plot_annot(surf, w=1200)
        brain.save_image(dst)

    def make_plot_label(self, label, surf='inflated', redo=False, **state):
        mrisubject = self.get('mrisubject', **state)
        if is_fake_mri(self.get('mri-dir')):
            mrisubject = self.get('common_brain')
            self.set(mrisubject=mrisubject, match=False)

        dst = self._make_plot_label_dst(surf, label)
        if not redo and os.path.exists(dst):
            return

        brain = self.plot_label(label, surf=surf)
        brain.save_image(dst)

    def make_plots_labels(self, surf='inflated', redo=False, **state):
        mrisubject = self.get('mrisubject', **state)
        if is_fake_mri(self.get('mri-dir')):
            mrisubject = self.get('common_brain')
            self.set(mrisubject=mrisubject, match=False)

        labels = self.load_labels().values()
        dsts = [self._make_plot_label_dst(surf, label.name)
                for label in labels]
        if not redo and all(os.path.exists(dst) for dst in dsts):
            return

        brain = self.plot_brain(surf, None, 'split', ['lat', 'med'], w=1200)
        for label, dst in zip(labels, dsts):
            brain.add_label(label)
            brain.save_image(dst)
            brain.remove_labels(hemi='lh')

    def _make_plot_label_dst(self, surf, label):
        analysis = 'Source Labels'
        folder = "{parc} {mrisubject} %s" % surf
        resname = label
        ext = 'png'
        dst = self.get('res-deep-file', mkdir=True, analysis=analysis,
                       folder=folder, resname=resname, ext=ext)
        return dst

    def make_proj(self, save=True, save_plot=True):
        """
        computes the first ``n_mag`` PCA components, plots them, and asks for
        user input (a tuple) on which ones to save.

        Parameters
        ----------
        epochs : mne.Epochs
            epochs which should be used for the PCA
        dest : str(path)
            path where to save the projections
        n_mag : int
            number of components to compute
        save : False | True | tuple
            False: don'r save proj fil; True: manuall pick componentws to
            include in the proj file; tuple: automatically include these
            components
        save_plot : False | str(path)
            target path to save the plot
        """
        proj = self.get('proj')
        opt = self.projs[proj]
        reject = {'mag': 1.5e-11}  # far lower than the data range
        if opt['base'] == 'raw':
            raw = self.load_raw(add_proj=False)

            # select time range of events
            events = load.fiff.events(raw)
            time = events['i_start'] / events.info['samplingrate']
            tstart = time.x.min() - 5
            tstop = time.x.max() + 5

            projs = mne.compute_proj_raw(raw, tstart, tstop, duration=5,
                                         n_grad=0, n_mag=9, n_eeg=0,
                                         reject=reject, n_jobs=1)
            fiff_obj = raw
        else:
            epoch = opt['base']
            rej = opt.get('rej', None)
            rej_ = '' if rej is None else rej
            self.set(epoch=epoch, rej=rej_)
            ds = self.load_epochs(add_proj=False)
            epochs = ds['epochs']
            if rej is None:
                epochs.reject = reject.copy()
                epochs._reject_setup()
            projs = mne.compute_proj_epochs(epochs, n_grad=0, n_mag=9, n_eeg=0)
            fiff_obj = epochs

        # convert projs to NDVar
        picks = mne.epochs.pick_types(fiff_obj.info, exclude='bads')
        sensor = load.fiff.sensor_dim(fiff_obj, picks=picks)
        projs_ndvars = []
        for p in projs:
            d = p['data']['data'][0]
            name = p['desc'][-5:]
            v = NDVar(d, (sensor,), name=name)
            projs_ndvars.append(v)

        # plot PCA components
        proj_file = self.get('proj-file')
        p = plot.Topomap(projs_ndvars, title=proj_file, ncol=3, w=9)
        if save_plot:
            dest = self.get('proj-plot')
            p.figure.savefig(dest)
        if save:
            rm = save
            title = "Select Projections"
            msg = ("which Projections do you want to select? (tuple / 'x' to "
                   "abort)")
            while not isinstance(rm, tuple):
                answer = ui.ask_str(msg, title, default='(0,)')
                rm = eval(answer)
                if rm == 'x': raise

            p.close()
            projs = [projs[i] for i in rm]
            mne.write_proj(proj_file, projs)

    def make_raw(self, redo=False, n_jobs=1, **kwargs):
        """Make a raw file

        Parameters
        ----------
        raw : str
            Name of the raw file to make.
        redo : bool
            If the file already exists, recreate it.
        n_jobs : int
            Number of processes for multiprocessing.

        Notes
        -----
        Due to the electronics of the KIT system sensors, signal lower than
        0.16 Hz is not recorded even when recording at DC.
        """
        dst = self.get('raw-file', **kwargs)
        if not redo and os.path.exists(dst):
            return

        raw_dst = self.get('raw')
        raw_src = 'clm'
        if raw_dst == raw_src:
            err = ("Raw %r can not be made (target same as source)" % raw_dst)
            raise ValueError(err)

        apply_proj = False
        raw = self.load_raw(raw=raw_src, add_proj=apply_proj, add_bads=False,
                            preload=True)
        if apply_proj:
            raw.apply_projector()

        if raw_dst == '0-40':
            raw.filter(None, 40, n_jobs=n_jobs, method='iir')
        elif raw_dst == '1-40':
            raw.filter(1, 40, n_jobs=n_jobs, method='iir')
        else:
            raise ValueError('raw = %r' % raw_dst)

        self.set(raw=raw_dst)
        raw.save(dst, overwrite=True)

    def make_rej(self, **kwargs):
        """Show the SelectEpochs GUI to do manual epoch selection for a given
        epoch

        The GUI is opened with the correct file name; if the corresponding
        file exists, it is loaded, and upon saving the correct path is
        the default.

        Parameters
        ----------
        kwargs :
            Kwargs for SelectEpochs
        """
        rej_args = self._params['rej']
        if not rej_args['kind'] == 'manual':
            err = ("Epoch rejection kind for rej=%r is not manual. See the "
                   ".epoch_rejection class attribute." % self.get('rej'))
            raise RuntimeError(err)

        epoch = self._epoch_state
        if 'sel_epoch' in epoch:
            msg = ("The current epoch {cur!r} inherits rejections from "
                   "{sel!r}. To access a rejection file for this epoch, call "
                   "`e.set(epoch={sel!r})` and then `e.make_rej()` "
                   "again.".format(cur=epoch['name'], sel=epoch['sel_epoch']))
            raise ValueError(msg)

        ds = self.load_epochs(ndvar=True, reject=False,
                              decim=rej_args.get('decim', 5))
        path = self.get('rej-file', mkdir=True)

        from ..gui import SelectEpochs
        SelectEpochs(ds, data='meg', path=path, vlim=2e-12, mark=self._eog_sns,
                     **kwargs)

    def make_report(self, test, parc=None, mask=None, pmin=None, tstart=0.15,
                    tstop=None, samples=1000, data='src',
                    sns_baseline=(None, 0), src_baseline=None, redo=False,
                    **state):
        """Create an HTML report on clusters

        Parameters
        ----------
        model : str
            Model (currently only repeated measures t-tests).
        contrast : None | str
            Define a non-standard contrast. Lead with + or - for one-tailed
            tests.
        parc : None
            Find clusters in whole area covered by parc and then in each label.
        mask : None | str
            Parcellation to apply as mask. Can only be specified if parc==None.
        pmin : None | scalar, 1 > pmin > 0
            Equivalent p-value for cluster threshold.
        samples : int
            Number of samples used to determine cluster p values for spatio-
            temporal clusters.
        sns_baseline : None | tuple
            Sensor space baseline interval.
        src_baseline : None | tuple
            Source space baseline interval.
        tstart, tstop : None | scalar
            Time window for finding clusters.
        redo : bool
            If the target file already exists, delete and recreate it.
        """
        # determine report file name
        if parc is None:
            if mask:
                folder = "%s Masked" % mask.capitalize()
            else:
                folder = "Whole Brain"
        elif mask:
            raise ValueError("Can't specify mask together with parc")
        else:
            state['parc'] = parc
            folder = "{parc}"
        self.set(test=test, **state)
        self._set_test_options(data, sns_baseline, src_baseline, pmin, tstart,
                               tstop)
        resname = "{epoch} {test} {test_options}"
        dst = self.get('res-g-deep-file', mkdir=True, fmatch=False,
                       folder=folder, resname=resname, ext='html', test=test,
                       **state)
        if not redo and os.path.exists(dst):
            return

        # load data
        group = self.get('group')
        ds, res = self.load_test(tstart, tstop, pmin, parc, mask, samples,
                                 group, data, sns_baseline, src_baseline, True)

        # start report
        t0 = time.time()
        title = self.format('{experiment} {epoch} {test} {test_options}')
        report = Report(title, site_title=title)

        # method intro
        include = 0.2  # uncorrected p to plot clusters
        info = List("Test Parameters:")
        info.add_item(self.format('{epoch} ~ {model}'))
        test_kind, model, contrast = self.tests[test]
        info.add_item("Test: %s, %s" % (test_kind, contrast))
        # cluster info
        cinfo = info.add_sublist("Cluster Permutation Test")
        if pmin is None:
            cinfo.add_item("P-values based on maximum value in randomizations")
        elif pmin == 'tfce':
            cinfo.add_item("Threshold-free cluster enhancement (Smith & "
                           "Nichols, 2009)")
        else:
            cinfo.add_item("Cluster threshold equivalent to p = %s" % pmin)
            mintime = self.cluster_criteria.get('mintime', None)
            # cluster criteria
            if mintime is None:
                cinfo.add_item("No cluster minimum duration")
            else:
                cinfo.add_item("Cluster minimum duration: %i ms" %
                               round(mintime * 1000))
            if data == 'src':
                minsource = self.cluster_criteria.get('minsource', None)
                if minsource is not None:
                    cinfo.add_item("At least %i contiguous sources." % minsource)
            elif data == 'sns':
                minsensor = self.cluster_criteria.get('minsensor', None)
                if minsensor is not None:
                    cinfo.add_item("At least %i contiguous sensors." % minsensor)
            info.add_item("Separate plots of all clusters with a p-value "
                          "< %s" % include)
        cinfo.add_item("%i permutations" % res.samples)
        cinfo.add_item("Time interval: %i - %i ms." % (round(tstart * 1000),
                                                       round(tstop * 1000)))
        report.append(info)

        # add subject information to experiment
        s_ds = table.repmeas('n', model, 'subject', ds=ds)
        s_ds2 = self.show_subjects(asds=True)
        s_ds.update(s_ds2[('subject', 'mri')])
        s_table = s_ds.as_table(midrule=True, count=True, caption="All "
                                "subjects included in the analysis with "
                                "trials per condition")
        report.append(s_table)

        # add experiment state to report
        t = self.show_state(hide=['annot', 'epoch-bare',
                                  'epoch-stim', 'ext', 'hemi', 'label',
                                  'subject', 'model', 'mrisubject'])
        report.append(t)

        y = ds['srcm']
        legend = None
        if parc is None and pmin in (None, 'tfce'):
            section = report.add_section("P<=.05")
            self._source_bin_table(section, test_kind, res, 0.05)
            clusters = res._clusters(0.05, maps=True)
            clusters.sort('tstart')
            title = "{tstart}-{tstop} {location} p={p}{mark} {effect}"
            for cluster in clusters.itercases():
                legend = self._source_time_cluster(section, cluster, y, model,
                                                   ds, title, legend)

            # trend section
            section = report.add_section("Trend: p<=.1")
            self._source_bin_table(section, test_kind, res, 0.1)

            # not quite there section
            section = report.add_section("Anything: P<=.2")
            self._source_bin_table(section, test_kind, res, 0.2)
        elif parc and pmin in (None, 'tfce'):
            # add picture of parc
            section = report.add_section(parc)
            caption = "Labels in the %s parcellation." % parc
            self._source_parc_image(section, caption)

            # add subsections for individual labels
            title = "{tstart}-{tstop} p={p}{mark} {effect}"
            for label in y.source.parc.cells:
                section = report.add_section(label.capitalize())

                clusters_sig = res._clusters(0.05, True, source=label)
                clusters_trend = res._clusters(0.1, True, source=label)
                clusters_trend = clusters_trend.sub("p>0.05")
                clusters_all = res._clusters(0.2, True, source=label)
                clusters_all = clusters_all.sub("p>0.1")
                clusters = combine((clusters_sig, clusters_trend, clusters_all))
                clusters.sort('tstart')
                src_ = y.sub(source=label)
                legend = self._source_time_clusters(section, clusters, src_,
                                                    ds, model, include,
                                                    title, legend)
        elif parc is None:  # thresholded, whole brain
            if mask:
                title = "Whole Brain Masked by %s" % mask.capitalize()
                section = report.add_section(title)
                caption = "Mask: %s" % mask.capitalize()
                self._source_parc_image(section, caption)
            else:
                section = report.add_section("Whole Brain")

            self._source_bin_table(section, test_kind, res)

            clusters = res._clusters(include, maps=True)
            clusters.sort('tstart')
            title = "{tstart}-{tstop} {location} p={p}{mark} {effect}"
            legend = self._source_time_clusters(section, clusters, y, ds,
                                                model, include, title, legend)
        else:  # thresholded, parc
            # add picture of parc
            section = report.add_section(parc)
            caption = "Labels in the %s parcellation." % parc
            self._source_parc_image(section, caption)
            self._source_bin_table(section, test_kind, res)

            # add subsections for individual labels
            title = "{tstart}-{tstop} p={p}{mark} {effect}"
            for label in y.source.parc.cells:
                section = report.add_section(label.capitalize())

                clusters = res._clusters(None, True, source=label)
                src_ = y.sub(source=label)
                legend = self._source_time_clusters(section, clusters, src_,
                                                    ds, model, include,
                                                    title, legend)

        # report signature
        t1 = time.time()
        dt = t1 - t0
        info = ["Written by %s" % socket.gethostname(),
                "Finished on %s" % time.strftime("%c"),
                "Processing time: %s" % str(datetime.timedelta(seconds=round(dt))),
                "Eelbrain version %s" % __version__,
                "MNE-Python version %s" % mne.__version__]
        signature = ' &#8212 \n'.join(info)
        report.append(signature)

        report.save_html(dst)

    def _source_parc_image(self, section, caption):
        "Add picture of the current parcellation"
        brain = self.plot_annot(w=1000)
        image = plot.brain.image(brain, 'parc.png')
        section.add_image_figure(image, caption)

    def _source_bin_table(self, section, test_kind, res, pmin=None):
        caption = ("All clusters in time bins. Each plot shows all sources "
                   "that are part of a cluster at any time during the "
                   "relevant time bin. Only the general minimum duration and "
                   "source number criterion are applied.")

        if test_kind == 'anova':
            cdists = [(cdist, cdist.name.capitalize()) for cdist in res._cdist]
        else:
            cdists = [(res._cdist, None)]

        for cdist, effect in cdists:
            ndvar = cdist.masked_parameter_map(pmin)
            if not ndvar.any():
                if effect:
                    text = '%s: nothing\n' % effect
                else:
                    text = 'Nothing\n'
                section.add_paragraph(text)
                continue
            elif effect:
                caption_ = "%s: %s" % (effect, caption)
            else:
                caption_ = caption
            im = plot.brain.bin_table(ndvar, surf='inflated')
            section.add_image_figure(im, caption_)

    def _source_time_clusters(self, section, clusters, y, ds, model, include,
                              title, legend=None):
        """
        Parameters
        ----------
        ...
        legend : None | fmtxt.Image
            Legend (if shared with other figures).

        Returns
        -------
        legend : fmtxt.Image
            Legend to share with other figures.
        """
        # compute clusters
        if clusters.n_cases == 0:
            section.append("No clusters found.")
            return
        clusters = clusters.sub("p < 1")
        if clusters.n_cases == 0:
            section.append("No clusters with p < 1 found.")
            return
        caption = "Clusters with p < 1"
        table_ = clusters.as_table(midrule=True, count=True, caption=caption)
        section.append(table_)

        # plot individual clusters
        clusters = clusters.sub("p < %s" % include)
        for cluster in clusters.itercases():
            legend = self._source_time_cluster(section, cluster, y, model,
                                               ds, title, legend)

        return legend

    def _source_time_cluster(self, section, cluster, y, model, ds, title,
                             legend):
        # extract cluster
        c_tstart = cluster['tstart']
        c_tstop = cluster['tstop']
        c_extent = cluster['cluster']
        c_spatial = c_extent.sum('time')

        # section/title
        tstart = int(round(c_tstart * 1000))
        tstop = int(round(c_tstop * 1000))
        if title is not None:
            title_ = title.format(tstart=tstart, tstop=tstop,
                                  p='%.3f' % cluster['p'],
                                  effect=cluster.get('effect', ''),
                                  location=cluster.get('location', ''),
                                  mark=cluster['*']).strip()
            while '  ' in title_:
                title_ = title_.replace('  ', ' ')
            section = section.add_section(title_)

        # descriton
        if 'p_parc' in cluster:
            txt = section.add_paragraph()
            txt.append("Corrected across all ROIs: ")
            eq = FMText('p=', mat=True)
            eq.append(cluster['p_parc'], drop0=True, fmt='%s')
            txt.append(eq)
            txt.append('.')

        # add cluster image to report
        brain = plot.brain.cluster(c_spatial, surf='inflated')
        image = plot.brain.image(brain, 'cluster_spatial.png', close=True)
        caption_ = ["Cluster"]
        if 'effect' in cluster:
            caption_.extend(('effect of', cluster['effect']))
        caption_.append("%i - %i ms." % (tstart, tstop))
        caption = ' '.join(caption_)
        section.add_image_figure(image, caption)

        # cluster time course
        idx = c_extent.any('time')
        tc = y[idx].mean('source')
        caption = ("Cluster average time course")
        p = plot.UTSStat(tc, model, match='subject', ds=ds, legend=None, w=7,
                         colors='2group-ob')
        # mark original cluster
        for ax in p._axes:
            ax.axvspan(c_tstart, c_tstop, color='r', alpha=0.2, zorder=-2)
        # legend
        if legend is None:
            legend_p = p.plot_legend()
            legend = legend_p.image("Legend.svg")
        image = p.image('cluster_time_course.svg')
        p.close()
        # add to report
        figure = section.add_figure(caption)
        figure.append(image)
        figure.append(legend)

        # cluster value
        idx = c_extent > 0
        v = y.mean(idx)
        p = plot.uv.boxplot(v, model, 'subject', ds=ds)
        image = p.image('cluster_boxplot.png')
        p.close()
        caption = "Average value in cluster by condition."
        figure = section.add_figure(caption)
        figure.append(image)
        # pairwise test table
        res = _test.pairwise(v, model, 'subject', ds=ds)
        figure = section.add_figure(caption)
        figure.append(res)

        return legend

    def make_src(self, redo=False):
        """Make the source space

        Parameters
        ----------
        redo : bool
            Recreate the source space even if the corresponding file already
            exists.
        """
        dst = self.get('src-file')
        if not redo and os.path.exists(dst):
            return

        src = self.get('src')
        kind, param = src.split('-')

        subject = self.get('mrisubject')
        subjects_dir = self.get('mri-sdir')
        try:
            cfg = mne.coreg.read_mri_cfg(subject, subjects_dir)
            is_scaled = True
        except IOError:
            is_scaled = False

        if is_scaled:
            # make sure the source space exists for the original
            subject_from = cfg['subject_from']
            self.set(mrisubject=subject_from)
            self.make_src()
            self.set(mrisubject=subject)
            mne.scale_source_space(subject, src, subjects_dir=subjects_dir)
        else:
            if kind == 'vol':
                mri = self.get('mri-file')
                bem = self.get('bem-file', fmatch=True)
                mne.setup_volume_source_space(subject, dst, pos=float(param),
                                              mri=mri, bem=bem, mindist=0.,
                                              exclude=0.,
                                              subjects_dir=subjects_dir)
            else:
                spacing = kind + param
                src = mne.setup_source_space(subject, None, spacing=spacing,
                                             subjects_dir=subjects_dir)
                mne.add_source_space_distances(src)
                src.save(dst)

    def _make_test(self, y, ds, test, model, contrast, samples, pmin, tstart,
                   tstop, dist_dim, parc_dim):
        """just compute the test result"""
        # find cluster criteria
        kwargs = {'samples': samples, 'tstart': tstart, 'tstop': tstop,
                  'dist_dim': dist_dim, 'parc':parc_dim}
        if pmin == 'tfce':
            kwargs['tfce'] = True
        elif pmin is not None:
            kwargs['pmin'] = pmin
            if 'mintime' in self.cluster_criteria:
                kwargs['mintime'] = self.cluster_criteria['mintime']

            if y.has_dim('source') and 'minsource' in self.cluster_criteria:
                kwargs['minsource'] = self.cluster_criteria['minsource']
            elif y.has_dim('sensor') and 'minsensor' in self.cluster_criteria:
                kwargs['minsensor'] = self.cluster_criteria['minsensor']

        # perform test
        if test == 'ttest_rel':
            c1, tail, c0 = re.match(r"\s*([\w|]+)\s*([<=>])\s*([\w|]+)",
                                    contrast).groups()
            if '|' in c1:
                c1 = tuple(c1.split('|'))
                c0 = tuple(c0.split('|'))

            if tail == '=':
                tail = 0
            elif tail == '>':
                tail = 1
            elif tail == '<':
                tail = -1
            else:
                raise ValueError("%r in t-test contrast=%r" % (tail, contrast))

            res = testnd.ttest_rel(y, model, c1, c0, 'subject', ds=ds,
                                   tail=tail, **kwargs)
        elif test == 't_contrast_rel':
            res = testnd.t_contrast_rel(y, model, contrast, 'subject', ds=ds,
                                        **kwargs)
        elif test == 'anova':
            res = testnd.anova(y, contrast, match='subject', ds=ds, **kwargs)
        else:
            raise ValueError("test=%s" % repr(test))

        return res

    def makeplt_coreg(self, redo=False, **kwargs):
        """
        Save a coregistration plot

        """
        self.set(**kwargs)

        fname = self.get('plot-file', name='{subject}_{experiment}',
                         analysis='coreg', ext='png', mkdir=True)
        if not redo and os.path.exists(fname):
            return

        from mayavi import mlab
        p = self.plot_coreg()
        p.save_views(fname, overwrite=True)
        mlab.close()

    def next(self, field='subject'):
        """Change field to the next value

        Parameters
        ----------
        field :
        """
        current = self.get(field)
        values = self.get_field_values(field)
        if current in values:
            idx = values.index(current) + 1
            if idx == len(values):
                next_ = values[0]
                print("The last %s was reached; rewinding to "
                      "%r" % (field, next_))
            else:
                next_ = values[idx]
                print("%s: %r -> %r" % (field, current, next_))
        else:
            err = ("The current %s %r is not in %s "
                   "values." % (field, current, field))
            raise RuntimeError(err)

        self.set(**{field: next_})

    def plot_annot(self, surf='inflated', views=['lat', 'med'], hemi='split',
                   alpha=0.7, borders=False, w=600, parc=None):
        """Plot the annot file on which the current parcellation is based

        kwargs are for self.plot_brain().

        Parameters
        ----------
        parc : None | str
            Parcellation to plot. If None, use parc from the current state.
        """
        if parc is None:
            parc = self.get('parc')
        else:
            parc = self.get('parc', parc=parc)

        title = parc
        brain = self.plot_brain(surf, title, hemi, views, w, True)
        self.make_annot()
        brain.add_annotation(parc, borders, alpha)
        return brain

    def plot_brain(self, surf='inflated', title=None, hemi='lh', views=['lat'],
                   w=500, clear=True, common_brain=True):
        """Create a PuSyrfer Brain instance

        Parameters
        ----------
        w : int
            Total window width.
        clear : bool
            If self.brain exists, replace it with a new plot (if False,
            the existsing self.brain is returned).
        common_brain : bool
            If the current mrisubject is a scaled MRI, use the common_brain
            instead.
        """
        import surfer
        if clear:
            self.brain = None
        else:
            if self.brain is None:
                pass
            elif self.brain._figures == [[None, None], [None, None]]:
                self.brain = None
            else:
                return self.brain

        # find subject
        mri_sdir = self.get('mri-sdir')
        if common_brain and is_fake_mri(self.get('mri-dir')):
            mrisubject = self.get('common_brain')
            self.set(mrisubject=mrisubject, match=False)
        else:
            mrisubject = self.get('mrisubject')

        if title is not None:
            title = title.format(mrisubject=mrisubject)

        if hemi in ('lh', 'rh'):
            self.set(hemi=hemi)
            height = len(views) * w * 3 / 4.
        else:
            height = len(views) * w * 3 / 8.

        config_opts = dict(background=(1, 1, 1), foreground=(0, 0, 0),
                           width=w, height=height)
        brain = surfer.Brain(mrisubject, hemi, surf, True, title, config_opts,
                             None, mri_sdir, views)

        self.brain = brain
        return brain

    def plot_coreg(self, **kwargs):
        from ..data.plot.coreg import dev_mri
        self.set(**kwargs)
        raw = _mne_Raw(self.get('raw-file'))
        return dev_mri(raw)

    def plot_label(self, label, surf='inflated', w=600, clear=False):
        """Plot a label"""
        if isinstance(label, basestring):
            label = self.load_label(label)
        title = label.name

        brain = self.plot_brain(surf, title, 'split', ['lat', 'med'], w, clear)
        brain.add_label(label, alpha=0.75)

    def run_mne_analyze(self, subject=None, modal=False):
        subjects_dir = self.get('mri-sdir')
        subject = subject or self.get('mrisubject')
        fif_dir = self.get('raw-dir', subject=subject)
        subp.run_mne_analyze(fif_dir, subject=subject,
                             subjects_dir=subjects_dir, modal=modal)

    def run_mne_browse_raw(self, subject=None, modal=False):
        fif_dir = self.get('raw-dir', subject=subject)
        subp.run_mne_browse_raw(fif_dir, modal)

    def run_subp(self, cmd, workers=2):
        """
        Add a command to the processing queue.

        Commands should have a form that can be submitted to
        :func:`subprocess.call`.

        Parameters
        ----------
        cmd : list of str
            The command.
        workers : int
            The number of workers to create. For 0, the process is executed in
            interpreter's thread. If > 0, the parameter is only used the
            first time the method is called.

        Notes
        -----
        The task queue can be inspected in the :attr:`queue` attribute
        """
        if cmd is None:
            return

        if workers == 0:
            env = os.environ.copy()
            self.set_env(env)
            mne.utils.run_subprocess(cmd, env=env)
            return

        if not hasattr(self, 'queue'):
            self.queue = Queue()
            env = os.environ.copy()
            self.set_env(env)

            def worker():
                while True:
                    cmd = self.queue.get()
                    subprocess.call(cmd, env=env)
                    self.queue.task_done()

            for _ in xrange(workers):
                t = Thread(target=worker)
                t.daemon = True
                t.start()

        self.queue.put(cmd)

    def set(self, subject=None, **state):
        """
        Set variable values.

        Parameters
        ----------
        subject : str
            Set the `subject` value. The corresponding `mrisubject` is
            automatically set to the corresponding mri subject.
        add : bool
            If the template name does not exist, add a new key. If False
            (default), a non-existent key will raise a KeyError.
        other : str
            All other keywords can be used to set templates.
        """
        if subject is not None:
            state['subject'] = subject
            if 'mrisubject' not in state:
                state['mrisubject'] = self._mri_subjects[subject]

        FileTree.set(self, **state)

    def _eval_epoch(self, epoch):
        """Set the current epoch

        Parameters
        ----------
        epoch : str
            An epoch name for an epoch defined in self.epochs. Several epochs
            can be combined with '|' (but not all functions support linked
            epochs).
        """
        # fix epoch name
        epochs = epoch.split('|')
        epochs.sort()
        epoch = '|'.join(epochs)

        # find epoch dicts
        self._params['epochs'] = [self.epochs[name] for name in epochs]
        return epoch

    def _eval_group(self, group):
        if group not in self.get_field_values('group'):
            if group not in self.get_field_values('subject'):
                raise ValueError("No group or subject named %r" % group)
        return group

    def _eval_model(self, model):
        if '*' in model:
            raise ValueError("Specify model with '%' instead of '*'")

        factors = [v.strip() for v in model.split('%')]

        # find order value for each factor
        ordered_factors = {}
        unordered_factors = []
        for factor in sorted(factors):
            if factor in self._model_order:
                v = self._model_order.index(factor)
                ordered_factors[v] = factor
            else:
                unordered_factors.append(factor)

        # recompose
        model = [ordered_factors[v] for v in sorted(ordered_factors)]
        if unordered_factors:
            model.extend(unordered_factors)
        return '%'.join(model)

    def _post_set_rej(self, _, rej):
        rej_args = self.epoch_rejection[rej]
        self._params['rej'] = rej_args
        cov_rej = rej_args.get('cov-rej', rej)
        self._fields['cov-rej'] = cov_rej

    def set_env(self, env=os.environ):
        """
        Set environment variables

        for mne/freesurfer:

         - SUBJECTS_DIR
        """
        env['SUBJECTS_DIR'] = self.get('mri-sdir')

    def set_inv(self, ori='free', depth=0.8, reg=False, snr=2, method='dSPM',
                pick_normal=False):
        """Alternative method to set the ``inv`` state.
        """
        items = [ori, depth if depth else None, 'reg' if reg else None, snr,
                 method, 'pick_normal' if pick_normal else None]
        inv = '-'.join(map(str, filter(None, items)))
        self.set(inv=inv)

    def _set_inv_as_str(self, inv):
        """
        Notes
        -----
        inv composed of the following elements, delimited with '-':

         1) 'free' | 'fixed' | float
         2) depth weighting (optional)
         3) regularization 'reg' (optional)
         4) snr
         5) method
         6) pick_normal:  'pick_normal' (optional)
        """
        make_kw = {}
        apply_kw = {}
        args = inv.split('-')
        ori = args.pop(0)
        if ori == 'fixed':
            make_kw['fixed'] = True
            make_kw['loose'] = None
        elif ori == 'free':
            make_kw['loose'] = 1
        else:
            ori = float(ori)
            if not 0 <= ori <= 1:
                err = ('First value of inv (loose parameter) needs to be '
                       'in [0, 1]')
                raise ValueError(err)
            make_kw['loose'] = ori

        method = args.pop(-1)
        if method == 'pick_normal':
            apply_kw['pick_normal'] = True
            method = args.pop(-1)
        if method in ("MNE", "dSPM", "sLORETA"):
            apply_kw['method'] = method
        else:
            err = ('Setting inv with invalid method: %r' % method)
            raise ValueError(err)

        snr = float(args.pop(-1))
        apply_kw['lambda2'] = 1. / snr ** 2

        regularize_inv = False
        if args:
            arg = args.pop(-1)
            if arg == 'reg':
                regularize_inv = True
                if args:
                    depth = args.pop(-1)
                else:
                    depth = None
            else:
                depth = arg

            if depth is not None:
                make_kw['depth'] = float(depth)

        if args:
            raise ValueError("Too many parameters in inv %r" % inv)

        self._fields['inv'] = inv
        self._params['make_inv_kw'] = make_kw
        self._params['apply_inv_kw'] = apply_kw
        self._params['reg_inv'] = regularize_inv

    def set_mri_subject(self, subject, mri_subject=None):
        """
        Reassign a subject's MRI

        Parameters
        ----------
        subject : str
            The (MEG) subject name.
        mri_subject : None | str
            The corresponding MRI subject. None resets to the default
            (mri_subject = subject)
        """
        if mri_subject is None:
            del self._mri_subjects[subject]
        else:
            self._mri_subjects[subject] = mri_subject
        if subject == self.get('subject'):
            self._state['mrisubject'] = mri_subject

    def _eval_parc(self, parc):
        # Freesurfer parcellations
        if parc in ('aparc.a2005s', 'aparc.a2009s', 'aparc',
                    'PALS_B12_Brodmann', 'PALS_B12_Lobes',
                    'PALS_B12_OrbitoFrontal', 'PALS_B12_Visuotopic'):
            return parc
        else:
            raise ValueError("Unknown parcellation:  parc=%r" % parc)

    def set_root(self, root, find_subjects=False):
        if root is None:
            root = ''
            find_subjects = False
        else:
            root = os.path.expanduser(root)
        self._fields['root'] = root
        if not find_subjects:
            self._field_values['subject'] = []
            return

        subjects = set()
        sub_dir = self.get(self._subject_loc)
        if os.path.exists(sub_dir):
            for dirname in os.listdir(sub_dir):
                isdir = os.path.isdir(os.path.join(sub_dir, dirname))
                if isdir and self.subject_re.match(dirname):
                    subjects.add(dirname)
        else:
            err = ("Subjects directory not found: %r. Initialize with "
                   "root=None or find_subjects=False, or specifiy proper "
                   "directory in experiment._subject_loc." % sub_dir)
            raise IOError(err)

        subjects = sorted(subjects)
        self._field_values['subject'] = subjects

        mrisubjects = [self._mri_subjects[s] for s in subjects]
        common_brain = self.get('common_brain')
        if common_brain:
            mrisubjects.insert(0, common_brain)
        self._field_values['mrisubject'] = mrisubjects

        if len(subjects) == 0:
            print("Warning: no subjects found in %r" % sub_dir)
            return

        # on init, subject is not in fields
        subject = self._fields.get('subject', None)
        if subject not in subjects:
            subject = subjects[0]
        self.set(subject=subject, add=True)

    def _post_set_test(self, _, test):
        _, model, _ = self.tests[test]
        self.set(model=model)

    def _set_test_options(self, data, sns_baseline, src_baseline, pmin, tstart,
                          tstop):
        """Set templates for test paths with test parameters

        Can be set before or after the test template.

        Parameters
        ----------
        data : 'sns' | 'src'
            Whether the analysis is in sensor or source space.
        ...
        """
        # data kind (sensor or source space)
        if data == 'sns':
            analysis = '{sns-kind} {evoked-kind}'
        elif data == 'src':
            analysis = '{src-kind} {evoked-kind}'
        else:
            raise ValueError("data needs to be 'sns' or 'src'")

        # test properties
        items = []

        # baseline
        if src_baseline is None:
            if sns_baseline is None:
                items.append('nobl')
            elif sns_baseline != (None, 0):
                pass
        elif sns_baseline == (None, 0):
            items.append('snsbl')
        elif sns_baseline:
            items.append('snsbl=%s' % str(sns_baseline))

        if src_baseline == (None, 0):
            items.append('srcbl')
        elif src_baseline:
            items.append('srcbl=%s' % str(src_baseline))

        # pmin
        if pmin is not None:
            items.append(str(pmin))

        # time window
        if tstart is None:
            tstart_repr = ''
        else:
            tstart_repr = '%i' % round(tstart * 1000)

        if tstop is None:
            tstop_repr = ''
        else:
            tstop_repr = '%i' % round(tstop * 1000)

        if tstart_repr or tstop_repr:
            items.append('-'.join((tstart_repr, tstop_repr)))

        self.set(test_options=' '.join(items), analysis=analysis, add=True)

    def show_subjects(self, mri=True, mrisubject=False, caption=True,
                      asds=False):
        """Create a Dataset with subject information

        Parameters
        ----------
        mri : bool
            Add a column specifying whether the subject is using a scaled MRI
            or whether it has its own MRI.
        mrisubject : bool
            Add a column showing the MRI subject corresponding to each subject.
        caption : bool | str
            Caption for the table (For True, use the default "Subject in group
            {group}".
        asds : bool
            Return the table as Dataset instead of an FMTxt Table.
        """
        # caption
        if caption is True:
            caption = self.format("Subject in group {group}")

        subject_list = []
        mri_list = []
        mrisubject_list = []
        for subject in self.iter():
            subject_list.append(subject)
            mrisubject_ = self.get('mrisubject')
            mrisubject_list.append(mrisubject_)
            if mri:
                mri_dir = self.get('mri-dir')
                if not os.path.exists(mri_dir):
                    mri_list.append('*missing')
                elif is_fake_mri(mri_dir):
                    mri_sdir = self.get('mri-sdir')
                    info = mne.coreg.read_mri_cfg(mrisubject_, mri_sdir)
                    cell = "%s * %s" % (info['subject_from'],
                                        str(info['scale']))
                    mri_list.append(cell)
                else:
                    mri_list.append(mrisubject_)

        ds = Dataset(caption=caption)
        ds['subject'] = Factor(subject_list)
        if mri:
            ds['mri'] = Factor(mri_list)
        if mrisubject:
            ds['mrisubject'] = Factor(mrisubject_list)

        if asds:
            return ds
        else:
            return ds.as_table(midrule=True, count=True)

    def show_summary(self, templates=['raw-file'], missing='-', link=' > ',
                     count=True):
        """
        Compile a table about the existence of files by subject

        Parameters
        ----------
        templates : list of str
            The names of the path templates whose existence to list
        missing : str
            The value to display for missing files.
        link : str
            String between file names.
        count : bool
            Add a column with a number for each subject.
        """
        if not isinstance(templates, (list, tuple)):
            templates = [templates]

        results = {}
        experiments = set()
        mris = {}
        for _ in self.iter_temp('raw-key'):
            items = []
            sub = self.get('subject')
            exp = self.get('experiment')
            mri_subject = self.get('mrisubject')
            if sub not in mris:
                if mri_subject == sub:
                    mri_dir = self.get('mri-dir')
                    if not os.path.exists(mri_dir):
                        mris[sub] = 'missing'
                    elif is_fake_mri(mri_dir):
                        mris[sub] = 'fake'
                    else:
                        mris[sub] = 'own'
                else:
                    mris[sub] = mri_subject

            for temp in templates:
                path = self.get(temp, match=False)
                if '*' in path:
                    try:
                        _ = os.path.exists(self.get(temp, match=True))
                        items.append(temp)
                    except IOError:
                        items.append(missing)

                else:
                    if os.path.exists(path):
                        items.append(temp)
                    else:
                        items.append(missing)

            desc = link.join(items)
            results.setdefault(sub, {})[exp] = desc
            experiments.add(exp)

        table = fmtxt.Table('l' * (2 + len(experiments) + count))
        if count:
            table.cell()
        table.cells('Subject', 'MRI')
        experiments = list(experiments)
        table.cells(*experiments)
        table.midrule()

        for i, subject in enumerate(sorted(results)):
            if count:
                table.cell(i)
            table.cell(subject)
            table.cell(mris[subject])

            for exp in experiments:
                table.cell(results[subject].get(exp, '?'))

        return table

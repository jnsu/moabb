"""Physionet left hand vs right hand."""

from ..datasets.alex_mi import AlexMI
from .base import BaseContext
from mne import Epochs, pick_types, find_events
from mne.epochs import concatenate_epochs
from sklearn.model_selection import cross_val_score, KFold


class AlexMI2Class(BaseContext):

    def __init__(self, tmin=0, tmax=3):
        self.tmin = tmin
        self.tmax = tmax
        self.dataset = AlexMI()

    def _epochs(self, subjects, event_id):
        """epoch data"""
        raw = self.dataset.get_data(subjects=subjects)[0]

        raw.filter(7., 35., method='iir')

        events = find_events(raw, shortest_event=0, stim_channel='Stim',
                             verbose=False)

        picks = pick_types(raw.info, meg=False, eeg=True, stim=False,
                           eog=False, exclude='bads')
        epochs = Epochs(raw, events, event_id, self.tmin, self.tmax,
                        proj=False, picks=picks, baseline=None,
                        preload=True, verbose=False)
        return epochs

    def prepare_data(self, subjects):
        """Prepare data for classification."""
        event_id = dict(right_hand=1, feet=2)
        epochs = self._epochs(subjects, event_id)
        groups = None
        X = epochs.get_data()*1e6
        y = epochs.events[:, -1] - 1
        return X, y, groups

    def score(self, clf, X, y, groups, n_jobs=1):
        """get the score"""
        cv = KFold(5)
        auc = cross_val_score(clf, X, y, groups=groups, cv=cv,
                              scoring='roc_auc', n_jobs=n_jobs)
        return auc.mean()


class AlexMIMultiClass(AlexMI2Class):

    def __init__(self, tmin=0, tmax=3):
        self.tmin = tmin
        self.tmax = tmax
        self.dataset = AlexMI()

    def prepare_data(self, subjects):
        """Prepare data for classification."""
        event_id = dict(right_hand=1, feet=2, rest=3)
        epochs = self._epochs(subjects, event_id)
        groups = None
        X = epochs.get_data()*1e6
        y = epochs.events[:, -1]
        return X, y, groups

    def score(self, clf, X, y, groups, n_jobs=1):
        """get the score"""
        cv = KFold(5)
        auc = cross_val_score(clf, X, y, groups=groups, cv=cv,
                              scoring='accuracy', n_jobs=n_jobs)
        return auc.mean()
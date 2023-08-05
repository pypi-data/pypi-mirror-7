#-*- coding: utf-8 -*-
# Copyright (C) 2009-2013, Luis Pedro Coelho <luis@luispedro.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

'''
dict_store: an in-memory dictionary.

Does not support multiple processes!
'''

from six.moves import cPickle as pickle
from collections import defaultdict

from abc import ABCMeta, abstractmethod
from .base import base_store
import six

def _resultname(name):
    return six.b('result:')+name

def _lockname(name):
    return six.b('lock:')+name


class dict_store(base_store):
    def __init__(self, backend=None):
        '''
        dict_store(backend=None)

        Parameters
        ----------
        backend : str, optional
                  filename to load/save to
        '''
        if backend is not None:
            try:
                self.store = pickle.load(open(backend))
            except IOError:
                self.store = {}
        else:
            self.store = {}
        self.backend = backend
        self.counts = defaultdict(int)

    def dump(self, object, name):
        '''
        self.dump(object, name)
        '''
        self.store[_resultname(name)] = pickle.dumps(object)
        self.counts['dump:{0}'.format(name)] += 1


    def can_load(self, name):
        '''
        can = can_load(name)
        '''
        self.counts['exists:{0}'.format(name)] += 1
        return _resultname(name) in self.store


    def load(self, name):
        '''
        obj = load(name)

        Loads the objects. Equivalent to pickle.load(), but a bit smarter at times.
        '''
        self.counts['load:{0}'.format(name)] += 1
        return pickle.loads(self.store[_resultname(name)])


    def remove(self, name):
        '''
        was_removed = remove(name)

        Remove the entry associated with name.

        Returns whether any entry was actually removed.
        '''
        self.counts['del:{0}'.format(name)] += 1
        if self.can_load(name):
            self.counts['true-del:{0}'.format(name)] += 1
            del self.store[_resultname(name)]


    def cleanup(self, active):
        '''
        cleanup()

        Implement 'cleanup' command
        '''
        existing = set(self.store.keys())
        for act in active:
            try:
                existing.remove(_resultname(act))
            except KeyError:
                pass
        for superflous in existing:
            del self.store[superflous]

    def remove_locks(self):
        '''
        removed = store.remove_locks()

        Remove all locks

        Returns
        -------
        removed : int
            Number of locks removed
        '''
        removed = 0
                # we need a copy of the keys because we change it inside
                # iteration:
        for k in list(self.store.keys()):
            if k.startswith(six.b('lock:')):
                del self.store[k]
                removed += 1
        return removed

    def list(self):
        '''
        for key in store.list():
            ...

        Iterates over all the keys in the store
        '''
        for k in self.store.keys():
            if k.startswith(six.b('result:')):
                yield k[len('result:'):]

    def listlocks(self):
        '''
        for key in store.listlocks():
            ...

        Iterates over all the keys in the store
        '''
        for k in self.store.keys():
            if k.startswith(six.b('lock:')):
                yield k[len('lock:'):]


    def getlock(self, name):
        return dict_lock(self.store, self.counts, name)

    def close(self):
        if self.backend is not None:
            pickle.dump(self.store, file(self.backend, 'w'))
            self.backend = None
    __del__ = close


_NOT_LOCKED, _LOCKED = 0,1
class dict_lock(object):
    '''
    dict_lock

    Functions:
    ----------

    get()
        acquire the lock
    release()
        release the lock
    is_locked()
        check lock state
    '''

    def __init__(self, store, counts, name):
        self.name = _lockname(name)
        self.store = store
        self.counts = counts

    def get(self):
        '''
        lock.get()
        '''

        self.counts[six.b('lock:') + self.name] += 1

        previous = self.store.get(self.name, _NOT_LOCKED)
        self.store[self.name] = _LOCKED
        return previous == _NOT_LOCKED


    def release(self):
        '''
        lock.release()

        Removes lock
        '''
        self.counts[six.b('unlock:') + self.name] += 1
        del self.store[self.name]

    def is_locked(self):
        '''
        locked = lock.is_locked()
        '''
        self.counts[six.b('islock:') + self.name] += 1
        return (self.store.get(self.name, _NOT_LOCKED) == _LOCKED)

# vim: set ts=4 sts=4 sw=4 expandtab smartindent:

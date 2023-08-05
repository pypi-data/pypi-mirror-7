# -*- coding: utf-8 -*-
'''
keeping.py raet protocol keep classes
'''
# pylint: skip-file
# pylint: disable=W0611

# Import python libs
import os
from collections import deque

try:
    import simplejson as json
except ImportError:
    import json

# Import ioflo libs
from ioflo.base.odicting import odict
from ioflo.base import aiding

from .. import raeting
from .. import keeping

from ioflo.base.consoling import getConsole
console = getConsole()

class LaneKeep(keeping.Keep):
    '''
    RAET protocol yard on lane data persistence for a given yeard

    keep/
        stackname/
            local/
                estate.eid.ext
            remote/
                estate.eid.ext
                estate.eid.ext
    '''
    LocalFields = ['ha', 'name', 'main', 'mid']
    RemoteFields = ['ha', 'name', 'mid',  'rmid']

    def __init__(self, prefix='estate', **kwa):
        '''
        Setup LaneKeep instance
        '''
        super(LaneKeep, self).__init__(prefix=prefix, **kwa)

def clearAllLaneSafe(dirpath):
    '''
    Convenience function to clear all lane keep data in dirpath
    '''
    keep = LaneKeep(dirpath=dirpath)
    keep.clearLocalData()
    keep.clearAllRemoteData()

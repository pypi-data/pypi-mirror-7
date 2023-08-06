"""
Copyright 2009-2014 Marek Rudnicki

This file is part of cochlea.

cochlea is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

cochlea is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with cochlea.  If not, see <http://www.gnu.org/licenses/>.


Description
-----------
Synchronization of inner ear models.

"""
from __future__ import division, absolute_import, print_function

__author__ = "Marek Rudnicki"


import numpy as np
import pandas as pd

import thorns as th
import thorns.waves as wv


def calc_synchronization(
        model,
        cfs=None,
        dbspls=None,
        model_pars=None,
        map_backend='serial'
):
    """Calculate vector strength of an inner ear model.

    """
    if model_pars is None:
        model_pars = {}

    if cfs is None:
        cfs = np.logspace(np.log10(125), np.log10(16e3), 16)

    if dbspls is None:
        dbspls = [20, 40, 60]


    space = [
        {
            'model': model,
            'dbspl': dbspl,
            'cf': cf,
            'model_pars': model_pars,
        }
        for cf in cfs
        for dbspl in dbspls
    ]


    sis = th.util.map(
        _run_model,
        space,
        backend=map_backend,
    )

    sis = pd.DataFrame(list(sis))
    # sis = sis.set_index(['dbspl', 'cf'])

    return sis




def _run_model(model, dbspl, cf, model_pars):

    duration = 100e-3
    onset = 10e-3

    fs = model_pars.setdefault('fs', 100e3)
    model_pars.setdefault('anf_num', (250,250,250))
    model_pars.setdefault('seed', 0)

    sound = wv.ramped_tone(
        fs=fs,
        freq=cf,
        duration=duration,
        pad=0,
        dbspl=dbspl
    )

    anf = model(
        sound=sound,
        cf=cf,
        **model_pars
    )


    ### We want to make sure the the output CF is equal to the desired
    ### CF.
    real_cf, = np.unique(anf['cf'])
    assert real_cf == cf

    hsr = anf[anf['type']=='hsr']
    hsr = th.trim(hsr, onset, None)
    si_hsr = th.vector_strength(hsr, cf)

    msr = anf[anf['type']=='msr']
    msr = th.trim(msr, onset, None)
    si_msr = th.vector_strength(msr, cf)

    lsr = anf[anf['type']=='lsr']
    lsr = th.trim(lsr, onset, None)
    si_lsr = th.vector_strength(lsr, cf)

    # print(si_hsr)
    # th.plot_raster(anf)
    # th.show()

    sis = {
        'cf': cf,
        'dbspl': dbspl,
        'hsr': si_hsr,
        'msr': si_msr,
        'lsr': si_lsr
    }

    return sis

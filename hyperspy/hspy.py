# -*- coding: utf-8 -*-
# Copyright 2007-2011 The Hyperspy developers
#
# This file is part of  Hyperspy.
#
#  Hyperspy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
#  Hyperspy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with  Hyperspy.  If not, see <http://www.gnu.org/licenses/>.

import matplotlib.pyplot as plt
plt.rcParams['image.cmap'] = 'gray'

from hyperspy.Release import version as __version__
from hyperspy import components
from hyperspy import signals
from hyperspy.io import load
from hyperspy.defaults_parser import preferences
from hyperspy import utils
from hyperspy.misc.eels.elements import elements_db as elements_EELS
from hyperspy.misc.eds.elements import elements_db as elements_EDS

def get_configuration_directory_path():
    import hyperspy.misc.config_dir
    return hyperspy.misc.config_dir.config_path 


        
def create_model(signal, *args, **kwargs):
    """Create a model object
    
    Any extra argument is passes to the Model constructor.
    
    Parameters
    ----------    
    signal: A signal class
    
    If the signal is an EELS signal the following extra parameters
    are available:
    
    auto_background : boolean
        If True, and if spectrum is an EELS instance adds automatically 
        a powerlaw to the model and estimate the parameters by the 
        two-area method.
    auto_add_edges : boolean
        If True, and if spectrum is an EELS instance, it will 
        automatically add the ionization edges as defined in the 
        Spectrum instance. Adding a new element to the spectrum using
        the components.EELSSpectrum.add_elements method automatically
        add the corresponding ionisation edges to the model.
    ll : {None, EELSSpectrum}
        If an EELSSPectrum is provided, it will be assumed that it is
        a low-loss EELS spectrum, and it will be used to simulate the 
        effect of multiple scattering by convolving it with the EELS
        spectrum.
    GOS : {'hydrogenic', 'Hartree-Slater', None}
        The GOS to use when auto adding core-loss EELS edges.
        If None it will use the Hartree-Slater GOS if 
        they are available, otherwise it will use the hydrogenic GOS.
    
    Returns
    -------
    
    A Model class
    
    """
    
    from hyperspy._signals.eels import EELSSpectrum
    from hyperspy.models.eelsmodel import EELSModel
    from hyperspy.model import Model
    if isinstance(signal, EELSSpectrum):
        return EELSModel(signal, *args, **kwargs)
    else:
        return Model(signal, *args, **kwargs)
        
def create_model_from_dict(model_dict):
    from hyperspy._signals.eels import EELSSpectrum, Spectrum
    from hyperspy.models.eelsmodel import EELSModel
    from hyperspy.model import Model

    if model_dict['spectrum_type'] == "<class 'hyperspy.signals.eels.EELSSpectrum'>":
        spectrum = EELSSpectrum({'data':model_dict['spectrum']})
        spectrum.set_microscope_parameters(
                beam_energy=model_dict['spectrum_mapped_parameters']['TEM']['beam_energy'], 
                convergence_angle=model_dict['spectrum_mapped_parameters']['TEM']['convergence_angle'],
                collection_angle=model_dict['spectrum_mapped_parameters']['TEM']['EELS']['collection_angle'])
    else:
        spectrum = Spectrum({'data':model_dict['spectrum']})


    #Navigation axes
    s_nav_axes = spectrum.axes_manager.navigation_axes
    for s_nav_axis, navigation_axis in zip(s_nav_axes, model_dict['navigation_axes']):
        s_nav_axis.scale = navigation_axis['scale']
        s_nav_axis.offset = navigation_axis['offset']
        s_nav_axis.units = navigation_axis['units']

    #Signal axes
    s_sig_axes = spectrum.axes_manager.signal_axes
    for s_sig_axis, signal_axis in zip(s_sig_axes, model_dict['signal_axes']):
        s_sig_axis.scale = signal_axis['scale']
        s_sig_axis.offset = signal_axis['offset']
        s_sig_axis.units = signal_axis['units']

    if model_dict['model_type'] == "<class 'hyperspy.models.eelsmodel.EELSModel'>":
        model = EELSModel(spectrum)        
        model.pop()
    else:
        model = Model(spectrum)        

    for _component in model_dict['components']: 
        comp_object = getattr(components, _component['_id_name'])
        if _component['_id_name'] == 'EELSCLEdge':
            component = comp_object(
                    _component['element'] + '_' + _component['subshell'],
                    GOS=_component['GOS'])
            component.name = _component['name']
        else:
            component = comp_object()
            component.name = _component['name']
        model.append(component)
    return(model)


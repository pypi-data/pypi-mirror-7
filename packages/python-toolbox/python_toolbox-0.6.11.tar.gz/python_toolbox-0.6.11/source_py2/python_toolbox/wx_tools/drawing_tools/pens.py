# Copyright 2009-2014 Ram Rachum.
# This program is distributed under the MIT license.

'''
This module defines the `` class.

See its documentation for more information.
'''

import wx

from python_toolbox import caching


is_mac = (wx.Platform == '__WXMAC__')
is_gtk = (wx.Platform == '__WXGTK__')
is_win = (wx.Platform == '__WXMSW__')


@caching.cache(max_size=100)
def get_focus_pen(color='black', width=1, dashes=[1, 4]):
    ''' '''
    if isinstance(color, basestring):
        color = wx.NamedColour(color)
        
    # todo: do `if is_mac`, also gtk maybe
    
    pen = wx.Pen(color, width, wx.USER_DASH)
    pen.SetDashes(dashes)
    return pen
    
    
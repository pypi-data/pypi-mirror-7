from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy
from ggplot.components import aes
from pandas import DataFrame

__all__ = ['geom']
__all__ = [str(u) for u in __all__]

class geom(object):
    """Base class of all Geoms"""
    DEFAULT_AES = dict()
    REQUIRED_AES = set()
    DEFAULT_PARAMS = dict()

    data = None
    aes = None
    manual_aes = None
    params = None

    # Some ggplot aesthetics are named different from the parameters of
    # the matplotlib function that will be used to plot.
    # This dictionary, of the form {ggplot-aes-name: matplotlib-aes-name},
    # connects the two.
    #
    # geoms should fill it out so that the plot
    # information they receive is properly named.
    # See: geom_point
    _aes_renames = dict()

    # A matplotlib plot function may require that an aethestic have a
    # single unique value. e.g. linestyle='dashed' and not
    # linestyle=['dashed', 'dotted', ...].
    # A single call to such a function can only plot lines with the
    # same linestyle. However, if the plot we want has more than one
    # line with different linestyles, we need to group the lines with
    # the same linestyle and plot them as one unit.
    #
    # geoms should fill out this set with such aesthetics so that the
    # plot information they receive can be plotted in a single call.
    # Use names as expected by matplotlib
    # See: geom_point
    _groups = set()

    def __init__(self, *args, **kwargs):
        self.valid_aes = set(self.DEFAULT_AES) ^ self.REQUIRED_AES
        self.aes, self.data = self._find_aes_and_data(args, kwargs)

        if 'colour' in kwargs:
            kwargs['color'] = kwargs.pop('colour')

        self.params = deepcopy(self.DEFAULT_PARAMS)
        self.manual_aes = {}
        for k, v in kwargs.items():
            if k in self.aes:
                raise Exception('Aesthetic, %s, specified twice' % k)
            elif k in self.valid_aes:
                self.manual_aes[k] = v
            elif k in self.DEFAULT_PARAMS:
                self.params[k] = v
            else:
                raise Exception('Cannot recognize argument: %s' % k)

        self._cache = {}
        # When putting together the plot information for the geoms,
        # we need the aethetics names to be matplotlib compatible.
        # These are created and stored in self._cache and so would
        # go stale if users or geoms change geom.manual_aes
        self._create_aes_with_mpl_names()

    def plot_layer(self, data, ax):
        self._verify_aesthetics(data)

        # should happen in the layer
        data = data[list(set(data.columns) & set(self.valid_aes))]

        # aesthetic precedence
        # geom.manual_aes > geom.aes > ggplot.aes (part of data)
        # NOTE: currently geom.aes is not handled. This may be
        # a bad place to do it -- may mess up faceting or just
        # inefficient. Probably in ggplot or layer.

        # Any aesthetic to be overridden by the manual aesthetics
        # should not affect the grouping of the data
        _overrided_aes = set(data.columns) & set(self.manual_aes)
        for ae in _overrided_aes:
            data.pop(ae)
        data = data.rename(columns=self._aes_renames)
        groups = self._groups & set(data.columns)

        # Create plot information that observes the aesthetic precedence
        # (grouped data + manual aesthetics) overwrite the default aesthetics
        for _data in self._get_grouped_data(data, groups):
            _data.update(self._cache['manual_aes_mpl'])
            pinfo = deepcopy(self._cache['default_aes_mpl'])
            pinfo.update(_data)
            self._plot_unit(pinfo, ax)

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.geoms.append(self)
        return gg

    def _verify_aesthetics(self, data):
        """
        Check if all the required aesthetics have been specified

        Raise an Exception if an aesthetic is missing
        """
        missing_aes = self.REQUIRED_AES - set(data.columns)
        if missing_aes:
            msg = '{} requires the following missing aesthetics: {}'
            raise Exception(msg.format(
                self.__class__.__name__, ', '.join(missing_aes)))

    def _find_aes_and_data(self, args, kwargs):
        """
        Identify the aes and data objects.

        Return a dictionary of the aes mappings and
        the data object.

        - args is a list
        - kwargs is a dictionary

        Note: This is a helper function for self.__init__
        It modifies the kwargs
        """
        passed_aes = {}
        data = None
        aes_err = 'Found more than one aes argument. Expecting zero or one'

        for arg in args:
            if isinstance(arg, aes) and passed_aes:
                raise Exception(aes_err)
            if isinstance(arg, aes):
                passed_aes = arg
            elif isinstance(arg, DataFrame):
                data = arg
            else:
                raise Exception('Unknown argument of type "{0}".'.format(type(arg)))

        if 'mapping' in kwargs and passed_aes:
            raise Exception(aes_err)
        elif not passed_aes and 'mapping' in kwargs:
            passed_aes = kwargs.pop('mapping')

        if data is None and 'data' in kwargs:
            data = kwargs.pop('data')

        _aes = {}
        for k, v in passed_aes.items():
            if k in self.valid_aes:
               _aes[k] = v
        return _aes, data

    def _create_aes_with_mpl_names(self):
        """
        Create copies of the manual and default aesthetics
        with matplotlib compatitble names.

        Uses self._aes_renames, and the results are stored
        in:
            self._cache['manual_aes_mpl']
            self._cache['default_aes_mpl']
        """
        def _rename_fn(aes_dict):
            # to prevent overwrites
            _d = {}
            for old, new in self._aes_renames.items():
                if old in aes_dict:
                    _d[new] = aes_dict.pop(old)
            aes_dict.update(_d)

        self._cache['manual_aes_mpl'] = deepcopy(self.manual_aes)
        self._cache['default_aes_mpl'] = deepcopy(self.DEFAULT_AES)
        _rename_fn(self._cache['manual_aes_mpl'])
        _rename_fn(self._cache['default_aes_mpl'])

    def _get_grouped_data(self, data, groups):
        """
        Split the data into groups.

        Parameters
        ----------
        data   : dataframe
            The data to be split into groups
        groups : set
            A set of column names in the data and by
            which the grouping will happen

        Returns
        -------
        out : list
            A list of dicts. Each dict represents a unique
            grouping. The dicts are of the form
            {'column-name': list-of-values | value}

        Note
        ----
        This is a helper function for self._plot_layer
        """
        out = []
        if groups:
            for name, _data in data.groupby(list(groups)):
                _data = _data.to_dict('list')
                for ae in groups:
                    _data[ae] = _data[ae][0]
                out.append(_data)
        else:
            _data = data.to_dict('list')
            out.append(_data)
        return out

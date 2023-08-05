
__all__ = ['SubModel']

from coopr.pyomo.base.component import Component
from coopr.pyomo.base.block import SimpleBlock

# Do we need to have SimpleSubModel and IndexedSubModel classes?


class SubModel(SimpleBlock):

    def __init__(self, *args, **kwargs):
        """Constructor"""
        #
        # Collect kwargs for SubModel
        #
        _rule = kwargs.pop('rule', None )
        _fixed = kwargs.pop('fixed', None )
        _var = kwargs.pop('var', None )
        _map = kwargs.pop('map', None )
        #
        # Initialize the SimpleBlock
        #
        SimpleBlock.__init__(self, *args, **kwargs)
        #
        # Initialize from kwargs
        #
        self._rule = _rule
        if isinstance(_fixed, Component):
            self._fixed = [_fixed]
        else:
            self._fixed = _fixed
        if isinstance(_var, Component):
            self._var = [_var]
        else:
            self._var = _var
        self._map = _map


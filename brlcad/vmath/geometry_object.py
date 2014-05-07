"""
Helper classes shared by the geometry code.
"""
from brlcad.exceptions import BRLCADException
import numpy as np


class ParameterStatus(object):
    """
    This is an enumerated type used to mark fields of geometry classes
    with their provenience/calculation status.
    currently calculating, to avoid infinite recursion as we
    calculate arc elements which depend on each other but can
    be calculated from alternative elements.
    """
    def __init__(self, status):
        self.status = status

    def __repr__(self):
        return self.status

# Initialized: marks parameters which were initialized in the __init__ call
Initialized = ParameterStatus("Initialized")
ParameterStatus.Initialized = Initialized
# Calculating: marks parameters which are currently calculating, used to
#              avoid infinite recursion when geometry elements depend on
#              each other and can be calculated from alternative inputs
Calculating = ParameterStatus("Calculating")
ParameterStatus.Calculating = Calculating
# Calculated:  marks parameters which were calculated from other elements
Calculated = ParameterStatus("Calculated")
ParameterStatus.Calculated = Calculated

ParameterStatus.states = {Initialized, Calculating, Calculated}


def create_property(name, context, param_wrapper, calc_func=None, doc=None):
    """
    Creates calculated properties of a geometry class.
    The returned property uses <calc_func> to calculate
    the value of the property. The value is only calculated once
    and cached for further access.
    This call also populates the calc_function_map and param_wrappers
    maps which allow programmatic access to the parameter handling.
    If calc_func is not provided, it will be looked up in the context
    as "_calculate_<name>", and if found, that one will be used.
    If there's no function with that name, the property will not be
    calculated, but must be initialized, making it a mandatory
    parameter of the geometry object.
    """
    param_wrappers = context.get("param_wrappers")
    calc_function_map = context.get("calc_function_map")
    if param_wrappers is None or calc_function_map is None:
        raise BRLCADException(
            "GeometryObject subclasses must define the class properties: "
            "param_wrappers, calc_function_map"
        )
    if name in calc_function_map or name in param_wrappers:
        raise BRLCADException("Programmer error: duplicate parameter name {}".format(name))
    param_wrappers[name] = param_wrapper
    if not calc_func:
        calc_func = context.get("_calculate_{}".format(name))
    if calc_func:
        if calc_func in calc_function_map.values():
            raise BRLCADException(
                "Programmer error: function {} is set up for parameter {}".format(calc_func, name)
            )
        calc_function_map[name] = calc_func
        if not doc:
            doc = getattr(calc_func, "__doc__", None)

    def getter(self):
        if self._param_status.get(name) is Calculating:
            return None
        value = self._props.get(name)
        if value is None:
            self._param_status[name] = Calculating
            if calc_func:
                value = calc_func(self)
            else:
                raise ValueError(
                    "Mandatory parameter <{}> missing for: {}".format(name, self)
                )
            if value is None:
                raise ValueError(
                    "Not enough information to calculate <{}> for: {}".format(name, self)
                )
            self._props[name] = value
            self._param_status[name] = Calculated
        return value

    return property(fget=getter, doc=doc)


class GeometryObject(object):
    """
    Base class for geometry classes.
    Subclasses should define class level members:

    calc_function_map = dict()
    param_wrappers = dict()

    Then in the subclass body you can define properties
    and their calculation functions like this:

    def _calculate_<prop_name>(self):
        # calculate the property from other elements;
        # return the calculated value if possible, otherwise return None,
        # meaning there is not enough information to do so:
        return None

    <prop_name> = GeometryObject.create_property(
        # this is unfortunately needed as it can't be discovered by reflection:
        name="<prop_name>"
        # needed to access the maps of wrappers and calculation functions:
        context=locals(),
        # needed to set up parameter wrappers:
        param_wrapper=Vector.wrap,
        # optional, only needed if you can't keep this name pattern:
        calc_func=_calculate_<prop_name>,
        # optional, if missing the doc string of calc_func will be used:
        doc="Doc string of the property",
    )

    The created property will call the calculation function, and cache it's
    value for further access. It will also make sure the calculation is not
    causing infinite recursion, by setting the parameter status to
    "Calculating" during calculation and skip re-entering calculation as
    long as it is in this state.

    If the verify() call should check a specific set of canonical
    parameters for consistency, the canonical_init_params class property
    should be defined and initialized in subclasses:

    canonical_init_params = { "param1", "param2", ... }

    """

    # Structures to be overridden by subclasses:

    calc_function_map = None
    """
    Maps property names to calculation functions used to
    calculate the property from other geometry elements.
    Should be overridden/initialized by subclasses !
    This will be populated when creating properties with
    the create_wrapper call.
    """

    param_wrappers = None
    """
    Maps parameter names to wrapper functions used to
    parse raw input into the right parameter type.
    Should be overridden/initialized by subclasses !
    This will be populated when creating properties with
    the create_wrapper call, but can contain here parameters
    which are not exposed as properties too.
    """

    canonical_init_params = None
    """
    The canonical set of init parameters.
    Should be overridden/initialized by subclasses !
    Will be used by verify() to check if the provided
    parameters can be resolved to this canonical set.
    """

    # end of structures to be overridden

    def __init__(self, verify=False, **kwargs):
        self._props = dict()
        self._param_status = dict()
        self._wrap_params(kwargs)
        # verify parameter consistency
        if verify:
            self.verify()

    @classmethod
    def wrap_param(cls, param_name, value):
        """
        Wraps/parses the given parameter with/to the expected type.
        For example a Vector parameter will be wrapped using:
        Vector.wrap(value),
        a float parameter will be wrapped using:
        float(value)

        This approach allows passing in parameters which can be of
        any type accepted by those wrappers, e.g. a string of comma
        separated numbers is a valid value for a Vector parameter.
        """
        wrapper = cls.param_wrappers.get(param_name)
        if value is not None:
            value = wrapper(value)
        return value

    def _wrap_params(self, params):
        unknown_params = set(params.keys()).difference(self.param_wrappers.keys())
        if unknown_params:
            raise ValueError(
                "Unknown {} parameters: {}".format(
                    self.__class__.__name__, unknown_params
                )
            )
        for param_name, value in params.items():
            self._props[param_name] = self.wrap_param(param_name, value)
            self._param_status[param_name] = Initialized

    def verify(self):
        verified_props = [getattr(self, param_name, None) for param_name in self.canonical_init_params]
        if verified_props.count(None) > 0:
            raise ValueError(
                "Parameter set is not complete to fully define the geometry object: {}".format(self)
            )
        crt_props = dict(self._props)
        for param_name, crt_value in crt_props.items():
            calc_func = self.calc_function_map.get(param_name)
            if calc_func is not None:
                calculated_value = calc_func(self)
                if not np.allclose(crt_value, calculated_value):
                    raise ValueError(
                        "Verify failed for {}, expected: {} but got {}".format(
                            param_name, calculated_value, crt_value
                        )
                    )

    def is_set(self, param_name):
        if self._param_status.get(param_name) is Calculating:
            return False
        return self._props.get(param_name) is not None

    def calculate(self, property_name):
        calc_func = self.calc_function_map.get(property_name)
        if calc_func is None:
            return None
        return calc_func()

    def __repr__(self):
        return "{}(**{})".format(self.__class__.__name__, self._props)

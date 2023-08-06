# -*- coding: utf-8 -*-
from __future__ import division
from collections import Counter
import numpy as np
import hashlib
import sympy

from .. import six
from . import operations


class FeatureMeta(type):

    """MetaClass for Features

    For each feature define its scala during class creation.
    Add classmethod to convert value according to feature type.
    """
    __store__ = dict()

    def __new__(cls, name, bases, attrs):
        scale = name[len("Feature"):].lower()
        class_ = super(FeatureMeta, cls).__new__(cls, name, bases, attrs)
        setattr(class_, "scale", scale)
        setattr(class_, "convert", classmethod(
            lambda cls, x: Feature.FEATURE_TYPE_MAP.get(
                scale, (Feature.DEFAULT_TYPE,))[0](x)))

        cls.__store__[scale] = class_
        return class_


@six.add_metaclass(FeatureMeta)
class Feature(object):
    """Feture representation
    Converts feature value according to one of the following types:

    nom:  nominal value represented by string
    lin:  float number in linear scale
    rank: integer number, arithmetic operations are not supported
    bin:  binary format, true/false or 1/0

    Feature does not know about data, does not have any mean or deviation.
    """

    # Map type to type (python_type, max_value_lenght)
    FEATURE_TYPE_MAP = {
        "nom": (str, 16),
        "lin": (float, ),
        "rank": (float, ),
        "bin": (bool, ),
    }
    DEFAULT_SCALE = "lin"
    DEFAULT_TYPE = FEATURE_TYPE_MAP[DEFAULT_SCALE][0]

    def __init__(self, title=None, formula=None, scale=None):
        """Init Feature class

        scale:      feature scale, defines result type and operations allowed
                    for feature.
        formula:    sympy.core.Expr - symbolic expression with feature formula
                    for atom features it is basic itemgetter and transform to
                    type, according to feature class. For not atom features
                    formula consist of expression with atom features as
                    variables.
        convert_atoms {"feature_title": feature} allows complicated feature
                    calculation.

        .. versionchanged:: 0.2.0
           If title is not provided, it is assumed that feature is not atomic
           and it was generated based on other features. To be able to print it
           need to generate name. Use hash for name of new feature. There is no
           way to generate it correctly with ability to use title as attribute.

        """
        assert title is not None or formula is not None
        self.formula = formula if formula is not None else sympy.Symbol(title)
        self.scale = self.scale or scale or self.DEFAULT_SCALE

        if title is not None:
            self.title = title
        else:
            self.title = 'f' + hashlib.md5(
                str(self.formula).encode('utf8')).hexdigest()

        self._atoms_map = {self.title: self}

    @property
    def proxy(self):
        """ Get proxy feature instance based on scale.

        .. versionchanged:: 0.2.0
           provide title to feature constructor

        """
        obj = self.__class__.__store__[self.scale](
            title=self.title, formula=self.formula)
        obj._atoms_map = self._atoms_map  # FIXME: add test to that line
        return obj

    @classmethod
    def getstat(cls, list_):
        return dict(Counter(list_))

    def __str__(self):
        return str(self.formula)

    def __repr__(self):
        return "{0}: {1} (scale={2})".format(self.__class__, self, self.scale)

    def __lt__(self, other):
        """Helper method to order features"""
        return (self.scale, self.title) < (other.scale, other.title)

    def __eq__(self, other):
        return not(self < other or other < self)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.scale, self.title))

    def __call__(self, objects):
        """ Call feature with objects.

        .. versionchanged:: 0.2.0
           Return list or generator for Data object instead of Data.

        .. versionchanged:: 0.2.1
           Handle case if feature is Atom, but not Symbol. Example: constant
           feature.

        """
        from ..data import Data

        if isinstance(objects, Data):
            values = (self(o) for o in objects.objects)
            if not objects.is_big:
                values = list(values)
            return values
        else:
            if self.formula.is_Atom:
                if self.formula.is_Symbol:
                    result = getattr(objects, self.title)
                else:
                    # Formula is constant
                    result = self.convert(self.formula)
            else:
                subs = {
                    str(arg): self._atoms_map[str(arg)](objects)
                    for arg in self.formula.atoms()
                    if isinstance(arg, sympy.Symbol)}
                result = self.formula.subs(subs)

            return self.convert(result)


class FeatureBin(Feature):
    def __and__(self, other):
        return operations.And(self, other)

    def __rand__(self, other):
        return self.__and__(other)

    def __xor__(self, other):
        return operations.Xor(self, other)

    def __rxor__(self, other):
        return self.__xor__(other)

    def __or__(self, other):
        return operations.Or(self, other)

    def __ror__(self, other):
        return self.__or__(other)


class FeatureLin(Feature):
    def getstat(cls, list_):
        return {
            "mean": np.array(list_).mean(),
            "std": np.array(list_).std(),
            "var": np.array(list_).var(),
            "min": np.array(list_).min(),
            "max": np.array(list_).max(),
        }

    def __neg__(self):
        f = FeatureLin(formula=-self.formula)
        f._atoms_map.update(self._atoms_map)
        return f

    def __add__(self, other):
        return operations.Add(self, other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return operations.Add(self, -other)

    def __rsub__(self, other):
        return -self.__sub__(other)

    def __mul__(self, other):
        return operations.Mul(self, other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __div__(self, other):
        factor = operations.Inverse(other) \
            if isinstance(other, Feature) \
            else 1.0 / other
        return operations.Mul(self, factor)

    def __rdiv__(self, other):
        return other * operations.Inverse(self)

    __rtruediv__ = __rdiv__
    __truediv__ = __div__

    def __pow__(self, other, modulo=None):
        return operations.Pow(self, other)

    def __rpow__(self, other, modulo=None):
        f = FeatureLin(formula=other ** self.formula)
        f._atoms_map.update(self._atoms_map)
        return f


class FeatureNom(Feature):
    pass


class FeatureRank(Feature):
    pass

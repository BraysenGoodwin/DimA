"""
DimA - Dimensional Analysis for Python

Created By: Braysen Goodwin

License: Open source

"""


'''
todo dictionary: { r:[unit, unit, ..] #remove units, a:[unit,unit,unt,...]#add units}

paths are given in unit -> targetunit with format [[conversion, power],[conversion,power], ..] and must be ran in order
   such that the each conversion is called as conversion.convert(value, power) where value is given by the user

uses one unit conversions

for example, this would be an appropriate conversion:
    Conversion("foot", "inch", lambda value, power: value * 12 ** power)

while this would not be an appropriate conversion:
    Conversion("foot pound", "inch pound", lambda value, power: value * 12 ** power)

    this is inappropriate becuase a "foot" can be converted into an "inch" using a "foot" -> "inch" conversion
        which would take care of any "foot" -> "inch" conversion regardless of the other units or powers

'''

import numbers
import math
from time import time

class DimA:

    conversions = []
    paths = []
    break_multiplier = 1
    break_additive = 5
    max_conversions = 12
    _initialized = False

    elapse=None

    def convert(value, unit, target_unit, using=[], **kwords):
        """
            DimA.convert(value, unit, target_unit, using=[], **{break_size: len(todo) * DimA.break_multiplier + DimA.break_additive, max_conversions: DimA.max_conversions, alg:DimA.algorithums["default"]})

            return(s) value
            #value which is converted from unit to target_unit

            raise(s) PathError
            #if no path of conversions can be found to take the unit to the target_unit
            #if this PathError is being raised when a path is to be found try changing the (or using) the break_size keyword argument or increasing
            #the the DimA.break_multiplier or DimA.break_additive

            Argument discriptions:
            unit -> a UnitList object or parsabelable String ("unit^power unit2^power2 ...") which is the starting unit for the path
            target_unit -> a UnitList which is the ending unit for the path
            using -> a list object which holds Conversion objects which may be used in creating the path
            break_size -> a keyword argument which describes how long the todo list can get before the trial process on that branch breaks
                This ALWAYS has to be at least the length of the unit and targetUnit + 1 (AKA: 'len(unit) + len(target_unit) + 1'), but will have to
                increase if the path must go through a conversion which increases the amount of units to look through (ex: "newton" -> "foot pound")
            max_conversions -> a keyword argument which will limit the amount of conversions inside a path before discarding it as a candidate

        """
        ul = DimA.normalizeToUnitList(unit)
        tl = DimA.normalizeToUnitList(target_unit)
        if unit == target_unit:
            return value
        DimA.tests = 0
        if kwords.get("max_conversions", DimA.max_conversions) < 1:
            raise ValueError("max_conversions can not be less than 1")
        if DimA.break_multiplier <= 0 and DimA.break_additive <= 0 and not kwords.get("break_size", False):
            raise ValueError("DimA.break_multiplier and DimA.break_additive can not be equal to or less than 0 while keyword argument 'break_size' is not given")
        t = time()
        path =DimA.algorithums[kwords.get("alg","default")](ul, tl, using, **kwords)
        DimA.elapse = time() - t
        #print(path)
        #print(DimA.tests)
        value = path.convert(value)
        #print("value: ",value)
        return value

    def get_path(unit, target_unit, using=[], **kwords):
        """
            DimA.get_path(unit, target_unit, using, **{break_size: len(todo) * DimA.break_multiplier + DimA.break_additive, max_conversions: DimA.max_conversions})

            return(s) Path
            #Path object loaded with conversions to take any value from unit to target_unit

            raise(s) PathError
            #if no path of conversions can be found to take the unit to the target_unit
            #if this PathError is being raised when a path is to be found try changing the (or using) the break_size keyword argument or increasing
            #the the DimA.break_multiplier

            Argument discriptions:
            unit -> a UnitList object which is the starting unit for the path
            target_unit -> a UnitList which is the ending unit for the path
            using -> a list object which holds Conversion objects which may be used in creating the path
            break_size -> a keyword argument which describes how long the todo list can get before the trial process on that branch breaks
                This ALWAYS has to be at least the length of the unit and targetUnit + 1 (AKA: 'len(unit) + len(target_unit) + 1'), but will have to
                increase if the path must go through a conversion which increases the amount of units to look through (ex: "newton" -> "foot pound")
            max_conversions -> a keyword argument which will limit the amount of conversions inside a path before discarding it as a candidate

        """
        return DimA._get_path(unit, target_unit, using, **kwords)

    def get_level_path(unit, target_unit, using=[], **kwords):
        return DimA._get_level_loop(unit, target_unit, using, **kwords)

    def _get_level_loop(unit, target_unit, using, level=1, **kwords):
        todo = unit.getTodoList(target_unit)
        for path in DimA.paths:
            if DimA.todo__eq__(todo, path.todo):
                return path
        blacklist = []
        path = []
        max_conversions = kwords.get("max_conversions", DimA.max_conversions)
        #print(max_conversions)
        break_size = kwords.get("break_size", len(todo) * DimA.break_multiplier + DimA.break_additive)
        #print(todo)
        level = 1
        lis = DimA._level_loop_alg(todo, target_unit, [], break_size, using, max_conversions)
        if len(lis) == 0:
            raise PathError("".join(("No path can be found from unit(s): ",str(unit)," to target unit(s): ", str(target_unit), " due to either: 'no conversions being used' or 'unit(s) exists in no conversion'")))
        if type(lis[-1]).__name__ == 'bool':
            path = lis[:-1]
            if kwords.get("auto_add", True):
                return Path(path, todo, auto_add=True)
            return Path(path, todo, auto_add=False)
        tup = 'tuple'
        bol = 'bool'
        while (level <= max_conversions):
            clip = []
            #print(len(lis))
            for args in lis:
                r = DimA._level_loop_alg(*args)
                if len(r) == 0:
                    continue
                if type(r[-1]).__name__ == bol:
                    path = r[:-1]
                    break
                clip.extend(r)
            if path:
                break
            lis = clip
            level += 1
        #print(len(DimA.conversions + using))
        #print(r)
        #print(path)
        if not path:
            raise PathError("".join(("No path can be found from unit(s): ",str(unit)," to target unit(s): ", str(target_unit), " with a break_size of: ", str(break_size), " and a max_conversion of: ", str(max_conversions))))
        #print(r)
        if kwords.get("auto_add", True):
            return Path(path, todo, auto_add=True)
        else:
            return Path(path, todo, auto_add=False)

    def _level_loop_alg(unit_todo, target_unit, path, break_size, using=[], max_conversions=math.inf, unitBlackList=[]):
        """
        DimA._path_loop_alg(unit_todo, target_unit, path, break_size, using=[], blacklist=[], level=1, max_conversions=math.inf)

        return(s) path or False
        #path is a list of conversion tupple returned as fallows [(conversion1, multiplier), (conversion2, multiplier), ...]
        #False is returned if the path does end with a completion of the todo list (AKA: len(todo) == 0)

        raise(s)
        #No errors are raised by this function

        Argument discriptions:
        unit_todo -> the todo list (list of units) whicch is checked for path completion
        target_unit -> a UnitList which states the finishing units of the path (never used)
        path -> a list of conversions which are stored for the trail, if a conversion completes the todo list then the path is returned. Interpret as fallows: [(conversion1, multiplier), (conversion2, multiplier), ...]
        break_size -> how long the todo list can get before returning False, leverage this to cut down the length of time needed to find a path (AKA: if len(todo) >= break_size: return False)
        using -> any conversions which should be considered in path finding which are not in the list DimA.conversions
        blacklist -> any conversions which should not be considered with the path finding, any path already considered will be put on this list
        level -> at what level of path finding the iterpreter is at
        max_conversions -> the max number of conversions that can be in a path before the path is discarded as a candidate
        """
        lis = []
        for conversion in DimA.conversions + using:
            DimA.tests += 1
            if conversion in path or not DimA.todo__effects__(unit_todo, conversion.todo):
                continue
            if DimA.todo__contain__(unitBlackList, conversion.todo):
                #return False
                continue
            toodo = [*DimA.todo__sub__t(unit_todo, conversion.todo)]
            toodo[0] = DimA.todo__compact__(toodo[0])
            if len(toodo[0]) >= break_size:
                continue
            path.append((conversion, toodo[1]))
            if len(toodo[0]) == 0:
                path.append(True)
                return path
            if len(path) == max_conversions:
                del path[-1]
                continue
            newUnitBlackList = list(unitBlackList)
            DimA.todo__q__(unit_todo, toodo[0], newUnitBlackList)
            lis.append((toodo[0], target_unit, list(path), break_size, using, max_conversions, newUnitBlackList))
            del path[-1]
        return lis
    
    def _get_path(unit, target_unit, using=[], level=1, **kwords):
        """
            DimA._get_path(unit, target_unit, using=[], level=1, **{break_size: len(todo) * DimA.break_multiplier + DimA.break_additive, max_conversions: DimA.max_conversions})

            return(s) list_of_conversions_in_order

            raise(s) PathError
            #if no path of conversions can be found to take the unit to the target_unit

            Argument discriptions:
            unit -> a UnitList object which is the starting unit for the path
            target_unit -> a UnitList which is the ending unit for the path
            using -> any conversions which should be used in the path finding process which are not already in DimA.conversions
            level -> where the trial process is, should always be 1 when this function is called
            break_size -> a keyword argument which describes how long the todo list can get before the trial process on that branch breaks
                This ALWAYS has to be at least the length of the unit and targetUnit + 1 (len(unit) + len(target_unit) + 1), but will have to
                increase if the path must go through a conversion which increases the amount of units to look through (ex: "newton" -> "foot pound")
            max_conversions -> a keyword argument which will limit the amount of conversions inside a path before discarding it as a candidate

        """
        todo = unit.getTodoList(target_unit)
        for path in DimA.paths:
            if DimA.todo__eq__(todo, path.todo):
                return path
        blacklist = []
        path = []
        max_conversions = kwords.get("max_conversions", DimA.max_conversions)
        #print(max_conversions)
        break_size = kwords.get("break_size", len(todo) * DimA.break_multiplier + DimA.break_additive)
        #print(todo)
        level += 1
        r = DimA._path_loop_alg(list(todo), target_unit, path, break_size, using, blacklist, level, max_conversions)
        level -= 1
        #print(len(DimA.conversions + using))
        #print(r)
        if not r:
            raise PathError("".join(("No path can be found from unit(s): ",str(unit)," to target unit(s): ", str(target_unit), " with a break_size of: ", str(break_size), " and a max_conversion of: ", str(max_conversions))))
        #print(r)
        if kwords.get("auto_add", True):
            return Path(r, todo, auto_add=True)
        else:
            return Path(r, todo, auto_add=False)

    def _path_loop_alg(unit_todo, target_unit, path, break_size, using=[], blacklist=[], level=1, max_conversions=math.inf, unitBlackList=[]):
        """
        DimA._path_loop_alg(unit_todo, target_unit, path, break_size, using=[], blacklist=[], level=1, max_conversions=math.inf)

        return(s) path or False
        #path is a list of conversion tupple returned as fallows [(conversion1, multiplier), (conversion2, multiplier), ...]
        #False is returned if the path does end with a completion of the todo list (AKA: len(todo) == 0)

        raise(s)
        #No errors are raised by this function

        Argument discriptions:
        unit_todo -> the todo list (list of units) whicch is checked for path completion
        target_unit -> a UnitList which states the finishing units of the path (never used)
        path -> a list of conversions which are stored for the trail, if a conversion completes the todo list then the path is returned. Interpret as fallows: [(conversion1, multiplier), (conversion2, multiplier), ...]
        break_size -> how long the todo list can get before returning False, leverage this to cut down the length of time needed to find a path (AKA: if len(todo) >= break_size: return False)
        using -> any conversions which should be considered in path finding which are not in the list DimA.conversions
        blacklist -> any conversions which should not be considered with the path finding, any path already considered will be put on this list
        level -> at what level of path finding the iterpreter is at
        max_conversions -> the max number of conversions that can be in a path before the path is discarded as a candidate
        """
        for conversion in DimA.conversions + using:
            DimA.tests += 1
            if conversion in blacklist or not DimA.todo__effects__(unit_todo, conversion.todo):
                continue
            if DimA.todo__contain__(unitBlackList, conversion.todo):
                #return False
                continue
            toodo = [*DimA.todo__sub__t(unit_todo, conversion.todo)]
            toodo[0] = DimA.todo__compact__(toodo[0])
            if len(toodo[0]) >= break_size:
                return False
            path.append((conversion, toodo[1]))
            if len(toodo[0]) == 0:
                return path
            blacklist.append(conversion)
            if len(path) > max_conversions:
                return False
            if len(path) == max_conversions:
                del path[-1]
                continue
            newUnitBlackList = list(unitBlackList)
            DimA.todo__q__(unit_todo, toodo[0], newUnitBlackList)
            level += 1
            r = DimA._path_loop_alg(toodo[0], target_unit, list(path), break_size, using, list(blacklist), level, max_conversions, newUnitBlackList)
            level -= 1
            del path[-1]
            blacklist.remove(conversion)
            if not r:
                continue
            return r
        return False
        

    def add_conversion(conversion):
        DimA.conversions.append(conversion)

    def add_conversions(iterable):
        for item in iterable:
            DimA.add_conversion(item)

    def normalizeToUnitList(unit_lis_rep):
        if isinstance(unit_lis_rep, UnitList):
            return unit_lis_rep
        if isinstance(unit_lis_rep, str):
            return UnitList(DimA.todo__compact__(DimA.parseUnits(unit_lis_rep)))
        if isinstance(unit_lis_rep, list):
            lis = []
            for item in unit_lis_rep:
                if isinstance(item, str):
                    t = DimA.parseUnit(item)
                    if t:
                        lis.append(t)
                if isinstance(item, Unit):
                    lis.append(t)
            return UnitList(lis)

    def normalizeToUnit(unit_rep):
        if isinstance(unit_rep, str):
            return DimA.parseUnit(unit_rep)
        return unit_rep

    def _normalize(unit_rep):
        return DimA.normalizeToUnitList(unit_rep)



    def parseUnits(string):
        """
        string comes in as 'unit_name^power second_unit_name^power ...'
        """
        lis = []
        for unit in string.split():
            u = DimA.parseUnit(unit)
            if u:
                lis.append(u)
        return lis

    def parseUnit(string):
        """
            return Unit if able to parse, return False if unable to parse
        """
        c = string.split("^")
        if len(c) > 1:
            return Unit(c[0], float(c[1]))
        if len(c) == 1:
            return Unit(c[0], float(1))
        return False

    def todo__sub__(todo, todoo):
        lis = []
        for unit in todo:
            if not unit in todoo:
                lis.append(unit.copy())
                continue
            unitt = unit - todoo[todoo.index(unit)]
            if unitt.power == 0:
                continue
            lis.append(unitt)
        for unit in todoo:
            if not unit in todo:
                u = unit.copy()
                u.power = -u.power
                lis.append(u)
        return lis

    def todo__sub__t(todo, todoo):
        lis = []
        #find common unit powers (as integer)
        for unit in todo:
            if not unit in todoo:
                continue
            lis.append(int(unit.power / todoo[todoo.index(unit)].power))
        #find min common multiplier (which is the max to be taken)
        minimum = min(lis, key=lambda x:abs(x))
        #subtract with this multiplier
        lis = []
        for unit in todo:
            if not unit in todoo:
                lis.append(unit.copy())
                continue
            unitt = unit.__sub__(todoo[todoo.index(unit)], other_multiplier=minimum)
            if unitt.power == 0:
                continue
            lis.append(unitt)
        for unit in todoo:
            if not unit in todo:
                u = unit.copy(minimum)
                u.power = -u.power
                lis.append(u)
        return (lis,minimum)

    def todo__effects__(todo, todoo):
        for unit in todo:
            if unit in todoo:
                return True
        return False

    def todo__compact__(todo):
        lis = []
        for unit in todo:
            if unit in lis:
                lis[lis.index(unit)] += unit
                continue
            lis.append(unit)
        return lis

    def todo__eq__(todo, todoo):
        if len(todo) != len(todoo):
            return False
        for unit in todo:
            if not unit in todoo:
                return False
            if not unit.strictEquality(todoo[todoo.index(unit)]):
                return False
        for unit in todoo:
            if not unit in todo:
                return False
            if not unit.strictEquality(todo[todo.index(unit)]):
                return False
        return True

    def todo__q__(original, other, lis):
        for unit in original:
            if not unit in other:
                if not unit in lis:
                    lis.append(unit.copy(True))

    def todo__contain__(todo1, todo2):
        for unit in todo1:
            if unit in todo2:
                return True
        return False

    algorithums={"level": get_level_path,"default": get_level_path,"layer": get_path}

                


class Conversion:

    def __init__(this, unit, target_unit, lambda_conversion, backward_conversion=None, auto_add=True):
        this.unit = DimA.normalizeToUnitList(unit)
        this.target_unit = DimA.normalizeToUnitList(target_unit)
        this.conversion = lambda_conversion
        this.todo = this._makeTodoList()
        if auto_add:
            DimA.add_conversion(this)
        if backward_conversion and auto_add:
            Conversion(target_unit, unit, backward_conversion, auto_add=True)

    def _makeTodoList(this):
        return this.unit.getTodoList(this.target_unit)
    
    def convert(this, value, power):
        return this.conversion(value,power)

    def _getTodoDict(this):
        pass

    def __repr__(this):
        return "".join((this.unit.__repr__()," -> ",this.target_unit.__repr__()))

class Path:

    def __init__(this, list_of_conversions, todo_list, auto_add=True):
        this.conversions = list_of_conversions
        this.todo = todo_list
        if auto_add:
            DimA.paths.append(this)
        

    def convert(this, value):
        for conversion in this.conversions:
            value = conversion[0].convert(value,conversion[1])
        return value

    def __repr__(this):
        return "->".join([x.__repr__() for x in this])

    def __iter__(this):
        return iter(this.conversions)

class UnitList:

    def __init__(this, list_of_units):
        this.units = list_of_units

    def __iter__(this):
        return iter(this.units)

    def __repr__(this):
        return "".join(["['", "', '".join([x.__repr__() for x in this]), "']"])

    def __mul__(this, other):
        if type(other) == int or type(other) == float:
            return UnitList([x.copy(other) for x in this])
        raise TypeError("can only multiply UnitList with type(s) float or int")

    def __rmul__(this, other):
        return this * other

    def __contains__(this, value):
        return value in this.units

    def __getitem__(this, key):
        for unit in this:
            if unit == key:
                return unit
        raise KeyError("".join([str(key), " is not in unit list ", this.__repr__()]))

    def __add__(this, other):
        other = DimA.normalizeToUnitList(other)
        ret = this.copy(True)
        for unit in other:
            ret.units.append(unit.copy(True))
        ret.compact()
        for unit in ret:
            if unit.power == 0:
                ret.units.remove(unit)
        return ret

    def get(this, key, default):
        try:
            return this[key]
        except KeyError:
            return default

    def getTodoList(this, other):
        todo = []
        for unit in this:
            if not unit in other:
                todo.append(Unit(unit.unit_string, -unit.power))
                continue
            if unit.power == other[unit].power:
                continue
            todo.append(Unit(unit.unit_string, other[unit].power - unit.power))
        for unit in other:
            if not unit in this:
                todo.append(unit.copy())
        return todo

    def copy(this, deep=False):
        if not deep:
            return UnitList(list(this.units))
        return UnitList([x.copy() for x in this.units])

    def __eq__(this, other):
        for unit in this:
            if not unit in other:
                return False
            if not unit.strictEquality(other[unit]):
                return False
        for unit in other:
            if not unit in this:
                return False
        return True

    def compact(this):
        this.units = DimA.todo__compact__(this.units)

    def __neg__(this):
        return UnitList([x.copy(-1) for x in this])

    def __sub__(this, other):
        if not isinstance(other, UnitList):
            raise TypeError("Type '" + type(other).__name__ + "' can not be subtracted from Type 'UnitList'")
        return this + -other

class Unit:

    def __init__(this, unit_string, power):
        this.unit_string = unit_string
        this.power = power

    def __repr__(this):
        return "".join((str(this.unit_string),"^", str(this.power)))

    def __eq__(this, other):
        if isinstance(other, str):
            return this == DimA.parseUnit(other)
        return this.unit_string == other.unit_string

    def strictEquality(this, other):
        return this == other and this.power == other.power

    def __sub__(this, other, this_multiplier=1, other_multiplier=1):
        other = DimA.normalizeToUnit(other)
        return Unit(this.unit_string, this.power * this_multiplier - other.power * other_multiplier)

    def __add__(this, other):
        if not isinstance(other, Unit):
            raise TypeError("".join("Type ",type(this).__name__," can not be added with ",type(other).__name__))
        return Unit(this.unit_string, this.power + other.power)

    def copy(this, multiplier=1):
        return Unit(this.unit_string, this.power*multiplier)

    def equals(this, other):
        return this.unit_string == other.unit_string and this.power == other.power

class Dimension(numbers.Real):

    def  __init__(self, value, units):
        self.value = value
        self.units = DimA.normalizeToUnitList(units)


    def __add__(self, other):
        if isinstance(other, Dimension):
            if self.units == other.units:
                return Dimension(self.value + other.value, self.units.copy())
            return Dimension(DimA.convert(other.value, other.units, self.units) + self.value, self.units.copy())
        return Dimension(self.value + other, self.units.copy())
    """
    #################################################
    """

    def convert(self, target_unit_list, **kwords):
        target_unit_list = DimA.normalizeToUnitList(target_unit_list)
        self.value = DimA.convert(self.value, self.units, target_unit_list, **kwords)
        self.units = target_unit_list.copy(True)

    def get_converted(self,target_unit_list, **kwords):
        return DimA.convert(self.value, self.units, DimA.normalizeToUnitList(target_unit_list), **kwords)
    
    def __repr__(self):
        return " ".join((str(self.value),self.units.__repr__()))
    
    def __abs__(self):
        return Dimension(abs(self.value),self.units.copy(True))

    def __ceil__(self):
        return math.ceil(self.value)

    def __eq__(self, other):
        if isinstance(other, Dimension):
            if other.units == self.units:
                return self.value == other.value
            return self.get_converted(other.units) == other.value
        return other == self.value

    def __float__(self):
        return float(self.value)

    def float(self):
        return Dimension(float(self), self.units.copy(True))

    def floor(self):
        return Dimension(math.floor(self), self.units.copy(True))

    def ceil(self):
        return Dimension(math.ceil(self), self.units.copy(True))

    def __floor__(self):
        return math.floor(self.value)

    def __floordiv__(self, other):
        if isinstance(other, Dimension):
            if self.units == other.units:
                return Dimension(self.value // other.value, self.units - other.units)
            try:
                return Dimension(self.value // other.value.get_converted(self.units), self.units - other.units)
            except PathError:
                return Dimension(self.value // other.value, self.units - other.units)
        return Dimension(self.value // other, self.units.copy(True))

    def __le__(self, other):
        if isinstance(other, Dimension):
            if self.units == other.units:
                return self.value <= other.value
            return self.value <= other.get_converted(self.units)
        return self.value <= other

    def __lt__(self, other):
        if isinstance(other, Dimension):
            if self.units == other.units:
                return self.value < other.value
            return self.value <= other.get_converted(self.units)
        return self.value < other

    def __mod__(self, other):
        """
        assumption: other.value should be in units of self.units
        """
        if isinstance(other, Dimension):
            if self.units == other.units:
                return Dimension(self.value % other.value, self.units.copy(True))
            return Dimension(self.value % other.get_converted(self.units), self.units.copy(True))
        return Dimension(self.value % other, self.units.copy(True))

    def __mul__(self, other):
        """
        assumption: other.value should be in units of self.units
        """
        if isinstance(other, Dimension):
            if self.units == other.units:
                return Dimension(self.value * other.value, self.units + other.units)
            try:
                return Dimension(self.value * other.get_converted(self.units), self.units + self.units)
            except PathError:
                return Dimension(self.value * other.value, self.units + other.units)
        return Dimension(self.value * other, self.units.copy(True))

    def __neg__(self):
        return Dimension(-self.value, self.units.copy(True))

    def __pos__(self):
        return Dimension(+self.value, self.units.copy(True))

    def __pow__(self, other):
        if isinstance(other, Dimension):
            raise TypeError("Can not use a Dimension as a power")
        return Dimension(self.value, other * self.units.copy(True))

    def __radd__(self, other):
        return self + other

    def __rfloordiv__(self, other):
        if isinstance(other, Dimension):
            if self.units == other.units:
                return Dimension(other.value // self.value, oether.units - self.units)
            try:
                return Dimension(other.value // self.get_converted(other.units), other.units - self.units)
            except PathError:
                return Dimension(other.value // self.value, other.units - self.units)
        return Dimension(other // self.value, -self.units)

    def __rmod__(self, other):
        if isinstance(other, Dimension):
            if other.units == self.units:
                return Dimension(other.value % self.value, other.units.copy(True))
            return Dimension(other.value % self.get_converted(other.units), other.units.copy(True))
        return Dimension(other % self.value, self.units.copy(True))

    def __rmul__(self, other):
        return self * other

    def __round__(self, other):
        if isinstance(other, Dimension):
            raise TypeError("The second argument in the 'round(arg1, arg2)' function can not be of type Dimension")
        return Dimension(round(self.value, other), self.units.copy(True))

    def __rpow__(self, other):
        raise TypeError("Can not use a Dimension as a power")

    def __rtruediv__(self, other):
        if isinstance(other, Dimension):
            if self.units == other.units:
                return Dimension(other.value / self.value, oether.units - self.units)
            try:
                return Dimension(other.value / self.get_converted(other.units), other.units - self.units)
            except PathError:
                return Dimension(other.value / self.value, other.units - self.units)
        return Dimension(other / self.value, -self.units)

    def __truediv__(self,other):
        if isinstance(other, Dimension):
            if self.units == other.units:
                return Dimension(self.value / other.value, self.units - other.units)
            try:
                return Dimension(self.value / other.get_converted(self.units), self.units - other.units)
            except PathError:
                return Dimension(self.value / other.value, self.units - other.units)
        return Dimension(self.value / other, self.units.copy(True))

    def __trunc__(self):
        return int(self.value)

    def int(self):
        return Dimension(int(self.value), self.units.copy(True))

class UnitLoader:
  
  imperialLoaded = False
  metricLoaded = False
  scientificLoaded = False
  systemConversionsLoaded = False
  
  @staticmethod
  def load_imperial():
    if not UnitLoader.imperialLoaded:
      #wieght
      Conversion("ounce","dram",lambda numeric, power: numeric * 16 ** power, lambda numeric, power: numeric / 16.0 ** power)
      Conversion("pound","ounce",lambda numeric, power: numeric * 16 ** power, lambda numeric, power: numeric / 16.0 ** power)
      Conversion("stone","pound",lambda numeric, power: numeric * 14 ** power, lambda numeric, power: numeric / 14.0 ** power)
      Conversion("quarter","stone",lambda numeric, power: numeric * 2 ** power, lambda numeric, power: numeric / 2.0 ** power)
      Conversion("hundredweight","quarter",lambda numeric, power: numeric * 4 ** power, lambda numeric, power: numeric / 4.0 ** power)
      Conversion("ton", "hundredweight",lambda numeric, power: numeric * 20 ** power, lambda numeric, power: numeric / 20.0 ** power)
      Conversion("long", "ton", lambda numeric, power: numeric, lambda numeric: numeric)
      #length
      Conversion("inch", "foot", lambda numeric, power: numeric / 12.0 ** power, lambda numeric, power: numeric * 12 ** power)
      Conversion("feet", "foot", lambda numeric, power: numeric, lambda numeric, power: numeric)
      Conversion("foot", "yard", lambda numeric, power: numeric / 3.0 ** power, lambda numeric, power: numeric * 3 ** power)
      Conversion("foot", "mile", lambda numeric, power: numeric / 5280.0 ** power, lambda numeric, power: numeric * 5280 ** power)
      Conversion("foot", "nauticalmile", lambda numeric, power: numeric / 6076.12 ** power, lambda numeric, power: numeric * 6076.12 ** power)
      UnitLoader.imperialLoaded = True
      UnitLoader.load_system_conversions()
  
  @staticmethod
  def load_metric():
    if not UnitLoader.metricLoaded:
      UnitLoader.__create_metic_prefixes__("gram")
      UnitLoader.__create_metic_prefixes__("liter")
      UnitLoader.__create_metic_prefixes__("meter")
      Conversion("milliliter", "centimeter^3", lambda numeric, power: numeric, lambda numeric, power: numeric)
      Conversion('tonne', "megagram", lambda numeric: numeric, lambda numeric: numeric)
      UnitLoader.load_system_conversions()
      UnitLoader.metricLoaded = True
  
  @staticmethod
  def load_system_conversions():
    if not UnitLoader.systemConversionsLoaded:
      Conversion("inch", "centimeter", lambda numeric, power: numeric * 2.54 ** power, lambda numeric, power: numeric / 2.54 ** power)
      Conversion("fahrenheit", "celsius", lambda numeric, power: ((numeric ** (1 / power) -32) * 5 / 9.0) ** power, lambda numeric, power: ((numeric ** (1 / power)) * 9 / 5.0 + 32) ** power)
      Conversion("kelvin", "cilsius", lambda numeric, power: (numeric ** (1 / power) - 273.15) ** power, lambda numeric, power: (numeric ** (1 / power) + 273.15) ** power)
      Conversion("gallon", "liter", lambda numeric, power: numeric * 4.54609 ** power, lambda numeric, power: numeric / 4.54609 ** power)
      Conversion("ounce", "gram", lambda numeric, power: numeric * 28.3495 ** power, lambda numeric, power: numeric / 28.3495 ** power)
      UnitLoader.systemConversionsLoaded = True
  
  @staticmethod
  def __create_metic_prefixes__(base_unit):
    Conversion(base_unit,"femto" + base_unit,lambda numeric, power: numeric * 1000000000000000.00 ** power, lambda numeric, power: numeric / 1000000000000000.00  ** power)
    Conversion(base_unit, "auto" + base_unit, lambda numeric, power: numeric * 1000000000000000000.00 ** power, lambda numeric, power: numeric / 1000000000000000000  ** power)
    Conversion(base_unit, "pico" + base_unit, lambda numeric, power: numeric * 1000000000000.00 ** power, lambda numeric, power: numeric / 1000000000000.00  ** power)
    Conversion(base_unit, "nano" + base_unit, lambda numeric, power: numeric * 1000000000.00 ** power, lambda numeric, power: numeric / 1000000000.00  ** power)
    Conversion(base_unit, "micro" + base_unit, lambda numeric, power: numeric * 1000000.00 ** power, lambda numeric, power: numeric / 1000000.00  ** power)
    Conversion(base_unit, "milli" + base_unit, lambda numeric, power: numeric * 1000 ** power, lambda numeric, power: numeric / 1000.00 ** power)
    Conversion(base_unit, "centi" + base_unit, lambda numeric, power: numeric * 100 ** power, lambda numeric, power: numeric / 100.00 ** power)
    Conversion(base_unit, "deci" + base_unit, lambda numeric, power: numeric * 10 ** power, lambda numeric, power: numeric / 10.00 ** power)
    Conversion(base_unit, "deka" + base_unit, lambda numeric, power: numeric * 0.1 ** power, lambda numeric, power: numeric / 0.1 ** power)
    Conversion(base_unit, "hecto" + base_unit, lambda numeric, power: numeric * 0.01 ** power, lambda numeric, power: numeric / 0.01 ** power)
    Conversion(base_unit, "kilo" + base_unit, lambda numeric, power: numeric * 0.001 ** power, lambda numeric, power: numeric / 0.001 ** power)
    Conversion(base_unit, "mega" + base_unit, lambda numeric, power: numeric / 1000000.00 ** power, lambda numeric, power: numeric * 1000000 ** power)
    Conversion(base_unit, "giga" + base_unit, lambda numeric, power: numeric / 1000000000.00 ** power, lambda numeric, power: numeric * 1000000000 ** power)
    Conversion(base_unit, "tera" + base_unit, lambda numeric, power: numeric / 1000000000000.00 ** power, lambda numeric, power: numeric * 1000000000000 ** power)
    Conversion(base_unit, "peta" + base_unit, lambda numeric, power: numeric / 1000000000000000.00 ** power, lambda numeric, power: numeric * 1000000000000000 ** power)
    Conversion(base_unit, "exa" + base_unit, lambda numeric, power: numeric / 1000000000000000000.00  ** power, lambda numeric, power: numeric * 1000000000000000000 ** power)
  
  @staticmethod
  def load_scientific():
    if not UnitLoader.scientificLoaded:
      Conversion("mol", "molecule", lambda numeric, power: numeric * 602200000000000000000000 ** power, lambda numeric, power: numeric / 602200000000000000000000.00 ** power)
      UnitLoader.load_system_conversions()
      UnitLoader.scientificLoaded = True
    
class PathError(Exception):

    def __init__(this, message="Bad Path"):
        super().__init__(message)




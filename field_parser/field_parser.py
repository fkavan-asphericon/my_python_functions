import re
import copy

# field Parse RE, for matching starting of the field definition name = fields.Monetary(
fieldParseREStart = r'(\s*)([a-zA-Z_]+?)(\s*?=\s*?fields.)([a-zA-Z2]+?)'
fieldParseRE = fieldParseREStart + r'(\(.*\))\s*'
INDENT_SIZE = 4
# AUTO INDENT for further use
INDENT = ''.join([' ' for k in range(INDENT_SIZE)])

# This is here for testing purposes
sampleFields = """
        # Comment should not be handled
        # Field without string
        vat_date = fields.Float(string='VAT Date',digits=(10,2),store=True)
        new_trolo_field = fields.Selection([
                ('te)stkey', meh),
                ('newkey', 'value2'),
                ('testkey', 'value1'),
                ('newkey', 'value2'),
            ],
            store=True,
            help='This is for helping',
            digits=(10, 2))
"""

# Lines below are also for testing, they should be commented in real code

# definition = r"newfield = fields.Selection([('testkey','value1'),('newkey','value2'),('testkey','value1'),('newkey','value2'),],string='New Field',store=True)"
# par = SingleParser(definition)
# par.params['kwargs'].update({'help':'This is for helping'})
# par.params['kwargs'].update({'digits':(10,2)})

# Single parser class definition, this can handle single field definition.
# There are no sophisticated checks if field definition is valid.
# So take care when using it.

class ParameterIterable:
    _value = []
    def __init__(self,value):
        self._value = value
    
    def __len__(self):
        return self._value.__len__()
    def __getitem__(self, key):
        return self._value.__getitem__(key)    
    def __setitem__(self, key, value):
        self._value.__setitem__(key, value)
    def __delitem__(self, key, value):
        self._value.__delitem__(key, value)
    def __getslice__(self, i, j):
        return self._value.__getslice__(i, j)
    def __setslice__(self, i, j, s):
        self._value.__setslice__(i, j, s)
    def __delslice__(self, i, j):
        return self._value.__delslice__(i, j)
    def __contains__(self, obj):
        return self._value.__contains__(obj)
    
    def __add__(self, other):
        if isinstance(other, ParameterIterable):
            return self._value.__add__(other._value)
        else:
            return self._value.__add__(other)
    
    def __iter__(self):
        return self._value.__iter__()
    def __next__(self):
        return self._value.__next__()
    def __str__(self) -> str:
        return ('[' + ', '.join(str(val) for val in self._value) + ']')
    def __repr__(self) -> str:
        return '%s(%s)' % (self.__class__.__name__, repr(self._value))
    
    def keys(self):
        return self._value.keys()

class ParameterList(ParameterIterable):
    _value = []
    def __init__(self, value):
        super().__init__(value)
    def append(self, value):
        self._value.append(value)

class ParameterTuple(ParameterIterable):
    _value = []
    def __init__(self,value):
        super().__init__(value)
    def __str__(self) -> str:
        return '(' + super().__str__()[1:-1] + ')'

class ParameterVariable:
    _name = ''
    def __init__(self,name):
        self._name = name
    def __str__(self) -> str:
        return self._name
    def __repr__(self) -> str:
        return 'ParameterVariable(%s)' % self._name
    def __len__(self):
        return len(self._name)
    
class ParameterString:
    _name = ''
    def __init__(self,name):
        name = name.strip()
        if name[0] in ['"',"'"]:
            name = name[1:-1]
        self._name = name
    def __str__(self) -> str:
        return '\'%s\'' % self._name
    def __repr__(self) -> str:
        return 'ParameterString(\'%s\')' % self._name
    def __len__(self):
        return len(self._name)

class Parameter:
    _name = ''
    _value = ''
    def __init__(self, name, value) -> None:
        self._name = name
        if isinstance(value,str):
            value = ParameterString(value)
        self._value = value
    
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self,val):
        self._name = val
    
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self,val):
        self._value = val

    @property
    def has_name(self):
        return bool(self._name)
    @has_name.setter
    def has_name(self,val):
        pass

    def __repr__(self):
        if self._name:
            return 'Parameter(%s,%s)' % (self._name, repr(self._value))
        else:
            return 'Parameter(%s)' % (repr(self._value))
    def __str__(self):
        if self._name:
            return '%s=%s' % (self._name, str(self._value))
        else:
            return str(self._value)
            
class SingleParser:    
    params = {}
    leadingSpaces = 0

    @property
    def parameters(self):
        return self.params['params']
    @parameters.setter
    def parameters(self,val):
        pass

    @property
    def name(self):
        return self.params['name']
    @name.setter
    def name(self,val):
        self.params['name'] = val

    @property
    def parameter_names(self):
        return [p.name for p in self.params['params'] if isinstance(p,Parameter) and p.name]
    @parameter_names.setter
    def parameter_names(self,val):
        pass

    @property
    def type(self):
        return self.params['type']
    @type.setter
    def type(self,val):
        self.params['type'] = val


    def __init__(self,definition):
        match = re.findall(fieldParseREStart, definition)
        self.leadingSpaces = len(match[0][0])
        self.params = SingleParser.getFieldParams(definition)
    
    def __len__(self):
        return len(self.dump(short=True))

    def insert(self, obj, force=False):
        if isinstance(obj,Parameter):
            parameter = self.getParameter(obj.name)
            if parameter:
                if force:
                    parameter.value = obj.value
            else:
                self.params['params'].append(obj)

        elif isinstance(obj,str):
            param_list = SingleParser.parseParams(obj)
            self.insert(param_list, force=force)
        elif isinstance(obj,ParameterList):
            for param in obj:
                self.insert(param, force=force)

    def update(self, obj):
        self.insert(obj, force=True)

    
    def get(self, name, default=None):
        param = self.getParameter(name)
        if param:
            return param.value
        return default
    
    def getParameter(self,name):
        if not name in self.parameter_names or not name:
            return None
        else:
            for k in range(len(self.params['params'])):
                parameter = self.params['params'][k]
                if name and isinstance(parameter,Parameter) and name == parameter.name:
                    return parameter

        

    @staticmethod
    def parseParams(params, recursive=False):
        allParamsUnparsed = params.split(',')
        allParams = []
        stack = ''
        while allParamsUnparsed:
            stack += ',' + allParamsUnparsed.pop(0)
            xstack = stack[1:].strip()
            if not xstack:
                break
            try:
                # print('Executing ', xstack)
                exec(xstack)
                allParams.append({'NameError':0, 'string':copy.copy(xstack)})
                stack = ''
            except NameError:
                allParams.append({'NameError':1, 'string':copy.copy(xstack)})
                stack = ''
            except SyntaxError:
                pass
        # print(allParams)
        fullParams = []
        for param in allParams:
            string_full = param['string']
            kwarg = re.match(r'\s*([a-zA-Z0-9_]+)\s*=+\s*(.+)', string_full)
            if kwarg:
                name, string = kwarg.groups()
            else:
                name = ''
                string = string_full
            current = None
            if param['NameError']:
                if string[0]=='[' and string[-1] == ']':
                    current = ParameterList(SingleParser.parseParams(string[1:-1], recursive=True))
                elif string[0]=='(' and string[-1] == ')':
                    current = ParameterTuple(SingleParser.parseParams(string[1:-1], recursive=True)) 
                else:
                    current = ParameterVariable(string)
            else:
                estring = eval(string)
                if isinstance(estring,str):
                    current = ParameterString(estring)
                else:
                    current = estring
            # print(repr(current))
            if not name:
                fullParams.append(current)
            else:
                fullParams.append(Parameter(name,current))
        # print('FULL PARAMS')
        # print(fullParams)
        if recursive:
            if len(fullParams) == 1:
                return fullParams[0]
            else:
                return fullParams
        return ParameterList(fullParams)


    @staticmethod
    def getFieldParams(definition): 
        definitionCleaned = ''.join([k.strip() for k in definition.split('\n')])
        fieldParams = {}
        findParams = re.findall(fieldParseRE,definitionCleaned)
        if findParams:
            params_def = findParams[0][4][1:-1]
            params = SingleParser.parseParams(params_def)
            fieldParams.update({
                'name':     findParams[0][1],
                'type':     findParams[0][3],
                'params':   params,
                'nparams':  len(params),
                'deflen':   len(params_def),
            })
        return fieldParams
    
    @staticmethod
    def getFieldDescription(fieldname):
        return ' '.join([s.capitalize() for s in fieldname.split('_')])
    
    def AutoFieldDescription(self):
        return SingleParser.getFieldDescription(self.name)
    
    def dump(self, params=None, short=False, leading_spaces = False):
        if not params:
            params = self.params
        res = '%s = fields.%s(%s)' % (params['name'], params['type'], SingleParser.dumpParams(params, short=short))
        if not short and '\n' in res:
            res = ('\n' + INDENT).join(res.split('\n'))
        if leading_spaces:
            ls = ''.join([' ' for k in range(self.leadingSpaces)])
            res = ls + ('\n'+ls).join(res.split('\n'))
        return res
    
    @staticmethod
    def dumpParams(params, short=False):
        allargs = []
        for param in params['params']:
            allargs.append(SingleParser.escapeParam(param, short=short))
        return (',%s' % (' ' if short else '\n')).join(allargs)

    @staticmethod
    def escapeParam(param, short=False):
        if isinstance(param,(str,ParameterString,ParameterVariable)):
            return str(param)
        
        elif isinstance(param,(Parameter)):
            return '%s=%s' % (param._name, SingleParser.escapeParam(param._value,short=short))
        
        elif not short and isinstance(param, (list, ParameterList)) and len(param) > 2:
            return ('[\n' + INDENT) + ('\n' + INDENT).join([SingleParser.escapeParam(key,short=True) for key in param]) +'\n]'
        
        elif not short and isinstance(param, (tuple, ParameterTuple)) and len(param) > 2:
            return ('(\n' + INDENT) + ('\n' + INDENT).join([SingleParser.escapeParam(key,short=True) for key in param]) +'\n)'
        
        else:
            return str(param)

def MultiParse(iterator, condition = None, changer = None):
    if not callable(iterator):
        string = copy.deepcopy(iterator)
        def iterator():
            for line in string.split('\n'):
                yield line
    
    # Condition should return:
    # 0  if it should continue
    # 1  if the stack should be finished
    # -1 if the satisfying field was found but not ended
    if not condition:
        def condition(stack):
            num_brackets = lambda s: s.count('(') - s.count(')')
            if re.findall(fieldParseREStart, stack):
                if num_brackets(stack) == 0:
                    return 1
                else:
                    return -1
            else:
                return 0
    
    if not changer:
        def changer(stack):
            return SingleParser(stack).dump(leading_spaces=True)
    
    stack = ''
    res = ''
    for line in iterator():
        stack += line
        cond = condition(stack)
        if cond == 1:
            res += changer(stack) + '\n'
            stack = ''
        elif cond == -1:
            pass
        else:
            stack = ''
            res += line + '\n'
    return res

def AutoAddString(stack):
    parsed_field = SingleParser(stack)
    parsed_field.insert(Parameter('string',parsed_field.AutoFieldDescription()))
    short = len(parsed_field) < 80
    return parsed_field.dump(short=short, leading_spaces=True)
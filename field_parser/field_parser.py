import re
import copy

# field Parse RE, for matching starting of the field definition name = fields.Monetary(
fieldParseREStart = r'\s*([a-zA-Z_]+?)(\s*?=\s*?fields.)([a-zA-Z2]+?)'
fieldParseRE = fieldParseREStart + r'(\(.*\))\s*'
INDENT_SIZE = 4
# AUTO INDENT for further use
INDENT = ''.join([' ' for k in range(INDENT_SIZE)])

# This is here for testing purposes
sampleFields = """
        # Comment should not be handled
        # Field without string
        vat_date = fields.Float(digits=(10,2),store=True)
        new_trolo_field = fields.Selection([
                ('testkey', 'value1')
                ('newkey', 'value2')
                ('testkey', 'value1')
                ('newkey', 'value2')
            ],
            store=True,
            help='This is for helping',
            digits=(10, 2))
"""

# Lines below are also for testing, they should be commented in real code

definition = r"newfield = fields.Selection([('testkey','value1'),('newkey','value2'),('testkey','value1'),('newkey','value2'),],string='New Field',store=True)"
par = SingleParser(definition)
par.params['kwargs'].update({'help':'This is for helping'})
par.params['kwargs'].update({'digits':(10,2)})

# Single parser class definition, this can handle single field definition.
# There are no sophisticated checks if field definition is valid.
# So take care when using it.

class SingleParser:    
    params = {}

    def __init__(self,definition):
        self.params = SingleParser.getFieldParams(definition)
    

    @staticmethod
    def getFieldParams(definition): 
        fieldParams = {}
        # For parsing parameters
        def Parse(*args,**kwargs):
            arguments = []
            kwarguments = {}
            for arg in args:
                arguments.append(arg)
            for kwarg in kwargs:
                kwarguments.update({kwarg: kwargs[kwarg]})            
            return {
                'args': arguments,
                'kwargs': kwarguments,
            }
        
        findParams = re.findall(fieldParseRE,definition)
        additionalParams = eval(re.sub(fieldParseRE,r'Parse\4',definition))
        if findParams:
            fieldParams.update({
                'name':     findParams[0][0],
                'type':     findParams[0][2],
                'args':     additionalParams['args'],
                'kwargs':   additionalParams['kwargs'],
                'nparams':  len(additionalParams['args']) + len(additionalParams['kwargs']),
                'deflen':   len(''.join(findParams[0]))
            })
        return fieldParams
    
    @staticmethod
    def getFieldDescription(fieldname):
        return ' '.join([s.capitalize() for s in fieldname.split('_')])
    
    def dump(self, params=None, short=False):
        if not params:
            params = self.params
        res = '%s = fields.%s(%s)' % (params['name'], params['type'], SingleParser.dumpParams(params, short=short))
        if not short and '\n' in res:
            res = ('\n' + INDENT).join(res.split('\n'))
        return res
    
    @staticmethod
    def dumpParams(params, short=False):
        allargs = []
        for arg in params['args']:
            allargs.append(SingleParser.escapeParam(arg, short=short))
        for arg in params['kwargs'].keys():
            allargs.append('%s=%s' % (arg, SingleParser.escapeParam(params['kwargs'][arg], short=short)))
        return (',%s' % (' ' if short else '\n')).join(allargs)

    @staticmethod
    def escapeParam(param, short=False):
        if isinstance(param,str):
            return r"'%s'" % param
        
        elif not short and isinstance(param, list) and len(param) > 2:
            return ('[\n' + INDENT) + ('\n' + INDENT).join([SingleParser.escapeParam(key,short=True) for key in param]) +'\n]'

        elif not short and isinstance(param, tuple) and len(param) > 2:
            return ('[\n' + INDENT) + ('\n' + INDENT).join([SingleParser.escapeParam(key,short=True) for key in param]) +'\n)'

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
            if re.findall(fieldParseRE, stack):
                return 1
            else:
                return 0
    
    if not changer:
        def changer(stack):
            return SingleParser(stack).dump()
    
    stack = ''
    for line in iterator():
        cond = condition(line)
        if cond == 1:
            stack += line
            print(changer(stack))
            stack = ''
        elif cond== -1:
            stack += line
        else:
            print(line)

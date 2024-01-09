def reverse_polish_notation(domain):
    stack = []
    places = {}
    placeholders = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    tokens = [k for k in placeholders]
    tokens_ref = [k for k in placeholders]
    domain = [list(k) if isinstance(k,tuple) else k for k in domain]
    domain = ['&' if k =='&amp;' else k for k in domain]

    if isinstance(domain[0],list):
        domain.insert(0,'&')

    for token in reversed(domain):
        if isinstance(token,list) or token in tokens_ref:
            ph = '%s' % tokens.pop(0)
            places[ph] = ''.join(map(str, token))
            stack.append(ph)
        else:
            operand1 = stack.pop()
            operand2 = stack.pop()
            token = '&' if token == '&amp;' else token
            # Simplification of braces
            if '|' in operand1 and operand1[-4] == '|' and token == '|':
                operand1 = operand1[1:-1]
            if '|' in operand1 and operand1[3] == '|' and token == '|':
                operand1 = operand1[1:-1]
            if '&' in operand1 and operand1[3] == '&' and token == '&':
                operand1 = operand1[1:-1]
            if '&' in operand1 and operand1[-4] == '&' and token == '&':
                operand1 = operand1[1:-1]
            stack.append(f"({operand1} {token} {operand2})")
    final = stack.pop()

    for k in tokens_ref:
        final = final.replace(k,'*%s*' % k)
    for k in places:
        final = final.replace('*%s*' %k ,places[k] if places[k] in tokens_ref else '(%s)' % places[k])
    return final[1:-1]

def polish_notation(domain):
    stack = []
    domain = [list(k) if isinstance(k,tuple) else k for k in domain]

    for token in domain:
        if is_domain_condition(token):
            stack.append(token)
        elif isinstance(token,list):
            stack.extend(polish_notation(condition_reformat(token)))
        else:
            stack.insert(0,token)
    return stack

def is_domain_condition(domain):
    
    placeholders = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    tokens = [k for k in placeholders]
    if domain in tokens:
        return True
    
    operands = ['=','!=','in','like','=like','ilike','=ilike','>','<','>=','<=','childof']
    if isinstance(domain,list) and len(domain) == 3 and domain[1] in operands:
        return True
    else:
        return False

def condition_reformat(token):
    if not len(token) % 2:
        raise ValueError('Condition has to have odd number of terms')
    
    if len(token) <= 3:
        return token
    else:
        next_join = False
        newtoken = []
        for key in token:
            newtoken.append('&' if key == '&amp;' else key)
            if next_join:
                next_join = False
                operand2 = newtoken.pop()
                operator = newtoken.pop()
                operand1 = newtoken.pop()
                newtoken.append([operand1,operator,operand2])
                continue
            if key == '&':
                next_join = True
        return newtoken



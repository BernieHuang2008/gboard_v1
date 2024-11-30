import board


def FUNC_connect(x, venv):
    venv['vars'][''.join(sorted([venv['objs'][x[0]], venv['objs'][x[1]]]))] = {
        'class': 'Segment',
        'value': tuple(sorted([venv['objs'][x[0]], venv['objs'][x[1]]])),
        'object': board.Segment(x[0], x[1])
    }


def FUNC_midpoint(src, venv):
    midpoint = board.Point((src[0].a.x + src[0].b.x) / 2, (src[0].a.y + src[0].b.y) / 2)
    src[0].newRelation([midpoint.id], "mid_point")
    board.objects[src[0].relation[-1][0][0]].newRelation([src[0].id], ".mid_point")
    return midpoint


def FUNC_as(src, venv):
    if src[1] not in venv['variables']:
        venv['variables'].append(src[1])
    venv['vars'][src[1]] = {
        'class': 'Point',
        'value': src[0].id,
        'object': src[0]
    }
    venv['objs'][src[0]] = src[1]


def FUNC_clear(*args):
    board.clear()


LANG_inter_key_words = ['connect', 'establish', 'show', '#', 'midpoint', 'as', 'clear']
LANG_keyword_func = {
    'connect': FUNC_connect,
    'midpoint': FUNC_midpoint,
    'as': FUNC_as,
    'clear': FUNC_clear
}


def token(code, token_index=False):
    def append_token(t):
        if token_index:
            j = i - 1
            while code[j] == ' ' and j > 0:
                j -= 1
            t['token_index'] = j + 1 - len(t['value'])
        tokens.append(t)

    tokens = []
    i = 0
    while i < len(code):
        ch = code[i]
        if ch == '#':
            append_token({
                'type': 'comment',
                'value': ch
            })
            break
        elif ch in '()':
            append_token({
                'type': 'paren',
                'value': ch
            })
        elif ch in '0123456789':
            value = ""
            while i < len(code) and ch in '0123456789':
                value += ch
                i += 1
                if i >= len(code):
                    break
                ch = code[i]
            append_token({
                'type': 'number',
                'value': value
            })
            i -= 1
        elif ch in '\'\"':
            value = ""
            start_ch = ch
            i += 1
            ch = code[i]
            while i < len(code) and ch != start_ch:
                value += ch
                i += 1
                if i >= len(code):
                    break
                ch = code[i]
            append_token({
                'type': 'string',
                'value': value
            })
        elif ch in '+-*/≤<=>≥':
            append_token({
                'type': 'operator',
                'value': ch
            })
        elif ch in 'abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            value = ""
            while i < len(code) and ch in "abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789":
                value += ch
                i += 1
                if i >= len(code):
                    break
                ch = code[i]
            while i < len(code) and ch == ' ':
                i += 1
                if i >= len(code):
                    break
                ch = code[i]
            _type = ''
            if value.lower() in LANG_inter_key_words:
                print(value.lower())
                _type = 'keyword'
                value = value.lower()
            elif ch == '(':
                _type = 'name'
            else:
                _type = 'var'
            append_token({
                'type': _type,
                'value': value
            })
            i -= 1
        i += 1
    return tokens


def Parse(s):
    def process_vars(var):
        pass

    def error_deal(error_type, error_message):
        print(error_type, error_message)
        return False

    def AST(tokens):
        ast = {
            'type': 'Program',
            'body': []
        }

        i = 0

        def walk():
            nonlocal i
            token = tokens[i]
            token_type = token['type']
            token_value = token['value']
            if token_type == 'comment':
                i += 1
                return {
                    'type': 'Comment',
                    'name': token_value
                }
            elif token_type == 'operator':
                i += 1
                return {
                    'type': 'Operator',
                    'name': token_value
                }
            elif token_type == 'var':
                i += 1
                process_vars(token_value)
                return {
                    'type': "Variable",
                    'name': token_value
                }
            elif token_type == 'number':
                i += 1
                return {
                    'type': 'NumberLiteral',
                    'value': token_value
                }
            elif token_type == 'string':
                i += 1
                return {
                    'type': 'StringLiteral',
                    'value': token_value
                }
            elif token_type == 'name' and tokens[i + 1]['type'] == 'paren':
                i += 1
                return False
            elif token_type == 'keyword':
                i += 1
                return {
                    'type': 'KeywordType',
                    'name': token_value
                }
            elif token_type == 'paren' and token_value == '(' and tokens[i - 1]['type'] == 'name':
                node = {
                    'type': 'CallExpression',
                    'name': tokens[i - 1]['value'],
                    'params': []
                }

                i += 1
                token = tokens[i]

                while (token['type'] != 'paren' or (token['type'] == 'paren' and token['value'] != ')')) \
                        and i < len(tokens):
                    # (a normal token as parameter /or/ a non-close paren) /and/ token in range
                    wk_res = walk()
                    if wk_res:
                        node['params'].append(wk_res)
                    token = tokens[i]

                i += 1
                return node
            i += 1
            return error_deal('AST-walk-411:token cannot identified', token)
            # end `walk()`

        while i < len(tokens):
            walk_res = walk()
            if walk_res:
                ast['body'].append(walk_res)

        return ast  # end `AST()`

    return AST(token(s))  # end `Parse()`


def find_upper(s):
    for i in range(len(s)):
        if s[i].isupper():
            return i
    return -1


def run(code, venv):
    p = Parse(code)['body']
    if not p:
        return False
    keyword = ''
    if p[0]['type'] == 'KeywordType':
        keyword = p[0]['name']
    if p[0]['type'] == 'KeywordType':
        keyword = p[0]['name']
    i = 0
    variables = []
    keyword_params = []
    while i < len(p):
        if p[i]['type'] == 'KeywordType' and p[i]['name'] == 'as':
            keyword_params = [LANG_keyword_func[keyword](keyword_params, venv)]
            keyword = 'as'
        elif p[i]['type'] == 'CallExpression' and p[i]['name'].lower() == "rect_coord":
            keyword_params.append(venv['coordinate'])
            venv['coord'] = {
                'class': p[i]['name'],
                'origin': p[i]['params'][0],
                'x-direction': p[i]['params'][1],
                'y-direction': p[i]['params'][2],
                'unit-distance': p[i]['params'][3]
            }
        elif p[i]['type'] == 'Variable':
            if keyword == 'as':
                keyword_params.append(p[i]['name'])
                i += 1
                continue
            elif p[i]['name'] not in venv['variables']:
                var_name = p[i]['name']
                second_upper_index = find_upper(var_name[1:]) + 1
                if second_upper_index != 0:
                    p[i]['name'] = ''.join(sorted([var_name[:second_upper_index], var_name[second_upper_index:]]))
            keyword_params.append(venv['vars'][p[i]['name']]['object'])
        elif p[i]['type'] == 'CallExpression' and 'A' <= p[i]['name'][0] <= 'Z' and all(
                x['type'] == 'NumberLiteral' for x in p[i]['params']):
            # defining a Point
            if p[i]['name'] in venv['variables']:
                venv['vars'][p[i]['name']]['object'].moveto(int(p[i]['params'][0]['value']),
                                                            int(p[i]['params'][1]['value']))
                venv['vars'][p[i]['name']] = {
                    'class': 'Point',
                    'value': tuple([int(x['value']) for x in p[i]['params']]),
                    'object': venv['vars'][p[i]['name']]['object']
                }
                venv['objs'][venv['vars'][p[i]['name']]['object']] = p[i]['name']
            else:
                variables.append(p[i]['name'])
                venv['vars'][p[i]['name']] = {
                    'class': 'Point',
                    'value': tuple([int(x['value']) for x in p[i]['params']]),
                    'object': board.Point(int(p[i]['params'][0]['value']), int(p[i]['params'][1]['value']))
                }
                venv['objs'][venv['vars'][p[i]['name']]['object']] = p[i]['name']
                keyword_params.append(venv['vars'][p[i]['name']]['object'])
        i += 1
    venv['variables'].extend(variables)
    if keyword:
        LANG_keyword_func[keyword](keyword_params, venv)
    venv['tmp'] = {}


def Run(codes):
    codes = codes.strip().split('\n')
    env = {
        'variables': [],
        'vars': {},
        'objs': {},
        'tmp': {}
    }
    for code in codes:
        run(code, env)
    return env


if __name__ == '__main__':
    print(Run("connect A(100, 200) B(500, 300)"))
    print(Run("establish Rectangular_Coordinates(O(0,0), OA, OB, OA)"))

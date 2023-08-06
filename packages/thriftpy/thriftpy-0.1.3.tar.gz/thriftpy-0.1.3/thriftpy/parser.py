# -*- coding: utf-8 -*-
# flake8: noqa

import functools
import itertools
import types

import pyparsing as pa

from .thrift import TType, TPayload, TException


def _or(*iterable):
    return functools.reduce(lambda x, y: x | y, iterable)


def parse(schema):
    result = {}

    # constants
    LPAR, RPAR, LBRACK, RBRACK, LBRACE, RBRACE, LABRACK, RABRACK, COLON, SEMI, COMMA, EQ = map(pa.Suppress, "()[]{}<>:;,=")

    # keywords
    _typedef, _const, _enum, _struct, _union, _exception, _service = map(pa.Keyword, ("typedef", "const", "enum", "struct", "union", "exception", "service"))

    # comment match
    single_line_comment = (pa.Suppress("//") | pa.Suppress("#")) + pa.restOfLine

    # general tokens
    identifier = pa.Word(pa.alphanums + '_')

    # general value
    value = pa.Forward()
    nums_ = pa.Word(pa.nums)
    integer_ = nums_.setParseAction(lambda s, l, t: [int(t[0])])
    double_ = pa.Combine(nums_ + '.' + nums_).setParseAction(lambda s, l, t: [float(t[0])])
    string_ = pa.quotedString.setParseAction(pa.removeQuotes)
    list_ = pa.Group(LBRACK + pa.delimitedList(value) + RBRACK).setParseAction(lambda s, l, t: t.asList())
    value << _or(double_, integer_, string_, list_)

    # scan for possible user defined types
    _typedef_prefix = _typedef + identifier + pa.Optional(pa.nestedExpr(opener='<', closer='>'))
    scan_utypes = _or(_typedef_prefix, _enum, _struct, _exception, _union) + identifier
    utypes = map(pa.Keyword, (t[-1] for t, _, _ in scan_utypes.scanString(schema)))

    # ttypes
    ttype = pa.Forward()
    t_list = pa.Group(pa.Keyword("list")("ttype") + LABRACK + ttype('v') + RABRACK)
    t_map = pa.Group(pa.Keyword("map")("ttype") + LABRACK + ttype('k') + COMMA + ttype('v') + RABRACK)
    orig_types = _or(t_list, t_map, *map(pa.Keyword, ("bool", "byte", "i16", "i32", "i64", "double", "string", "binary")))
    ttype << _or(orig_types, *utypes)

    # typedef parser
    typedef = _typedef + orig_types("ttype") + identifier("name")
    result["typedefs"] = {t.name: t.ttype for t, _, _ in typedef.scanString(schema)}

    # const parser
    const = _const + ttype("ttype") + identifier("name") + EQ + value("value")
    result["consts"] = {c.name: c.value for c, _, _ in const.scanString(schema)}

    # enum parser
    enum_value = pa.Group(identifier('name') + pa.Optional(EQ + integer_('value')) + pa.Optional(COMMA))
    enum_list = pa.Group(pa.ZeroOrMore(enum_value))("members")
    enum = _enum + identifier("name") + LBRACE + enum_list + RBRACE
    enum.ignore(single_line_comment)
    result["enums"] = {e.name: e for e, _, _ in enum.scanString(schema)}

    # struct parser
    category = _or(*map(pa.Literal, ("required", "optional")))
    struct_field = pa.Group(integer_("id") + COLON + pa.Optional(category) + ttype("ttype") + identifier("name") + pa.Optional(EQ + value("value")) + pa.Optional(_or(SEMI, COMMA)))
    struct_members = pa.Group(pa.ZeroOrMore(struct_field))("members")
    struct = _or(_struct, _union) + identifier("name") + LBRACE + struct_members + RBRACE
    struct.ignore(single_line_comment)
    # struct defines is ordered
    result["structs"] = [s for s, _, _ in struct.scanString(schema)]

    # exception parser
    exception = _exception + identifier("name") + LBRACE + struct_members + RBRACE
    exception.ignore(single_line_comment)
    result["exceptions"] = [s for s, _, _ in exception.scanString(schema)]

    # service parser
    ftype = _or(ttype, pa.Keyword("void"))
    api_param = pa.Group(integer_("id") + COLON + ttype("ttype") + identifier("name") + pa.Optional(_or(SEMI, COMMA)))
    api_params = pa.Group(pa.ZeroOrMore(api_param))
    service_api = pa.Group(ftype("ttype") + identifier("name") + LPAR + api_params("params") + RPAR + pa.Optional(pa.Keyword("throws") + LPAR + api_params("throws") + RPAR) + pa.Optional(_or(SEMI, COMMA)))
    service_apis = pa.Group(pa.ZeroOrMore(service_api))("apis")
    service = _service + identifier("name") + LBRACE + service_apis + RBRACE
    service.ignore(single_line_comment)
    service.ignore(pa.cStyleComment)
    result["services"] = [s for s, _, _ in service.scanString(schema)]

    return result


def load(thrift_file):
    module_name = thrift_file[:thrift_file.find('.')]
    with open(thrift_file, 'r') as f:
        result = parse(f.read())
    struct_names = [s.name for s in itertools.chain(result["structs"],
                                                    result["exceptions"])]

    # load thrift schema as module
    thrift_schema = types.ModuleType(module_name)
    _type = lambda n, o: type(n, (o, ), {"__module__": module_name})

    def _ttype(t):
        if isinstance(t, str):
            if t in struct_names:
                return TType.STRUCT, getattr(thrift_schema, t)
            elif t in result["enums"]:
                return TType.I32
            elif t in result["typedefs"]:
                return _ttype(result["typedefs"][t])
            else:
                return getattr(TType, t.upper())

        if t.ttype == "list":
            return TType.LIST, _ttype(t.v)
        elif t.ttype == "map":
            return TType.MAP, (_ttype(t.k), _ttype(t.v))
        else:
            raise Exception("ttype parse error: {0}".format(t))

    def _ttype_spec(ttype, name):
        ttype = _ttype(ttype)
        if isinstance(ttype, int):
            return ttype, name
        else:
            return ttype[0], name, ttype[1]

    # load consts
    for name, value in result["consts"].items():
        setattr(thrift_schema, name, value)

    # load enums
    for name, enum in result["enums"].items():
        attrs = {"__module__": module_name}
        value = 0
        for m in enum.members:
            if m.value != '':
                value = int(m.value)
            attrs[m.name] = value
            value += 1
        enum_cls = type(name, (object, ), attrs)
        setattr(thrift_schema, enum.name, enum_cls)

    # load structs/unions
    for struct in result["structs"]:
        attrs = {"__module__": module_name}
        thrift_spec, default_spec = {}, []
        for m in struct.members:
            thrift_spec[int(m.id)] = _ttype_spec(m.ttype, m.name)
            default_spec.append((m.name, m.value or None))
        attrs["thrift_spec"] = thrift_spec
        attrs["default_spec"] = sorted(default_spec)
        struct_cls = type(struct.name, (TPayload, ), attrs)
        setattr(thrift_schema, struct.name, struct_cls)

    # load exceptions
    for exc in result["exceptions"]:
        attrs = {"__module__": module_name}
        thrift_spec, default_spec = {}, []
        for m in exc.members:
            thrift_spec[int(m.id)] = _ttype_spec(m.ttype, m.name)
            default_spec.append((m.name, m.value or None))
        attrs["thrift_spec"] = thrift_spec
        attrs["default_spec"] = sorted(default_spec)
        exc_cls = type(exc.name, (TException, ), attrs)
        setattr(thrift_schema, exc.name, exc_cls)

    # load services
    for service in result["services"]:
        service_cls = _type(service.name, object)
        thrift_services = []
        for api in service.apis:
            thrift_services.append(api.name)

            # generate default spec from thrift spec
            _default_spec = lambda s: [(s[k][1], None) for k in sorted(s)]

            # api args payload
            args_name = "%s_args" % api.name
            args_attrs = {"__module__": module_name}

            args_thrift_spec = {}
            for param in api.params:
                args_thrift_spec[int(param.id)] = _ttype_spec(param.ttype,
                                                              param.name)
            args_attrs["thrift_spec"] = args_thrift_spec
            args_attrs["default_spec"] = _default_spec(args_thrift_spec)
            args_cls = type(args_name, (TPayload, ), args_attrs)
            setattr(service_cls, args_name, args_cls)

            # api result payload
            result_name = "%s_result" % api.name
            result_attrs = {"__module__": module_name}

            if api.ttype == "void":
                result_thrift_spec = {}
            else:
                result_thrift_spec = {0: _ttype_spec(api.ttype, "success")}

            if hasattr(api, "throws"):
                for t in api.throws:
                    result_thrift_spec[int(t.id)] = _ttype_spec(t.ttype,
                                                                t.name)

            result_attrs["thrift_spec"] = result_thrift_spec
            result_attrs["default_spec"] = _default_spec(result_thrift_spec)
            result_cls = type(result_name, (TPayload, ), result_attrs)
            setattr(service_cls, result_name, result_cls)

        setattr(service_cls, "thrift_services", thrift_services)
        setattr(thrift_schema, service.name, service_cls)

    return thrift_schema

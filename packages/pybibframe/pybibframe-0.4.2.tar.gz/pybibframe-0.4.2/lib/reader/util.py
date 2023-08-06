from enum import Enum #https://docs.python.org/3.4/library/enum.html

from versa.pipeline import *
from versa import I, VERSA_BASEIRI, ORIGIN, RELATIONSHIP, TARGET, ATTRIBUTES

from bibframe.contrib.datachefids import slugify, idgen, FROM_EMPTY_HASH


#FIXME: Make proper use of subclassing (implementation derivation)
class bfcontext(context):
    def __init__(self, origin, rel, linkset, linkspace, base=None, hashidgen=None, existing_ids=None, logger=None):
        self.origin = origin
        self.rel = rel
        self.linkset = linkset
        self.linkspace = linkspace
        self.base = base
        self.hashidgen = hashidgen
        self.existing_ids = existing_ids
        self.logger = logger
        return

    def copy(self, origin=None, rel=None, linkset=None, linkspace=None, base=None, hashidgen=None, existing_ids=None, logger=None):
        origin = origin if origin else self.origin
        rel = rel if rel else self.rel
        linkset = linkset if linkset else self.linkset
        linkspace = linkspace if linkspace else self.linkspace
        base = base if base else self.base
        logger = logger if logger else self.logger
        hashidgen = hashidgen if hashidgen else self.hashidgen
        existing_ids = existing_ids if existing_ids else self.existing_ids
        return bfcontext(origin, rel, linkset, linkspace, base=base, logger=logger, hashidgen=hashidgen, existing_ids=existing_ids)


class action(Enum):
    replace = 1


class origin_class(Enum):
    work = 1
    instance = 2


class base_transformer(object):
    def __init__(self, use_origin):
        self._use_origin = use_origin
        return

    def initialize(self, hashidgen, existing_ids):
        self._hashidgen = hashidgen
        self._existing_ids = existing_ids
        return

    #Functions that take a prototype link set and generate a transformed link set

    def rename(self, rel=None):
        '''
        Update the label of the relationship to be added to the link space
        '''
        def _rename(ctx, workid, iid):
            new_o = {origin_class.work: workid, origin_class.instance: iid}[self._use_origin]
            newlinkset = []
            #Just work with the first provided statement, for now
            (o, r, t, a) = ctx.linkset[0]
            newlinkset.append((I(new_o), I(iri.absolutize(rel, ctx.base)), t, {}))
            return newlinkset
        return _rename

    def materialize(self, typ, rel, unique=None, mr_properties=None):
        '''
        Create a new resource related to the origin
        '''
        mr_properties = mr_properties or {}
        def _materialize(ctx, workid, iid):
            _typ = typ(ctx) if callable(typ) else typ
            _rel = rel(ctx) if callable(rel) else rel
            rels = _rel if isinstance(_rel, list) else [_rel]
            new_o = {origin_class.work: workid, origin_class.instance: iid}[self._use_origin]
            newlinkset = []
            #Just work with the first provided statement, for now
            (o, r, t, a) = ctx.linkset[0]
            if unique is not None:
                objid = self._hashidgen.send([_typ] + unique(ctx))
            else:
                objid = next(self._hashidgen)
            for _rel in rels:
                if _rel:
                    #FIXME: Fix this properly, by slugifying & making sure slugify handles all numeric case (prepend '_')
                    if _rel.isdigit(): _rel = '_' + _rel
                    newlinkset.append((I(new_o), I(iri.absolutize(_rel, ctx.base)), I(objid), {}))
            if objid not in self._existing_ids:
                if _typ: newlinkset.append((I(objid), VTYPE_REL, I(iri.absolutize(_typ, ctx.base)), {}))
                #FIXME: Should we be using Python Nones to mark blanks, or should Versa define some sort of null resource?
                for k, v in mr_properties.items():
                    k = k(ctx) if callable(k) else k
                    newctx = ctx.copy(origin=I(objid), rel=k)
                    #newctx = ctx.copy(origin=I(objid), rel=rels[0], linkset=[(I(objid), I(iri.absolutize(_rel, ctx.base)), None, {})])
                    v = v(newctx) if callable(v) else v
                    if isinstance(v, list):
                        newlinkset.extend(v)
                    elif k and v is not None:
                        #FIXME: Fix this properly, by slugifying & making sure slugify handles all numeric case (prepend '_')
                        if k.isdigit(): k = '_' + k
                        newlinkset.append((I(objid), I(iri.absolutize(k, newctx.base)), v, {}))
                self._existing_ids.add(objid)
            return newlinkset
        return _materialize


def all_subfields(ctx):
    '''
    Utility to return a hash from all subfields mentioned in the MARC prototype link

    :param ctx: Versa context used in processing (e.g. includes the prototype link
    :return: Tuple of key/value tuples from the attributes; suitable for hashing
    '''
    return sorted(list(ctx.linkset[0][ATTRIBUTES].items()))


def subfield(key):
    '''
    Action function generator to look up a MARC subfield at processing time based on the given prototype linkset

    :param key: Key for looking up desired subfield value
    :return: Versa action function to do the actual work
    '''
    def _subfield(ctx):
        '''
        Versa action function Utility to return a hash from all subfields mentioned in the MARC prototype link

        :param ctx: Versa context used in processing (e.g. includes the prototype link
        :return: Tuple of key/value tuples from the attributes; suitable for hashing
        '''
        return ctx.linkset[0][ATTRIBUTES].get(key)
    return _subfield


def values(*rels):
    '''
    Action function generator to multiplex a relationship at processing time

    :param rels: List of relationships to establish
    :return: Versa action function to do the actual work
    '''
    def _values(ctx):
        '''
        Versa action function Utility to specify a list of relationships

        :param ctx: Versa context used in processing (e.g. includes the prototype link
        :return: Tuple of key/value tuples from the attributes; suitable for hashing
        '''
        computed_rels = [ rel(ctx) if callable(rel) else rel for rel in rels ]
        return computed_rels
    return _values


def normalizeparse(text_in):
    '''
    Action function generator to multiplex a relationship at processing time

    :param rels: List of relationships to establish
    :return: Versa action function to do the actual work
    '''
    def _normalizeparse(ctx):
        '''
        Versa action function Utility to specify a list of relationships

        :param ctx: Versa context used in processing (e.g. includes the prototype link
        :return: Tuple of key/value tuples from the attributes; suitable for hashing
        '''
        _text_in = text_in(ctx) if callable(text_in) else text_in
        return slugify(_text_in, False) if _text_in else ''
    return _normalizeparse


def ifexists(test, value):
    '''
    Action function generator to multiplex a relationship at processing time

    :param rels: List of relationships to establish
    :return: Versa action function to do the actual work
    '''
    def _ifexists(ctx):
        '''
        Versa action function Utility to specify a list of relationships

        :param ctx: Versa context used in processing (e.g. includes the prototype link
        :return: Tuple of key/value tuples from the attributes; suitable for hashing
        '''
        _test = test(ctx) if callable(test) else test
        _value = value(ctx) if callable(value) else value
        return _value if _test else None
    return _ifexists


def materialize(typ, unique=None, mr_properties=None):
    '''
    Create a new resource related to the origin
    '''
    mr_properties = mr_properties or {}
    def _materialize(ctx):
        _typ = typ(ctx) if callable(typ) else typ
        #rels = [ link[RELATIONSHIP] for link in ctx.linkset ]
        newlinkset = []
        #Just work with the first provided statement, for now
        (o, r, t, a) = ctx.linkset[0]
        if unique is not None:
            objid = ctx.hashidgen.send([_typ, unique(ctx)])
        else:
            objid = next(self._hashidgen)
        #for rel in rels:
        if ctx.rel:
            #FIXME: Fix this properly, by slugifying & making sure slugify handles all numeric case (prepend '_')
            rel = '_' + ctx.rel if ctx.rel.isdigit() else ctx.rel
            newlinkset.append((I(ctx.origin), I(iri.absolutize(rel, ctx.base)), I(objid), {}))
        if objid not in ctx.existing_ids:
            if _typ: newlinkset.append((I(objid), VTYPE_REL, I(iri.absolutize(_typ, ctx.base)), {}))
            #FIXME: Should we be using Python Nones to mark blanks, or should Versa define some sort of null resource?
            for k, v in mr_properties.items():
                k = k(ctx) if callable(k) else k
                newctx = ctx.copy(origin=I(objid), rel=k)
                #newctx = ctx.copy(origin=I(objid), rel=rels[0], linkset=[(I(objid), I(iri.absolutize(rel, ctx.base)), None, {})])
                v = v(newctx) if callable(v) else v
                if isinstance(v, list):
                    newlinkset.extend(v)
                elif k and v is not None:
                    #FIXME: Fix this properly, by slugifying & making sure slugify handles all numeric case (prepend '_')
                    if k.isdigit(): k = '_' + k
                    newlinkset.append((I(objid), I(iri.absolutize(k, newctx.base)), v, {}))
            #To avoid losing info include subfields which come via Versa attributes
            for k, v in ctx.linkset[0][ATTRIBUTES].items():
                newlinkset.append((I(objid), I(iri.absolutize('sf-' + k, ctx.base)), v, {}))
            ctx.existing_ids.add(objid)
        return newlinkset
    return _materialize


onwork = base_transformer(origin_class.work)
oninstance = base_transformer(origin_class.instance)

def initialize(hashidgen=None, existing_ids=None):
    onwork.initialize(hashidgen, existing_ids)
    oninstance.initialize(hashidgen, existing_ids)


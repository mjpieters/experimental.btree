from logging import getLogger

logger = getLogger('experimental.btree')

SMALLSETSIZE = 200
BIGSMALLRATIO = 20

HAS_COPTIMIZATIONS = True
try:
    from experimental.btree.difference import ciidifference
    from experimental.btree.intersection import ciiintersection
except ImportError:
    HAS_COPTIMIZATIONS = False


def patch_intersection(treetype, settype, module=None):

    setintersection = treetype.intersection

    def intersection(o1, o2):
        if not o2 or not o1:
            # Avoid len of unsized or zero division
            return setintersection(o1, o2)

        s1 = type(o1) is settype
        s2 = type(o2) is settype

        if s1 and s2:
            return setintersection(o1, o2)
        elif s1 or s2:
            # Only do this if one of them is a set, we are slower at treesets.
            # We don't check the size of the treeset, so we sometimes loop over
            # a very small one, but there's no way to tell, without loading it.
            if s1 and len(o1) < SMALLSETSIZE:
                small = o1
                big = o2
            elif s2 and len(o2) < SMALLSETSIZE:
                small = o1
                big = o2
            else:
                return setintersection(o1, o2)

            new = settype()
            ins = new.insert
            has = big.has_key
            for i in small:
                if has(i):
                    ins(i)
            return new
        return setintersection(o1, o2)

    if not hasattr(treetype, '_old_intersection'):
        treetype._old_intersection = treetype.intersection
        treetype.intersection = intersection
        logger.debug('Patched %s' % str(treetype.intersection))
    if module is not None and not hasattr(module, '_old_intersection'):
        module._old_intersection = module.intersection
        module.intersection = intersection
        logger.debug('Patched %s' % str(module.intersection))


def patch_weightedIntersection(treetype, settypes):
    setintersection = treetype.intersection
    weightedsetintersection = treetype.weightedIntersection

    def weightedIntersection(o1, o2, w1=1, w2=1):
        if isinstance(o1, settypes) and isinstance(o2, settypes):
            return (w1+w2), setintersection(o1, o2)
        return weightedsetintersection(o1, o2, w1, w2)

    if not hasattr(treetype, '_old_weightedIntersection'):
        treetype._old_weightedIntersection = treetype.weightedIntersection
        treetype.weightedIntersection = weightedIntersection
        logger.debug('Patched %s' % str(treetype.weightedIntersection))


def patch_difference(treetype, settype, module=None):

    setdifference = treetype.difference

    def difference(o1, o2):
        # Bail out as soon as possible if one or both are None
        if not o1 or not o2:
            return setdifference(o1, o2)
        # Both are real sets, of unknown size
        l1 = len(o1)
        # Difference returns bucket if o1 is btree
        if l1 < SMALLSETSIZE and isinstance(o1, settype):
            l2 = len(o2)
            if l2/l1 > BIGSMALLRATIO:
                new = settype()
                ins = new.insert
                has = o2.has_key
                for i in o1:
                    if not has(i):
                        ins(i)
                return new

        return setdifference(o1, o2)

    if not hasattr(treetype, '_old_difference'):
        treetype._old_difference = treetype.difference
        treetype.difference = difference
        logger.debug('Patched %s' % str(treetype.difference))
    if module is not None and not hasattr(module, '_old_difference'):
        module._old_difference = module.difference
        module.difference = difference
        logger.debug('Patched %s' % str(module.difference))


def patch_cintersection(module, method):
    if not hasattr(module, '_old_intersection'):
        module._old_intersection = module.intersection
        module.intersection = method
        logger.debug('Patched %s' % str(module.intersection))


def patch_cdifference(module, method):
    if not hasattr(module, '_old_difference'):
        module._old_difference = module.difference
        module.difference = method
        logger.debug('Patched %s' % str(module.difference))


def apply(no_coptimizations=False):
    global HAS_COPTIMIZATIONS
    if no_coptimizations:
        HAS_COPTIMIZATIONS = False

    from BTrees.IIBTree import IISet, IITreeSet
    from BTrees import IIBTree
    patch_weightedIntersection(IIBTree, (IISet, IITreeSet))

    from Products.ExtendedPathIndex import ExtendedPathIndex
    from Products.PluginIndexes.common import UnIndex
    from Products.PluginIndexes.DateIndex import DateIndex
    from Products.PluginIndexes.DateRangeIndex import DateRangeIndex
    from Products.PluginIndexes.KeywordIndex import KeywordIndex
    from Products.PluginIndexes.PathIndex import PathIndex
    from Products.ZCatalog import Catalog

    # We leave out the BooleanIndex on purpose - our code is much slower on it
    if HAS_COPTIMIZATIONS:
        patch_cdifference(IIBTree, ciidifference)
        patch_cdifference(DateRangeIndex, ciidifference)
        patch_cintersection(IIBTree, ciiintersection)
        patch_cintersection(Catalog, ciiintersection)
        patch_cintersection(DateIndex, ciiintersection)
        patch_cintersection(DateRangeIndex, ciiintersection)
        patch_cintersection(ExtendedPathIndex, ciiintersection)
        patch_cintersection(PathIndex, ciiintersection)
        patch_cintersection(UnIndex, ciiintersection)
    else:
        patch_difference(IIBTree, IISet)
        patch_difference(IIBTree, IISet, DateRangeIndex)
        patch_intersection(IIBTree, IISet, Catalog)
        patch_intersection(IIBTree, IISet, DateIndex)
        patch_intersection(IIBTree, IISet, DateRangeIndex)
        patch_intersection(IIBTree, IISet, ExtendedPathIndex)
        patch_intersection(IIBTree, IISet, PathIndex)
        patch_intersection(IIBTree, IISet, UnIndex)

    from BTrees.IOBTree import IOSet
    from BTrees import IOBTree
    patch_intersection(IOBTree, IOSet)
    patch_difference(IOBTree, IOSet)

    from BTrees.OIBTree import OISet, OITreeSet
    from BTrees import OIBTree
    patch_intersection(OIBTree, OISet)
    patch_weightedIntersection(OIBTree, (OISet, OITreeSet))
    patch_difference(OIBTree, OISet)

    from BTrees.OOBTree import OOSet
    from BTrees import OOBTree
    patch_intersection(OOBTree, OOSet)
    patch_difference(OOBTree, OOSet)
    patch_difference(OOBTree, OOSet, KeywordIndex)


def unpatch(treetype):
    old = getattr(treetype, '_old_intersection', None)
    if old is None:
        return
    treetype.intersection = old
    del treetype._old_intersection
    logger.debug('Removing patch from %s' % str(treetype.intersection))
    treetype.difference = treetype._old_difference
    del treetype._old_difference
    logger.debug('Removing patch from %s' % str(treetype.difference))
    if hasattr(treetype, 'weightedIntersection'):
        treetype.weightedIntersection = treetype._old_weightedIntersection
        del treetype._old_weightedIntersection
        logger.debug('Removing patch from %s' % str(treetype.weightedIntersection))

def unapply():
    from BTrees import IIBTree
    unpatch(IIBTree)

    from BTrees import IOBTree
    unpatch(IOBTree)

    from BTrees import OIBTree
    unpatch(OIBTree)

    from BTrees import OOBTree
    unpatch(OOBTree)

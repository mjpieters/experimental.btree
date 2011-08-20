from time import time
import unittest

from experimental.btree import setpatches
setpatches.apply(no_coptimizations=True)
from BTrees.IIBTree import intersection as intersection2
from BTrees.IIBTree import difference as difference2

setpatches.unapply()

from BTrees.IIBTree import intersection
from BTrees.IIBTree import difference

from BTrees.IIBTree import IISet, IITreeSet

try:
    from experimental.btree.difference import ciidifference
    from experimental.btree.intersection import ciiintersection
except ImportError:
    ciidifference = None
    ciiintersection = None

SMALLSETSIZE = 30
BIGSETSIZE = 1000000
LOOP = 100

class TestIntersection(unittest.TestCase):

    level = 2

    def timing(self, small, large, text=''):
        new = 0.0
        old = 0.0
        c = 0.0
        loop = LOOP
        for i in xrange(loop):
            start = time()
            intersection2(small, large)
            new+=(time()-start)

            start = time()
            intersection(small, large)
            old+=(time()-start)

            start = time()
            ciiintersection(small, large)
            c+=(time()-start)

        new_ratio = old / new
        c_ratio = old / c

        new_report = False
        if new_ratio <= 0.4 or new_ratio > 2:
            new_report = True
        c_report = False
        if c_ratio <= 0.8 or c_ratio > 1.2:
            c_report = True

        if c_report or new_report:
            print
            print text
            print 'Old x%s: %.6f' % (loop, old)
            print 'New x%s: %.6f - factor: %.2f' % (loop, new, new_ratio)
            print 'Cyt x%s: %.6f - factor: %.2f' % (loop, c, c_ratio)

    def test_None(self):
        bigsize = BIGSETSIZE
        large = IITreeSet(xrange(bigsize))
        self.timing(large, None, 'Intersection large, None')
        self.timing(None, large, 'Intersection None, large')

    def test_empty(self):
        bigsize = BIGSETSIZE
        smallsize = 0
        small = IISet(xrange(smallsize))
        large = IITreeSet(xrange(bigsize))

        self.timing(small, large, 'Intersection empty set + large treeset')
        self.timing(large, small, 'Intersection large treeset + empty set')

        small = IITreeSet(xrange(smallsize))
        large = IISet(xrange(bigsize))
        self.timing(small, large, 'Intersection empty tree set + large set')
        self.timing(large, small, 'Intersection large set + empty tree set')

    def test_heavy_start(self):
        bigsize = BIGSETSIZE
        smallsize = SMALLSETSIZE

        small = IISet(xrange(smallsize))
        large = IITreeSet(xrange(smallsize))
        self.timing(small, large,
            'Intersection small set low values + small treeset')
        self.timing(large, small,
            'Intersection small treeset + small set low values')

        small = IISet(xrange(smallsize))
        large = IITreeSet(xrange(bigsize))
        self.timing(small, large,
            'Intersection small set low values + large treeset')
        self.timing(large, small,
            'Intersection large treeset + small set low values')

        small = IISet(xrange(smallsize))
        large = IISet(xrange(bigsize))
        self.timing(small, large,
            'Intersection small set low values + large set')
        self.timing(large, small,
            'Intersection large set + small set low values')

        small = IITreeSet(xrange(smallsize))
        large = IISet(xrange(bigsize))
        self.timing(small, large,
            'Intersection small treeset + large set')
        self.timing(large, small,
            'Intersection large set + small treeset')

    def test_heavy_end(self):
        bigsize = BIGSETSIZE
        smallsize = SMALLSETSIZE

        small = IISet(xrange(bigsize-smallsize,bigsize))
        large = IITreeSet(xrange(smallsize))
        self.timing(small, large,
            'Intersection small set high values + small treeset')
        self.timing(large, small,
            'Intersection small treeset + small set high values')

        small = IISet(xrange(bigsize-smallsize,bigsize))
        large = IITreeSet(xrange(bigsize))
        self.timing(small, large,
            'Intersection small set high values + large treeset')
        self.timing(large, small,
            'Intersection large treeset + small set high values')

        small = IISet(xrange(bigsize-smallsize,bigsize))
        large = IISet(xrange(bigsize))
        self.timing(small, large,
            'Intersection small set high values + large set')
        self.timing(large, small,
            '\nIntersection large set + small set high values')

    def test_even_dist(self):
        bigsize = BIGSETSIZE
        smallsize = SMALLSETSIZE

        small = IISet(xrange(0, bigsize, bigsize/smallsize))
        large = IITreeSet(xrange(smallsize))
        self.timing(small, large,
            'Intersection small set even distribution + small treeset')
        self.timing(large, small,
            'Intersection small treeset + small set even distribution')

        small = IISet(xrange(0, bigsize, bigsize/smallsize))
        large = IITreeSet(xrange(bigsize))
        self.timing(small, large,
            'Intersection small set even distribution + large treeset')
        self.timing(large, small,
            'Intersection large treeset + small set even distribution')

        small = IISet(xrange(0, bigsize, bigsize/smallsize))
        large = IISet(xrange(bigsize))

        self.timing(small, large,
            'Intersection small set even distribution + large set')
        self.timing(large, small,
            'Intersection large set, small set even distribution')

    def test_small(self):
        smallsize = SMALLSETSIZE
        small = IITreeSet(xrange(smallsize))
        large = IITreeSet(xrange(smallsize))
        self.timing(small, large, 'Intersection small tree sets')

        small = IISet(xrange(smallsize))
        large = IISet(xrange(smallsize))
        self.timing(small, large, 'Intersection small sets')

    def test_large(self):
        bigsize = BIGSETSIZE / 10
        small = IITreeSet(xrange(bigsize))
        large = IITreeSet(xrange(bigsize))
        self.timing(small, large, 'Intersection Large tree sets')

        small = IISet(xrange(bigsize))
        large = IISet(xrange(bigsize))
        self.timing(small, large, 'Intersection Large sets')


class TestDifference(unittest.TestCase):

    level = 2

    def timing(self, small, large):
        new = 0.0
        old = 0.0
        c = 0.0
        loop = LOOP
        for i in xrange(10):
            start = time()
            difference(small, large)
            old+=(time()-start)

            start = time()
            difference2(small, large)
            new+=(time()-start)

            if ciidifference is not None:
                start = time()
                ciidifference(small, large)
                c+=(time()-start)

        print 'Old x%s: %.6f' % (loop, old)
        print 'New x%s: %.6f' % (loop, new)
        if ciidifference is not None:
            print 'Cyt x%s: %.6f - factor: %.2f' % (loop, c, old / c)

    def test_heavy_start(self):
        bigsize = BIGSETSIZE
        smallsize = SMALLSETSIZE
        small = IISet(xrange(smallsize))
        large = IITreeSet(xrange(bigsize))
        print '\nDifference Small set low values + large treeset'
        self.timing(small, large)

        small = IISet(xrange(smallsize))
        large = IISet(xrange(bigsize))
        print '\nDifference Small set low values + large set'
        self.timing(small, large)

    def test_heavy_end(self):
        bigsize = BIGSETSIZE
        smallsize = SMALLSETSIZE
        small = IISet(xrange(bigsize-smallsize,bigsize))
        large = IITreeSet(xrange(bigsize))
        print '\nDifference Small set high values + large treeset'
        self.timing(small, large)

        small = IISet(xrange(bigsize-smallsize,bigsize))
        large = IISet(xrange(bigsize))
        print '\nDifference Small set high values + large set'
        self.timing(small, large)

    def test_even_dist(self):
        bigsize = BIGSETSIZE
        smallsize = SMALLSETSIZE
        small = IISet(xrange(0, bigsize, bigsize/smallsize))
        large = IITreeSet(xrange(bigsize))
        print '\nDifference Small set even distribution + large treeset'
        self.timing(small, large)

        small = IISet(xrange(0, bigsize, bigsize/smallsize))
        large = IISet(xrange(bigsize))
        print '\nDifference Small set even distribution + large set'
        self.timing(small, large)

    def test_large(self):
        bigsize = BIGSETSIZE
        small = IITreeSet(xrange(bigsize))
        large = IITreeSet(xrange(bigsize))
        print '\nDifference Large sets'
        self.timing(small, large)

    def test_lookup(self):
        bigsize = 1000000
        smallsize = 1000
        large = IISet(xrange(bigsize))
        small = IISet(xrange(0, bigsize, bigsize/smallsize))

        start = time()
        for i in small:
            large[i]
        print "\ngetitem distributed %.6f" % (time()-start)

        start = time()
        for i in small:
            large[bigsize-1]
        print "getitem end %.6f" % (time()-start)

        start = time()
        for i in small:
            large[0]
        print "getitem start %.6f" % (time()-start)

        start = time()
        for i in small:
            large.has_key(i)
        print "\nhas_key distributed %.6f" % (time()-start)

        start = time()
        for i in small:
            large.has_key(bigsize-1)
        print "has_key end %.6f" % (time()-start)

        start = time()
        for i in small:
            large.has_key(0)
        print "has_key start %.6f" % (time()-start)


    def test_findlargesmallset(self):
        # Test different approaches to finding the large and small set
        bigsize = 10
        smallsize = 2
        o1 = IISet(xrange(bigsize))
        l1 = len(o1)
        o2 = IISet(xrange(0, bigsize, bigsize/smallsize))
        l2 = len(o2)

        # 3 approaches: if/else, sorted and max/min
        def alternative1():
            if l1 < l2:
                ls = l1
                small = o1
                lb = l2
                big = o2
            else:
                ls = l2
                small = o2
                lb = l1
                big = o1
            return (ls, small), (lb, big)

        def alternative2():
            return sorted(((l2,o2), (l1,o1)))

        def alternative3():
            small = min((l2,o2),(l1,o1))
            big = max((l2,o2),(l1,o1))
            return small,big

        self.failUnlessEqual(list(alternative1()), list(alternative2()))
        self.failUnlessEqual(list(alternative1()), list(alternative3()))

        start = time()
        for i in xrange(1000):
            alternative1()
        print '\nif/else took %.6f' % (time()-start)

        start = time()
        for i in xrange(1000):
            alternative2()
        print 'sorted took  %.6f' % (time()-start)

        start = time()
        for i in xrange(1000):
            alternative3()
        print 'minmax took  %.6f' % (time()-start)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestIntersection))
    suite.addTest(makeSuite(TestDifference))
    return suite

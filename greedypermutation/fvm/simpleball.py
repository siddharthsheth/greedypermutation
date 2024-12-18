from ds2.priorityqueue import PriorityQueue
from metricspaces import metric_class


@metric_class
class SimpleBall:
    """
    A SimpleBall has a center, a radius, a numer of points that it contains, and a
    pair of children. This means that each ball is the root of an entire ball
    tree. There is no difference between a ball and a ball tree.

    The difference between Ball and SimpleBall is that Ball also implements
    search methods. SimpleBall, on the other hand, computes approximate node radii.
    """

    def __init__(self, point):
        self.center = point
        self._len = 1
        self.radius = 0
        self.left = None
        self.right = None

    def dist(self, other):
        return self.metric.dist(self.center, other)

    def isleaf(self):
        return self.left is None

    def farthest(self, q):
        """Find the distance to the farthest point to `q`."""
        if self.isleaf():
            return self.dist(q)
        else:
            H = [self]
            best = 0
            while H:
                ball = H.pop()
                best = max(best, ball.dist(q))
                if not ball.isleaf() and ball.dist(q) + ball.radius > best:
                    H.append(ball.left)
                    H.append(ball.right)
            return best

    def approx_radii(self):
        """
        Recursively approximate the `radius` of every ball in the tree rooted at self.
        """
        if not hasattr(self, "scale"):
            raise RuntimeError("Missing scale parameter.")
        if not hasattr(self, "gp"):
            raise RuntimeError("Missing gp-approx parameter.")
        if self.isleaf():
            self.radius = 0
        else:
            self.left.approx_radii()
            self.right.approx_radii()
            # SID: To compute approximate node radii, we need scale and locally greedy parameters
            self.radius = min(
                max(self.left.radius, self.dist(self.right.center) + self.right.radius),
                self.scale * self.gp * self.dist(self.right.center) / (self.scale - 1),
            )

    def exact_radii(self):
        """
        Recursively compute the `radius` of every ball in the tree rooted at self.
        """
        if self.isleaf():
            self.radius = 0
        else:
            self.left.exact_radii()
            self.right.exact_radii()
            # SID: To compute approximate node radii, we need scale and locally greedy parameters
            self.radius = max(self.left.radius, self.right.farthest(self.center))

    def count(self):
        """
        Recursively compute the count of every ball in the tree rooted at self.
        """
        if self.isleaf():
            self._len = 1
        else:
            self.left.count()
            self.right.count()
            self._len = len(self.left) + len(self.right)

    def __len__(self):
        return self._len

    def __iter__(self):
        """
        Iterate over the points.

        Note that the current immplementation is simple, but not as efficient
        asymptotically as the non-recursive approach.  This is an issue with
        recursive iterators.
        """
        if self.isleaf():
            yield self.center
        else:
            yield from self.left
            yield from self.right

    def heap(self):
        """
        Construct and return a heap ordered by decreasing radius.
        The heap is initialized to contain `self`.
        """
        return PriorityQueue([self], key=lambda x: -x.radius)

    def _str(self, s="", tabs=0):
        if self is not None:
            s += tabs * "|\t" + str(self.center) + "\n"
            if not self.isleaf():
                s = self.left._str(s, tabs=tabs + 1)
                s = self.right._str(s, tabs=tabs + 1)
            s += tabs * "|\t" + "\n"
        return s

    def __str__(self):
        return self._str()

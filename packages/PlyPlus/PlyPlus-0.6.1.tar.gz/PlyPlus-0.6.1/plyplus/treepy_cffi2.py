from itertools import islice, chain

import cffi

ffi = cffi.FFI()

decl = """
    typedef wchar_t CHAR;

    typedef enum
    {
        BRANCH,
        LEAF
    } node_type;

    typedef struct node {
       CHAR* data;
       node_type type;

       /* Branch only */
       int n_children;
       struct node** children;

    } node;

    node* tree_create(CHAR* data);
    void node_set_data(node*, CHAR* data);
    void tree_destory(node* tree);
"""

ffi.cdef(decl)
c = ffi.verify(decl+"""
    #include <assert.h>
    #include <stdlib.h>
    #include <wchar.h>

    node* tree_create(CHAR* data)
    {
        assert (data);

        node* n = (node*)malloc(sizeof(node));
        assert (n);

        n->data = (CHAR*)malloc(wcslen(data) * sizeof(CHAR));
        assert (n->data);

        wcscpy(n->data, data);
        n->n_children = 0;
        n->children = NULL;
        return n;
    }

    void node_set_data(node* n, CHAR* data)
    {
        return;
        assert (n);
        assert (data);
        assert (n->data);

        free(n->data);

        n->data = (CHAR*)malloc(wcslen(data) * sizeof(CHAR));
        assert (n->data);
    }

    void tree_destory(node* tree)
    {
        int i;
        for (i=0; i < tree->n_children; i++)
        {
            // tree->children[i].parent = NULL;
            tree_destory( tree->children[i] );
        }

        // assert (!tree->parent);

        free(tree->data);
        free(tree);
    }
""")


_DEBUG = False

_DATA = 0
_NODES = 1

def _join_paths(p1, p2):
    assert isinstance(p1, (tuple, list))
    if not isinstance(p2, (tuple, list)):
        p2 = [p2]
    return p1 + type(p1)(p2)

def _lslice_path(p):
    return p[0], islice(p, 1, None)
def _rslice_path(p):
    return islice(p, len(p)-1), p[-1]

class NodeInterface(object):
    def _pretty(self, indent):
        l = [ '%s%s%s' % (' |'*indent, '-- ' if indent else '', self.data) ]
        l += chain(*[child._pretty(indent+1) for child in self.children])
        return l

    def pretty(self, indent=0):
        return '\n'.join(self._pretty(indent))

    def _get_data(self):
        return ffi.string(self.cnode.data)
    def _set_data(self, data):
        assert isinstance(data, (str, unicode))
        c.node_set_data(self.cnode, ffi.new('CHAR[]', unicode(data)))
    data = property(_get_data, _set_data, doc="Data of node")


    def expand_kids_by_index(self, *indices):   # XXX: remove!
        for i in sorted(indices, reverse=True): # reverse so that changing tail won't affect indices
            kid = self.children[i]
            self.children[i:i+1] = kid.children

    def __eq__(self, other):
        return self.data == other.data and self.children == other.children
    def __ne__(self, other):
        return not (self.data == other.data)
    def __repr__(self):
        return '%s(%s, %s)' % (type(self).__name__, self.data, list(self.children))
    def __str__(self):
        return '%s%s' % (self.data, list(self.children))


class Node(NodeInterface):
    def __init__(self, root, path, raw_node):
        if _DEBUG:
            assert root and raw_node, (root, raw_node)
            assert path is not None
            assert isinstance(raw_node, list), raw_node     # XXX
        self.root = root
        self.path = path
        self.raw_node = raw_node
        self._children = Children(self)

    def become_node_of(self, tree):     # XXX remove!!!
        return self

    @property
    def children(self):
        return self._children

class ChildrenInterface(object):
    def get_raw_node(self, path):
        if isinstance(path, (tuple, list, islice)):
            p_first, p_rest = _lslice_path(path)
            node = self.raw_nodes[p_first]
            for p in p_rest:
                node = node[_NODES][p]
        else:
            node = self.raw_nodes[path]

        if _DEBUG:
            assert isinstance(node, list), (node, path, self.raw_nodes)     # XXX
        return node


class Children(ChildrenInterface):
    def __init__(self, node):
        self.node = node
        self.cnode = node.cnode
        # if _DEBUG:
        #     assert all(isinstance(n, list) for n in self.raw_nodes)     # XXX

    def append(self, tree):
        if _DEBUG:
            assert isinstance(tree, (Tree, Node)), repr(tree)   # XXX just tree
        # new_node = tree.become_node_of(self.node.root).raw_node
        # assert isinstance(new_node, list)
        # self.raw_nodes.append(new_node)
    def insert(self, index, tree):
        assert isinstance(tree, (Tree, Node)), repr(tree)   # XXX just tree
        new_node = tree.become_node_of(self.node.root).raw_node
        assert isinstance(new_node, list)
        self.raw_nodes.insert(index, new_node)
    def extend(self, iterable):
        for tree in iterable:
            self.append(tree)
        return self
    def __len__(self):
        return len(self.raw_nodes)
    def __nonzero__(self):
        return len(self)
    def __iter__(self):
        N = Node
        root = self.node.root
        return (N(root, i, rn) for i, rn in enumerate(self.raw_nodes))
    def list_of_branches(self):
        N = Node
        root = self.node.root
        return [N(root, i, rn) for i, rn in enumerate(self.raw_nodes) if rn[_NODES]]
    def __getitem__(self, path):
        if isinstance(path, int):   # Just an optimization -- the general case can handle it
            return Node(self.node.root, path, self.raw_nodes[path])

        if isinstance(path, slice):     # TODO make better
            return [Node(self.node.root, i, rn) for i, rn in enumerate(self.raw_nodes[path])]

        return Node(self.node.root, path, self.get_raw_node(path))
    def __setitem__(self, path, tree):
        if isinstance(path, slice):     # TODO make better
            raw_nodes = [n.raw_node for n in tree]
            assert all(isinstance(n, list) for n in raw_nodes)
            self.raw_nodes[path] = raw_nodes
            return

        assert isinstance(tree, Tree)

        new_node = tree.become_node_of(self.node.root).raw_node
        assert isinstance(new_node, list)
        if isinstance(path, int):
            self.raw_nodes[path] = new_node
        else:
            p_rest, p_last = _rslice_path(path)
            self.get_raw_node(p_rest)[_NODES][p_last] = new_node

    def __delitem__(self, path):
        p_rest, p_last = _rslice_path(path)
        del self.get_raw_node(p_rest)[_NODES][p_last]

    __iadd__ = extend

    def __eq__(self, other):
        return all(t1==t2 for t1, t2 in zip(self, other))


class Tree(NodeInterface):
    def __init__(self, data, nodes=()):
        assert isinstance(data, (str, unicode)), data

        if not isinstance(nodes, (list, tuple, ChildrenInterface)):
            raise TypeError("Type %r not supported for nodes" % nodes)

        self.cnode = c.tree_create(ffi.new('CHAR[]', unicode(data)))

        self._children = Children(self)

        for n in nodes:
            if isinstance(n, (Node,Tree)):  # XXX just tree
                self.children.append(n)
            else:
                self.children.append(Tree(n))

    def __del__(self):
        if hasattr(self, 'cnode'):
            c.tree_destory(self.cnode)

    @property
    def children(self):
        return self._children

    @property
    def root(self):
        return self

    def become_node_of(self, tree):
        return self     # TODO


class Visitor(object):
    def visit(self, tree):
        open_queue = [tree]
        queue = []

        while open_queue:
            node = open_queue.pop()
            queue.append(node)
            open_queue += node.children.list_of_branches()

        for node in reversed(queue):
            # assert node.children
            getattr(self, node.data, self.__default__)(node)

    def __default__(self, tree):
        pass

class Visitor_Recurse(object):

    def visit(self, tree):
        self._visit(tree)
        return tree

    def _visit(self, tree):
        if not tree.children:
            return

        pre_f = getattr(self, u'pre_' + tree.data, None)
        if pre_f:
            pre_f(tree)

        for branch in tree.children.list_of_branches():
            self._visit(branch)

        f = getattr(self, tree.data, self.__default__)
        return f(tree)

    def __default__(self, tree):
        pass

class Transformer(object):
    def transform2(self, tree):
        return self._transform(tree)

    def _transform(self, tree):
        if not tree.children:
            return tree

        pre_f = getattr(self, u'pre_' + tree.data, None)
        if pre_f:
            return pre_f(tree)

        branches = [
                self._transform(branch) if branch.children else branch
                for branch in tree.children
            ]

        #assert isinstance(tree.data, (str, unicode))    # XXX remove!
        new_tree = Tree(tree.data, branches)

        f = getattr(self, new_tree.data, self.__default__)
        return f(new_tree)

    def __default__(self, tree):
        return tree


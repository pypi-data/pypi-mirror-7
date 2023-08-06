import os
import sys
import inspect
import traceback
import logging
import re

from spykeutils.plugin.analysis_plugin import AnalysisPlugin


logger = logging.getLogger('spykeviewer')


def _compare_nodes(x, y):
    """ Directory Nodes should come first, then sort alphabetically.
    """
    ret = int(isinstance(y, PluginManager.DirNode)) - \
        int(isinstance(x, PluginManager.DirNode))
    return ret or (1 - 2 * int(x.name < y.name))


class PluginManager:
    """ Manages plugins loaded from a directory.
    """
    class Node:
        def __init__(self, parent, data, path, name):
            self.parent = parent
            self.data = data
            self.name = name
            self.path = path

        def childCount(self):
            return 0

        def row(self):
            if self.parent:
                return self.parent.children.index(self)
            return 0

    class DirNode(Node):
        def __init__(self, parent, data, path=''):
            """ Recursively walk down the tree, loading all legal
            plugin classes along the way.
            """
            PluginManager.Node.__init__(self, parent, data, path, '')
            self.children = []

            if path:
                self.addPath(path)

        def child(self, row):
            """ Return child at given position.
            """
            return self.children[row]

        def childCount(self):
            """ Return number of children.
            """
            return len(self.children)

        def get_dir_child(self, path):
            """ Return child node with given directory name.
            """
            for n in self.children:
                if os.path.split(n.path)[1] == os.path.split(path)[1] and \
                        isinstance(n, PluginManager.DirNode):
                    return n
            return None

        def addPath(self, path):
            """ Add a new path.
            """
            if not path:
                return

            self.name = os.path.split(path)[1]

            for f in os.listdir(path):
                # Don't include hidden directories
                if f.startswith('.'):
                    continue

                p = os.path.join(path.decode('utf-8'), f).encode('utf-8')
                if os.path.isdir(p):
                    new_node = self.get_dir_child(p)
                    if new_node:
                        new_node.addPath(p)
                    else:
                        new_node = PluginManager.DirNode(self, None, p)
                        if new_node.childCount():
                            self.children.append(new_node)
                else:
                    if not f.endswith('.py'):
                        continue

                    # Found a Python file, execute it and look for plugins
                    exc_globals = {}
                    try:
                        # We turn all encodings to UTF-8, so remove encoding
                        # comments manually
                        f = open(p, 'r')
                        lines = f.readlines()
                        if not lines:
                            continue
                        if re.findall('coding[:=]\s*([-\w.]+)', lines[0]):
                            lines.pop(0)
                        elif re.findall('coding[:=]\s*([-\w.]+)', lines[1]):
                            lines.pop(1)
                        source = ''.join(lines).decode('utf-8')
                        code = compile(source, p, 'exec')

                        sys.path.insert(0, path)
                        exec(code, exc_globals)
                    except Exception:
                        logger.warning('Error during execution of ' +
                                       'potential plugin file ' + p + ':\n' +
                                       traceback.format_exc() + '\n')
                    finally:
                        if sys.path[0] == path:
                            sys.path.pop(0)

                    for cl in exc_globals.values():
                        if not inspect.isclass(cl):
                            continue

                        # Should be a subclass of AnalysisPlugin...
                        if not issubclass(cl, AnalysisPlugin):
                            continue
                        # ...but should not be AnalysisPlugin (can happen
                        # when directly imported)
                        if cl == AnalysisPlugin:
                            continue

                        # Plugin class found, add it to tree
                        try:
                            instance = cl()
                            instance.source_file = p
                        except Exception:
                            etype, evalue, etb = sys.exc_info()
                            evalue = etype('Exception while creating %s: %s' %
                                           (cl.__name__, evalue))
                            raise etype, evalue, etb
                        self.children.append(PluginManager.Node(
                            self, instance, p, instance.get_name()))

            self.children.sort(cmp=_compare_nodes)

    def __init__(self):
        self.root = self.DirNode(None, None)

    def add_path(self, path):
        """ Add a new path to the manager.
        """
        self.root.addPath(path)
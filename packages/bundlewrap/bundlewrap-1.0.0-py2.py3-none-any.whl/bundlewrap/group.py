import re

from .exceptions import RepositoryError
from .utils import cached_property
from .utils.text import mark_for_translation as _, validate_name


def _build_error_chain(loop_node, last_node, nodes_in_between):
    """
    Used to illustrate subgroup loop paths in error messages.

    loop_node:          name of node that loops back to itself
    last_node:          name of last node pointing back to loop_node,
                        causing the loop
    nodes_in_between:   names of nodes traversed during loop detection,
                        does include loop_node if not a direct loop,
                        but not last_node
    """
    error_chain = []
    for visited in nodes_in_between:
        if (loop_node in error_chain) != (loop_node == visited):
            error_chain.append(visited)
    error_chain.append(last_node)
    error_chain.append(loop_node)
    return error_chain


class Group(object):
    """
    A group of nodes.
    """
    def __init__(self, group_name, infodict=None):
        if infodict is None:
            infodict = {}

        if not validate_name(group_name):
            raise RepositoryError(_("'{}' is not a valid group name").format(group_name))

        self.name = group_name
        self.bundle_names = infodict.get('bundles', [])
        self.immediate_subgroup_names = infodict.get('subgroups', [])
        self.metadata = infodict.get('metadata', {})
        self.password = infodict.get('password', None)
        self.patterns = infodict.get('member_patterns', [])
        self.static_member_names = infodict.get('members', [])

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def __repr__(self):
        return "<Group: {}>".format(self.name)

    def __str__(self):
        return self.name

    @cached_property
    def nodes(self):
        """
        List of all nodes in this group.
        """
        result = []
        result += list(self._nodes_from_static_members)
        result += list(self._nodes_from_subgroups)
        result += list(self._nodes_from_patterns)
        return sorted(set(result))

    @property
    def _nodes_from_static_members(self):
        for node_name in self.static_member_names:
            yield self.repo.get_node(node_name)

    @property
    def _nodes_from_subgroups(self):
        for subgroup in self.subgroups:
            for node in subgroup.nodes:
                yield node

    @property
    def _nodes_from_patterns(self):
        for pattern in self.patterns:
            compiled_pattern = re.compile(pattern)
            for node in self.repo.nodes:
                if not compiled_pattern.search(node.name) is None:
                    yield node

    def _check_subgroup_names(self, visited_names):
        """
        Recursively finds subgroups and checks for loops.
        """
        for name in self.immediate_subgroup_names:
            if name not in visited_names:
                group = self.repo.get_group(name)
                for group_name in group._check_subgroup_names(
                    visited_names + [self.name],
                ):
                    yield group_name
            else:
                error_chain = _build_error_chain(
                    name,
                    self.name,
                    visited_names,
                )
                raise RepositoryError(_(
                    "{group} can't be a subgroup of itself "
                    "({chain})").format(
                        group=name,
                        chain=" -> ".join(error_chain),
                    )
                )
        if self.name not in visited_names:
            yield self.name

    @cached_property
    def subgroups(self):
        """
        Iterator over all subgroups as group objects.
        """
        for group_name in self._check_subgroup_names([self.name]):
            yield self.repo.get_group(group_name)

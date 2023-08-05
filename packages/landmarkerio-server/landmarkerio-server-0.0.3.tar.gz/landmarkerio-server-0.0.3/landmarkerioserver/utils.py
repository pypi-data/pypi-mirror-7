import itertools
from collections import namedtuple

Group = namedtuple('Group', ['label', 'n', 'index'])


def parse_group(group):
    x = group.split('\n')
    label, n_str = x[0].split(' ')
    n = int(n_str)
    index_str = x[1:]
    if len(index_str) == 0:
        return Group(label, n, [])
    index = [[int(j) for j in i.split(' ')] for i in index_str]
    indexes = set(itertools.chain.from_iterable(index))
    if min(indexes) < 0 or max(indexes) > n:
        raise ValueError("invalid connectivity")
    return Group(label, n, index)


def group_to_json(group, n_dims):
    group_json = {}
    lms = [{'point': [None] * n_dims}] * group.n
    group_json['landmarks'] = lms
    group_json['connectivity'] = group.index
    group_json['label'] = group.label
    return group_json


def groups_to_json(groups, n_dims):
    lm_json = {'version': 1, 'groups': []}
    for g in groups:
        lm_json['groups'].append(group_to_json(g, n_dims))
    return lm_json


def load_template(path, n_dims):
    with open(path, 'rb') as f:
        ta = f.read().strip().split('\n\n')
    groups = [parse_group(g) for g in ta]
    return groups_to_json(groups, n_dims)

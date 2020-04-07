import subprocess
import logging
import shutil
import os
import queue
import xml.etree.ElementTree as ET
import tempfile
import copy

root_logger = logging.getLogger()

NS = {'ns': 'http://www.srcML.org/srcML/src',
      'pos': 'http://www.srcML.org/srcML/position'}

LINEKEY = '{{{}}}line'.format(NS['pos'])
COLUMNKEY = '{{{}}}column'.format(NS['pos'])

basic_tag = ['expr_stmt', 'decl_stmt', 'function_decl', 'function']
c_stmt_tag = basic_tag + ['if', 'while', 'for', 'do', 'break', 'continue',
                          'return', 'switch', 'case', 'default', 'block',
                          'label', 'goto', 'empty_stmt', 'typedef']
# maybe should include <then>, <else>, <elseif>
# Todo: Java tag


def is_before(pos1: dict, pos2: dict) -> bool:
    return (pos1['line'] < pos2['line'] or
            (pos1['line'] == pos2['line'] and pos1['column'] <= pos2['column']))


def node_statistics(node: ET.Element) -> str:
    return '{}, {}, {}, {}, {}'.format(
        node, node.tag, node.text, node.tail, node.attrib
    )


def xml_to_code(tree: ET) -> bytes:
    """
    srcml tree to code of byte string

    :param tree: xml.etree.ElementTree of source code
    :return: ByteString of code
    """
    # xml to file
    fd, temp_path = tempfile.mkstemp(suffix='.xml')
    tree.write(temp_path)
    # run srcml
    try:
        result = subprocess.run(
            ['srcml {}'.format(temp_path)],
            shell=True,
            executable='/bin/bash',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=500,
            check=True
        )
    except subprocess.SubprocessError as e:
        root_logger.error('subprocess cmd: {}, stdout: {}'.format(e.cmd,
                                                                  e.stdout))
        ret = e.stdout
    else:
        ret = result.stdout
    finally:
        os.close(fd)
        os.remove(temp_path)
        return ret


def node_to_code(node: ET.Element) -> bytes:
    """
    node to code of byte string
    """
    return xml_to_code(ET.ElementTree(node))


def code_to_xml(code_path: str, pos_flag: bool) -> ET:
    """
    source code path to srcml tree

    :param code_path: source code path
    :return: xml.etree.ElementTree.Element of source code
    """
    # get source code language
    extension = '.' + str(os.path.basename(code_path).split('.')[-1])
    # copy source code to temp path
    fd, temp_path = tempfile.mkstemp(suffix=extension)
    shutil.copy(code_path, temp_path)
    # run srcML
    try:
        ret = subprocess.run(
            [('srcml --position --tab=1 {}' if pos_flag else 'srcml {}').format(
                temp_path)],
            shell=True,
            executable='/bin/bash',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=500,
            check=True
        )
    except subprocess.SubprocessError as e:
        root_logger.error('subprocess cmd: {}, stdout: {}'.format(e.cmd,
                                                                  e.stdout))
        os.close(fd)
        os.remove(temp_path)
        exit(1)
    else:
        os.close(fd)
        os.remove(temp_path)
        element = ET.fromstring(ret.stdout)
        return ET.ElementTree(element=element, file=None)


def get_position(node: ET.Element) -> ({}, {}):
    """
    Get node position on the source code.
    :param node: ET.Element
    :return: Tuple of start position and end position.
    """
    for child in node.iter():
        if LINEKEY in child.attrib:
            start = {'line': int(child.attrib[LINEKEY]),
                     'column': int(child.attrib[COLUMNKEY])}
            break
    for child in reversed(list(node.iter())):
        if LINEKEY in child.attrib:
            end = {'line': int(child.attrib[LINEKEY]),
                   'column': int(child.attrib[COLUMNKEY])}
            break
    return start, end


def is_stmt_tag(tag: str) -> bool:
    """
    Check tag is one of the statement tag

    :param tag: Element tage
    :return: whether it is one of the statement tag
    """

    # Todo java
    for stmt_tag in c_stmt_tag:
        NS_tag = '{{{}}}{}'.format(NS['ns'], stmt_tag)
        if NS_tag == tag:
            return True
    return False


def is_expr_tag(tag: str) -> bool:
    """
    Check tag is a expr tag

    :param tag: Element tage
    :return: whether it is expr tag
    """

    # Todo java
    return tag == '{{{}}}expr'.format(NS['ns'])


def is_pos_node(node: ET.Element) -> bool:
    return node.tag == '{{{}}}position'.format(NS['pos'])


def is_ORBS_print_node(node: ET.Element) -> bool:
    """
    Get node with expr tag, return if is is a printf statement logging ORBS log
    """
    assert (node.tag == '{{{}}}expr'.format(NS['ns']))
    expr_call_path = './ns:call'
    expr_call_name_path = os.path.join(expr_call_path, 'ns:name')
    expr_call_arg_literal_path = os.path.join(
        expr_call_path, 'ns:argument_list/ns:argument/ns:expr/ns:literal')
    expr_call_name = node.find(expr_call_name_path, NS)
    expr_call_arg_literal = node.find(expr_call_arg_literal_path, NS)
    if expr_call_name is not None and expr_call_arg_literal is not \
            None and expr_call_arg_literal.text.startswith('"\\nORBS'):
        return True
    else:
        return False


def is_standalone_ORBS_log_node(node: ET.Element) -> bool:
    """
    Get node with stmt tag, return if it is stand-alone ORBS log node or not
    """
    expr_path = './ns:expr'
    if node.tag == '{{{}}}expr_stmt'.format(NS['ns']):
        expr_node = node.find(expr_path, NS)
        if expr_node is not None:
            return is_ORBS_print_node(expr_node)
    else:
        return False


def is_ternary_ORBS_log_node(node: ET.Element) -> bool:
    """
    get node with expr tag, return if it is ORBS ternary log or not
    """
    ternary_node = node.find('.ns:ternary', NS)
    if ternary_node is not None:
        ternary_then_expr = ternary_node.find('./ns:then/ns:expr', NS)
        if ternary_then_expr is not None:
            return is_ORBS_print_node(ternary_then_expr)
        else:
            return False
    else:
        return False


def is_decl_node(node: ET.Element) -> bool:
    """
    get node with stmt tag, return if it is decl node or not
    """
    return (node.tag == '{{{}}}function_decl'.format(NS['ns']) or
            node.tag == '{{{}}}decl_stmt'.format(NS['ns']))

def is_init_node(node: ET.Element) -> bool:
    """
    get node with stmt tag, return if it is init node or not
    """
    if node.tag == '{{{}}}expr_stmt'.format(NS['ns']):
        expr_node = node.fine('./ns:expr', NS)
        if len(expr_node) == 3:
            if (expr_node[0].tag == '{{{}}}name'.format(NS['ns']) and
                expr_node[1].tag == '{{{}}}operator'.format(NS['ns']) and
                expr_node[1].text == '=' and
                expr_node[2].tag == '{{{}}}literal'.format(NS['ns'])):
                return True
    return False

def is_ret_node(node: ET.Element) -> bool:
    """
    get node with stmt tag, return if it is ret node or not
    """
    return node.tag == '{{{}}}return'.format(NS['ns'])


def copy_tree(tree: ET) -> (ET, {ET.Element: ET.Element}):
    """
    Get ET return copy of ET and mapping from element in copied ET to element
    in original ET
    """
    copy_tree = copy.deepcopy(tree)
    orig_node_list = get_bfs_node_list(tree)
    copy_node_list = get_bfs_node_list(copy_tree)
    return copy_tree, dict(zip(copy_node_list, orig_node_list))


def remove_position(tree: ET, parent_dict):
    node_list = get_bfs_node_list(tree)
    for node in node_list:
        if is_pos_node(node):
            parent_dict[node].remove(node)
        else:
            if LINEKEY in node.attrib:
                node.attrib.pop(LINEKEY)
                node.attrib.pop(COLUMNKEY)


def get_bfs_node_list(tree: ET) -> [ET.Element]:
    root = tree.getroot()
    node_list = []
    q = queue.Queue()
    q.put(root)
    while not q.empty():
        node = q.get()
        node_list.append(node)
        for child in node:
            q.put(child)
    return node_list


def get_parent_dict_and_stmt(tree: ET) -> ({ET.Element: ET.Element},
                                           [ET.Element]):
    """
    Get child -> parent dict and stmt node list

    :param tree: source code ET
    :return: parent_dict, stmt_list
    """
    node_list = get_bfs_node_list(tree)
    parent_dict = {}
    stmt_list = []
    for node in node_list:
        if is_stmt_tag(node.tag) and not is_standalone_ORBS_log_node(node):
            stmt_list.append(node)
        for child in node:
            parent_dict[child] = node
    return parent_dict, stmt_list


def delete_node(parent_node: ET.Element, child_node: ET.Element):
    """
    Remove child_node from parent_node.
    Make sure it does not break the code structure
    """
    if 'block' in child_node.tag:
        child_node_idx = list(parent_node).index(child_node)
        if child_node_idx:
            previous_node = parent_node[child_node_idx - 1]
            if previous_node.tail:
                if previous_node.tail:
                    previous_node.tail += ';'
                else:
                    previous_node.tail = ';'
        else:
            if parent_node.text:
                parent_node.text += ';'
            else:
                parent_node.text = ';'
    if 'block' in parent_node.tag:
        child_node_idx = list(parent_node).index(child_node)
        if child_node.tail:
            if child_node_idx:
                previous_node = parent_node[child_node_idx - 1]
                if previous_node.tail:
                    previous_node.tail += child_node.tail
                else:
                    previous_node.tail = child_node.tail
            else:
                if parent_node.text:
                    parent_node.text += child_node.tail
                else:
                    parent_node.text = child_node.tail
    parent_node.remove(child_node)


def remove_annotation_node(tree: ET, parent_dict) -> ET:
    """
    Return tree without ORBS log
    """
    node_list = get_bfs_node_list(tree)
    for node in node_list:
        if is_stmt_tag(node.tag) and is_standalone_ORBS_log_node(node):
            parent_node = parent_dict[node]
            delete_node(parent_node, node)
            parent_dict.pop(node)
        elif is_expr_tag(node.tag) and is_ternary_ORBS_log_node(node):
            parent_node = parent_dict[node]
            # 지우고, condition 넣고, parent_dict 수정하고
            delete_node(parent_node, node)
            ternary_condition_expr = node.find('.ns:ternary/ns:condition/ns:expr', NS)
            ternary_condition_expr.tail = ')'
            parent_node
            parent_node.append(ternary_condition_expr)
            parent_dict.pop(node)
            parent_dict[ternary_condition_expr] = parent_node


def get_criteria_line_col(log_node: ET.Element) -> (int, int):
    """
    Get line number and column number from ORBS log node
    """
    arg_list_node = log_node.find('./ns:expr/ns:call/ns:argument_list', NS)
    line = int(arg_list_node[1].find('./ns:expr/ns:literal', NS).text)
    col = int(arg_list_node[2].find('./ns:expr/ns:literal', NS).text)
    return line, col


def get_node_by_line_col(tree: ET, line: int, col: int) -> ET.Element:
    """
    Get node from tree by its line and col.
    Tree needs position.
    If there's no such node return None.
    """
    for node in tree.getroot().iter():
        if LINEKEY in node.attrib:
            if (line == int(node.attrib[LINEKEY]) and
                    col == int(node.attrib[COLUMNKEY])):
                return node
    return None


def get_parent_stmt_node(child_node: ET.Element,
                         parent_dict: dict) -> ET.Element:
    """
    Get the smallest parent node containing child node.
    If there's no such node return None.
    """
    parent_node = child_node
    while(not is_stmt_tag(parent_node.tag)):
        parent_node = parent_dict[parent_node]
    return parent_node


def get_node_index_in_tree(tree: ET, node: ET.Element) -> int:
    """
    Return the index of the node in tree represented as an index from
    node list generated from the tree
    """
    node_list = get_bfs_node_list(tree)
    return node_list.index(node)


def get_node_by_index(tree: ET, index: int) -> ET.Element:
    """
    Get node from tree by the index of the node in the node list generated
    from the tree
    """
    node_list = get_bfs_node_list(tree)
    return node_list[index]


def get_stmt_with_log_node(stmt_node: ET.Element,
                           log_node_list: [ET.Element]) -> ET.Element:
    """
    Get merged node which contains stmt_node and log nodes
    """
    add_log_node_list = list(
        filter(lambda log_node: log_node not in stmt_node.iter(),
               log_node_list))
    if not add_log_node_list:
        return stmt_node
    else:
        ret = ET.Element('blank')
        node_list = add_log_node_list + [stmt_node]
        start_pos_list = list(map(lambda pos: (pos['line'], pos['column']),
                                  map(lambda node: get_position(node)[0],
                                      node_list)))
        for node, start_pos in sorted(zip(node_list, start_pos_list),
                                      key=lambda x: x[1]):
            ret.append(node)
        return ret

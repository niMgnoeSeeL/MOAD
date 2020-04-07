import os
import copy
import shutil
import logging
import difflib
import xml.etree.ElementTree as ET
from .srcml import srcml
from .factor_manager import FactorManager

root_logger = logging.getLogger()


class SrcMLTree:

    file_path = None
    tree = None
    parent_dict = {}
    stmt_list = []

    def __init__(
        self, dir_path, filename: str, project_name: str, save_flag: bool = True,
    ):
        self.filename = filename
        self.original_filename = (
            ".".join(self.filename.split(".")[:-1]) + "_original." + self.filename.split(".")[-1]
        )
        self.tree = srcml.code_to_xml(os.path.join(dir_path, self.filename), True)
        self.sanity_check(dir_path)
        self.parent_dict, self.stmt_list = srcml.get_parent_dict_and_stmt(self.tree)
        # size: the number of the stmt node
        self.size = len(list(self.stmt_list))

        self.log_dict = self.get_log_dict(dir_path)

        srcml_data_path = os.path.join("output", "unit", project_name)
        if not os.path.exists(srcml_data_path):
            save_flag = True
        if save_flag:
            if os.path.exists(srcml_data_path):
                shutil.rmtree(srcml_data_path)
            os.makedirs(srcml_data_path)
            self.save_unit(srcml_data_path)
        # remove position
        srcml.remove_position(self.tree, self.parent_dict)
        if save_flag:
            self.save_left(srcml_data_path)

    def get_log_dict(self, dir_path: str) -> dict:
        """
        Create mapping from stmt node to the list of ORBS log nodes in the stmt
        """
        orig_tree_w_pos = srcml.code_to_xml(os.path.join(dir_path, self.original_filename), True)
        orig_tree_w_pos_parent_dict, _ = srcml.get_parent_dict_and_stmt(orig_tree_w_pos)
        orig_tree_wo_pos, orig_wopos_to_pos_mapping = srcml.copy_tree(orig_tree_w_pos)
        orig_pos_to_wopos_mapping = dict(
            zip(
                list(map(lambda x: x[1], orig_wopos_to_pos_mapping.items())),
                list(map(lambda x: x[0], orig_wopos_to_pos_mapping.items())),
            )
        )
        orig_tree_wo_pos_parent_dict, _ = srcml.get_parent_dict_and_stmt(orig_tree_wo_pos)
        srcml.remove_position(orig_tree_wo_pos, orig_tree_wo_pos_parent_dict)
        tree_wo_log, wolog_to_log_mapping = srcml.copy_tree(self.tree)
        wolog_parent_dict, _ = srcml.get_parent_dict_and_stmt(tree_wo_log)
        srcml.remove_annotation_node(tree_wo_log, wolog_parent_dict)
        srcml.remove_position(tree_wo_log, wolog_parent_dict)

        log_dict = {}
        for stmt_node in self.stmt_list:
            log_dict[stmt_node] = []
        node_list = srcml.get_bfs_node_list(self.tree)
        standalone_log_node_list = list(
            filter(
                lambda node: srcml.is_stmt_tag(node.tag)
                and srcml.is_standalone_ORBS_log_node(node),
                node_list,
            )
        )
        ternary_log_node_list = list(
            filter(
                lambda node: srcml.is_expr_tag(node.tag) and srcml.is_ternary_ORBS_log_node(node),
                node_list,
            )
        )

        for log_node in standalone_log_node_list:
            line, col = srcml.get_criteria_line_col(log_node)
            var_node = srcml.get_node_by_line_col(orig_tree_w_pos, line, col)
            stmt_node = srcml.get_parent_stmt_node(var_node, orig_tree_w_pos_parent_dict)
            stmt_node_in_wo_pos_tree = orig_pos_to_wopos_mapping[stmt_node]
            stmt_node_index = srcml.get_node_index_in_tree(
                orig_tree_wo_pos, stmt_node_in_wo_pos_tree
            )
            stmt_node_in_wo_log_tree = srcml.get_node_by_index(tree_wo_log, stmt_node_index)
            stmt_node_in_tree = wolog_to_log_mapping[stmt_node_in_wo_log_tree]
            log_dict[stmt_node_in_tree].append(log_node)
        for log_node in ternary_log_node_list:
            stmt_node = srcml.get_parent_stmt_node(log_node, self.parent_dict)
            log_dict[stmt_node].append(log_node)
        return log_dict

    def sanity_check(self, dir_path):
        """
        Annotated tree needs to be same with the tree generated from original
        when ORBS log nodes have been deleted
        """
        tree_copy, _ = srcml.copy_tree(self.tree)
        parent_dict, _ = srcml.get_parent_dict_and_stmt(tree_copy)
        srcml.remove_annotation_node(tree_copy, parent_dict)
        code = srcml.xml_to_code(tree_copy)
        with open(os.path.join(dir_path, self.original_filename), "rb") as f:
            original_code = f.read()
        if code != original_code:
            differ = difflib.Differ()
            diff = list(
                differ.compare(
                    str(original_code.decode("utf-8")).splitlines(keepends=True),
                    str(code.decode("utf-8")).splitlines(keepends=True),
                )
            )
            diff_str = "".join(diff)
            raise Exception(
                "SrcML sanity check failed. Code without annotion \
differs from the original code.\n\
Original:\n{}\nW/O annotation:\n{}\n\
Diff:\n{}".format(
                    original_code.decode("utf-8"), code.decode("utf-8"), diff_str,
                )
            )

    def save_unit(self, srcml_data_path):
        srcml_unit_path = os.path.join(srcml_data_path, "unit")
        srcml_xml_path = os.path.join(srcml_unit_path, "xml")
        srcml_src_path = os.path.join(srcml_unit_path, "src")
        os.makedirs(srcml_xml_path, exist_ok=True)
        os.makedirs(srcml_src_path, exist_ok=True)
        for idx, stmt_node in enumerate(self.stmt_list):
            stmt_with_log_node = srcml.get_stmt_with_log_node(stmt_node, self.log_dict[stmt_node])
            tree = ET.ElementTree(stmt_with_log_node)
            copy_tree, mapping = srcml.copy_tree(tree)
            copy_parent_dict, _ = srcml.get_parent_dict_and_stmt(copy_tree)
            # For better representation
            if copy_tree.getroot().tag == "blank":
                copy_tree.getroot()[-1].tail = None

            src_path = os.path.join(
                srcml_src_path,
                self.filename + "_{}".format(idx) + "." + self.filename.split(".")[-1],
            )
            os.makedirs(os.path.dirname(src_path), exist_ok=True)
            start_pos, end_pos = srcml.get_position(copy_tree.getroot())
            with open(src_path, "w") as f:
                f.write(
                    "// {} stmt: [{}:{} - {}:{}]\n".format(
                        stmt_node.tag.split("}")[1],
                        start_pos["line"],
                        start_pos["column"],
                        end_pos["line"],
                        end_pos["column"],
                    )
                )
                f.write(" " * (start_pos["column"] - 1))

            code = srcml.xml_to_code(copy_tree)
            with open(src_path, "ab") as f:
                f.write(code)
                for log_node in self.log_dict[stmt_node]:
                    f.write("\n".encode())
                    start_pos, end_pos = srcml.get_position(log_node)
                    f.write(
                        "// log: [{}:{} - {}:{}] ".format(
                            start_pos["line"],
                            start_pos["column"],
                            end_pos["line"],
                            end_pos["column"],
                        ).encode()
                    )
                    f.write(srcml.node_to_code(log_node))

            srcml.remove_position(copy_tree, copy_parent_dict)
            xml_path = os.path.join(srcml_xml_path, self.filename + "_{}".format(idx) + ".xml")
            os.makedirs(os.path.dirname(xml_path), exist_ok=True)
            copy_tree.write(xml_path)

    def save_left(self, srcml_data_path):
        srcml_left_path = os.path.join(srcml_data_path, "left")
        srcml_xml_path = os.path.join(srcml_left_path, "xml")
        srcml_src_path = os.path.join(srcml_left_path, "src")
        os.makedirs(srcml_xml_path, exist_ok=True)
        os.makedirs(srcml_src_path, exist_ok=True)
        for i in range(len(self.stmt_list)):
            one_deleted = [False] * i + [True] + [False] * ((len(self.stmt_list)) - i - 1)
            tree = self.create_SrcMLTree(one_deleted).tree
            xml_path = os.path.join(srcml_xml_path, self.filename + "_{}".format(i) + ".xml")
            os.makedirs(os.path.dirname(xml_path), exist_ok=True)
            tree.write(xml_path)

            code = srcml.xml_to_code(tree)
            src_path = os.path.join(
                srcml_src_path,
                self.filename + "_{}".format(i) + "." + self.filename.split(".")[-1],
            )
            os.makedirs(os.path.dirname(src_path), exist_ok=True)
            with open(src_path, "wb") as f:
                f.write(code)

    def create_SrcMLTree(self, deleted_list: [bool]):
        assert len(deleted_list) == len(self.stmt_list)
        rep_SrcMLTree = copy.deepcopy(self)
        for idx, deleted in enumerate(deleted_list):
            if deleted:
                child_node = rep_SrcMLTree.stmt_list[idx]
                parent_node = rep_SrcMLTree.parent_dict[child_node]
                srcml.delete_node(parent_node, child_node)
                for log_node in rep_SrcMLTree.log_dict[child_node]:
                    srcml.delete_node(rep_SrcMLTree.parent_dict[log_node], log_node)
        return rep_SrcMLTree


class SrcMLFactorManager(FactorManager):

    _tree_dict = {}
    _size = -1

    @property
    def tree_dict(self):
        return self._tree_dict

    @property
    def size(self):
        return self._size

    def __init__(self, project_name, program_space):
        super().__init__(program_space)

        self._factor = []
        for filename in self._program_space.files:
            srcMLTree = SrcMLTree(self._program_space.orig_dir, filename, project_name)
            self._tree_dict[filename] = srcMLTree
            self._factor += list(zip([filename] * len(srcMLTree.stmt_list), srcMLTree.stmt_list))
        self._size = len(self._factor)

        # Debug
        root_logger.debug("self._size = {}".format(self._size))
        root_logger.debug("self._factor[0] = {}".format(self._factor[0]))

    def get_file_scope(self, filename: str, attempt: [bool]) -> [bool]:
        """
        return the sublist of attempt list for specific file (filename)
        :param filename: the specific file of the concern
        :param attempt: the whole attempt list of unit
        :return: the partial list of the attempt list of the scope of concern.
        """
        idx = 0
        fn = None
        for fn in self._program_space.files:
            if fn == filename:
                break
            else:
                idx += self._tree_dict[fn].size
        return attempt[idx : idx + self._tree_dict[fn].size]

    def get_slice_position(self, filename: str, stmt_node: ET.Element) -> int:
        """
        return the position of stmt_node in srcml tree of specific file(
        filename) on the unit list
        :param filename: specific file
        :param stmt_node: stmt node in the srcml tree
        :return: position on the unit list
        """
        return self._factor.index((filename, stmt_node))

    def create_program(self, factor, iter_cnt, save_flag, only_code=False):
        work_dir = super().create_program(factor, iter_cnt, save_flag, only_code)

        for filename in self._program_space.files:
            tree = self.tree_dict[filename]
            sliced_tree = tree.create_SrcMLTree(self.get_file_scope(filename, factor))
            code = srcml.xml_to_code(sliced_tree.tree)
            filepath = os.path.join(work_dir, filename)
            with open(filepath, "wb") as f:
                f.write(code)
                root_logger.debug("Filename:{} Code:\n{}".format(filename, code.decode("utf-8")))

        return work_dir

    def revise_factor(self, factor):
        revised_factor = list(factor)
        deletion_factor = [self._factor[i] for i in range(self._size) if factor[i] == 1]

        for filename, stmt_node in deletion_factor:
            srcMLTree = self.tree_dict[filename]
            for child in stmt_node.iter():
                if child in srcMLTree.stmt_list:
                    revised_factor[self.get_slice_position(filename, child)] = 1
        return revised_factor

    def is_valid_factor(self, factor) -> bool:
        """
        if factor deletes decl or initialization or return statement, return false
        """
        deletion_factor = [self._factor[i] for i in range(self._size) if factor[i] == 1]

        for filename, stmt_node in deletion_factor:
            if (
                srcml.is_decl_node(stmt_node)
                or srcml.is_init_node(stmt_node)
                or srcml.is_ret_node(stmt_node)
            ):
                return False
        return True

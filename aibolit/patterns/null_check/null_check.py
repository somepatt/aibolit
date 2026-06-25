# SPDX-FileCopyrightText: Copyright (c) 2019-2026 Aibolit
# SPDX-License-Identifier: MIT
from typing import List

from aibolit.ast_framework import ASTNodeType, AST
from aibolit.ast_framework.ast_node import ASTNode


class NullCheck():
    """
    If we check that something equals
    (or not equals) null (except in constructor)
    it is considered a pattern.
    """
    def value(self, ast: AST) -> List[int]:
        lines: List[int] = []
        for method_declaration in ast.proxy_nodes(ASTNodeType.METHOD_DECLARATION):
            method_ast = ast.subtree(method_declaration)
            for bin_op in method_ast.proxy_nodes(ASTNodeType.BINARY_OPERATION):
                if self._check_null(bin_op):
                    lines.append(self._null_operand(bin_op).line)
            for method_invocation in method_ast.proxy_nodes(ASTNodeType.METHOD_INVOCATION):
                if self._check_null_invocation(method_invocation):
                    lines.append(method_invocation.line)
        return lines

    def _check_null(self, bin_operation: ASTNode) -> bool:
        return (
            bin_operation.operator in ['==', '!=']
            and self._null_operand(bin_operation) is not None
        )

    def _check_null_invocation(self, method_invocation: ASTNode) -> bool:
        return (
            self._is_require_non_null(method_invocation)
            or self._is_of_nullable(method_invocation)
            or self._is_assert_throws_with_null(method_invocation)
        )

    def _is_require_non_null(self, method_invocation: ASTNode) -> bool:
        return (
            method_invocation.qualifier == 'Objects'
            and method_invocation.member == 'requireNonNull'
        )

    def _is_of_nullable(self, method_invocation: ASTNode) -> bool:
        return (
            method_invocation.qualifier == 'Optional'
            and method_invocation.member == 'ofNullable'
            and any(self._is_null_literal(argument) for argument in method_invocation.arguments)
        )

    def _is_assert_throws_with_null(self, method_invocation: ASTNode) -> bool:
        return (
            method_invocation.qualifier in ('', None)
            and method_invocation.member == 'assertThrows'
            and len(method_invocation.arguments) > 1
            and self._is_null_pointer_exception(method_invocation.arguments[0])
            and any(
                self._contains_null_literal(argument)
                for argument in method_invocation.arguments[1:]
            )
        )

    def _is_null_pointer_exception(self, node: ASTNode) -> bool:
        return (
            node.node_type == ASTNodeType.CLASS_REFERENCE
            and node.type.name == 'NullPointerException'
        )

    def _contains_null_literal(self, node: ASTNode) -> bool:
        if self._is_null_literal(node):
            return True
        return any(
            self._contains_null_literal(child)
            for child in node.children
            if isinstance(child, ASTNode)
        )

    def _null_operand(self, bin_operation: ASTNode) -> ASTNode | None:
        if self._is_null_literal(bin_operation.operandl):
            return bin_operation.operandl
        if self._is_null_literal(bin_operation.operandr):
            return bin_operation.operandr
        return None

    def _is_null_literal(self, node: ASTNode) -> bool:
        return (
            node.node_type == ASTNodeType.LITERAL
            and node.value == 'null'
        )

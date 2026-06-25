# SPDX-FileCopyrightText: Copyright (c) 2019-2026 Aibolit
# SPDX-License-Identifier: MIT

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from aibolit.patterns.null_check.null_check import NullCheck
from aibolit.ast_framework import AST
from aibolit.utils.ast_builder import build_ast


class NullCheckTestCase(TestCase):
    current_directory = Path(__file__).absolute().parent

    def test_null_check(self):
        filepath = self.current_directory / '1.java'
        ast = AST.build_from_javalang(build_ast(filepath))
        pattern = NullCheck()
        lines = pattern.value(ast)
        self.assertEqual(lines, [7])

    def test_null_check_in_constructor(self):
        filepath = self.current_directory / '2.java'
        ast = AST.build_from_javalang(build_ast(filepath))
        pattern = NullCheck()
        lines = pattern.value(ast)
        self.assertEqual(lines, [])

    def test_null_check_comparison_result_assignment(self):
        filepath = self.current_directory / '3.java'
        ast = AST.build_from_javalang(build_ast(filepath))
        pattern = NullCheck()
        lines = pattern.value(ast)
        self.assertEqual(lines, [7])

    def test_null_check_ternary(self):
        filepath = self.current_directory / '4.java'
        ast = AST.build_from_javalang(build_ast(filepath))
        pattern = NullCheck()
        lines = pattern.value(ast)
        self.assertEqual(lines, [7])

    def test_null_check_not_equal_comparison(self):
        filepath = self.current_directory / '5.java'
        ast = AST.build_from_javalang(build_ast(filepath))
        pattern = NullCheck()
        lines = pattern.value(ast)
        self.assertEqual(lines, [7])

    def test_null_check_with_left_null_operand(self):
        lines = self._lines_for(
            '''
            class NullCheck {
                void x(String param) {
                    if (null != param && !param.isEmpty()) {
                        throw new RuntimeException("oops");
                    }
                }
            }
            '''
        )
        self.assertEqual(lines, [4])

    def test_null_check_with_require_non_null(self):
        lines = self._lines_for(
            '''
            import java.util.Objects;

            class NullCheck {
                void x(String bar) {
                    Objects.requireNonNull(bar, "bar must not be null");
                }
            }
            '''
        )
        self.assertEqual(lines, [6])

    def test_null_check_with_of_nullable(self):
        lines = self._lines_for(
            '''
            import java.util.Optional;

            class NullCheck {
                void x() {
                    Optional<String> op2 = Optional.ofNullable(null);
                }
            }
            '''
        )
        self.assertEqual(lines, [6])

    def test_null_check_with_assert_throws_and_null_argument(self):
        lines = self._lines_for(
            '''
            import static org.junit.jupiter.api.Assertions.assertThrows;

            class NullCheck {
                void x() {
                    assertThrows(NullPointerException.class, () -> wrapperSum(null, 2));
                }

                private int wrapperSum(String left, int right) {
                    return right;
                }
            }
            '''
        )
        self.assertEqual(lines, [6])

    def _lines_for(self, code: str) -> list[int]:
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / 'NullCheck.java'
            file_path.write_text(code, encoding='utf-8')
            ast = AST.build_from_javalang(build_ast(file_path))
        return NullCheck().value(ast)

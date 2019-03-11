import pytest
from inspect import cleandoc

from py2tex.floating_environment import _FloatingEnvironment



class Test_FloatingEnvironment:
    def test_floating_environment_default(self):
        env = _FloatingEnvironment('default')
        assert env.build() == cleandoc(
            r'''
            \begin{default}[h!]
            \centering
            \end{default}
            ''')

    def test_floating_environment_with_options(self):
        env = _FloatingEnvironment('with_options', position='t', centered=False)
        assert env.build() == cleandoc(
            r'''
            \begin{with_options}[t]
            \end{with_options}
            ''')

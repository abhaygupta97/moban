import os

from lml.plugin import PluginInfo

import moban.exceptions as exceptions
from mock import patch
from nose.tools import eq_, raises
from moban.engine import ENGINES, Engine, Context, expand_template_directories
from moban.extensions import jinja_global


@PluginInfo("library", tags=["testmobans"])
class TestPypkg:
    def __init__(self):
        __package_path__ = os.path.dirname(__file__)
        self.resources_path = os.path.join(__package_path__, "fixtures")


def test_expand_pypi_dir():
    dirs = list(expand_template_directories("testmobans:template-tests"))
    for directory in dirs:
        assert os.path.exists(directory)


@patch("moban.utils.get_moban_home", return_value="/user/home/.moban/repos")
@patch("os.path.exists", return_value=True)
def test_expand_repo_dir(_, __):
    dirs = list(expand_template_directories("git_repo:template"))

    expected = ["/user/home/.moban/repos/git_repo/template"]
    eq_(expected, dirs)


def test_default_template_type():
    engine_class = ENGINES.get_engine("jj2")
    assert engine_class == Engine


def test_default_mako_type():  # fake mako
    engine_class = ENGINES.get_engine("mako")
    assert engine_class.__name__ == "MakoEngine"


@raises(exceptions.NoThirdPartyEngine)
def test_unknown_template_type():
    ENGINES.get_engine("unknown_template_type")


@raises(exceptions.DirectoryNotFound)
def test_non_existent_tmpl_directries():
    Engine("abc", "tests")


@raises(exceptions.DirectoryNotFound)
def test_non_existent_config_directries():
    Engine("tests", "abc")


@raises(exceptions.DirectoryNotFound)
def test_non_existent_ctx_directries():
    Context(["abc"])


def test_file_tests():
    output = "test.txt"
    path = os.path.join("tests", "fixtures", "jinja_tests")
    engine = Engine([path], path)
    engine.render_to_file("file_tests.template", "file_tests.yml", output)
    with open(output, "r") as output_file:
        content = output_file.read()
        eq_(content, "yes\nhere")
    os.unlink(output)


def test_globals():
    output = "globals.txt"
    test_dict = dict(hello="world")
    jinja_global("test", test_dict)
    path = os.path.join("tests", "fixtures", "globals")
    engine = Engine([path], path)
    engine.render_to_file("basic.template", "basic.yml", output)
    with open(output, "r") as output_file:
        content = output_file.read()
        eq_(content, "world\n\ntest")
    os.unlink(output)

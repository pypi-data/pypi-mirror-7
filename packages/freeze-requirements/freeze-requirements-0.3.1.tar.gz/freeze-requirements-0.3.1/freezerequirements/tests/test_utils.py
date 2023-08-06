from nose.tools import assert_equal

from freezerequirements.utils import likely_distro, group_and_select_packages


def test_likely_distro():
    distro = likely_distro('lizard-2013-01-29-16-44-48.878536.tar.gz')
    assert_equal(distro.key, 'lizard')
    assert_equal(distro.version, '2013-01-29-16-44-48.878536')
    distro = likely_distro('stashy-client-0.1.3.tar.gz')
    assert_equal(distro.key, 'stashy-client')
    assert_equal(distro.version, '0.1.3')


def test_group_and_select_packages():
    pkgs = [
        ['foo-1.3.tar.gz', 'bar-0.1.tar.gz'],
        ['foo-1.4.tar.gz'],
        [
            'baz-2014-01-29-16-44-48.878536.tar.gz',
            'baz-2013-01-29-16-44-48.878536.tar.gz', 
        ],
    ]
    assert_equal(group_and_select_packages(pkgs), {
        'foo': ['1.4', '1.3'],
        'bar': ['0.1'],
        'baz': ['2014-01-29-16-44-48.878536', '2013-01-29-16-44-48.878536'],
    })

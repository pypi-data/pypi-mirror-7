from semverpy import SemVerPy


def test_same():
    ver = SemVerPy('1.0.1-a')
    print(str(ver))
    assert str(ver) == '1.0.1-a'

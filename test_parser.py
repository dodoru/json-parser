import json
from json_parser import (
    JsonParser,
)


def test_json_parse():
    def test_parse(m):
        c1 = json.dumps(m)
        d0 = json.loads(c1)

        d1 = JsonParser.loads(c1)

        c2 = json.dumps(m, indent=4)
        d2 = JsonParser.loads(c2)

        assert d0 == d1
        assert d0 == d2

    # 测试嵌套字典
    m0 = '22\\"'
    test_parse(m0)

    m1 = dict(
        a=1,
        b='22\\"',
        c=None,
        d=dict(
            a=1,
            b='22',
        ),
        e=dict()
    )
    test_parse(m1)

    # 测试嵌套字典
    m2 = dict(
        a=dict(
            b=dict(
                c1='mmm',
                c2='xxx',
                c=dict(
                    d1=None,
                    d2=222,
                    d3=True,
                    d4=False,
                    d5=""
                )
            )
        )
    )
    # test_parse(m2)

    # 测试列表
    m3 = [1, 2, 3, True, False, 'hello', "  "]
    test_parse(m3)

    # 测试嵌套列表
    m4 = [[], [1, 2, 3], True, False, 'hello', "  "]
    test_parse(m4)

    # 测试字典嵌套列表
    m5 = dict(
        m1=dict(m11=dict(
            name="nico",
            msg='mt',
            age=22,
        )),
        m2=dict(
            ture=True,
            false=False,
            null=None,
        ),
        l1=[[1, 2, 3], []],
        l2=[1, 2, True, False],
    )
    test_parse(m5)

    # 测试列表嵌套字典
    m6 = [
        dict(a1=dict(b1=11, b2=True), a2=False),
        1,
        22,
        True,
        None,
        'test'
    ]
    test_parse(m6)

    # 大测试
    m7 = [m1, m2, m3, m4, m5, m6]
    test_parse(m7)


if __name__ == '__main__':
    test_json_parse()

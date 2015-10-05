import pytest
from kulka.response import parser


VALID_MRSP = [
    0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
    0x09, 0x0A, 0x0B, 0x31, 0x32, 0x33, 0x34, 0x35
]


def create_response(mrsp, seq, data):
    given = bytearray([0xFF, 0xFF, mrsp, seq, len(data)] + data)
    given.append(sum(given[2:]) & 0xFF ^ 0xFF)
    return given


@pytest.mark.parametrize('mrsp', VALID_MRSP)
@pytest.mark.randomize(seq=int, data=pytest.nonempty_list_of(int),
                       min_num=0, max_num=255)
def test_truncated_packet(mrsp, seq, data):
    given = create_response(mrsp, seq, data)

    for i in range(len(given) - 1):
        with pytest.raises(ValueError):
            parser(given[:i])


@pytest.mark.parametrize('mrsp', VALID_MRSP)
@pytest.mark.randomize(seq=int, data=pytest.nonempty_list_of(int),
                       min_num=0, max_num=255)
def test_valid_example(mrsp, seq, data):
    response_, _ = parser(create_response(mrsp, seq, data))

    assert response_.MRSP == mrsp
    assert response_.seq == seq
    assert response_.data == bytearray(data)


@pytest.mark.parametrize('mrsp', VALID_MRSP)
@pytest.mark.randomize(seq=int, data=pytest.nonempty_list_of(int),
                       junk=pytest.nonempty_list_of(int), min_num=0,
                       max_num=255)
def test_junk_before_valid_data(mrsp, seq, data, junk):
    given = bytearray(junk) + create_response(mrsp, seq, data)
    response_, skipped = parser(given)

    assert skipped == len(junk) + len(data) + 6
    assert response_.MRSP == mrsp
    assert response_.seq == seq
    assert response_.data == bytearray(data)

import pytest
from kulka.response import Response


def create_response(mrsp, seq, data):
    given = bytearray([0xFF, 0xFF, mrsp, seq, len(data)] + data)
    given.append(sum(given[2:]) & 0xFF ^ 0xFF)
    return given


@pytest.mark.randomize(mrsp=int, seq=int, data=pytest.nonempty_list_of(int),
                       min_num=0, max_num=255)
def test_truncated_packet(mrsp, seq, data):
    given = create_response(mrsp, seq, data)

    for i in range(len(given) - 1):
        with pytest.raises(ValueError):
            Response.frombytes(given[:i])


@pytest.mark.randomize(mrsp=int, seq=int, data=pytest.nonempty_list_of(int),
                       min_num=0, max_num=255)
def test_valid_example(mrsp, seq, data):
    response, _ = Response.frombytes(create_response(mrsp, seq, data))

    assert response.mrsp == mrsp
    assert response.seq == seq
    assert response.data == bytearray(data)


@pytest.mark.randomize(mrsp=int, seq=int, data=pytest.nonempty_list_of(int),
                       junk=pytest.nonempty_list_of(int), min_num=0,
                       max_num=255)
def test_junk_before_valid_data(mrsp, seq, data, junk):
    given = bytearray(junk) + create_response(mrsp, seq, data)
    response, skipped = Response.frombytes(given)

    assert skipped == len(junk)
    assert response.mrsp == mrsp
    assert response.seq == seq
    assert response.data == bytearray(data)

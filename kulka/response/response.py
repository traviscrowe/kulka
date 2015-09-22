from itertools import islice


class Response(object):

    def __init__(self, mrsp, seq=None, data=None):
        self.mrsp = mrsp
        self.seq = seq
        self.data = data or bytearray()

    @classmethod
    def frombytes(cls, data):
        skipped = 0

        try:
            while True:
                gen = islice(data, skipped, None)

                if next(gen) != 0xFF:
                    skipped += 1
                    continue

                sop2 = next(gen)

                if sop2 != 0xFF:
                    skipped += 1
                    continue

                mrsp = next(gen)
                seq = next(gen)
                dlen = next(gen)

                payload = bytearray(islice(gen, dlen))

                if len(payload) < dlen:
                    skipped += 1
                    continue

                cksum = (mrsp + seq + dlen + sum(payload)) & 0xFF ^ 0xFF

                if cksum != next(gen):
                    skipped += 1
                    continue

                return cls(mrsp, seq, payload), skipped
        except StopIteration:
            raise ValueError()

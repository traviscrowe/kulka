from itertools import islice
from collections import deque


def packets():
    classes = deque([Packet])

    while classes:
        class_ = classes.popleft()
        classes.extend(class_.__subclasses__())

        if not class_.abstract():
            yield class_


def parser(data):
    for consumed, _ in enumerate(data):
        for class_ in packets():
            response = class_.try_parse(islice(data, consumed, None))

            if response is not None:
                return response, consumed + response.size()

    raise ValueError()


class Packet(object):

    SOP1 = 0xFF
    SOP2 = None

    def __new__(cls, *_, **__):
        if cls.abstract():
            raise NotImplementedError()

        return super(Packet, cls).__new__(cls)

    @classmethod
    def abstract(cls):
        return cls.SOP2 is None

    @classmethod
    def try_parse(cls, data):
        raise NotImplementedError()

    def size(self):
        raise NotImplementedError()


class ResponsePacket(Packet):

    SOP2 = 0xFF
    MRSP = None

    def __init__(self, seq, data):
        self.seq = seq
        self.data = data

    @classmethod
    def abstract(cls):
        return cls.MRSP is None or super(ResponsePacket, cls).abstract()

    @classmethod
    def try_parse(cls, data):
        try:
            if next(data) != cls.SOP1:
                return

            if next(data) != cls.SOP2:
                return

            if next(data) != cls.MRSP:
                return

            seq = next(data)
            dlen = next(data)
            data_ = bytearray(islice(data, dlen))

            if dlen != len(data_):
                return

            chk = (cls.MRSP + seq + dlen + sum(data_)) & 0xFF ^ 0xFF

            if chk != next(data):
                return

            return cls(seq, data_)
        except StopIteration:
            pass

    def size(self):
        return len(self.data) + 6


class ResponseOk(ResponsePacket):

    MRSP = 0x00


class ResponseEGen(ResponsePacket):

    MRSP = 0x01


class ResponseEChksum(ResponsePacket):

    MRSP = 0x02


class ResponseEFrag(ResponsePacket):

    MRSP = 0x03


class ResponseEBadCmd(ResponsePacket):

    MRSP = 0x04


class ResponseEUnsupp(ResponsePacket):

    MRSP = 0x05


class ResponseEBadMsg(ResponsePacket):

    MRSP = 0x06


class ResponseEParam(ResponsePacket):

    MRSP = 0x07


class ResponseEExec(ResponsePacket):

    MRSP = 0x08


class ResponseEBadDid(ResponsePacket):

    MRSP = 0x09


class ResponseMemBusy(ResponsePacket):

    MRSP = 0x0A


class ResponseBadPassword(ResponsePacket):

    MRSP = 0x0B


class ResponsePowerNogood(ResponsePacket):

    MRSP = 0x31


class ResponsePageIllegal(ResponsePacket):

    MRSP = 0x32


class ResponseFlashFail(ResponsePacket):

    MRSP = 0x33


class ResponseMaCorrupt(ResponsePacket):

    MRSP = 0x34


class ResponseMsgTimeout(ResponsePacket):

    MRSP = 0x35


class AsyncPacket(Packet):

    SOP2 = 0xFE
    ID_CODE = None

    def __init__(self, data):
        self.data = data

    @classmethod
    def abstract(cls):
        return cls.ID_CODE is None or super(AsyncPacket, cls).abstract()

    @classmethod
    def try_parse(cls, data):
        try:
            if next(data) != cls.SOP1:
                return

            if next(data) != cls.SOP2:
                return

            if next(data) != cls.ID_CODE:
                return

            dlen_msb = next(data)
            dlen_lsb = next(data)
            dlen = dlen_msb << 8 | dlen_lsb

            data_ = bytearray(islice(data, dlen))
            if dlen != len(data_):
                return

            chk = (cls.ID_CODE + dlen_msb + dlen_lsb + sum(data_)) & 0xFF ^ 0xFF

            if next(data) != chk:
                return

            return cls(data_)
        except StopIteration:
            pass

    def size(self):
        return len(self.data) + 6


class PowerNotifications(AsyncPacket):

    ID_CODE = 0x01


class Level1DiagnosticResponse(AsyncPacket):

    ID_CODE = 0x02


class SensorDataStreaming(AsyncPacket):

    ID_CODE = 0x03


class ConfigBlockContent(AsyncPacket):

    ID_CODE = 0x04


class PreSleepWarning(AsyncPacket):

    ID_CODE = 0x05


class MacroMarker(AsyncPacket):

    ID_CODE = 0x06


class CollisionDetected(AsyncPacket):

    ID_CODE = 0x07


class OrbBasicPrintMessage(AsyncPacket):

    ID_CODE = 0x08


class OrbBasicErrorMessageAscii(AsyncPacket):

    ID_CODE = 0x09


class OrbBasicErrorMessageBinary(AsyncPacket):

    ID_CODE = 0x0A


class SelfLevelResult(AsyncPacket):

    ID_CODE = 0x0B


class GyroAxisLimitExceeded(AsyncPacket):

    ID_CODE = 0x0C


class SpherosSoulData(AsyncPacket):

    ID_CODE = 0x0D


class LevelUpNotification(AsyncPacket):

    ID_CODE = 0x0E


class ShieldDamageNotification(AsyncPacket):

    ID_CODE = 0x0F


class XpUpdateNotification(AsyncPacket):

    ID_CODE = 0x10


class BoostUpdateNotification(AsyncPacket):

    ID_CODE = 0x11

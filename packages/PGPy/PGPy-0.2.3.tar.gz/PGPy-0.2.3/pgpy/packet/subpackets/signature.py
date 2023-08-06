""" signature.py

Signature SubPackets
"""
import calendar
from datetime import datetime

from .types import SubPacket

from ..types import CompressionAlgo
from ..types import HashAlgo
from ..types import PFIntEnum
from ..types import SymmetricKeyAlgo
from ...util import bytes_to_int
from ...util import int_to_bytes


class SigSubPacket(SubPacket):
    class Type(SubPacket.Type):
        # 0x00 - Reserved
        # 0x01 - Reserved
        SigCreationTime = 0x02
        SigExpirationTime = 0x03
        ExportableCertification = 0x04
        TrustSignature = 0x05
        RegularExpression = 0x06
        Revocable = 0x07
        # 0x08 - Reserved
        KeyExpirationTime = 0x09
        # 0x0A - Placeholder for backwards compatibility
        PreferredSymmetricAlgorithms = 0x0B
        RevocationKey = 0x0C
        # 0x0D - Reserved
        # 0x0E - Reserved
        # 0x0F - Reserved
        Issuer = 0x10
        # 0x11 - Reserved
        # 0x12 - Reserved
        # 0x13 - Reserved
        NotationData = 0x14
        PreferredHashAlgorithms = 0x15
        PreferredCompressionAlgorithms = 0x16
        KeyServerPreferences = 0x17
        PreferredKeyServer = 0x18
        PrimaryUserID = 0x19
        PolicyURL = 0x1A
        KeyFlags = 0x1B
        SignerUserID = 0x1C
        RevocationReason = 0x1D
        Features = 0x1E
        SignatureTarget = 0x1F
        EmbeddedSignature = 0x20

        @classmethod
        def opaque(cls):
            return Opaque

        @property
        def subclass(self):
            classes = {'SigCreationTime': SigCreationTime,
                       'SigExpirationTime': SigExpirationTime,
                       'ExportableCertification': None,
                       'TrustSignature': None,
                       'RegularExpression': None,
                       'Revocable': Revocable,
                       'KeyExpirationTime': KeyExpirationTime,
                       'PreferredSymmetricAlgorithms': PreferredSymmetricAlgorithm,
                       'RevocationKey': None,
                       'Issuer': Issuer,
                       'NotationData': None,
                       'PreferredHashAlgorithms': PreferredHashAlgorithm,
                       'PreferredCompressionAlgorithms': PreferredCompressionAlgorithm,
                       'KeyServerPreferences': KeyServerPreferences,
                       'PreferredKeyServer': PreferredKeyServer,
                       'PrimaryUserID': PrimaryUserID,
                       'PolicyURL': PolicyURL,
                       'KeyFlags': KeyFlags,
                       'SignerUserID': None,
                       'RevocationReason': None,
                       'Features': Features,
                       'EmbeddedSignature': EmbeddedSignature}

            if classes[self.name] is not None:
                return classes[self.name]

            # new behavior: return Opaque instead of raising NotImplementedError for any subpacket that isn't
            # yet supported
            return Opaque


class Opaque(SigSubPacket):
    name = "unknown"

    def parse(self, packet):
        self.payload = packet

    def __bytes__(self):
        _bytes = super(Opaque, self).__bytes__()
        _bytes += self.payload
        return _bytes


class SigCreationTime(SigSubPacket):
    name = "signature creation time"

    def parse(self, packet):
        self.payload = datetime.utcfromtimestamp(bytes_to_int(packet))

    def __bytes__(self):
        _bytes = super(SigCreationTime, self).__bytes__()
        _bytes += int_to_bytes(calendar.timegm(self.payload.timetuple()), self.length - 1)
        return _bytes


class ExpirationTime(SigSubPacket):
    def parse(self, packet):
        self.payload = self.payload = bytes_to_int(packet)

    def __bytes__(self):
        _bytes = super(ExpirationTime, self).__bytes__()
        _bytes += int_to_bytes(self.payload, self.length - 1)
        return _bytes


class SigExpirationTime(ExpirationTime):
    pass


class KeyExpirationTime(ExpirationTime):
    name = "key expiration time"


class BooleanSigSubPacket(SigSubPacket):
    def parse(self, packet):
        self.payload = True if bytes_to_int(packet[:1]) == 1 else False

    def __bytes__(self):
        _bytes = super(BooleanSigSubPacket, self).__bytes__()
        _bytes += int_to_bytes(1 if self.payload else 0)
        return _bytes


class Revocable(BooleanSigSubPacket):
    name = "revocable"


class PrimaryUserID(BooleanSigSubPacket):
    name = "primary User ID"


class PolicyURL(SigSubPacket):
    name = "policy URL"

    def parse(self, packet):
        self.payload = packet

    def __bytes__(self):
        _bytes = super(PolicyURL, self).__bytes__()
        _bytes += self.payload
        return _bytes


class PreferredAlgorithm(SigSubPacket):
    def __bytes__(self):
        _bytes = super(PreferredAlgorithm, self).__bytes__()
        for b in self.payload:
            _bytes += b.__bytes__()
        return _bytes


class PreferredSymmetricAlgorithm(PreferredAlgorithm):
    name = "preferred symmetric algorithms"

    def parse(self, packet):
        self.payload = []
        pos = 0
        while pos < len(packet):
            self.payload.append(SymmetricKeyAlgo(bytes_to_int(packet[pos:(pos + 1)])))
            pos += 1


class PreferredHashAlgorithm(PreferredAlgorithm):
    name = "preferred hash algorithms"

    def parse(self, packet):
        self.payload = []
        pos = 0
        while pos < len(packet):
            self.payload.append(HashAlgo(bytes_to_int(packet[pos:(pos + 1)])))
            pos += 1


class PreferredCompressionAlgorithm(PreferredAlgorithm):
    name = "preferred compression algorithms"

    def parse(self, packet):
        self.payload = []
        pos = 0
        while pos < len(packet):
            self.payload.append(CompressionAlgo(bytes_to_int(packet[pos:(pos + 1)])))
            pos += 1


class Issuer(SigSubPacket):
    name = "issuer key ID"

    def parse(self, packet):
        # python 2.7
        if type(packet) is str:
            self.payload = ''.join('{:02x}'.format(ord(c)) for c in packet).upper().encode('latin-1')

        # python 3.x
        else:
            self.payload = ''.join('{:02x}'.format(c) for c in packet).upper().encode('latin-1')

    def __bytes__(self):
        _bytes = super(Issuer, self).__bytes__()
        _bytes += int_to_bytes(int(self.payload, 16), self.length - 1)
        return _bytes


class PreferenceFlags(SigSubPacket):
    class Flags:
        # Override this in subclasses
        pass

    def parse(self, packet):
        self.payload = []
        bits = bytes_to_int(packet)
        for flag in sorted(self.Flags.__members__.values()):
            if bits & flag.value:
                self.payload.append(flag)

    def __bytes__(self):
        _bytes = super(PreferenceFlags, self).__bytes__()
        _bytes += int_to_bytes(sum([f.value for f in self.payload]), self.length - 1)
        return _bytes


class KeyServerPreferences(PreferenceFlags):
    class Flags(PFIntEnum):
        NoModify = 0x80

        def __str__(self):
            flags = {'NoModify': "No-modify"}

            return flags[self.name]

    name = "key server preferences"


class PreferredKeyServer(SigSubPacket):
    name = "preferred key server"

    def parse(self, packet):
        self.payload = packet.decode()

    def __bytes__(self):
        _bytes = super(PreferredKeyServer, self).__bytes__()
        _bytes += self.payload.encode('latin-1')
        return _bytes


class KeyFlags(PreferenceFlags):
    class Flags(PFIntEnum):
        CertifyKeys = 0x01
        SignData = 0x02
        EncryptComms = 0x04
        EncryptStorage = 0x08
        PrivateSplit = 0x10
        Authentication = 0x20
        PrivateShared = 0x80

        def __str__(self):
            flags = {'CertifyKeys': "This key may be used to certify other keys",
                     'SignData': "This key may be used to sign data",
                     'EncryptComms': "This key may be used to encrypt communications",
                     'EncryptStorage': "This key may be used to encrypt storage",
                     'PrivateSplit': "The private component of this key may have been split by a secret-sharing mechanism",
                     'Authentication': "This key may be used for authentication",
                     'PrivateShared': "The private component of this key may be in the possession of more than one person"}

            return flags[self.name]

    name = "key flags"


class Features(PreferenceFlags):
    class Flags(PFIntEnum):
        ModificationDetection = 0x01

        def __str__(self):
            if self == Features.Flags.ModificationDetection:
                return "Modification detection (packets 18 and 19)"

    name = "features"


class EmbeddedSignature(SigSubPacket):
    """
    5.2.3.26.  Embedded Signature

    (1 signature packet body)

    This subpacket contains a complete Signature packet body as
    specified in Section 5.2 above.  It is useful when one signature
    needs to refer to, or be incorporated in, another signature.
    """

    class FakeHeader(object):
        tag = None

        def __bytes__(self):
            return b''

    name = "embedded signature"

    def parse(self, packet):
        from ..fields.fields import Header
        from ..packets import Signature

        self.payload = Signature()
        # this is a dirty hack, and I'm not proud of it
        self.payload.header = EmbeddedSignature.FakeHeader()
        self.payload.header.tag = Header.Tag.Signature
        self.payload.parse(packet)

    def __bytes__(self):
        _bytes = super(EmbeddedSignature, self).__bytes__()
        _bytes += self.payload.__bytes__()
        return _bytes

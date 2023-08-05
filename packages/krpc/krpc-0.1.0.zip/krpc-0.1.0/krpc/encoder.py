# TODO: avoid using internals
from google.protobuf.internal import encoder as protobuf_encoder
from krpc.types import _Types, _ValueType, _MessageType, _ClassType, _EnumType


class _Encoder(object):
    """ Routines for encoding messages and values in the protocol buffer serialization format """

    @classmethod
    def hello_message(cls, name=None):
        """ Generate a hello message with the given name
            truncated to fit if necessary """
        header = b'\x48\x45\x4C\x4C\x4F\xBA\xDA\x55'
        if name is None:
            name = ''
        else:
            name = cls._unicode_truncate(name, 32, 'utf-8')
        name = name.encode('utf-8')
        identifier = name + (b'\x00' * (32-len(name)))
        return header + identifier

    @classmethod
    def _unicode_truncate(cls, string, length, encoding='utf-8'):
        """ Shorten a unicode string so that it's encoding uses at
            most length bytes. """
        encoded = string.encode(encoding=encoding)[:length]
        return encoded.decode(encoding, 'ignore')


    @classmethod
    def encode(cls, x, typ):
        """ Encode a message or value of the given protocol buffer type """
        if isinstance(typ, _MessageType):
            return x.SerializeToString()
        elif isinstance(typ, _ValueType):
            return cls._encode_value(x, typ)
        elif isinstance(typ, _EnumType):
            return cls._encode_value(x, _Types().as_type('int32'))
        elif isinstance(typ, _ClassType):
            object_id = x._object_id if x is not None else 0
            return cls._encode_value(object_id, _Types().as_type('uint64'))
        else:
            raise RuntimeError ('Cannot encode objects of type ' + str(type(x)))

    @classmethod
    def encode_delimited(cls, x, typ):
        """ Encode a message or value with size information
            (for use in a delimited communication stream) """
        data = cls.encode(x, typ)
        delimiter = protobuf_encoder._VarintBytes(len(data))
        return delimiter + data

    @classmethod
    def _encode_value(cls, value, typ):
        return getattr(_ValueEncoder, 'encode_' + typ.protobuf_type)(value)


class _ValueEncoder(object):
    """ Routines for encoding values in the protocol buffer serialization format """

    @classmethod
    def encode_double(cls, value):
        data = []
        def write(x):
            data.append(x)
        #TODO: only handles finite values
        encoder = protobuf_encoder.DoubleEncoder(1,False,False)
        encoder(write, value)
        return ''.join(data[1:]) # strips the tag value

    @classmethod
    def encode_float(cls, value):
        data = []
        def write(x):
            data.append(x)
        #TODO: only handles finite values
        encoder = protobuf_encoder.FloatEncoder(1,False,False)
        encoder(write, value)
        return ''.join(data[1:]) # strips the tag value

    @classmethod
    def _encode_varint(cls, value):
        data = []
        def write(x):
            data.append(x)
        protobuf_encoder._VarintEncoder()(write, value)
        return ''.join(data)

    @classmethod
    def _encode_signed_varint(cls, value):
        data = []
        def write(x):
            data.append(x)
        protobuf_encoder._SignedVarintEncoder()(write, value)
        return ''.join(data)

    @classmethod
    def encode_int32(cls, value):
        return cls._encode_signed_varint(value)

    @classmethod
    def encode_int64(cls, value):
        return cls._encode_signed_varint(value)

    @classmethod
    def encode_uint32(cls, value):
        if value < 0:
            raise ValueError('Value must be non-negative, got %d' % value)
        return cls._encode_varint(value)

    @classmethod
    def encode_uint64(cls, value):
        if value < 0:
            raise ValueError('Value must be non-negative, got %d' % value)
        return cls._encode_varint(value)

    @classmethod
    def encode_bool(cls, value):
        return cls._encode_varint(value)

    @classmethod
    def encode_string(cls, value):
        data = []
        def write(x):
            data.append(x)
        encoded = value.encode('utf-8')
        protobuf_encoder._VarintEncoder()(write, len(encoded))
        write(encoded)
        return ''.join(data)

    @classmethod
    def encode_bytes(cls, value):
        return ''.join([cls._encode_varint(len(value)), value])

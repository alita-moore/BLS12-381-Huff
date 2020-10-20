'''
This file is an interface between py-evm and this repo; it's a collection 
of *current* internal methods of the py-evm codebase that when combined 
deliver desirable uses
'''
from typing import NewType, Callable, TypeVar, Union, Type, AnyStr
import copy
import re
import binascii
from abc import ABCMeta, abstractmethod

from eth_hash.auto import keccak
from eth.vm.message import Message
from eth.consensus import ConsensusContext
from eth.rlp.headers import BlockHeader
from eth.db.chain import ChainDB
from eth.db.atomic import AtomicDB
from eth.vm.chain_context import ChainContext
from collections.abc import Mapping

######################### Typing

HexStr = NewType('HexStr', str)
Any = object()
text_types = (str,)
integer_types = (int,)
string_types = (bytes, str, bytearray)
T = TypeVar("T")
_HEX_REGEXP = re.compile("[0-9a-fA-F]*")
Primitives = Union[bytes, int, bool]
BlockNumber = NewType('BlockNumber', int)
Address = NewType('Address', bytes)
HexAddress = NewType('HexAddress', HexStr)
ChecksumAddress = NewType('ChecksumAddress', HexAddress)
bytes_types = (bytes, bytearray)

def is_text(value: Any) -> bool:
    return isinstance(value, text_types)

def is_integer(value: Any) -> bool:
    return isinstance(value, integer_types) and not isinstance(value, bool)

def is_boolean(value: Any) -> bool:
    return isinstance(value, bool)

def is_string(value: Any) -> bool:
    return isinstance(value, string_types)

def is_bytes(value: Any) -> bool:
    return isinstance(value, bytes_types)

def is_checksum_formatted_address(value: Any) -> bool:

    if not is_hex_address(value):
        return False
    elif remove_0x_prefix(value) == remove_0x_prefix(value).lower():
        return False
    elif remove_0x_prefix(value) == remove_0x_prefix(value).upper():
        return False
    else:
        return True

def is_hex_address(value: Any) -> bool:
    """
    Checks if the given string of text type is an address in hexadecimal encoded form.
    """
    if not is_hexstr(value):
        return False
    else:
        unprefixed = remove_0x_prefix(value)
        return len(unprefixed) == 40

def is_checksum_address(value: Any) -> bool:
    if not is_text(value):
        return False

    if not is_hex_address(value):
        return False
    return value == to_checksum_address(value)

def is_binary_address(value: Any) -> bool:
    """
    Checks if the given string is an address in raw bytes form.
    """
    if not is_bytes(value):
        return False
    elif len(value) != 20:
        return False
    else:
        return True

def is_address(value: Any) -> bool:
    """
    Checks if the given string in a supported value
    is an address in any of the known formats.
    """
    if is_checksum_formatted_address(value):
        return is_checksum_address(value)
    elif is_hex_address(value):
        return True
    elif is_binary_address(value):
        return True
    else:
        return False

######################### Conversions

def is_0x_prefixed(value: Any) -> bool:
    if not is_text(value):
        raise TypeError(
            "is_0x_prefixed requires text typed arguments. Got: {0}".format(repr(value))
        )
    return value.startswith("0x") or value.startswith("0X")

def remove_0x_prefix(value: HexStr) -> HexStr:
    if is_0x_prefixed(value):
        return HexStr(value[2:])
    return value

def add_0x_prefix(value: HexStr) -> HexStr:
    if is_0x_prefixed(value):
        return value
    return HexStr("0x" + value)

def to_hex(
    primitive: Primitives = None, hexstr: HexStr = None, text: str = None
) -> HexStr:
    """
    Auto converts any supported value into its hex representation.
    Trims leading zeros, as defined in:
    https://github.com/ethereum/wiki/wiki/JSON-RPC#hex-value-encoding
    """
    if hexstr is not None:
        return add_0x_prefix(HexStr(hexstr.lower()))

    if text is not None:
        return encode_hex(text.encode("utf-8"))

    if is_boolean(primitive):
        return HexStr("0x1") if primitive else HexStr("0x0")

    if isinstance(primitive, (bytes, bytearray)):
        return encode_hex(primitive)
    elif is_string(primitive):
        raise TypeError(
            "Unsupported type: The primitive argument must be one of: bytes,"
            "bytearray, int or bool and not str"
        )

    if is_integer(primitive):
        return HexStr(hex(primitive))

    raise TypeError(
        "Unsupported type: '{0}'.  Must be one of: bool, str, bytes, bytearray"
        "or int.".format(repr(type(primitive)))
    )

def encode_hex(value: AnyStr) -> HexStr:
    if not is_string(value):
        raise TypeError("Value must be an instance of str or unicode")
    elif isinstance(value, (bytes, bytearray)):
        ascii_bytes = value
    else:
        ascii_bytes = value.encode("ascii")

    binary_hex = binascii.hexlify(ascii_bytes)
    return add_0x_prefix(HexStr(binary_hex.decode("ascii")))

def decode_hex(value: str) -> bytes:
    if not is_text(value):
        raise TypeError("Value must be an instance of str")
    non_prefixed = remove_0x_prefix(HexStr(value))
    # unhexlify will only accept bytes type someday
    ascii_hex = non_prefixed.encode("ascii")
    return binascii.unhexlify(ascii_hex)

def to_bytes(
    primitive: Primitives = None, hexstr: HexStr = None, text: str = None
) -> bytes:
    if is_boolean(primitive):
        return b"\x01" if primitive else b"\x00"
    elif isinstance(primitive, bytearray):
        return bytes(primitive)
    elif isinstance(primitive, bytes):
        return primitive
    elif is_integer(primitive):
        return to_bytes(hexstr=to_hex(primitive))
    elif hexstr is not None:
        if len(hexstr) % 2:
            # type check ignored here because casting an Optional arg to str is not possible
            hexstr = "0x0" + remove_0x_prefix(hexstr)  # type: ignore
        return decode_hex(hexstr)
    elif text is not None:
        return text.encode("utf-8")
    raise TypeError(
        "expected a bool, int, byte or bytearray in first arg, or keyword of hexstr or text"
    )

def is_hexstr(value: Any) -> bool:
    if not is_text(value):
        return False

    elif value.lower() == "0x":
        return True

    unprefixed_value = remove_0x_prefix(value)
    if len(unprefixed_value) % 2 != 0:
        value_to_decode = "0" + unprefixed_value
    else:
        value_to_decode = unprefixed_value

    if not _HEX_REGEXP.fullmatch(value_to_decode):
        return False

    try:
        # convert from a value like '09af' to b'09af'
        ascii_hex = value_to_decode.encode("ascii")
    except UnicodeDecodeError:
        # Should have already been caught by regex above, but just in case...
        return False

    try:
        # convert to a value like b'\x09\xaf'
        value_as_bytes = binascii.unhexlify(ascii_hex)
    except binascii.Error:
        return False
    except TypeError:
        return False
    else:
        return bool(value_as_bytes)

def hexstr_if_str(
    to_type: Callable[..., T], hexstr_or_primitive: Union[bytes, int, str]
) -> T:
  """
  Convert to a type, assuming that strings can be only hexstr (not unicode text)

  :param to_type function: takes the arguments (primitive, hexstr=hexstr, text=text),
      eg~ to_bytes, to_text, to_hex, to_int, etc
  :param hexstr_or_primitive bytes, str, int: value to convert
  """
  if isinstance(hexstr_or_primitive, str):
    if remove_0x_prefix(HexStr(hexstr_or_primitive)) and not is_hexstr(
        hexstr_or_primitive
    ):
      raise ValueError(
        "when sending a str, it must be a hex string. Got: {0!r}".format(
          hexstr_or_primitive
        )
      )
    return to_type(hexstr=hexstr_or_primitive)
  else:
    return to_type(hexstr_or_primitive)

def to_normalized_address(value: AnyStr) -> HexAddress:
    """
    Converts an address to its normalized hexadecimal representation.
    """
    try:
        hex_address = hexstr_if_str(to_hex, value).lower()
    except AttributeError:
        raise TypeError(
            "Value must be any string, instead got type {}".format(type(value))
        )
    if is_address(hex_address):
        return HexAddress(HexStr(hex_address))
    else:
        raise ValueError(
            "Unknown format {}, attempted to normalize to {}".format(value, hex_address)
        )

def to_checksum_address(value: AnyStr) -> ChecksumAddress:
    """
    Makes a checksum address given a supported format.
    """
    norm_address = to_normalized_address(value)
    address_hash = encode_hex(keccak(text=remove_0x_prefix(HexStr(norm_address))))

    checksum_address = add_0x_prefix(
        HexStr(
            "".join(
                (
                    norm_address[i].upper()
                    if int(address_hash[i], 16) > 7
                    else norm_address[i]
                )
                for i in range(2, 42)
            )
        )
    )
    return ChecksumAddress(HexAddress(checksum_address))

def to_canonical_address(address: AnyStr) -> Address:
    """
    Given any supported representation of an address
    returns its canonical form (20 byte long string).
    """
    return Address(decode_hex(to_normalized_address(address)))

######################### Tools

def _get_factory(f, kwargs):
  factory = kwargs.pop('factory', dict)
  if kwargs:
    raise TypeError("{}() got an unexpected keyword argument "
                      "'{}'".format(f.__name__, kwargs.popitem()[0]))
  return factory

def assemble(*codes):
  return b''.join(
    hexstr_if_str(to_bytes, element)
    for element in codes
  )

def merge(*dicts, **kwargs):
    """ Merge a collection of dictionaries

    >>> merge({1: 'one'}, {2: 'two'})
    {1: 'one', 2: 'two'}

    Later dictionaries have precedence

    >>> merge({1: 2, 3: 4}, {3: 3, 4: 4})
    {1: 2, 3: 3, 4: 4}

    See Also:
        merge_with
    """
    if len(dicts) == 1 and not isinstance(dicts[0], Mapping):
        dicts = dicts[0]
    factory = _get_factory(merge, kwargs)

    rv = factory()
    for d in dicts:
      rv.update(d)
    return rv

###########################################################################

GENESIS_HEADER = BlockHeader(
    difficulty=17179869184,
    block_number=BlockNumber(0),
    gas_limit=5000,
)

def setup_computation(vm_class, code):
  CANONICAL_ADDRESS_A = to_canonical_address("0x0f572e5295c57f15886f9b263e2f6d2d6c7b5ec6")
  CANONICAL_ADDRESS_B = to_canonical_address("0xcd1722f3947def4cf144679da39c4c32bdc35681")
  message = Message(
    to=CANONICAL_ADDRESS_A,
    sender=CANONICAL_ADDRESS_B,
    create_address=CANONICAL_ADDRESS_B,
    value=0,
    data=b'',
    code=code,
    gas=1000000,
  )

  chain_context = ChainContext(None)
  tx_context = vm_class._state_class.transaction_context_class(
      gas_price=1,
      origin=CANONICAL_ADDRESS_B,
  )

  db = AtomicDB()
  vm = vm_class(GENESIS_HEADER, ChainDB(db), chain_context, ConsensusContext(db))
  computation = vm_class._state_class.computation_class(
      state=vm.state,
      message=message,
      transaction_context=tx_context,
  )

  return computation

"""Protocol definitions for Arduino load cell communication."""

import struct
from enum import IntEnum
from typing import List, Tuple, Dict, Any, Optional, NamedTuple


# System constants
MAX_LOAD_CELLS = 4


class Status(IntEnum):
    """Load cell controller status codes."""
    IDLE = 0
    ZEROING = 1
    CALIBRATING = 2
    STREAMING = 3
    ERROR = 255


class Error(IntEnum):
    """Error codes for load cell operations."""
    NONE = 0
    INVALID_COMMAND = 1
    INVALID_CELL_ID = 2
    CELL_NOT_CONFIGURED = 3
    CALIBRATION_FAILED = 4


class Command(IntEnum):
    """Command bit flags for load cell operations."""
    CONFIGURE = 1 << 0  # 0b00000001
    ZERO = 1 << 1       # 0b00000010
    CALIBRATE = 1 << 2  # 0b00000100
    RESET = 1 << 3      # 0b00001000


class CommandPacket(NamedTuple):
    """Command packet sent from Python to Arduino."""
    seq_id: int        # Sequence ID for tracking requests
    flags: int         # Command flags bitfield
    cell_id: int       # Target cell ID (255 = all cells)
    dout_pin: int      # DOUT pin for configuration
    sck_pin: int       # SCK pin for configuration
    calibration_mass: float  # Mass for calibration
    reserved: bytes    # Reserved for future use
    
    @classmethod
    def format(cls) -> str:
        """Get the struct format string for this packet."""
        return '<BBBBBf2s'  # seq_id(B), flags(B), cell_id(B), dout_pin(B), sck_pin(B), cal_mass(f), reserved(2B)
    
    @classmethod
    def size(cls) -> int:
        """Get the size in bytes of this packet."""
        return struct.calcsize(cls.format())
    
    def pack(self) -> bytes:
        """Pack this packet into bytes for transmission."""
        return struct.pack(
            self.format(),
            self.seq_id,
            self.flags,
            self.cell_id,
            self.dout_pin,
            self.sck_pin,
            self.calibration_mass,
            self.reserved
        )
    
    @classmethod
    def unpack(cls, data: bytes) -> 'CommandPacket':
        """Unpack bytes into a CommandPacket."""
        return cls(*struct.unpack(cls.format(), data))
    
    @classmethod
    def create(cls, seq_id: int, flags: int = 0, cell_id: int = 0, 
               dout_pin: int = 0, sck_pin: int = 0, 
               calibration_mass: float = 0.0) -> 'CommandPacket':
        """Create a new CommandPacket with the given parameters."""
        return cls(
            seq_id=seq_id,
            flags=flags, 
            cell_id=cell_id,
            dout_pin=dout_pin,
            sck_pin=sck_pin,
            calibration_mass=calibration_mass,
            reserved=bytes([0, 0])
        )


class ResponsePacket(NamedTuple):
    """Response packet sent from Arduino to Python."""
    seq_id: int              # Sequence ID matching the request
    status: int              # Global status code
    error: int               # Error code
    active_cell: int         # Currently active cell (255 = none)
    cell_configured: bytes   # Configuration status for each cell (4 bytes)
    cell_readings: List[float]  # Current readings for each cell (4 floats)
    calibration_factors: List[float]  # Calibration factors for each cell (4 floats)
    
    @classmethod
    def format(cls) -> str:
        """Get the struct format string for this packet."""
        # Format: seq_id(B) + status(B) + error(B) + active_cell(B) + 
        #         cell_configured(4B) + cell_readings(4f) + calibration_factors(4f)
        return f'<BBBB{MAX_LOAD_CELLS}B{MAX_LOAD_CELLS}f{MAX_LOAD_CELLS}f'
    
    @classmethod
    def size(cls) -> int:
        """Get the size in bytes of this packet."""
        return struct.calcsize(cls.format())
    
    def pack(self) -> bytes:
        """Pack this packet into bytes for transmission."""
        return struct.pack(
            self.format(),
            self.seq_id,
            self.status,
            self.error,
            self.active_cell,
            *self.cell_configured,
            *self.cell_readings,
            *self.calibration_factors
        )
    
    @classmethod
    def unpack(cls, data: bytes) -> 'ResponsePacket':
        """Unpack bytes into a ResponsePacket."""
        unpacked = struct.unpack(cls.format(), data)
        
        seq_id = unpacked[0]
        status = unpacked[1]
        error = unpacked[2]
        active_cell = unpacked[3]
        
        # Extract cell configuration bytes (4 bytes)
        cell_configured = bytes(unpacked[4:4+MAX_LOAD_CELLS])
        
        # Extract cell readings (4 floats)
        offset = 4 + MAX_LOAD_CELLS
        cell_readings = list(unpacked[offset:offset+MAX_LOAD_CELLS])
        
        # Extract calibration factors (4 floats)
        offset += MAX_LOAD_CELLS
        calibration_factors = list(unpacked[offset:offset+MAX_LOAD_CELLS])
        
        return cls(
            seq_id=seq_id,
            status=status,
            error=error,
            active_cell=active_cell,
            cell_configured=cell_configured,
            cell_readings=cell_readings,
            calibration_factors=calibration_factors
        )


def cell_configured_to_bool(cell_configured: bytes) -> List[bool]:
    """Convert cell_configured bytes to a list of booleans."""
    return [bool(b) for b in cell_configured]


def bool_to_cell_configured(configured: List[bool]) -> bytes:
    """Convert a list of booleans to cell_configured bytes."""
    return bytes([int(b) for b in configured]) 
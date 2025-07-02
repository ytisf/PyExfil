class FileDoesNotExist(Exception):
    """Raised when the input file does not exist."""
    def __init__(self, file_path):
        self.message = f"Input file '{file_path}' does not exist!"
        super().__init__(self.message)

class InvalidPacketFormat(Exception):
    """Raised when the packet format is invalid."""
    def __init__(self, packet):
        self.message = f"The packet format is invalid: {packet}"
        super().__init__(self.message)

class DecryptionFailed(Exception):
    """Raised when decryption of data fails."""
    def __init__(self, reason):
        self.message = f"Decryption failed: {reason}"
        super().__init__(self.message)

class CompressionError(Exception):
    """Raised when compression or decompression fails."""
    def __init__(self, reason):
        self.message = f"Compression error: {reason}"
        super().__init__(self.message)

class PacketMissing(Exception):
    """Raised when a required packet is missing during reassembly."""
    def __init__(self, packet_number):
        self.message = f"Packet number {packet_number} is missing."
        super().__init__(self.message)

class HashMismatch(Exception):
    """Raised when there is a mismatch in hash values."""
    def __init__(self, expected_hash, actual_hash):
        self.message = f"Hash mismatch: expected {expected_hash}, got {actual_hash}"
        super().__init__(self.message)

class UnsupportedPythonVersion(Exception):
    """Raised when the Python version is not supported."""
    def __init__(self, version):
        self.message = f"Unsupported Python version: {version}. Please use Python 3 or above."
        super().__init__(self.message)

class LibraryNotFound(Exception):
    """Raised when the required library for audio processing is not found."""
    def __init__(self, library_name):
        self.message = f"Required library '{library_name}' not found."
        super().__init__(self.message)

class PermissionDenied(Exception):
    """Raised when the script does not have permission to access the audio device."""
    def __init__(self, operation):
        self.message = f"Permission denied for {operation} operation."
        super().__init__(self.message)

class UnsupportedOS(Exception):
    """Raised when the operating system is not supported by the script."""
    def __init__(self, os_name):
        self.message = f"Operating system '{os_name}' is not supported."
        super().__init__(self.message)

class FetchDataError(Exception):
    """Raised when the script does not have permission to access the audio device."""
    def __init__(self, url):
        self.message = f"Could not fetch data from {url}."
        super().__init__(self.message)


class SendDataError(Exception):
    """Raised when there was an error in sending data to firebase"""
    def __init__(self, url):
        self.message = f"Could not send data to {url}."
        super().__init__(self.message)


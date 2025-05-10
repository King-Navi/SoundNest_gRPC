class InvalidImageFormatError(ValueError):
    """Raised when the image extension is not supported."""
    pass

class InvalidImageContentError(ValueError):
    """Raised when the image content is invalid or corrupted."""
    pass

class ImageSavingError(Exception):
    """Raised when the image could not be saved to disk."""
    pass

class SongSavingError(Exception):
    """Raised when the song could not be saved to disk."""
    pass

class InvalidSongFormatError(ValueError):
    """Raised when the image extension is not supported."""
    pass

class MissingArguments(ValueError):
    def __init__(self, missing: str):
        self.missing = missing
        message = f"Missing required argument: {missing}"
        super().__init__(message)

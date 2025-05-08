class InvalidImageFormatError(ValueError):
    """Raised when the image extension is not supported."""
    pass

class InvalidImageContentError(ValueError):
    """Raised when the image content is invalid or corrupted."""
    pass

class ImageSavingError(Exception):
    """Raised when the image could not be saved to disk."""
    pass

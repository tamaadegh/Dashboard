
import sys
import inspect
import imagekitio
from imagekitio import ImageKit

try:
    print(f"Python Version: {sys.version}")
    print(f"ImageKitio Version: {getattr(imagekitio, '__version__', 'unknown')}")
    print(f"ImageKitio File: {imagekitio.__file__}")
    
    # Inspect ImageKit.__init__ parameters
    sig = inspect.signature(ImageKit.__init__)
    print(f"ImageKit.__init__ signature: {sig}")
    
    # Check if public_key is in parameters
    params = list(sig.parameters.keys())
    print(f"Parameters: {params}")

    # Check for exceptions module
    try:
        from imagekitio.exceptions import BadRequestException
        print("imagekitio.exceptions.BadRequestException: FOUND")
    except ImportError:
        print("imagekitio.exceptions.BadRequestException: NOT FOUND")

except Exception as e:
    print(f"Error inspecting imagekitio: {e}")

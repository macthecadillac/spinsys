"""
This file is part of spinsys.

Spinsys is free software: you can redistribute it and/or modify
it under the terms of the BSD 3-clause license. See LICENSE.txt
for exact terms and conditions.


This module provides custom exception classes for more convenient
exception handling. The following classes are included:
    NoConvergence
    SizeMismatchError
    NotFoundError
    OutOfBoundsError
"""


class NoConvergence(Exception):
    pass


class SizeMismatchError(Exception):
    pass


class NotFoundError(Exception):
    pass


class OutOfBoundsError(Exception):
    pass


class SameSite(Exception):
    pass

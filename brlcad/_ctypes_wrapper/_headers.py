"""
brlcad._ctypes_wrapper._headers
~~~~~~~~~~~~~~~~

Shared types.
"""

import ctypes

# /usr/include/x86_64-linux-gnu/bits/types.h: 148
__time_t = ctypes.c_long

# /usr/include/time.h: 75
time_t = __time_t

# /usr/include/x86_64-linux-gnu/bits/types.h: 140
__off_t = ctypes.c_long

# # /usr/include/x86_64-linux-gnu/bits/types.h: 141
__off64_t = ctypes.c_long

# /usr/include/x86_64-linux-gnu/sys/types.h: 86
off_t = __off_t

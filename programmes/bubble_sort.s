BR .start

.swapped
DATA 0
.i
DATA .array - 1
.buffer
DATA 0
.array
DATA 4
DATA 1
DATA 3
DATA 5
.array_end
DATA 2

.start
LDAC 0
STAM .swapped

.loop
LDAM .i
LDBC 1
ADD
STAM .i
LDAI 0
LDBM .i
LDBI 1
SUB
BRN .swap

LDAM .i
LDBM .array_end
SUB
BRZ .start

.swap
# BX = array[i+1]
# buffer = array[i]
LDAM .i
LDAI 0
STAM .buffer
# AX = array[i+1]
LDAM .i
LDAI 1
# BX = i
LDBM .i
# array[i] = array[i+1]
STAI 0
# array[i+1] = buffer
LDAM .buffer
STAI 1
LDAC 1
STAM .swapped
BR .loop

LDAM .swapped
BRZ .start

.end
HALT
BR .start

.swapped
DATA 1
.i
DATA .array - 1
.buffer
DATA 0
.array
DATA 4
DATA 3
DATA 3
DATA 5
DATA 2

.start
LDAM .swapped
BRZ .end

LDAC 0
STAM .swapped
LDAC .array - 1
STAM .i

.loop
LDAM .i
LDBC 1
ADD
STAM .i
LDAI 1
LDBM .i
LDBI 0
SUB
BRN .swap
BR .loop_end

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

.loop_end
LDAM .i
LDBC .start - 2
SUB
BRZ .start
BR .loop

.end
HALT
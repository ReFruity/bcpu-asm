BR .start

.i
DATA .array + 1
.j
DATA 1
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
LDAC .array_end + 1
LDBM .i
SUB
BRZ .end
LDAM .i
STAM .j

.loop
LDAM .j
LDBC .array - 1
SUB
BRZ .increment_i
.compare
LDAM .j
PFIX 0xF
LDAI 0xF
LDBM .j
LDBI 0
SUB
BRN .increment_i
.swap
LDAM .j
PFIX 0xF
LDAI 0xF
STAM .buffer
LDAM .j
LDAI 0
LDBM .j
PFIX 0xF
STAI 0xF
LDAM .buffer
LDBM .j
STAI 0
.decrement_j
LDAM .j
LDBC 1
SUB
STAM .j
BR .loop
.increment_i
LDAM .i
LDBC 1
ADD
STAM .i
.loop_end
BR .start

.end
HALT

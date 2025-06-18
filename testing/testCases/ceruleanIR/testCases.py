
from ...test import *

allCeruleanIRTests = TestGroup ("All CeruleanIR Tests", "", [
    Test ("Hello World", code="""
function int32 @main () {
    block entry {
        %i_ptr = alloca (type(int32), int32(1))
        store (ptr(%i_ptr), int32(0), int32(0))
        jmp (block(for_cond))
    }
    block for_cond {
        %i_curr = load (type(int32), ptr(%i_ptr), int32(0))
        jge (int32(%i_curr), int32(13), block(for_end))
        jmp (block(for_body))
    }
    block for_body {
        %char = load (type(char), ptr("Hello, World!"), int32(%i_curr))
        call @__builtin__print__char (char(%char))
        jmp (block(for_update))
    }
    block for_update {
        %i_next = add (int32(%i_curr), int32(1))
        store (ptr(%i_ptr), int32(0), int32(%i_next))
        jmp (block(for_cond))
    }
    block for_end {
        call @__builtin__println ()
        return ()
    }
}""", expectedOutput="Hello, World!\n", sourceLang=TestSource.CeruleanIR),
])

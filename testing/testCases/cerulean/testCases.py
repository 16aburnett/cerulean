
from ...test import *

allCeruleanTests = TestGroup ("All Cerulean Tests", "", [
    Test ("Empty file", code="function void main(){}", expectedOutput="", sourceLang=TestSource.Cerulean),
    TestGroup ("Printing", "", [
        Test ("print int", code="function void main(){print (7);}", expectedOutput="7", sourceLang=TestSource.Cerulean),
        Test ("print float", code="function void main(){print (3.14);}", expectedOutput="3.14", sourceLang=TestSource.Cerulean),
        Test ("print char", code='function void main(){print (\'A\');}', expectedOutput="A", sourceLang=TestSource.Cerulean),
        Test ("print char[]", code='function void main(){print (\"Amy\");}', expectedOutput="Amy", sourceLang=TestSource.Cerulean),
        Test ("print with no arg should fail", code='function void main(){print ();}', expectedCompilerOutput="Semantic Error: No function matching signature print()", shouldCompile=False, sourceLang=TestSource.Cerulean)
    ]),
    TestGroup ("Arithmetic", "", [
        TestGroup ("Integer Arithmetic", "", [
            TestGroup ("Addition", "", [
                Test ("Test0", code="function void main(){print (21 + 23);}", expectedOutput="44", sourceLang=TestSource.Cerulean),
                Test ("Test1", code="function void main(){print (21 + -23);}", expectedOutput="-2", sourceLang=TestSource.Cerulean),
                Test ("Test2", code="function void main(){print (-21 + 23);}", expectedOutput="2", sourceLang=TestSource.Cerulean),
                Test ("Test3", code="function void main(){print (-21 + -23);}", expectedOutput="-44", sourceLang=TestSource.Cerulean),
                Test ("Test4", code="function void main(){print (2000000000 + 1000000000);}", expectedOutput="3000000000", expectedOutputAMYASM="3000000000", sourceLang=TestSource.Cerulean)
            ]),
            TestGroup ("Subtraction", "", [
                Test ("Test0", code="function void main(){print (21 - 23);}", expectedOutput="-2", sourceLang=TestSource.Cerulean),
                Test ("Test1", code="function void main(){print (21 - -23);}", expectedOutput="44", sourceLang=TestSource.Cerulean),
                Test ("Test2", code="function void main(){print (-21 - 23);}", expectedOutput="-44", sourceLang=TestSource.Cerulean),
                Test ("Test3", code="function void main(){print (-21 - -23);}", expectedOutput="2", sourceLang=TestSource.Cerulean),
                Test ("Test4", code="function void main(){print (-2000000000 - 1000000000);}", expectedOutput="-3000000000", expectedOutputAMYASM="-3000000000", sourceLang=TestSource.Cerulean)
            ]),
            TestGroup ("Multiplication", "", [
                Test ("Test0", code="function void main(){print (3 * 31);}", expectedOutput="93", sourceLang=TestSource.Cerulean),
                Test ("Test1", code="function void main(){print (7 * -7);}", expectedOutput="-49", sourceLang=TestSource.Cerulean),
                Test ("Test2", code="function void main(){print (-9 * 4);}", expectedOutput="-36", sourceLang=TestSource.Cerulean),
                Test ("Test3", code="function void main(){print (-5 * -20);}", expectedOutput="100", sourceLang=TestSource.Cerulean),
                Test ("Test4", code="function void main(){print (-1000000000 * 1000000000);}", expectedOutput="-1000000000000000000", expectedOutputAMYASM="-1000000000000000000", sourceLang=TestSource.Cerulean)
            ]),
            TestGroup ("Division", "", [
                Test ("Test0", code="function void main(){print (45 / 9);}", expectedOutput="5", sourceLang=TestSource.Cerulean),
                Test ("Test1", code="function void main(){print (45 / -5);}", expectedOutput="-9", sourceLang=TestSource.Cerulean),
                Test ("Test2", code="function void main(){print (-5 / 2);}", expectedOutput="-2", expectedOutputAMYASM="-3", expectedOutputPython="-3", sourceLang=TestSource.Cerulean),
                Test ("Test3", code="function void main(){print (-5 / -20);}", expectedOutput="0", sourceLang=TestSource.Cerulean)
            ]),
            TestGroup ("Mod", "", [
                Test ("Test0", code="function void main(){print (45 % 9);}", expectedOutput="0", sourceLang=TestSource.Cerulean),
                Test ("Test1", code="function void main(){print (45 % 2);}", expectedOutput="1", sourceLang=TestSource.Cerulean),
                Test ("Test2", code="function void main(){print (-5 % 2);}", expectedOutput="-1", expectedOutputAMYASM="1", expectedOutputPython="1", sourceLang=TestSource.Cerulean),
                Test ("Test3", code="function void main(){print (-5 % -20);}", expectedOutput="-5", sourceLang=TestSource.Cerulean)
            ]),
            TestGroup ("Combining Operators", "", [
                Test (
                    "Test0", 
                    code="""function void main(){
int32 x = (-17 + 42 * (2 + 2) + 1) * -1;
int32 y = x * 23;
print (y);
}""", 
                    expectedOutput="-3496",
                    sourceLang=TestSource.Cerulean
                ),
            ])
        ])
    ]),
    TestGroup ("Variables", "", [
        Test ("Declaration", code="function void main(){int32 x; int32 y = 10;}", expectedOutput="", sourceLang=TestSource.Cerulean),
        Test ("Assignment", code="function void main(){int32 x = 10;}", expectedOutput="", sourceLang=TestSource.Cerulean),
        Test ("Variable value", code="function void main(){float32 x = 3.14;print(x);}", expectedOutput="3.14", sourceLang=TestSource.Cerulean),
        Test ("Arithmetic With Variables", code="function void main(){int32 x = 30; int32 y = 42; print ((x + y) / 8);}", expectedOutput="9", sourceLang=TestSource.Cerulean),
        Test ("Reassign Variables", code="function void main(){int32 x = 10; x = 42; print(x);}", expectedOutput="42", sourceLang=TestSource.Cerulean),
        Test ("Ensure reference before assignment fails", code="function void main(){int32 x; print (x);}", shouldCompile=False, expectedCompilerOutput="", sourceLang=TestSource.Cerulean),
    ]),
    TestGroup ("Misc", "", [
        Test ("Test0", code="function void main(){int32 x = 10;print (x);}", expectedOutput="10", sourceLang=TestSource.Cerulean),
        Test ("Test1", code="function void main(){int32 x = 10;print (x+2);}", expectedOutput="12", sourceLang=TestSource.Cerulean),
        Test ("Test2", code="function void main(){int32 x = 10;print (x*2);}", expectedOutput="20", sourceLang=TestSource.Cerulean),
    ]),
    TestGroup ("Functions", "", [
        Test ("Super Simple Function Declaration", code=
            """
            function void print10 ()
            {
                print (10);
            }
            function void main () {
                print10 ();
            }
            """, expectedOutput="10", sourceLang=TestSource.Cerulean),
        Test ("Test Parameters", code=
            """
            function void printint (int32 a)
            {
                print (a);
            }
            function void main () {
                printint (42);
            }
            """, expectedOutput="42", sourceLang=TestSource.Cerulean),
        Test ("Test Return", code=
            """
            function float32 getPI ()
            {
                return 3.14;
            }
            function void main () {
                print (getPI());
            }
            """, expectedOutput="3.14", sourceLang=TestSource.Cerulean),
        Test ("Test Return no value", code=
            """
            function void printsomething ()
            {
                print ("this");
                return;
                print ("not this");
            }
            function void main() {printsomething();}
            """, expectedOutput="this", sourceLang=TestSource.Cerulean),
        TestGroup (
            "Max function", 
            """
            function int32 max (int32 a, int32 b)
            {
                if (a >= b)
                    return a;
                return b;
            }
            """, 
            [
                Test ("a < b", "function void main(){print (max(-3, 7));}", expectedOutput="7", sourceLang=TestSource.Cerulean),
                Test ("a == b", "function void main(){print (max(7, 7));}", expectedOutput="7", sourceLang=TestSource.Cerulean),
                Test ("a > b", "function void main(){print (max(42, 3));}", expectedOutput="42", sourceLang=TestSource.Cerulean),
            ]
        ),
    ]),
])

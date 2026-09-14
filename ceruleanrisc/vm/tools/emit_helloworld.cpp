// This is just a super simple helper script for generating bytecode files
#include "criscvm.hpp"
#include "encoders.hpp"
#include <fstream>
#include <vector>
#include <cstdint>

int main (int argc, char* argv[]) {

    std::vector<uint8_t> bytecode;
    const std::string msg = "Hello\n";
    for (char c : msg) {
        pushInstr(bytecode, encodeRI(Opcode::LLI, 9, c));
        pushInstr(bytecode, encodeRI(Opcode::LUI, 9, 0));
        pushInstr(bytecode, encodeR(Opcode::PUTCHAR, 9));
    }
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    std::ofstream out("helloworld.criscbc", std::ios::binary);
    out.write(reinterpret_cast<const char*>(bytecode.data()), bytecode.size());
    out.close();

    return 0;
}
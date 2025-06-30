// TeeBuf is a custom stream buffer that duplicates output to both the original stream and a string stream for capturing output.
#pragma once
#include <streambuf>
#include <ostream>
#include <sstream>

class TeeBuf : public std::streambuf {
public:
    TeeBuf(std::streambuf* original, std::ostringstream& capture)
        : originalBuf(original), captureStream(capture) {}

protected:
    int overflow(int c) override {
        if (c != EOF) {
            captureStream.put(static_cast<char>(c));
            originalBuf->sputc(c);
        }
        return c;
    }

private:
    std::streambuf* originalBuf;
    std::ostringstream& captureStream;
};

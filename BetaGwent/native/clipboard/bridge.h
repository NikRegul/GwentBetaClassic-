#pragma once
#include <windows.h>
#include <cstdint>
#include <cstddef>

namespace bgclip {
constexpr char ProbeFormat[] = "betagwent:windows-clipboard-v1";
constexpr char ReadProbeFormat[] = "betagwent:windows-paste-v1";
constexpr char ReadBeginFormat[] = "betagwent:windows-paste-begin-v1";
constexpr char ReadBitFormat[] = "betagwent:windows-paste-bit-v1";
using Store = void(__fastcall*)(void*, const wchar_t*, size_t);
using Thunk = void(__fastcall*)(const void*, void*, const void*, void*, unsigned, const void*);
struct Image {
    const unsigned char* data;
    size_t size;
    uintptr_t pointerBase;
};
struct Hooks {
    void** storeSlot = nullptr;
    void** thunkSlot = nullptr;
    unsigned storeMatches = 0;
    unsigned thunkMatches = 0;
};
Hooks FindHooks(const Image& image);
bool ValidDeck(const wchar_t* text, size_t count);
bool WriteDeck(const wchar_t* text, size_t count);
bool NormalizeDeck(const wchar_t* text, size_t count, wchar_t* output, size_t capacity, size_t& length);
bool ReadDeck(wchar_t* output, size_t capacity, size_t& length);
bool DeckBit(const wchar_t* text, size_t count, const char* query);
bool Install(const Hooks& hooks);
void __fastcall OnTextStore(void*, const wchar_t*, size_t);
void __fastcall SetData(const void*, void*, const void*, void*, unsigned, const void*);
}

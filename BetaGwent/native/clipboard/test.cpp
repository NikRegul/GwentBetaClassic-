#include "bridge.h"
#include <string>
#include <vector>
#include <cstdio>
#include <cstring>
#include <cwchar>
#include <cstdlib>
static unsigned checks=0;
static void Check(bool ok,const char* label) {
    if(!ok){std::fprintf(stderr,"FAIL: %s\n",label);std::exit(1);}checks++;
}
static std::wstring Deck(unsigned cards=25) {
    std::wstring s=L"BG1:2:131101:";
    for(unsigned i=0;i<cards;i++){if(i)s+=L',';s+=L"112210";}return s;
}
static void Scan(const wchar_t* filename) {
    HMODULE resource=LoadLibraryExW(filename,nullptr,LOAD_LIBRARY_AS_IMAGE_RESOURCE);
    Check(resource!=nullptr,"map executable as resource, without executing it");
    auto base=reinterpret_cast<const unsigned char*>(reinterpret_cast<uintptr_t>(resource)&~uintptr_t(3));
    auto dos=reinterpret_cast<const IMAGE_DOS_HEADER*>(base);
    auto nt=reinterpret_cast<const IMAGE_NT_HEADERS64*>(base+dos->e_lfanew);
    auto h=bgclip::FindHooks({base,nt->OptionalHeader.SizeOfImage,nt->OptionalHeader.ImageBase});
    Check(h.storeMatches==1&&h.thunkMatches==1&&h.storeSlot&&h.thunkSlot,"one structurally validated clipboard and one setData thunk");
    std::printf("IMAGE storeSlotRva=0x%zx thunkSlotRva=0x%zx\n",reinterpret_cast<const unsigned char*>(h.storeSlot)-base,reinterpret_cast<const unsigned char*>(h.thunkSlot)-base);
    FreeLibrary(resource);
}
struct Value {uint32_t flags=0;uint32_t pad=0;uint64_t unused=0;const void* data=nullptr;uint64_t tail=0;};
static_assert(sizeof(Value)==32,"AS3 value layout");
static void __fastcall Noop(void*,const wchar_t*,size_t) {}
static const wchar_t* simulatedPayload=nullptr;
static bool simulatedResult=false;
static unsigned originalCalls=0;
static void __fastcall FalseThunk(const void*,void*,const void*,void* result,unsigned,const void*) {
    originalCalls++;auto v=static_cast<Value*>(result);v->flags=1;v->data=simulatedResult?reinterpret_cast<void*>(1):nullptr;
    if(simulatedPayload)bgclip::OnTextStore(nullptr,simulatedPayload,std::wcslen(simulatedPayload));
}
static std::wstring ReadClipboard() {
    Check(OpenClipboard(nullptr)!=FALSE,"open clipboard for verification");
    auto data=GetClipboardData(CF_UNICODETEXT);Check(data!=nullptr,"Unicode clipboard data exists");
    auto p=static_cast<const wchar_t*>(GlobalLock(data));Check(p!=nullptr,"read clipboard text");
    std::wstring result=p;GlobalUnlock(data);CloseClipboard();return result;
}
struct HeldClipboard {HANDLE ready;HANDLE release;volatile LONG opened=0;};
static DWORD WINAPI HoldClipboard(void* parameter) {
    auto held=static_cast<HeldClipboard*>(parameter);
    auto window=CreateWindowExW(0,L"STATIC",L"Clipboard test",0,0,0,0,0,HWND_MESSAGE,nullptr,GetModuleHandleW(nullptr),nullptr);
    if(window && OpenClipboard(window))InterlockedExchange(&held->opened,1);
    SetEvent(held->ready);WaitForSingleObject(held->release,2000);
    if(held->opened)CloseClipboard();if(window)DestroyWindow(window);return 0;
}
static void PutText(HWND window,const std::wstring& text) {
    Check(OpenClipboard(window)!=FALSE,"open isolated clipboard as external application");
    Check(EmptyClipboard()!=FALSE,"empty isolated clipboard");
    HGLOBAL memory=GlobalAlloc(GMEM_MOVEABLE,(text.size()+1)*sizeof(wchar_t));
    Check(memory!=nullptr,"allocate external Unicode text");
    auto data=static_cast<wchar_t*>(GlobalLock(memory));Check(data!=nullptr,"lock external Unicode text");
    std::memcpy(data,text.c_str(),(text.size()+1)*sizeof(wchar_t));GlobalUnlock(memory);
    Check(SetClipboardData(CF_UNICODETEXT,memory)!=nullptr,"set external Windows text");CloseClipboard();
}
int wmain(int argc,wchar_t** argv) {
    bool isolated=false;
    for(int i=1;i<argc;i++)if(std::wcscmp(argv[i],L"--isolated-clipboard")==0)isolated=true;
    if(isolated) {
        // Each window station has its own clipboard. Integration tests must
        // never empty or overwrite the user's interactive Windows clipboard.
        auto original=GetProcessWindowStation();
        auto station=CreateWindowStationW(nullptr,0,WINSTA_ALL_ACCESS,nullptr);
        Check(station && station!=original,"create private window station");
        Check(SetProcessWindowStation(station)!=FALSE,"select isolated clipboard station");
        auto desktop=CreateDesktopW(L"BetaGwentClipboardTests",nullptr,nullptr,0,GENERIC_ALL,nullptr);
        Check(desktop && SetThreadDesktop(desktop),"use private noninteractive desktop");
    }
    for(unsigned n:{25u,26u,39u,40u}){auto s=Deck(n);Check(bgclip::ValidDeck(s.data(),s.size()),"legal deck length");}
    for(unsigned n:{0u,1u,24u,41u}){auto s=Deck(n);Check(!bgclip::ValidDeck(s.data(),s.size()),"illegal deck length");}
    for(auto s:{L"",L"BG1:0:1:1",L"text",L"BG1:2:0:1"})Check(!bgclip::ValidDeck(s,std::wcslen(s)),"invalid prefix and fields");
    auto good=Deck();
    wchar_t normalized[321]{};size_t length=0;
    for(auto padding:{L"",L" \t\r\n",L"\ufeff\u00a0\u2003\u3000"}) {
        auto input=std::wstring(padding)+good+padding;
        Check(bgclip::NormalizeDeck(input.data(),input.size(),normalized,321,length) && length==good.size() && normalized==good,"trim only surrounding whitespace and preserve full code");
    }
    for(auto bad:{L"",L"ordinary Windows text",L"BG1:2:1:2"})
        Check(!bgclip::NormalizeDeck(bad,std::wcslen(bad),normalized,321,length) && length==0,"reject non-deck clipboard text");
    Check(!bgclip::NormalizeDeck(good.data(),good.size(),normalized,good.size(),length),"output requires terminator space");
    auto embedded=good;embedded[20]=0;
    Check(!bgclip::NormalizeDeck(embedded.data(),embedded.size(),normalized,321,length),"embedded NUL rejected");
    const std::wstring symbols=L"0123456789:,BG";
    for(size_t n=0;n<=symbols.size();n++) {
        unsigned symbol=0;
        for(unsigned bit=0;bit<4;bit++) {
            auto query=std::to_string(n)+":"+std::to_string(bit);
            if(bgclip::DeckBit(symbols.data(),symbols.size(),query.c_str()))symbol|=1u<<bit;
        }
        Check(symbol==(n<symbols.size()?n+1:0),"all alphabet characters and terminator encode losslessly");
    }
    for(auto query:{"","-1:0","0:4","0:0x","9999:0","1","1:","1:0:0"})
        Check(!bgclip::DeckBit(symbols.data(),symbols.size(),query),"malformed bit query rejected");
    for(auto suffix:{L",",L" x",L"\n",L",0",L",9999999999999999999999"}) {
        auto bad=good+suffix;Check(!bgclip::ValidDeck(bad.data(),bad.size()),"reject malformed tail");
    }
    Check(!bgclip::ValidDeck(nullptr,25),"null rejected");
    Check(!bgclip::ValidDeck(good.data(),321),"oversize rejected before dereference");
    for(int i=1;i<argc;i++) {
        if(std::wcscmp(argv[i],L"--image")==0&&i+1<argc)Scan(argv[++i]);
    }
    std::vector<unsigned char> invalid(4096,0);Check(!bgclip::FindHooks({invalid.data(),invalid.size(),0}).storeSlot,"invalid PE disabled");
    auto page=static_cast<void**>(VirtualAlloc(nullptr,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE));
    Check(page!=nullptr,"allocate isolated callback fixture");
    page[0]=reinterpret_cast<void*>(&Noop);page[1]=reinterpret_cast<void*>(&FalseThunk);
    DWORD old;Check(VirtualProtect(page,4096,PAGE_READONLY,&old)!=FALSE,"fixture read-only");
    bgclip::Hooks hooks{page,page+1,1,1};Check(bgclip::Install(hooks),"install atomic pointer bridge");
    MEMORY_BASIC_INFORMATION memory{};VirtualQuery(page,&memory,sizeof(memory));Check(memory.Protect==PAGE_READONLY,"page protection restored");
    auto thunk=reinterpret_cast<bgclip::Thunk>(page[1]);
    const char* format=bgclip::ProbeFormat;Value args[2];args[0].flags=10;args[0].data=&format;
    Value result;
    thunk(nullptr,nullptr,nullptr,&result,2,args);Check((result.flags&31)==1&&reinterpret_cast<uintptr_t>(result.data)==1,"probe reports installed bridge without copying");
    format=bgclip::ReadProbeFormat;thunk(nullptr,nullptr,nullptr,&result,2,args);
    Check(result.data==reinterpret_cast<void*>(1),"Windows paste capability available without reading clipboard");
    format=bgclip::ReadBitFormat;const char* query="0:0";args[1].flags=10;args[1].data=&query;
    thunk(nullptr,nullptr,nullptr,&result,2,args);Check(!result.data,"no snapshot before first read");
    const char* plain="air:text";args[0].data=&plain;
    thunk(nullptr,nullptr,nullptr,&result,2,args);Check(result.data==nullptr,"ordinary failed setData remains failed");
    Check(!bgclip::Install({page,page+1,2,1}),"ambiguous matches disabled");
    Check(!bgclip::Install(hooks),"repeated install cannot hook itself");
    for(int i=1;i<argc;i++)if(std::wcscmp(argv[i],L"--clipboard")==0 || std::wcscmp(argv[i],L"--isolated-clipboard")==0) {
        if(i+1<argc && std::wcsncmp(argv[i+1],L"BG1:",4)==0)good=argv[i+1];
        simulatedPayload=good.c_str();simulatedResult=false;
        thunk(nullptr,nullptr,nullptr,&result,2,args);
        Check(result.data==reinterpret_cast<void*>(1),"setData reports actual Windows callback success");
        simulatedPayload=nullptr;simulatedResult=false;
        Check(ReadClipboard()==good,"Windows round trip exactly matches BG1");
        Check(bgclip::ReadDeck(normalized,321,length) && normalized==good && length==good.size(),"native Windows read returns complete copied deck");
        auto owner=CreateWindowExW(0,L"STATIC",L"External app fixture",0,0,0,0,0,HWND_MESSAGE,nullptr,GetModuleHandleW(nullptr),nullptr);
        Check(owner!=nullptr,"create external app window on test station");
        for(unsigned cards:{25u,40u}) {
            auto external=Deck(cards);PutText(owner,L"\ufeff\r\n "+external+L"\t\n");
            auto sequence=GetClipboardSequenceNumber();
            Check(bgclip::ReadDeck(normalized,321,length) && normalized==external,"paste Windows external Unicode deck, 25 and 40 cards");
            Check(GetClipboardSequenceNumber()==sequence,"Windows read leaves clipboard unchanged");
        }
        PutText(owner,good);format=bgclip::ReadBeginFormat;args[0].data=&format;
        thunk(nullptr,nullptr,nullptr,&result,2,args);Check(result.data==reinterpret_cast<void*>(1),"snapshot begin reads actual Windows clipboard");
        PutText(owner,L"unrelated newer clipboard contents");
        format=bgclip::ReadBitFormat;std::wstring reconstructed;
        for(size_t n=0;n<=320;n++) {
            unsigned symbol=0;
            for(unsigned bit=0;bit<4;bit++) {
                auto key=std::to_string(n)+":"+std::to_string(bit);query=key.c_str();
                thunk(nullptr,nullptr,nullptr,&result,2,args);if(result.data)symbol|=1u<<bit;
            }
            if(!symbol)break;
            Check(symbol<=symbols.size(),"snapshot alphabet valid");reconstructed+=symbols[symbol-1];
        }
        Check(reconstructed==good,"immutable snapshot survives intervening Windows clipboard change");
        {   // r7 regression: own formats never call the game's setData once the layout is known.
            unsigned before=originalCalls;auto startTick=GetTickCount64();
            for(unsigned n=0;n<1284;n++){query="0:0";thunk(nullptr,nullptr,nullptr,&result,2,args);}
            Check(originalCalls==before,"bit queries bypass the original setData");
            Check(GetTickCount64()-startTick<500,"1284 bit queries finish quickly");
            Check((result.flags&31)==1,"bypassed reply keeps the Boolean layout");
        }
        format=bgclip::ReadBeginFormat;thunk(nullptr,nullptr,nullptr,&result,2,args);
        Check(!result.data,"invalid Windows text fails begin");
        format=bgclip::ReadBitFormat;query="0:0";thunk(nullptr,nullptr,nullptr,&result,2,args);
        Check(!result.data,"failed begin clears old snapshot");
        for(auto bad:{std::wstring(),std::wstring(5000,L'x'),std::wstring(L"ordinary text"),good+L","}) {
            PutText(owner,bad);Check(!bgclip::ReadDeck(normalized,321,length)&&length==0,"empty, oversized and malformed clipboard rejected");
        }
        PutText(owner,good);format=plain;
        Check(bgclip::WriteDeck(good.data(),good.size()),"restore bridge clipboard ownership before load-hang regression");
        Check(!bgclip::WriteDeck(L"unrelated",9),"reject unrelated text");
        Check(ReadClipboard()==good,"invalid data leaves clipboard unchanged");
        // Regression (0.9.0 load hang): another thread empties the clipboard while
        // the copying thread is busy and pumps no messages. The owner must not be
        // this thread, or EmptyClipboard blocks on WM_DESTROYCLIPBOARD.
        HANDLE other=CreateThread(nullptr,0,[](void*)->DWORD{
            if(!OpenClipboard(nullptr))return 2;BOOL emptied=EmptyClipboard();CloseClipboard();return emptied?0:3;},nullptr,0,nullptr);
        Check(other!=nullptr,"start foreign clipboard thread");
        Check(WaitForSingleObject(other,3000)==WAIT_OBJECT_0,"foreign EmptyClipboard never waits for the busy copying thread");
        DWORD code=1;GetExitCodeThread(other,&code);CloseHandle(other);
        Check(code==0,"foreign EmptyClipboard succeeds");
        Check(bgclip::WriteDeck(good.data(),good.size()),"copy again after foreign empty");
        Check(ReadClipboard()==good,"second Windows round trip exactly matches BG1");
        HeldClipboard held{CreateEventW(nullptr,TRUE,FALSE,nullptr),CreateEventW(nullptr,TRUE,FALSE,nullptr),0};
        auto thread=CreateThread(nullptr,0,HoldClipboard,&held,0,nullptr);
        Check(thread && WaitForSingleObject(held.ready,2000)==WAIT_OBJECT_0 && held.opened,"hold clipboard from another thread");
        simulatedPayload=good.c_str();simulatedResult=true;
        thunk(nullptr,nullptr,nullptr,&result,2,args);
        simulatedPayload=nullptr;simulatedResult=false;
        Check(result.data==nullptr,"Windows failure overrides internal copied=true");
        Check(!bgclip::ReadDeck(normalized,321,length)&&length==0,"busy Windows clipboard read fails without stale data");
        SetEvent(held.release);Check(WaitForSingleObject(thread,2000)==WAIT_OBJECT_0,"release test clipboard lock");
        CloseHandle(thread);CloseHandle(held.ready);CloseHandle(held.release);
        Check(ReadClipboard()==good,"busy clipboard failure preserves prior deck");
        DestroyWindow(owner);
    }
    VirtualFree(page,0,MEM_RELEASE);
    std::printf("PASS checks=%u\n",checks);return 0;
}

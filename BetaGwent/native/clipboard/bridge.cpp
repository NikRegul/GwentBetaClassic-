// Connect the existing GFx text clipboard callback to Windows. No executable
// instructions, saves, scripts, input functions or clipboard polling are changed.
#include "bridge.h"
#include <cstring>
#include <climits>
#include <cwchar>

extern "C" IMAGE_DOS_HEADER __ImageBase;
namespace bgclip {
static Store originalStore = nullptr;
static Thunk originalThunk = nullptr;
struct Attempt { bool occurred = false; bool success = false; };
static thread_local Attempt attempt;
// The clipboard owner window lives on our own thread with its own message loop.
// Windows sends synchronous messages to the clipboard owner (for example
// WM_DESTROYCLIPBOARD when any application empties the clipboard). An owner on
// a game thread that is busy loading a save blocks that sender, and the load,
// until the game's message queue is woken. Game threads never own it here.
constexpr UINT CopyMessage = WM_APP + 0x42;
constexpr UINT ReadMessage = WM_APP + 0x43;
struct CopyRequest { volatile LONG refs; LONG result; size_t count; wchar_t text[1]; };
static void Release(CopyRequest* r) { if(InterlockedDecrement(&r->refs)==0)HeapFree(GetProcessHeap(),0,r); }
struct ReadRequest { volatile LONG refs; HANDLE ready; bool result; size_t count; wchar_t text[321]; };
static void Release(ReadRequest* r) {
    if(InterlockedDecrement(&r->refs)==0){CloseHandle(r->ready);HeapFree(GetProcessHeap(),0,r);}
}
static volatile LONG pendingRead=0;
struct Snapshot { wchar_t text[321]{}; size_t count=0; };
static thread_local Snapshot snapshot;
static INIT_ONCE ownerOnce = INIT_ONCE_STATIC_INIT;
static HWND ownerWindow = nullptr;

static const unsigned char* FromPointer(const Image& im, uintptr_t p, size_t size) {
    if (p < im.pointerBase || size > im.size || p-im.pointerBase > im.size-size) return nullptr;
    return im.data+(p-im.pointerBase);
}
static bool Bytes(const Image& im, uintptr_t p, const char* bytes, size_t size) {
    auto data=FromPointer(im,p,size);return data && std::memcmp(data,bytes,size)==0;
}
static uintptr_t Pointer(const unsigned char* p) {
    uintptr_t value;std::memcpy(&value,p,sizeof(value));return value;
}
static bool Code(const Image& im, uintptr_t p, const IMAGE_NT_HEADERS64* nt) {
    if (!FromPointer(im,p,32))return false;
    const auto sections=IMAGE_FIRST_SECTION(nt);
    for(unsigned n=0;n<nt->FileHeader.NumberOfSections;n++) {
        const auto& s=sections[n];auto rva=p-im.pointerBase;
        if(rva>=s.VirtualAddress && rva-s.VirtualAddress<s.Misc.VirtualSize)
            return (s.Characteristics&IMAGE_SCN_MEM_EXECUTE)!=0;
    }
    return false;
}
Hooks FindHooks(const Image& im) {
    Hooks found;
    if(!im.data || im.size<sizeof(IMAGE_NT_HEADERS64))return found;
    const auto dos=reinterpret_cast<const IMAGE_DOS_HEADER*>(im.data);
    if(dos->e_magic!=IMAGE_DOS_SIGNATURE || dos->e_lfanew<0 || size_t(dos->e_lfanew)>im.size-sizeof(IMAGE_NT_HEADERS64))return found;
    const auto nt=reinterpret_cast<const IMAGE_NT_HEADERS64*>(im.data+dos->e_lfanew);
    if(nt->Signature!=IMAGE_NT_SIGNATURE || nt->FileHeader.Machine!=IMAGE_FILE_MACHINE_AMD64 || nt->OptionalHeader.Magic!=IMAGE_NT_OPTIONAL_HDR64_MAGIC)return found;
    auto sections=IMAGE_FIRST_SECTION(nt);
    if(reinterpret_cast<const unsigned char*>(sections)+nt->FileHeader.NumberOfSections*sizeof(IMAGE_SECTION_HEADER)>im.data+im.size)return found;
    for(unsigned n=0;n<nt->FileHeader.NumberOfSections;n++) {
        const auto& s=sections[n];
        if(!(s.Characteristics&IMAGE_SCN_MEM_READ) || (s.Characteristics&(IMAGE_SCN_MEM_WRITE|IMAGE_SCN_MEM_EXECUTE|IMAGE_SCN_MEM_DISCARDABLE)))continue;
        size_t size=s.Misc.VirtualSize;
        if(s.VirtualAddress>im.size || size>im.size-s.VirtualAddress)continue;
        for(size_t off=0;off+96<=size;off+=8) {
            auto row=im.data+s.VirtualAddress+off;
            uintptr_t f[8];std::memcpy(f,row,sizeof(f));
            if(Bytes(im,f[4],"\x48\x8d\x41\x18\xc3",5) && Bytes(im,f[5],"\x48\x8b\x41\x38\xc3",5)
               && f[1]==f[2] && Bytes(im,f[1],"\x33\xc0\xc3",3) && Bytes(im,f[3],"\x32\xc0\xc3",3)
               && Bytes(im,f[7],"\xc2\0\0",3)
               && (Bytes(im,f[6],"\x33\xc0\x48\x39\x41\x38\x0f\x95\xc0\xc3",10)
                   || Bytes(im,f[6],"\x48\x83\x79\x38\0\x0f\x95\xc0\xc3",9))) {
                bool code=true;for(auto p:f)code=code && Code(im,p,nt);
                if(code){found.storeMatches++;found.storeSlot=reinterpret_cast<void**>(const_cast<unsigned char*>(row+56));}
            }
            // Adjacent native ThunkInfo records: setData, setDataHandler.
            if(Bytes(im,f[2],"setData\0",8) && Bytes(im,Pointer(row+64),"setDataHandler\0",15)
               && f[4]==0x400680 && Code(im,f[0],nt) && Code(im,Pointer(row+48),nt)) {
                found.thunkMatches++;found.thunkSlot=reinterpret_cast<void**>(const_cast<unsigned char*>(row));
            }
        }
    }
    if(found.storeMatches!=1 || found.thunkMatches!=1){found.storeSlot=nullptr;found.thunkSlot=nullptr;}
    return found;
}

bool ValidDeck(const wchar_t* text,size_t count) {
    if(!text || count<5 || count>320 || std::wmemcmp(text,L"BG1:",4)!=0)return false;
    size_t at=4;
    auto number=[&](wchar_t delimiter,int& value) {
        if(at==count || text[at]<L'1' || text[at]>L'9')return false;
        value=0;
        do {int digit=text[at]-L'0';if(value>(INT_MAX-digit)/10)return false;value=value*10+digit;at++;}
        while(at<count && text[at]>=L'0' && text[at]<=L'9');
        if(delimiter==0)return at==count;
        if(at==count || text[at]!=delimiter)return false;
        at++;return true;
    };
    int faction=0,leader=0;
    if(!number(L':',faction) || !(faction==2||faction==4||faction==8||faction==16||faction==32) || !number(L':',leader))return false;
    unsigned cards=0;
    while(at<count) {
        int id=0;
        if(text[at]<L'1'||text[at]>L'9')return false;
        do {int digit=text[at]-L'0';if(id>(INT_MAX-digit)/10)return false;id=id*10+digit;at++;}
        while(at<count && text[at]>=L'0'&&text[at]<=L'9');
        if(++cards>40)return false;
        if(at==count)break;
        if(text[at++]!=L',' || at==count)return false;
    }
    return cards>=25;
}
static bool Space(wchar_t c) {
    return c==L' ' || (c>=9&&c<=13) || c==0xa0 || c==0xfeff || c==0x1680
        || (c>=0x2000&&c<=0x200a) || c==0x2028 || c==0x2029 || c==0x202f || c==0x205f || c==0x3000;
}
bool NormalizeDeck(const wchar_t* text,size_t count,wchar_t* output,size_t capacity,size_t& length) {
    length=0;
    if(!text || !output || count>4096 || !capacity)return false;
    size_t start=0,end=count;
    while(start<end&&Space(text[start]))start++;
    while(end>start&&Space(text[end-1]))end--;
    size_t size=end-start;
    if(size>=capacity || !ValidDeck(text+start,size))return false;
    std::memmove(output,text+start,size*sizeof(wchar_t));output[size]=0;length=size;return true;
}
// Four Boolean replies encode each BG1 character. This uses the existing,
// validated AS3 Boolean thunk ABI, without manufacturing VM-owned strings.
// A begin call freezes one Windows read; bit queries never touch the clipboard.
bool DeckBit(const wchar_t* text,size_t count,const char* query) {
    if(!text || !query || !*query || count>320)return false;
    unsigned position=0,digits=0;
    while(*query>='0'&&*query<='9') {
        if(++digits>3)return false;
        position=position*10+unsigned(*query++-'0');
    }
    if(*query++!=':' || *query<'0' || *query>'3' || query[1]!=0 || position>=count)return false;
    unsigned bit=unsigned(*query-'0'),symbol=0;
    wchar_t c=text[position];
    if(c>=L'0'&&c<=L'9')symbol=unsigned(c-L'0')+1;
    else if(c==L':')symbol=11;else if(c==L',')symbol=12;else if(c==L'B')symbol=13;else if(c==L'G')symbol=14;
    return (symbol&(1u<<bit))!=0;
}
static bool ReadOwned(HWND owner,wchar_t* text,size_t& count) {
    count=0;
    bool opened=false;
    for(unsigned n=0;n<5;n++){if(OpenClipboard(owner)){opened=true;break;}Sleep(10);}
    if(!opened)return false;
    bool read=false;
    auto memory=GetClipboardData(CF_UNICODETEXT);
    if(memory) {
        SIZE_T bytes=GlobalSize(memory);
        if(bytes>=sizeof(wchar_t) && bytes<=4096*sizeof(wchar_t) && bytes%sizeof(wchar_t)==0) {
            auto source=static_cast<const wchar_t*>(GlobalLock(memory));
            if(source) {
                size_t length=0,limit=bytes/sizeof(wchar_t);
                while(length<limit && source[length])length++;
                if(length<limit)read=NormalizeDeck(source,length,text,321,count);
                GlobalUnlock(memory);
            }
        }
    }
    CloseClipboard();return read;
}
static bool WriteOwned(HWND owner,const wchar_t* text,size_t count) {
    HGLOBAL memory=GlobalAlloc(GMEM_MOVEABLE,(count+1)*sizeof(wchar_t));if(!memory)return false;
    auto target=static_cast<wchar_t*>(GlobalLock(memory));
    if(!target){GlobalFree(memory);return false;}
    std::memcpy(target,text,count*sizeof(wchar_t));target[count]=0;GlobalUnlock(memory);
    bool opened=false;
    for(unsigned n=0;n<5;n++){if(OpenClipboard(owner)){opened=true;break;}Sleep(10);}
    if(!opened){GlobalFree(memory);return false;}
    bool copied=EmptyClipboard() && SetClipboardData(CF_UNICODETEXT,memory)!=nullptr;
    CloseClipboard();if(!copied)GlobalFree(memory);
    return copied;
}
static LRESULT CALLBACK OwnerProc(HWND window,UINT message,WPARAM wParam,LPARAM lParam) {
    if(message==ReadMessage) {
        auto request=reinterpret_cast<ReadRequest*>(wParam);
        request->result=ReadOwned(window,request->text,request->count);
        SetEvent(request->ready);InterlockedExchange(&pendingRead,0);Release(request);
        return 0;
    }
    if(message==CopyMessage) {
        auto request=reinterpret_cast<CopyRequest*>(wParam);
        LONG copied=WriteOwned(window,request->text,request->count)?1:0;
        InterlockedExchange(&request->result,copied);Release(request);
        return copied;
    }
    return DefWindowProcW(window,message,wParam,lParam);
}
static DWORD WINAPI OwnerThread(void* readyEvent) {
    WNDCLASSW type{};type.lpfnWndProc=OwnerProc;type.hInstance=reinterpret_cast<HINSTANCE>(&__ImageBase);type.lpszClassName=L"GwentBetaClipboardOwner";
    RegisterClassW(&type);
    ownerWindow=CreateWindowExW(0,type.lpszClassName,L"Gwent Beta Classic Clipboard",0,0,0,0,0,HWND_MESSAGE,nullptr,type.hInstance,nullptr);
    SetEvent(static_cast<HANDLE>(readyEvent));
    if(!ownerWindow)return 0;
    MSG message;
    while(GetMessageW(&message,nullptr,0,0)>0){TranslateMessage(&message);DispatchMessageW(&message);}
    return 0;
}
static BOOL CALLBACK StartOwner(PINIT_ONCE,void*,void**) {
    HANDLE ready=CreateEventW(nullptr,TRUE,FALSE,nullptr);if(!ready)return TRUE;
    HANDLE thread=CreateThread(nullptr,0,OwnerThread,ready,0,nullptr);
    if(thread){WaitForSingleObject(ready,2000);CloseHandle(thread);}
    CloseHandle(ready);
    return TRUE;
}
bool WriteDeck(const wchar_t* text,size_t count) {
    if(!ValidDeck(text,count))return false;
    InitOnceExecuteOnce(&ownerOnce,StartOwner,nullptr,nullptr);
    if(!ownerWindow)return false;
    // The request owns a copy of the text: after a timeout the owner thread may
    // still finish it, so it is freed by whichever side releases it last.
    auto request=static_cast<CopyRequest*>(HeapAlloc(GetProcessHeap(),0,sizeof(CopyRequest)+count*sizeof(wchar_t)));
    if(!request)return false;
    request->refs=2;request->result=0;request->count=count;std::memcpy(request->text,text,count*sizeof(wchar_t));request->text[count]=0;
    DWORD_PTR result=0;
    // Bounded: a stuck clipboard can never stall the game for long.
    bool sent=SendMessageTimeoutW(ownerWindow,CopyMessage,reinterpret_cast<WPARAM>(request),0,
                                  SMTO_ABORTIFHUNG,1000,&result)!=0;
    bool copied=sent && result==1;
    Release(request); // the owner releases its reference after handling it, even late
    OutputDebugStringA(copied?"[BetaGwentClipboard] Windows copy OK\n":"[BetaGwentClipboard] Windows copy failed\n");
    return copied;
}
bool ReadDeck(wchar_t* output,size_t capacity,size_t& length) {
    length=0;
    if(!output || capacity<321)return false;
    InitOnceExecuteOnce(&ownerOnce,StartOwner,nullptr,nullptr);
    if(!ownerWindow || InterlockedCompareExchange(&pendingRead,1,0)!=0)return false;
    auto request=static_cast<ReadRequest*>(HeapAlloc(GetProcessHeap(),HEAP_ZERO_MEMORY,sizeof(ReadRequest)));
    if(!request){InterlockedExchange(&pendingRead,0);return false;}
    request->refs=2;request->ready=CreateEventW(nullptr,TRUE,FALSE,nullptr);
    if(!request->ready || !PostMessageW(ownerWindow,ReadMessage,reinterpret_cast<WPARAM>(request),0)) {
        Release(request);Release(request);InterlockedExchange(&pendingRead,0);return false;
    }
    // Post + refcounted heap storage keeps timeout handling safe even when a
    // delayed clipboard renderer is blocked. At most one read can be pending.
    bool read=WaitForSingleObject(request->ready,1000)==WAIT_OBJECT_0 && request->result;
    if(read){length=request->count;std::memcpy(output,request->text,(length+1)*sizeof(wchar_t));}
    Release(request);return read;
}
void __fastcall OnTextStore(void* self,const wchar_t* text,size_t count) {
    if(count && count<=321 && text && text[count-1]==0)count--;
    if(ValidDeck(text,count)){attempt.occurred=true;attempt.success=WriteDeck(text,count);}
    if(originalStore)originalStore(self,text,count);
}
static bool Readable(const void* p,size_t size) {
    MEMORY_BASIC_INFORMATION m{};
    if(!p || !VirtualQuery(p,&m,sizeof(m)) || m.State!=MEM_COMMIT || (m.Protect&(PAGE_GUARD|PAGE_NOACCESS)))return false;
    auto at=reinterpret_cast<uintptr_t>(p),base=reinterpret_cast<uintptr_t>(m.BaseAddress);
    return at>=base && size<=m.RegionSize && at-base<=m.RegionSize-size;
}
static bool ValueText(unsigned argc,const void* argv,unsigned index,char* output,size_t capacity) {
    if(index>=argc || !Readable(argv,(index+1)*32))return false;
    auto value=static_cast<const unsigned char*>(argv)+index*32;
    uint32_t flags;std::memcpy(&flags,value,4);
    if((flags&31)!=10)return false; // AS3::Value string, common to both SDKs.
    auto node=reinterpret_cast<const void*>(Pointer(value+16));
    if(!Readable(node,8))return false;
    auto chars=reinterpret_cast<const char*>(Pointer(static_cast<const unsigned char*>(node)));
    MEMORY_BASIC_INFORMATION m{};
    if(!chars || !VirtualQuery(chars,&m,sizeof(m)) || m.State!=MEM_COMMIT || (m.Protect&(PAGE_GUARD|PAGE_NOACCESS)))return false;
    size_t available=reinterpret_cast<uintptr_t>(m.BaseAddress)+m.RegionSize-reinterpret_cast<uintptr_t>(chars);
    for(size_t n=0;n<capacity;n++) {
        if(n>=available && !Readable(chars+n,1))return false;
        output[n]=chars[n];if(!output[n])return true;
    }
    return false;
}
// r7: 0.9.0 Import read ~1300 Boolean queries through setData. Each one first
// ran the game's own setData (Windows clipboard work in the engine): ~15 s on
// Next-Gen and a freeze on Classic 1.32. Our betagwent:* formats are answered
// here; the Boolean Value layout is copied from the first original reply.
static unsigned char booleanTemplate[32];
static volatile LONG haveTemplate=0;
static bool OwnFormat(const char* format) { return std::strncmp(format,"betagwent:",10)==0; }
static bool Answer(const char* format,unsigned argc,const void* argv,bool& success) {
    if(std::strcmp(format,ProbeFormat)==0 || std::strcmp(format,ReadProbeFormat)==0){success=true;return true;}
    if(std::strcmp(format,ReadBeginFormat)==0){snapshot.count=0;success=ReadDeck(snapshot.text,321,snapshot.count);return true;}
    if(std::strcmp(format,ReadBitFormat)==0) {
        char query[16]{};success=ValueText(argc,argv,1,query,sizeof(query)) && DeckBit(snapshot.text,snapshot.count,query);return true;
    }
    return false;
}
void __fastcall SetData(const void* info,void* vm,const void* self,void* result,unsigned argc,const void* argv) {
    char own[64]{};
    if(InterlockedCompareExchange(&haveTemplate,0,0) && ValueText(argc,argv,0,own,sizeof(own)) && OwnFormat(own)) {
        bool success=false;
        if(Answer(own,argc,argv,success)) {
            std::memcpy(result,booleanTemplate,sizeof(booleanTemplate));
            *(static_cast<unsigned char*>(result)+16)=static_cast<unsigned char>(success);
            return;
        }
    }
    auto previous=attempt;attempt={};
    originalThunk(info,vm,self,result,argc,argv);
    uint32_t flags=0;std::memcpy(&flags,result,4);
    if((flags&31)==1) {
        if(!InterlockedCompareExchange(&haveTemplate,0,0)) {
            std::memcpy(booleanTemplate,result,sizeof(booleanTemplate));booleanTemplate[16]=0;
            InterlockedExchange(&haveTemplate,1);
        }
        char format[64]{};bool handled=attempt.occurred,success=attempt.success;
        if(ValueText(argc,argv,0,format,sizeof(format))) {
            if(OwnFormat(format) && Answer(format,argc,argv,success))handled=true;
        }
        if(handled)*(static_cast<unsigned char*>(result)+16)=static_cast<unsigned char>(success);
    }
    attempt=previous;
}
static bool Replace(void** slot,void* expected,void* replacement) {
    DWORD old=0,ignored=0;
    if(!VirtualProtect(slot,sizeof(void*),PAGE_READWRITE,&old))return false;
    bool changed=InterlockedCompareExchangePointer(slot,replacement,expected)==expected;
    bool protectedAgain=VirtualProtect(slot,sizeof(void*),old,&ignored)!=0;
    return changed && protectedAgain;
}
bool Install(const Hooks& hooks) {
    if(!hooks.storeSlot || !hooks.thunkSlot || hooks.storeMatches!=1 || hooks.thunkMatches!=1)return false;
    if(*hooks.storeSlot==reinterpret_cast<void*>(&OnTextStore) || *hooks.thunkSlot==reinterpret_cast<void*>(&SetData))return false;
    originalStore=reinterpret_cast<Store>(*hooks.storeSlot);originalThunk=reinterpret_cast<Thunk>(*hooks.thunkSlot);
    if(!originalStore || !originalThunk)return false;
    if(!Replace(hooks.storeSlot,reinterpret_cast<void*>(originalStore),reinterpret_cast<void*>(&OnTextStore)))return false;
    if(!Replace(hooks.thunkSlot,reinterpret_cast<void*>(originalThunk),reinterpret_cast<void*>(&SetData))) {
        Replace(hooks.storeSlot,reinterpret_cast<void*>(&OnTextStore),reinterpret_cast<void*>(originalStore));return false;
    }
    return true;
}
}

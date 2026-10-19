#include "bridge.h"
#include <cwchar>
#include <cstring>
static INIT_ONCE once=INIT_ONCE_STATIC_INIT;
static bool installed=false;

static BOOL CALLBACK Initialize(PINIT_ONCE,void*,void**) {
    wchar_t name[MAX_PATH]{};
    if(!GetModuleFileNameW(nullptr,name,MAX_PATH))return TRUE;
    auto leaf=std::wcsrchr(name,L'\\');leaf=leaf?leaf+1:name;
    if(_wcsicmp(leaf,L"witcher3.exe")!=0)return TRUE;
    auto base=reinterpret_cast<const unsigned char*>(GetModuleHandleW(nullptr));
    const auto dos=reinterpret_cast<const IMAGE_DOS_HEADER*>(base);
    const auto nt=reinterpret_cast<const IMAGE_NT_HEADERS64*>(base+dos->e_lfanew);
    auto hooks=bgclip::FindHooks({base,nt->OptionalHeader.SizeOfImage,reinterpret_cast<uintptr_t>(base)});
    if(!hooks.storeSlot || !hooks.thunkSlot) {
        OutputDebugStringA("[BetaGwentClipboard] Unsupported clipboard layout; left unchanged\n");return TRUE;
    }
    // The two data slots refer to this DLL for the rest of the process lifetime.
    // Pinning prevents an ASI loader from unloading a live callback.
    HMODULE pinned=nullptr;
    if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,
        reinterpret_cast<LPCWSTR>(&bgclip::OnTextStore),&pinned))return TRUE;
    installed=bgclip::Install(hooks);
    OutputDebugStringA(installed?"[BetaGwentClipboard] Native clipboard connected\n":"[BetaGwentClipboard] Installation failed; clipboard unavailable\n");
    return TRUE;
}
extern "C" __declspec(dllexport) BOOL BetaGwentClipboardInitialize() {
    InitOnceExecuteOnce(&once,Initialize,nullptr,nullptr);return installed?TRUE:FALSE;
}
static DWORD WINAPI Worker(void*) {BetaGwentClipboardInitialize();return 0;}
BOOL WINAPI DllMain(HINSTANCE instance,DWORD reason,void*) {
    if(reason==DLL_PROCESS_ATTACH) {
        (void)instance; // Keep CRT/TLS thread notifications for the static runtime.
        HANDLE worker=CreateThread(nullptr,0,Worker,nullptr,0,nullptr);
        if(worker)CloseHandle(worker); // No waiting or loader calls under loader lock.
    }
    return TRUE;
}

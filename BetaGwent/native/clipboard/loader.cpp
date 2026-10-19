// Minimal optional bootstrap. Existing dinput8/ASI loaders must be preserved;
// they can load plugins/GwentBetaClipboard.asi instead of this DLL.
#include <windows.h>
#include <unknwn.h>
#include <cwchar>
static HMODULE instance=nullptr,systemInput=nullptr;
static INIT_ONCE once=INIT_ONCE_STATIC_INIT;
static BOOL CALLBACK Initialize(PINIT_ONCE,void*,void**) {
    wchar_t path[MAX_PATH]{};
    UINT length=GetSystemDirectoryW(path,MAX_PATH);
    if(length && length<MAX_PATH-13) {
        wcscat_s(path,L"\\dinput8.dll");systemInput=LoadLibraryExW(path,nullptr,LOAD_LIBRARY_SEARCH_SYSTEM32);
    }
    if(!systemInput)return TRUE;
    if(GetModuleFileNameW(instance,path,MAX_PATH)) {
        auto leaf=std::wcsrchr(path,L'\\');
        if(leaf) {
            leaf[1]=0;
            if(wcscat_s(path,L"plugins\\GwentBetaClipboard.asi")==0) {
                HMODULE module=LoadLibraryExW(path,nullptr,LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR|LOAD_LIBRARY_SEARCH_SYSTEM32);
                if(module) {
                    using Start=BOOL(*)();auto start=reinterpret_cast<Start>(GetProcAddress(module,"BetaGwentClipboardInitialize"));
                    if(start)start();
                }
            }
        }
    }
    return TRUE;
}
static FARPROC Resolve(const char* name) {
    InitOnceExecuteOnce(&once,Initialize,nullptr,nullptr);
    return systemInput?GetProcAddress(systemInput,name):nullptr;
}
extern "C" HRESULT WINAPI Proxy_DirectInput8Create(HINSTANCE app,DWORD version,REFIID iid,void** out,IUnknown* outer) {
    using Fn=HRESULT(WINAPI*)(HINSTANCE,DWORD,REFIID,void**,IUnknown*);
    auto fn=reinterpret_cast<Fn>(Resolve("DirectInput8Create"));return fn?fn(app,version,iid,out,outer):E_FAIL;
}
extern "C" HRESULT WINAPI Proxy_DllCanUnloadNow() {
    using Fn=HRESULT(WINAPI*)();auto fn=reinterpret_cast<Fn>(Resolve("DllCanUnloadNow"));return fn?fn():S_FALSE;
}
extern "C" HRESULT WINAPI Proxy_DllGetClassObject(REFCLSID clsid,REFIID iid,void** out) {
    using Fn=HRESULT(WINAPI*)(REFCLSID,REFIID,void**);auto fn=reinterpret_cast<Fn>(Resolve("DllGetClassObject"));return fn?fn(clsid,iid,out):E_FAIL;
}
extern "C" HRESULT WINAPI Proxy_DllRegisterServer() {
    using Fn=HRESULT(WINAPI*)();auto fn=reinterpret_cast<Fn>(Resolve("DllRegisterServer"));return fn?fn():E_FAIL;
}
extern "C" HRESULT WINAPI Proxy_DllUnregisterServer() {
    using Fn=HRESULT(WINAPI*)();auto fn=reinterpret_cast<Fn>(Resolve("DllUnregisterServer"));return fn?fn():E_FAIL;
}
BOOL WINAPI DllMain(HINSTANCE module,DWORD reason,void*) {
    if(reason==DLL_PROCESS_ATTACH)instance=module;return TRUE;
}

using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

class PatchPlayer
{
    static void Main(string[] args)
    {
        var resolver = new DefaultAssemblyResolver();
        resolver.AddSearchDirectory(System.IO.Path.GetDirectoryName(args[0]));
        var assembly = AssemblyDefinition.ReadAssembly(args[0], new ReaderParameters { AssemblyResolver = resolver });
        var helper = AssemblyDefinition.ReadAssembly(args[1]);
        var install = helper.MainModule.GetType("BetaPremiumCapture").Methods.Single(m => m.Name == "Install");
        int disabled = 0, hooks = 0;
        foreach (var type in assembly.MainModule.Types)
            foreach (var method in type.Methods)
            {
                if (type.Name == "DynamicCardSettings" && method.Name == "get_Quality")
                {
                    method.Body = new MethodBody(method);
                    method.Body.GetILProcessor().Emit(OpCodes.Ldc_I4_3);
                    method.Body.GetILProcessor().Emit(OpCodes.Ret);
                    continue;
                }
                if (type.Name == "DynamicCardView" && method.HasBody)
                    foreach (var instruction in method.Body.Instructions)
                        if (instruction.Operand is MethodReference reference && reference.DeclaringType.FullName == "UnityEngine.Time" && reference.Name == "get_unscaledDeltaTime")
                            reference.Name = "get_deltaTime"; // deterministic offline capture clock
                if (!method.HasBody || method.ReturnType.FullName != "System.Void") continue;
                bool startup = method.CustomAttributes.Any(a => a.AttributeType.Name == "RuntimeInitializeOnLoadMethodAttribute");
                bool scene = !type.Namespace.StartsWith("Assets.Script.DynamicCards") &&
                    (method.Name == "Awake" || method.Name == "Start" || method.Name == "OnEnable");
                bool hook = type.Name == "DailyQuestTicker" && method.Name == "Install";
                if (!startup && !scene && !hook) continue;
                method.Body = new MethodBody(method);
                var il = method.Body.GetILProcessor();
                if (hook) { il.Emit(OpCodes.Call, assembly.MainModule.ImportReference(install)); hooks++; }
                il.Emit(OpCodes.Ret);
                disabled++;
            }
        if (hooks != 1) throw new Exception("Expected exactly one runtime hook, got " + hooks);
        assembly.Write(args[2]);
        Console.WriteLine("Offline copy: disabled " + disabled + " startup methods; hook installed.");
    }
}

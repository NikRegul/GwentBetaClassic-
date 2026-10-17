using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Web.Script.Serialization;
using System.Windows.Forms;
using System.Xml;
using Microsoft.Win32;

public class PayloadFile { public string Path; public string Sha256; public long Bytes; }
public class Package { public string Version; public string Platform; public string ModFolder; public List<PayloadFile> Files; }
public class SliceStream : Stream {
    readonly Stream inner; readonly long start, length; long position;
    public SliceStream(Stream stream,long offset,long size) { inner=stream;start=offset;length=size; }
    public override bool CanRead { get{return true;} } public override bool CanSeek { get{return true;} } public override bool CanWrite { get{return false;} }
    public override long Length { get{return length;} } public override long Position {get{return position;}set{Seek(value,SeekOrigin.Begin);}}
    public override int Read(byte[] b,int o,int c) { inner.Position=start+position;int n=inner.Read(b,o,(int)Math.Min(c,length-position));position+=n;return n; }
    public override long Seek(long p,SeekOrigin origin) { long next=origin==SeekOrigin.Begin?p:origin==SeekOrigin.Current?position+p:length+p;if(next<0||next>length)throw new IOException("Payload range");return position=next; }
    public override void Flush() {} public override void SetLength(long v){throw new NotSupportedException();} public override void Write(byte[] b,int o,int c){throw new NotSupportedException();}
}
public static class Installer {
    public static string ExePath { get { return Assembly.GetExecutingAssembly().Location; } }
    public static ZipArchive OpenPayload(out FileStream source) {
        source=File.Open(ExePath,FileMode.Open,FileAccess.Read,FileShare.Read);
        source.Position=source.Length-24;var r=new BinaryReader(source,Encoding.UTF8,true);
        if(Encoding.ASCII.GetString(r.ReadBytes(8))!="BGSETUP1")throw new IOException("Не найден пакет установщика.");
        long offset=r.ReadInt64(),length=r.ReadInt64();if(offset<0||length<0||offset+length!=source.Length-24)throw new IOException("Повреждён пакет установщика.");
        return new ZipArchive(new SliceStream(source,offset,length),ZipArchiveMode.Read,false);
    }
    public static Package ReadPackage() {
        FileStream source;using(var archive=OpenPayload(out source))using(source)using(var reader=new StreamReader(archive.GetEntry("package.json").Open()))
            return new JavaScriptSerializer{MaxJsonLength=int.MaxValue}.Deserialize<Package>(reader.ReadToEnd());
    }
    public static string Hash(string path) {using(var sha=SHA256.Create())using(var f=File.OpenRead(path))return BitConverter.ToString(sha.ComputeHash(f)).Replace("-","").ToLowerInvariant();}
    static string SafePath(string root,string relative) {
        string full=System.IO.Path.GetFullPath(System.IO.Path.Combine(root,relative.Replace('/',System.IO.Path.DirectorySeparatorChar)));
        if(!full.StartsWith(System.IO.Path.GetFullPath(root).TrimEnd('\\')+"\\",StringComparison.OrdinalIgnoreCase))throw new IOException("Недопустимый путь пакета.");return full;
    }
    public static void Extract(string root,Action<int,string> progress) {
        var package=ReadPackage();Directory.CreateDirectory(root);FileStream source;
        using(var archive=OpenPayload(out source))using(source) {
            int n=0;
            foreach(var file in package.Files) {
                string destination=SafePath(root,file.Path);Directory.CreateDirectory(System.IO.Path.GetDirectoryName(destination));
                var entry=archive.GetEntry("files/"+file.Path);if(entry==null||entry.Length!=file.Bytes)throw new IOException("Неполный пакет: "+file.Path);
                using(var input=entry.Open())using(var output=new FileStream(destination,FileMode.CreateNew,FileAccess.Write))input.CopyTo(output);
                if(Hash(destination)!=file.Sha256)throw new IOException("Ошибка проверки: "+file.Path);
                if(progress!=null)progress(++n*100/package.Files.Count,file.Path);
            }
        }
    }
    public static Dictionary<string,string> ReadLocalization(string settings) {
        var result=new Dictionary<string,string>(StringComparer.OrdinalIgnoreCase);if(!File.Exists(settings))return result;bool section=false;
        foreach(string raw in File.ReadAllLines(settings)) {
            string line=raw.Trim();if(line.StartsWith("[")){section=line.Equals("[Localization]",StringComparison.OrdinalIgnoreCase);continue;}
            if(!section||line.StartsWith(";"))continue;int split=line.IndexOf('=');if(split>0)result[line.Substring(0,split).Trim()]=line.Substring(split+1).Trim();
        }
        return result;
    }
    public static int TextChoice(string code) {
        switch((code??"").ToUpperInvariant().Replace('_','-')) {
            case "RU":return 1;case "DE":return 3;case "FR":return 4;case "IT":return 5;case "PL":return 6;case "ES":return 7;case "MX":case "ESMX":case "ES-MX":return 8;
            case "BR":case "PT":case "PTBR":case "PT-BR":return 9;case "JP":case "JA":return 10;case "KR":case "KO":return 11;case "CN":case "ZH":case "ZHCN":case "ZH-CN":return 12;case "TW":case "ZHTW":case "ZH-TW":return 13;default:return 2;
        }
    }
    public static int VoiceChoice(string code) {
        switch((code??"").ToUpperInvariant().Replace('_','-')) {case "RU":return 1;case "DE":return 3;case "IT":return 4;case "BR":case "PT":case "PTBR":case "PT-BR":return 5;default:return 2;}
    }
    public static string SettingsFile(string docs,string platform) {
        string folder=System.IO.Path.Combine(docs,"The Witcher 3");string standard=System.IO.Path.Combine(folder,"user.settings"),dx12=System.IO.Path.Combine(folder,"dx12user.settings");
        if(platform=="1.32"||!File.Exists(dx12))return standard;
        if(!File.Exists(standard)||File.GetLastWriteTimeUtc(dx12)>=File.GetLastWriteTimeUtc(standard))return dx12;return standard;
    }
    static void SetDefaults(string file,int text,int voice) {
        Directory.CreateDirectory(System.IO.Path.GetDirectoryName(file));var lines=File.Exists(file)?File.ReadAllLines(file).ToList():new List<string>();int section=-1,end=lines.Count;
        for(int i=0;i<lines.Count;i++)if(lines[i].Trim().Equals("[Hidden]",StringComparison.OrdinalIgnoreCase)){section=i;for(int j=i+1;j<lines.Count;j++)if(lines[j].Trim().StartsWith("[")){end=j;break;}break;}
        if(section<0){if(lines.Count>0&&lines[lines.Count-1]!="")lines.Add("");lines.Add("[Hidden]");section=lines.Count-1;end=lines.Count;}
        for(int i=end-1;i>section;i--)if(lines[i].TrimStart().StartsWith("BetaGwentTextLanguage=",StringComparison.OrdinalIgnoreCase)||lines[i].TrimStart().StartsWith("BetaGwentVoiceLanguage=",StringComparison.OrdinalIgnoreCase)){lines.RemoveAt(i);end--;}
        lines.Insert(end,"BetaGwentVoiceLanguage="+voice);lines.Insert(end,"BetaGwentTextLanguage="+text);string temporary=file+".betagwent-new";
        File.WriteAllLines(temporary,lines,new UTF8Encoding(false));if(File.Exists(file))File.Replace(temporary,file,null);else File.Move(temporary,file);
    }
    static void RegisterLanguages(string file) {
        var xml=new XmlDocument{PreserveWhitespace=true};xml.Load(file);var variables=xml.SelectSingleNode("/UserConfig/Group[@id='Hidden']/VisibleVars");if(variables==null)throw new IOException("Не найдена штатная группа Hidden в конфигурации игры.");
        foreach(string id in new[]{"BetaGwentTextLanguage","BetaGwentVoiceLanguage"})if(variables.SelectSingleNode("Var[@id='"+id+"']")==null){var node=xml.CreateElement("Var");node.SetAttribute("id",id);node.SetAttribute("displayName",id);node.SetAttribute("displayType",id=="BetaGwentTextLanguage"?"SLIDER;0;13;1":"SLIDER;0;5;1");variables.AppendChild(node);}
        string temporary=file+".betagwent-new";xml.Save(temporary);File.Replace(temporary,file,null);
    }
    public static string Install(string game,string settings,int text,int voice,Action<int,string> progress) {
        var package=ReadPackage();game=System.IO.Path.GetFullPath(game);string id=DateTime.Now.ToString("yyyyMMdd-HHmmss")+"-"+Guid.NewGuid().ToString("N").Substring(0,8);
        string stage=SafePath(game,".BetaGwentInstall-"+id),backup=SafePath(game,"BetaGwentBackup/"+id);Directory.CreateDirectory(stage);Extract(stage,progress);
        var moved=new List<Tuple<string,string>>();var installed=new List<string>();Directory.CreateDirectory(backup);bool hadSettings=File.Exists(settings),changedSettings=false,changedConfig=false;
        string hiddenConfig=SafePath(game,"bin/config/r4game/user_config_matrix/pc/hidden.xml");
        try {
            Directory.CreateDirectory(SafePath(game,"Mods"));
            foreach(string name in new[]{"modBetaGwent0924","modBetaGwentClassic132"}) {
                string old=SafePath(game,"Mods/"+name);if(!Directory.Exists(old))continue;
                string destination=SafePath(backup,"Mods/"+name);Directory.CreateDirectory(System.IO.Path.GetDirectoryName(destination));Directory.Move(old,destination);moved.Add(Tuple.Create(old,destination));
            }
            string docs=SafePath(game,"BetaGwentDocs");if(Directory.Exists(docs)){string saved=SafePath(backup,"BetaGwentDocs");Directory.Move(docs,saved);moved.Add(Tuple.Create(docs,saved));}
            string stagedMod=SafePath(stage,"Mods/"+package.ModFolder),target=SafePath(game,"Mods/"+package.ModFolder);Directory.Move(stagedMod,target);installed.Add(target);
            string stagedDocs=SafePath(stage,"BetaGwentDocs");if(Directory.Exists(stagedDocs)){Directory.Move(stagedDocs,docs);installed.Add(docs);}else Directory.CreateDirectory(docs);
            Directory.CreateDirectory(SafePath(backup,"Config"));File.Copy(hiddenConfig,SafePath(backup,"Config/hidden.xml"));RegisterLanguages(hiddenConfig);changedConfig=true;
            if(hadSettings){Directory.CreateDirectory(SafePath(backup,"Settings"));File.Copy(settings,SafePath(backup,"Settings/"+System.IO.Path.GetFileName(settings)));}
            SetDefaults(settings,text,voice);changedSettings=true;
            var record=new {Version=package.Version,Platform=package.Platform,Backup=backup,Settings=settings,InitialTextChoice=text,InitialVoiceChoice=voice,AllFiveVoicesInstalled=true};
            File.WriteAllText(System.IO.Path.Combine(docs,"InstallReport.json"),new JavaScriptSerializer().Serialize(record),Encoding.UTF8);
            Directory.Delete(stage,true);return backup;
        } catch {
            foreach(string path in installed.AsEnumerable().Reverse())if(Directory.Exists(path))Directory.Move(path,SafePath(stage,"rollback-"+System.IO.Path.GetFileName(path)));
            foreach(var item in moved.AsEnumerable().Reverse())if(Directory.Exists(item.Item2)){Directory.CreateDirectory(System.IO.Path.GetDirectoryName(item.Item1));Directory.Move(item.Item2,item.Item1);}
            if(changedSettings){if(hadSettings)File.Copy(SafePath(backup,"Settings/"+System.IO.Path.GetFileName(settings)),settings,true);else File.Delete(settings);}
            if(changedConfig)File.Copy(SafePath(backup,"Config/hidden.xml"),hiddenConfig,true);throw;
        }
    }
    public static bool IsGame(string folder,string platform) {
        string exe=System.IO.Path.Combine(folder,"bin/x64/witcher3.exe");if(!File.Exists(exe)||!Directory.Exists(System.IO.Path.Combine(folder,"content/content0")))return false;
        // The executable's resource version is 3.0.x even in Classic 1.32.
        // Detect the installed resource format used by the actual game.
        string bundle=System.IO.Path.Combine(folder,"content/content0/bundles/startup.bundle");if(!File.Exists(bundle))return false;
        using(var file=File.OpenRead(bundle)){var reader=new BinaryReader(file);if(Encoding.ASCII.GetString(reader.ReadBytes(8))!="POTATO70")return false;file.Position=20;int version=reader.ReadUInt16();return platform=="1.32"?version==3:version==5;}
    }
    public static string FindGame(string platform) {
        var paths=new List<string>();
        foreach(var hive in new[]{Registry.LocalMachine,Registry.CurrentUser})foreach(string keyName in new[]{@"SOFTWARE\GOG.com\Games",@"SOFTWARE\WOW6432Node\GOG.com\Games",@"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",@"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"})
            using(var key=hive.OpenSubKey(keyName)){if(key==null)continue;foreach(string child in key.GetSubKeyNames())using(var item=key.OpenSubKey(child)){if(item==null)continue;foreach(string name in new[]{"path","PATH","InstallLocation"}){var value=item.GetValue(name) as string;if(!String.IsNullOrEmpty(value)&&value.IndexOf("witcher",StringComparison.OrdinalIgnoreCase)>=0)paths.Add(value);}}}
        paths.AddRange(new[]{@"D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt",@"D:\GOG Galaxy\Games\The Witcher 3",@"C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3",@"D:\SteamLibrary\steamapps\common\The Witcher 3"});
        return paths.FirstOrDefault(p=>IsGame(p,platform))??"";
    }
}
public class SetupForm : Form {
    bool installing;
    readonly Package package;readonly TextBox folder=new TextBox();readonly ComboBox text=new ComboBox(),voice=new ComboBox();readonly Label detected=new Label(),status=new Label();readonly ProgressBar progress=new ProgressBar();readonly Button install=new Button();string settings;
    readonly string[] textNames={"Как в игре","Русский","English","Deutsch","Français","Italiano","Polski","Español","Español (Latinoamérica)","Português (Brasil)","日本語","한국어","简体中文","繁體中文"};
    readonly string[] voiceNames={"Как в игре","Русский","English","Deutsch","Italiano","Português (Brasil)"};
    public SetupForm() {
        package=Installer.ReadPackage();Text="Gwent Beta Classic — "+package.Platform;ClientSize=new Size(660,490);FormBorderStyle=FormBorderStyle.FixedDialog;MaximizeBox=false;StartPosition=FormStartPosition.CenterScreen;Font=new Font("Segoe UI",10);BackColor=Color.FromArgb(245,246,248);
        var title=new Label{Text="Gwent Beta Classic",Font=new Font("Segoe UI",23,FontStyle.Bold),AutoSize=true,Location=new Point(28,22)};Controls.Add(title);
        Controls.Add(new Label{Text=package.Version+" · "+package.Platform+" · 5 озвучек / 13 языков текста",AutoSize=true,Location=new Point(30,70)});
        Controls.Add(new Label{Text="Папка игры",AutoSize=true,Location=new Point(30,114)});folder.SetBounds(30,139,500,30);Controls.Add(folder);
        var browse=new Button{Text="Обзор…",Location=new Point(540,138),Size=new Size(90,30)};browse.Click+=(s,e)=>{using(var dialog=new FolderBrowserDialog()){dialog.Description="Выберите папку The Witcher 3";if(dialog.ShowDialog()==DialogResult.OK)folder.Text=dialog.SelectedPath;}};Controls.Add(browse);
        Controls.Add(new Label{Text="Язык текста",AutoSize=true,Location=new Point(30,192)});Controls.Add(new Label{Text="Язык озвучки",AutoSize=true,Location=new Point(340,192)});
        text.DropDownStyle=voice.DropDownStyle=ComboBoxStyle.DropDownList;text.Items.AddRange(textNames);voice.Items.AddRange(voiceNames);text.SetBounds(30,218,285,30);voice.SetBounds(340,218,290,30);text.SelectedIndex=voice.SelectedIndex=0;Controls.Add(text);Controls.Add(voice);
        detected.SetBounds(30,261,600,48);Controls.Add(detected);
        Controls.Add(new Label{Text="Языки можно переключать в моде отдельными кнопками.\nСохранённый выбор при обновлении остаётся прежним.",Location=new Point(30,320),Size=new Size(600,44)});
        progress.SetBounds(30,382,600,18);Controls.Add(progress);status.SetBounds(30,407,450,46);Controls.Add(status);
        install.Text="Установить";install.SetBounds(485,431,145,34);install.Click+=InstallClick;Controls.Add(install);
        settings=Installer.SettingsFile(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),package.Platform);RefreshDetection();folder.Text=Installer.FindGame(package.Platform);
        folder.TextChanged+=(s,e)=>ValidateFolder();FormClosing+=(s,e)=>{if(installing){e.Cancel=true;status.Text="Дождитесь завершения установки.";}};ValidateFolder();
    }
    void RefreshDetection() {
        var values=Installer.ReadLocalization(settings);string tx=values.ContainsKey("TextLanguage")?values["TextLanguage"]:"EN",vo=values.ContainsKey("SpeechLanguage")?values["SpeechLanguage"]:"EN";
        string actual=voiceNames[Installer.VoiceChoice(vo)];detected.Text="В игре: текст "+textNames[Installer.TextChoice(tx)]+"; озвучка "+vo+".\nАвтоматический выбор озвучки мода: "+actual+".";
    }
    void ValidateFolder(){bool valid=Installer.IsGame(folder.Text,package.Platform);install.Enabled=valid;status.Text=valid?"Игра найдена. Готово к установке.":"Выберите папку игры версии "+package.Platform+".";}
    async void InstallClick(object sender,EventArgs e) {
        if(Process.GetProcessesByName("witcher3").Length>0){MessageBox.Show("Закройте игру перед установкой.",Text);return;}
        installing=true;install.Enabled=false;folder.Enabled=text.Enabled=voice.Enabled=false;string game=folder.Text;int tx=text.SelectedIndex,vo=voice.SelectedIndex;
        try {
            string backup=await System.Threading.Tasks.Task.Run(()=>Installer.Install(game,settings,tx,vo,(n,path)=>BeginInvoke((Action)(()=>{progress.Value=n;status.Text="Установка: "+System.IO.Path.GetFileName(path);}))));
            progress.Value=100;status.Text="Установлено. Можно запускать игру.";MessageBox.Show("Установка завершена.\nПредыдущие файлы сохранены в:\n"+backup,Text,MessageBoxButtons.OK,MessageBoxIcon.Information);
        } catch(Exception error){status.Text="Установка не завершена.";MessageBox.Show(error.Message+"\nПри нехватке прав запустите установщик от администратора.",Text,MessageBoxButtons.OK,MessageBoxIcon.Error);}
        finally {installing=false;folder.Enabled=text.Enabled=voice.Enabled=true;ValidateFolder();}
    }
    [STAThread]public static int Main(string[] args) {
        try {
            if(args.Length>0&&args[0]=="--verify") { string root=System.IO.Path.Combine(System.IO.Path.GetTempPath(),"BetaGwentVerify-"+Guid.NewGuid().ToString("N"));Installer.Extract(root,null);if(!root.StartsWith(System.IO.Path.GetTempPath(),StringComparison.OrdinalIgnoreCase))throw new IOException("Test path");Directory.Delete(root,true);Console.WriteLine("Payload verified");return 0; }
            Application.EnableVisualStyles();Application.SetCompatibleTextRenderingDefault(false);
            using(var form=new SetupForm()) {
                if(args.Length==2&&args[0]=="--preview") {var window=form.Handle;foreach(Control child in form.Controls){var handle=child.Handle;}form.PerformLayout();using(var bitmap=new Bitmap(form.Width,form.Height)){form.DrawToBitmap(bitmap,new Rectangle(Point.Empty,bitmap.Size));bitmap.Save(args[1]);}return 0;}
                Application.Run(form);
            } return 0;
        } catch(Exception error){if(args.Length>0){Console.Error.WriteLine(error.ToString());return 1;}MessageBox.Show(error.Message,"Gwent Beta Classic",MessageBoxButtons.OK,MessageBoxIcon.Error);return 1;}
    }
}

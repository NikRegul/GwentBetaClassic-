// Offline frame export in an isolated copy of the supplied Mono Unity player.
using System;
using System.Collections;
using System.IO;
using System.Reflection;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;
using Assets.Script.DynamicCards;

public sealed class BetaPremiumCapture : MonoBehaviour
{
    static bool installed;
    public static void Install()
    {
        if (installed) return;
        installed = true;
        var root = new GameObject("BetaGwent offline premium capture");
        DontDestroyOnLoad(root);
        root.AddComponent<BetaPremiumCapture>();
    }

    IEnumerator Start()
    {
        // Scene/account services are disabled by the copy-only assembly patch.
        foreach (var root in SceneManager.GetActiveScene().GetRootGameObjects())
            if (root != gameObject) root.SetActive(false);
        AudioListener.volume = 0;
        Application.runInBackground = true;
        QualitySettings.vSyncCount = 0;
        Application.targetFrameRate = -1;
        Time.captureFramerate = 24;
        // The clone's settings getter is patched to High; never write user prefs.
        var output = Environment.GetEnvironmentVariable("BETA_PREMIUM_OUTPUT");
        var list = Environment.GetEnvironmentVariable("BETA_PREMIUM_IDS");
        if (String.IsNullOrEmpty(output) || String.IsNullOrEmpty(list)) { Application.Quit(2); yield break; }
        Directory.CreateDirectory(output);
        var canvasObject = new GameObject("Capture canvas", typeof(Canvas));
        canvasObject.GetComponent<Canvas>().renderMode = RenderMode.ScreenSpaceOverlay;
        var imageObject = new GameObject("Portrait", typeof(RectTransform), typeof(CanvasRenderer), typeof(Image));
        imageObject.transform.SetParent(canvasObject.transform, false);
        var rect = imageObject.GetComponent<RectTransform>();
        rect.sizeDelta = new Vector2(356, 512);
        var image = imageObject.GetComponent<Image>();
        var flags = BindingFlags.Instance | BindingFlags.NonPublic;
        var targetField = typeof(DynamicCardView).GetField("texture", flags);
        var readyField = typeof(DynamicCardView).GetField("preparing", flags);
        foreach (var id in File.ReadAllLines(list))
        {
            if (String.IsNullOrWhiteSpace(id)) continue;
            var directory = Path.Combine(output, id.Trim());
            Directory.CreateDirectory(directory);
            if (File.Exists(Path.Combine(directory, "complete.json"))) continue;
            DynamicCardView.Bind(image, id.Trim(), false, false, null, false, false, null, null, true);
            var view = image.GetComponent<DynamicCardView>();
            float deadline = Time.realtimeSinceStartup + 120;
            while ((bool)readyField.GetValue(view) && Time.realtimeSinceStartup < deadline) yield return null;
            var texture = targetField.GetValue(view) as RenderTexture;
            if (texture == null) { File.WriteAllText(Path.Combine(directory, "failed.txt"), "No rendered portrait"); continue; }
            // Sample only looping clips. Authoring entrance clips never enter the atlas.
            var model=typeof(DynamicCardView).GetField("model",flags).GetValue(view) as GameObject;
            var animators=new List<Animator>();var loops=new List<AnimationClip>();
            foreach(var animator in model.GetComponentsInChildren<Animator>(true)) {
                AnimationClip loop=null;
                if(animator.runtimeAnimatorController!=null)foreach(var clip in animator.runtimeAnimatorController.animationClips)
                    if(clip.isLooping&&(loop==null||clip.name.IndexOf("Loop",StringComparison.OrdinalIgnoreCase)>=0))loop=clip;
                if(loop==null)continue;
                animator.enabled=false;animators.Add(animator);loops.Add(loop);
                Debug.Log("LEADER_LOOP_ONLY "+id+" "+loop.name+" length="+loop.length);
                loop.SampleAnimation(animator.gameObject,0);
            }
            if(loops.Count==0)throw new Exception("No verified loop animation for leader "+id);
            for(int n=0;n<24;n++)yield return new WaitForEndOfFrame();
            var render=typeof(DynamicCardView).GetMethod("RenderCard",flags);
            var age=typeof(DynamicCardView).GetField("age",flags);
            var entry=typeof(DynamicCardView).GetField("entry",flags).GetValue(view);
            float intro=(float)entry.GetType().GetField("introDuration").GetValue(entry);
            var scaled = RenderTexture.GetTemporary(256, 312, 0, RenderTextureFormat.ARGB32);
            var pixels = new Texture2D(256, 312, TextureFormat.RGB24, false);
            for (int n = 0; n < 96; n++)
            {
                age.SetValue(view,intro+n/24f);
                yield return new WaitForEndOfFrame();
                for(int a=0;a<loops.Count;a++)loops[a].SampleAnimation(animators[a].gameObject,(n/24f)%loops[a].length);
                // Bypass the original real-time preview throttle during deterministic export.
                render.Invoke(view,null);
                if (n % 2 != 0) continue;
                var previous = RenderTexture.active;
                // Original DynamicCardFraming art UV, then the same top-biased
                // cover crop as paintBetaFace (256/312 rather than 0.6957).
                Graphics.Blit(texture, scaled, new Vector2(.68260696f, .8138f), new Vector2(.16602942f, .1291f));
                RenderTexture.active = scaled;
                pixels.ReadPixels(new Rect(0, 0, 256, 312), 0, 0);
                pixels.Apply();
                RenderTexture.active = previous;
                File.WriteAllBytes(Path.Combine(directory, (n/2).ToString("D4") + ".png"), pixels.EncodeToPNG());
            }
            Destroy(pixels);
            RenderTexture.ReleaseTemporary(scaled);
            File.WriteAllText(Path.Combine(directory, "complete.json"), "{\"fps\":12,\"frames\":48,\"width\":256,\"height\":312,\"loopOnly\":true,\"introExcluded\":true,\"source\":\"Unity loop clips sampled directly\",\"artId\":\""+id.Trim()+"\"}");
            DynamicCardView.Bind(image, "", true);
            yield return null;
        }
        File.WriteAllText(Path.Combine(output, "complete.txt"), "Capture completed");
        Application.Quit(0);
    }
}

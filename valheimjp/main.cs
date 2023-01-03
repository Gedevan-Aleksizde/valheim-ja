using System;
using System.Collections.Generic;
using BepInEx;
using BepInEx.Logging;
using UnityEngine;
using UnityEngine.UI;
using Jotunn;
using Jotunn.Utils;
using Jotunn.Entities;
using Jotunn.Managers;
using Jotunn.Configs;
using BepInEx.Configuration;
using HarmonyLib;
using System.Linq;
using System.IO;
using System.Text.RegularExpressions;


namespace ValheimJP
{
    [BepInPlugin(PluginGUID, "Correct Localization JP for Valheim", "1.0.0")]
    [BepInDependency(Jotunn.Main.ModGuid)]
    [NetworkCompatibility(CompatibilityLevel.EveryoneMustHaveMod, VersionStrictness.Minor)]
    [BepInDependency("cinnabun.backpacks-v1.0.0", BepInDependency.DependencyFlags.SoftDependency)]
    public class TextCorrector : BaseUnityPlugin
    {
        public const string PluginGUID = "Gedevan-Aleksizde.mods.ValheimJP";
        public static readonly Dictionary<string, string> defaultFontCorrespondence = new Dictionary<string, string>()
        {
            {"Norse", "Yu Mincho"},
            {"Norsebold", "Yu Mincho Bold"},
            {"prstart", "Yu Mincho" },
            {"prstartk", "Yu Mincho"},
            {"rune", "Yu Mincho" },
            {"Arial", "Yu Mincho" },
            {"AveriaSerifLibre-Regular", "Yu Mincho" },
            {"AveriaSerifLibre-Light",  "Yu Mincho"},
            {"AveriaSerifLibre-Bold", "Yu Mincho Bold" },
            {"AveriaSerifLibre-Italic", "Yu Mincho" },
            {"AveriaSerifLibre-BoldItalic", "Yu Mincho Bold" },
            {"AveriaSansLibre-Regular", "Yu Gothic"},
            {"AveriaSansLibre-Light",  "Yu Gothic"},
            {"AveriaSansLibre-Bold", "Yu Gothic Bold"},
            {"AveriaSansLibre-Italic", "Yu Gothic" },
            {"AveriaSansLibre-BoldItalic", "Yu Gothic Bold" }
        };
        public static ConfigEntry<string> fallbackFont;
        public static ConfigEntry<bool> correctFont;
        public static ConfigEntry<bool> debugMode;
        public static ConfigEntry<bool> textOverflow;
        public static ConfigEntry<string> howToReplace;
        public static Dictionary<string, ConfigEntry<string>> newFontNames = new Dictionary<string, ConfigEntry<string>>();
        internal static new ManualLogSource Logger;


        private void Awake()
        {
            Logger = base.Logger;
            this.LoadCfg();
            Harmony.CreateAndPatchAll(typeof(TextCorrector));
            if (correctFont.Value) Harmony.CreateAndPatchAll(typeof(CorrectFontPatch));
            AddLocalizationText();
        }
        private void Start()
        {
            Localization.instance.m_endChars = Localization.instance.m_endChars.Concat<char>(new char[] { '、', '。', '〈', '〉', '「', '」', '『', '』', '《', '》' }).ToArray<char>();
        }
        private void LoadCfg()
        {
            Config.SaveOnConfigSet = true;
            // Why dare you use CP932, Windows
            // We can write multibyte chars if change MO2 plugin source code, but Idk its precice influence
            correctFont = Config.Bind<bool>("General", "CorrectFont", true, "Enable to replace to the correct fonts");
            debugMode = Config.Bind<bool>("General", "DebugMode", false, "Enable to output verbose log");
            textOverflow = Config.Bind<bool>("General", "TextOverflow", false, "Enable to overflow all texts");
            howToReplace = Config.Bind<string>("General", "HowToReplace", "Override", "'Override', or 'Fallback' ");
            foreach (KeyValuePair<string, string> kv in defaultFontCorrespondence)
            {
                ConfigEntry<string> fontName = Config.Bind<string>("NewFonts", kv.Key, kv.Value, $"font name which is replaced with {kv.Key}");
                newFontNames.Add(kv.Key, fontName);
            }
            fallbackFont = Config.Bind<string>("NewFonts", "FallbackFont", "Yu Mincho", "a fallback font name");
            Logger.LogInfo($"fallbackfont = {TextCorrector.fallbackFont.Value}");
            Logger.LogInfo($"correctFont = {TextCorrector.correctFont.Value}");
            Logger.LogInfo($"textOverflow {TextCorrector.textOverflow.Value}");

        }
        private void AddLocalizationText()
        {
            Dictionary<string, string> correctedText;
            CustomLocalization Localization = new CustomLocalization();
            AssetBundle ab = AssetUtils.LoadAssetBundle("ValheimJP/Assets/correcttext_japanese");
            string text = ab.LoadAsset<TextAsset>("CorrectText_Japanese").text;
            correctedText = SimpleJson.SimpleJson.DeserializeObject<Dictionary<string, string>>(text);
            Localization.AddTranslation("Japanese", correctedText);
            // TODO: Jotunn hardcoded to output log as the Debug level by each entries. it's too verbose... why you dare do so??
            LocalizationManager.Instance.AddLocalization(Localization);
        }
        private class CorrectFontPatch
        {
            private static CorrectFontPatch _instance;
            public List<string> defaultFontNames = new List<string>();
            public Dictionary<string, string[]> newFontNamesStr = new Dictionary<string, string[]>();
            public Dictionary<(string, int), Font> FontAssets = new Dictionary<(string, int), Font>();

            public static CorrectFontPatch Instance
            {
                get
                {
                    if(_instance is null)
                    {
                        _instance = new CorrectFontPatch();
                    }
                    return _instance;
                }
                private set => _instance = value;
            }
            public CorrectFontPatch()
            {
                TextCorrector.Logger.LogInfo("Correct Font Patch Instance Created.");
                foreach(KeyValuePair<string, ConfigEntry<string>> kv in TextCorrector.newFontNames) // why cant write in one-liner?
                {
                    this.newFontNamesStr.Add(kv.Key, Regex.Split(kv.Value.Value, ",(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))").Concat<string>(new string[] { TextCorrector.fallbackFont.Value }).ToArray<string>() );
                }
            }
            [HarmonyPatch(typeof(Text), "OnEnable")]
            [HarmonyPostfix]
            private static void CorrectCorrectCorrect(Text __instance)
            {
                ChangeFont(__instance);
            }
            
            // [HarmonyPatch(typeof(TextViewer), "ShowText", new Type[] { typeof(TextViewer.Style), typeof(string), typeof(string), typeof(bool) })]
            // [HarmonyPrefix]
            private static void KeepOriginalFontOnRune(TextViewer __instance, bool __runOriginal, TextViewer.Style style, string topic, string text, bool autoHide)
            {

                if(style == TextViewer.Style.Rune)
                {
                    string _text = Localization.instance.Localize(text);
                    __runOriginal = false;
                    __instance.m_topic.text = topic;
                    __instance.m_text.text = _text;
                    __instance.m_runeText.text = _text;
                    __instance.m_animator.SetBool(TextViewer.m_visibleID, value: true);
                    __instance.m_autoHide = true;
                    __instance.m_openPlayerPos = Player.m_localPlayer.transform.position;
                    __instance.m_showTime = 0f;
                    ZLog.Log("Show text " + topic + ":" + text);
                }
            }
            private static void ChangeFont(Text text)
            {
                if (text.text.Contains("塞がっている") || text.text.Contains("blocked") || text.text.Contains("Cargo"))
                {
                    if(TextCorrector.debugMode.Value) TextCorrector.Logger.LogDebug($"text={text.text}, go={text.gameObject.name}(root={text.gameObject.transform.root}), font={text.font.name}");
                    
                }
                if (text.font != null)
                {
                    string[] newFontNames;
                    if (!Instance.newFontNamesStr.TryGetValue(text.font.name, out newFontNames))
                    {
                        newFontNames = new string[] { TextCorrector.fallbackFont.Value };
                    }
                    if (TextCorrector.howToReplace.Value != "Override" )
                    {
                      newFontNames = (new string[] { text.font.fontNames[0] }).Concat<string>(newFontNames).ToArray<string>();
                    }
                    if (text.font.fontNames != newFontNames)
                    {
                        if (TextCorrector.debugMode.Value)  TextCorrector.Logger.LogDebug($"new fallbacks for '{text.font.name}' = {string.Join(", ", newFontNames)}");
                        text.font.fontNames = newFontNames;
                    }
                }
            }
        }
        /*
        [HarmonyPatch(typeof(Localization), "Localize", typeof(Transform))]
        [HarmonyPrefix]
        // [HarmonyWrapSafe]
        private static void AddExtraLocalizationText(Transform root)
        {
            foreach (Text text in root.gameObject.GetComponentsInChildren<Text>(includeInactive: true))
            {
                if (text.text == "Cargo")
                {
                    TextCorrector.Logger.LogDebug("Cargo is Localized");
                    text.text = "$tool_cargo";
                }
            }
        }*/
        //[HarmonyPatch(typeof(Localization), MethodType.Constructor)]
        //[HarmonyPostfix]
        private static void TweakLocalizationSettings(Localization __instance)
        {
            __instance.m_endChars = __instance.m_endChars.Concat<char>(new char[] { '、', '。' }).ToArray<char>();
            if (TextCorrector.debugMode.Value) TextCorrector.Logger.LogDebug($"m_endChars={__instance.m_endChars}");
        }
        [HarmonyPatch(typeof(FejdStartup), "SetupGui")]
        [HarmonyPostfix]
        private static void HarmonyTest()
        {
            if (TextCorrector.debugMode.Value) TextCorrector.Logger.LogDebug("----- Harmony Test: FejdStartup.SetupGui called ----");
        }
        //TODO: Jotunn なしの場合は LoadCSV で割り込めば簡単か?
    }
}
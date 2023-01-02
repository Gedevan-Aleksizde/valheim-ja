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
        public static ConfigEntry<string> fontPreset;
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
        private void LoadCfg()
        {
            Config.SaveOnConfigSet = true;
            // Why dare you use CP932, Windows
            // We can write multibyte chars if change MO2 plugin source code, but Idk its precice influence
            correctFont = Config.Bind<bool>("General", "CorrectFont", true, "Enable to replace to the correct fonts");
            debugMode = Config.Bind<bool>("General", "DebugMode", true, "Enable to output verbose log");
            textOverflow = Config.Bind<bool>("General", "TextOverflow", false, "Enable to overflow all texts");
            fontPreset = Config.Bind<string>("General", "FontPreset", "Yu", "Font Preset, 'Yu', 'Native', or 'Custom' ");
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
            public Dictionary<string, string> newFontNamesStr = new Dictionary<string, string>();
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
                foreach(KeyValuePair<string, ConfigEntry<string>> kv in TextCorrector.newFontNames) // why cant write in one-liner
                {
                    this.newFontNamesStr.Add(kv.Key, kv.Value.Value);
                }
            }
            [HarmonyPatch(typeof(Localization), "Localize", typeof(Transform))]
            [HarmonyPostfix]
            // [HarmonyWrapSafe]
            private static void CorrectFont(Transform root)
            {
                TextCorrector.Logger.LogDebug("Localization.Localize called");
                Text[] aho = root.gameObject.GetComponentsInChildren<Text>(includeInactive: true);
                foreach (Text text in aho)
                {
                    ChangeFont(text);
                }
            }
            [HarmonyPatch(typeof(Localization), "ReLocalizeVisible", typeof(Transform))]
            [HarmonyPostfix]
            // [HarmonyWrapSafe]
            private static void CorrectFontVisible(Transform root)
            {
                // TODO: Why so frequently called?
                // TextCorrector.Logger.LogDebug("Localization.ReLocalizeVisible called");
                foreach (Text text in root.gameObject.GetComponentsInChildren<Text>(includeInactive: true))
                {
                    if (text.gameObject.activeInHierarchy)
                    {
                        // TODO: what's the Localization.instance.textStrings?
                        ChangeFont(text);
                    }
                }
                
            }
            [HarmonyPatch(typeof(Sign), "Awake")]
            [HarmonyPrefix]
            private static void CorrectFontSign(Sign __instance)
            {
                ChangeFont(__instance.m_textWidget);
            }
            [HarmonyPatch(typeof(Text), "OnEnable")]
            [HarmonyPostfix]
            private static void CorrectCorrectCorrect(Text __instance)
            {
                ChangeFont(__instance);
            }
            [HarmonyPatch(typeof(Text), "AssignDefaultFont")]
            [HarmonyPostfix]
            private static void ChangeDefaultFont(Text __instance)
            {
                if (!Instance.defaultFontNames.Contains(__instance.font.name))
                {
                    TextCorrector.Logger.LogDebug($"NEW FONT FOUND: {__instance.font.name}");
                    Instance.defaultFontNames.Add(__instance.font.name);
                }
                __instance.font.name = TextCorrector.fallbackFont.Value;
                ChangeFont(__instance);
            }
            private static void ChangeFont(Text text)
            {
                if (text.font != null)
                {
                    if (!Instance.defaultFontNames.Contains(text.font.name))
                    {
                        TextCorrector.Logger.LogDebug($"NEW FONT FOUND: {text.font.name}");
                        Instance.defaultFontNames.Add(text.font.name);
                    }
                    if (!Instance.newFontNamesStr.TryGetValue(text.font.name, out string newFontName))
                    {
                        if (Instance.newFontNamesStr.Values.Contains<string>(text.font.name))
                        {
                            newFontName = text.font.name;
                        }
                        else
                        {
                            if (TextCorrector.debugMode.Value)
                            {
                                TextCorrector.Logger.LogWarning($"substitute font for '{text.font.name}' not found");
                            }
                            newFontName = TextCorrector.fallbackFont.Value;
                        }
                    }
                    if (!Instance.FontAssets.ContainsKey((newFontName, text.font.fontSize)) && text.font.name != newFontName)
                    {

                        Font newFont = Font.CreateDynamicFontFromOSFont(newFontName, text.font.fontSize);
                        Instance.FontAssets.Add((newFontName, text.font.fontSize), newFont);
                    }
                    if (newFontName != text.font.name)
                    {
                        TextCorrector.Logger.LogDebug($"FONT CHANGE: {text.font.name} (style:{text.fontStyle}) to {newFontName}: {text.text}");
                        text.font = Instance.FontAssets[(newFontName, text.font.fontSize)];
                    }
                    // Localize
                    if (TextCorrector.textOverflow.Value)
                    {
                        text.horizontalOverflow = HorizontalWrapMode.Wrap;
                        text.verticalOverflow = VerticalWrapMode.Overflow;
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
        [HarmonyPatch(typeof(FejdStartup), "SetupGui")]
        [HarmonyPostfix]
        private static void HarmonyTest()
        {
            TextCorrector.Logger.LogDebug("----- Harmony Test: FejdStartup.SetupGui called ----");
        }
        //TODO: Jotunn なしの場合は LoadCSV で割り込めば簡単か?
    }
}
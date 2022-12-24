using System.Collections.Generic;
using BepInEx;
using BepInEx.Logging;
using UnityEngine;
using Jotunn;
using Jotunn.Utils;
using Jotunn.Entities;
using Jotunn.Managers;

namespace ValheimJP
{
    [BepInPlugin(PluginGUID, "Corrected Japanese Text of Valheim", "1.0.0")]
    [BepInDependency(Jotunn.Main.ModGuid)]
    [NetworkCompatibility(CompatibilityLevel.EveryoneMustHaveMod, VersionStrictness.Minor)]
    [BepInDependency("cinnabun.backpacks-v1.0.0", BepInDependency.DependencyFlags.SoftDependency)]
    public class TextCorrecter : BaseUnityPlugin
    {
        public const string PluginGUID = "Gedevan-Aleksizde.mods.ValheimJP";
        private void Awake()
        {
            AddLocalizations();
        }
        private void AddLocalizations()
        {
            Dictionary<string, string> correctedText;
            CustomLocalization Localization = new CustomLocalization();
            AssetBundle ab = AssetUtils.LoadAssetBundle("ValheimJP/Assets/correctedtext_japanese");
            Logger.LogInfo(ab);
            string text = ab.LoadAsset<TextAsset>("CorrectedText_Japanese").text;
            Debug.Log($"text length{text.Length}");
            correctedText = SimpleJson.SimpleJson.DeserializeObject<Dictionary<string, string>>(text);
            Localization.AddTranslation("Japanese", correctedText);
            LocalizationManager.Instance.AddLocalization(Localization);
        }
    }
}
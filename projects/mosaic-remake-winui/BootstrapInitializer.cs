using Microsoft.Windows.ApplicationModel.DynamicDependency;
using System;
using System.Runtime.CompilerServices;

namespace MosaicRemake.WinUI;

internal static class BootstrapInitializer
{
    [ModuleInitializer]
    internal static void InitializeWindowsAppSdk()
    {
        uint majorMinorVersion = Microsoft.WindowsAppSDK.Release.MajorMinor;
        string versionTag = Microsoft.WindowsAppSDK.Release.VersionTag;
        var minVersion = new PackageVersion(Microsoft.WindowsAppSDK.Runtime.Version.UInt64);
        var options = Bootstrap.InitializeOptions.OnNoMatch_ShowUI;

        if (!Bootstrap.TryInitialize(majorMinorVersion, versionTag, minVersion, options, out int hr))
        {
            Environment.Exit(hr);
        }
    }
}

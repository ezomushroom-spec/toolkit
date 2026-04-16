namespace Microsoft.WindowsAppSDK
{
    internal class Release
    {
        internal const ushort Major = 1;
        internal const ushort Minor = 6;
        internal const ushort Patch = 0;
        internal const uint MajorMinor = 0x00010006;
        internal const string Channel = "stable";
        internal const string VersionTag = "";
        internal const string VersionShortTag = "";
        internal const string FormattedVersionTag = "";
        internal const string FormattedVersionShortTag = "";
    }

    namespace Runtime
    {
        internal class Identity
        {
            internal const string Publisher = "CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US";
            internal const string PublisherId = "8wekyb3d8bbwe";
        }

        internal class Version
        {
            internal const ushort Major = 6000;
            internal const ushort Minor = 401;
            internal const ushort Build = 2352;
            internal const ushort Revision = 0;
            internal const ulong UInt64 = 0x1770019109300000;
            internal const string DotQuadString = "6000.401.2352.0";
        }
    }
}

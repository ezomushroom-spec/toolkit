using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Media.Imaging;
using Microsoft.UI.Windowing;
using MosaicRemake.WinUI.Services;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices.WindowsRuntime;
using System.Threading;
using Windows.Storage;
using Windows.Storage.Pickers;
using Windows.ApplicationModel.DataTransfer;
using Windows.Graphics;
using Windows.Graphics.Imaging;

namespace MosaicRemake.WinUI;

public sealed partial class MainWindow : Window
{
    private const int PreviewDecodePixelWidth = 1200;
    private const int MaxPreviewBitmapCacheCount = 12;
    private const int MaxPreviewMetadataCacheCount = 48;
    private const int MaxDecodedSourceCacheCount = 8;
    private const int InitialWarmupMetadataCount = 10;
    private const int InitialWarmupDecodeCount = 4;
    private readonly PythonBridgeService _pythonBridgeService = new();
    private readonly List<string> _inputImagePaths = [];
    private readonly List<ImageListEntry> _imageListEntries = [];
    private readonly Dictionary<string, string> _previewCache = [];
    private readonly Dictionary<string, ImageSource> _previewBitmapCache = [];
    private readonly Queue<string> _previewBitmapCacheOrder = new();
    private readonly Dictionary<string, BridgePreviewMetadataResponse> _previewMetadataCache = [];
    private readonly Queue<string> _previewMetadataCacheOrder = new();
    private readonly Dictionary<string, DecodedPreviewSource> _decodedPreviewSourceCache = [];
    private readonly Queue<string> _decodedPreviewSourceCacheOrder = new();
    private readonly DispatcherTimer _previewDebounceTimer = new();
    private readonly DispatcherTimer _prefetchTimer = new();
    private readonly SemaphoreSlim _renderRequestLock = new(1, 1);
    private CancellationTokenSource? _backgroundWarmupCts;
    private string? _selectedModelPath;
    private string? _selectedInputFolderPath;
    private string? _selectedOutputFolderPath;
    private string? _selectedPreviewSourcePath;
    private int _currentImageIndex = -1;
    private int _latestRenderRequestId;
    private int _previewRequestVersion;
    private int _thumbnailLoadVersion;
    private int _scheduledPrefetchVersion;
    private bool _suppressImageListSelection;

    public MainWindow()
    {
        InitializeComponent();
        ConfigureWindow();
        ConfigureEvents();
        ConfigureInitialState();
        SetStatus(_pythonBridgeService.CanLocateBridge()
            ? "WinUI シェルを起動しました。Python bridge は検出済みです。"
            : "WinUI シェルを起動しました。Python bridge はまだ未検出です。");
        _ = InitializeBridgeStateAsync();
    }

    private void ConfigureWindow()
    {
        var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(this);
        var windowId = Microsoft.UI.Win32Interop.GetWindowIdFromWindow(hwnd);
        var appWindow = AppWindow.GetFromWindowId(windowId);
        appWindow.Resize(new SizeInt32(1400, 920));
    }

    private void ConfigureEvents()
    {
        SelectModelButton.Click += async (_, _) => await SelectModelAsync();
        SelectInputButton.Click += async (_, _) => await SelectInputFolderAsync();
        SelectOutputButton.Click += async (_, _) => await SelectOutputFolderAsync();
        ReviewButton.Click += async (_, _) => await RequestRenderPreviewAsync();
        BatchButton.Click += (_, _) => SetStatus("一括処理は次段で Python core 呼び出しへ接続します。");
        PreviousImageButton.Click += async (_, _) => await MovePreviewImageAsync(-1);
        NextImageButton.Click += async (_, _) => await MovePreviewImageAsync(1);
        ImageListView.SelectionChanged += async (_, _) => await OnImageListSelectionChangedAsync();
        _previewDebounceTimer.Interval = TimeSpan.FromMilliseconds(180);
        _previewDebounceTimer.Tick += async (_, _) =>
        {
            _previewDebounceTimer.Stop();
            await RequestRenderPreviewIfReadyAsync();
        };
        _prefetchTimer.Interval = TimeSpan.FromMilliseconds(350);
        _prefetchTimer.Tick += async (_, _) =>
        {
            _prefetchTimer.Stop();
            await PrefetchNextPreviewIfIdleAsync(_scheduledPrefetchVersion);
        };

        MaskTypeComboBox.SelectionChanged += (_, _) => SchedulePreviewRefresh();
        ShapeTypeComboBox.SelectionChanged += (_, _) => SchedulePreviewRefresh();
        ImageSizeComboBox.SelectionChanged += (_, _) => SchedulePreviewRefresh();
        ConfigureClassSettingsEvents();
        StrengthSlider.ValueChanged += (_, _) =>
        {
            StrengthValueText.Text = $"{StrengthSlider.Value:F0}";
            SchedulePreviewRefresh();
        };
        MarginSlider.ValueChanged += (_, _) =>
        {
            MarginValueText.Text = $"{MarginSlider.Value:F0}px";
            SchedulePreviewRefresh();
        };
        ShowBoxesCheckBox.Checked += (_, _) => SchedulePreviewRefresh();
        ShowBoxesCheckBox.Unchecked += (_, _) => SchedulePreviewRefresh();
        ModelDropBorder.DragOver += OnModelDragOver;
        ModelDropBorder.Drop += OnModelDrop;
        InputDropBorder.DragOver += OnFolderDragOver;
        InputDropBorder.Drop += OnInputDrop;
        OutputDropBorder.DragOver += OnFolderDragOver;
        OutputDropBorder.Drop += OnOutputDrop;
    }

    private void ConfigureInitialState()
    {
        ModelPathText.Text = "既定モデルを使用します。";
        InputPathText.Text = "未選択";
        OutputPathText.Text = "未選択";
        MaskTypeComboBox.SelectedIndex = 0;
        ShapeTypeComboBox.SelectedIndex = 1;
        ImageSizeComboBox.SelectedIndex = 1;
        StrengthSlider.Value = 20;
        MarginSlider.Value = 18;
        PussyConfSlider.Value = 30;
        PenisConfSlider.Value = 30;
        TesticlesConfSlider.Value = 30;
        AnusConfSlider.Value = 30;
        NipplesConfSlider.Value = 30;
        BreastConfSlider.Value = 30;
        StrengthValueText.Text = "20";
        MarginValueText.Text = "18px";
        RefreshClassConfidenceTexts();
        ImagePositionText.Text = "画像 0 / 0";
        PreviousImageButton.IsEnabled = false;
        NextImageButton.IsEnabled = false;
        _imageListEntries.Clear();
        ImageListView.Items.Clear();
        _previewBitmapCache.Clear();
        _previewBitmapCacheOrder.Clear();
        _previewMetadataCache.Clear();
        _previewMetadataCacheOrder.Clear();
        _decodedPreviewSourceCache.Clear();
        _decodedPreviewSourceCacheOrder.Clear();
        ShowPreviewPlaceholder("入力フォルダを選ぶと、最初の画像をここへ表示します。");
    }

    private void SetStatus(string message)
    {
        StatusText.Text = message;
    }

    private async Task InitializeBridgeStateAsync()
    {
        if (!_pythonBridgeService.CanLocateBridge())
        {
            return;
        }

        var health = await _pythonBridgeService.RunHealthAsync();
        if (!health.Ok || health.Response is null)
        {
            return;
        }

        ApplyBridgeHealthResponse(health.Response);
        if (health.Response.ModelLoaded)
        {
            _ = _pythonBridgeService.RunWarmupAsync(health.Response.ModelPath);
        }
    }

    private async Task SelectModelAsync()
    {
        var picker = new FileOpenPicker();
        picker.FileTypeFilter.Add(".pt");
        InitializePicker(picker);

        var file = await picker.PickSingleFileAsync();
        if (file is null)
        {
            SetStatus("モデル選択をキャンセルしました。");
            return;
        }

        _selectedModelPath = file.Path;
        ModelPathText.Text = _selectedModelPath;
        SetStatus("推論モデルを更新しました。");
        _ = _pythonBridgeService.RunWarmupAsync(_selectedModelPath);
        await RequestRenderPreviewAsync();
    }

    private async Task SelectInputFolderAsync()
    {
        var picker = new FolderPicker();
        picker.FileTypeFilter.Add("*");
        InitializePicker(picker);

        var folder = await picker.PickSingleFolderAsync();
        if (folder is null)
        {
            SetStatus("入力フォルダ選択をキャンセルしました。");
            return;
        }

        _selectedInputFolderPath = folder.Path;
        InputPathText.Text = _selectedInputFolderPath;
        await LoadInputImagesAsync(_selectedInputFolderPath, "入力フォルダを更新しました。");
    }

    private async Task SelectOutputFolderAsync()
    {
        var picker = new FolderPicker();
        picker.FileTypeFilter.Add("*");
        InitializePicker(picker);

        var folder = await picker.PickSingleFolderAsync();
        if (folder is null)
        {
            SetStatus("出力フォルダ選択をキャンセルしました。");
            return;
        }

        _selectedOutputFolderPath = folder.Path;
        OutputPathText.Text = _selectedOutputFolderPath;
        SetStatus("出力フォルダを更新しました。");
    }

    private async Task RequestRenderPreviewAsync()
    {
        CancelBackgroundWarmup();
        Interlocked.Increment(ref _latestRenderRequestId);
        if (!await _renderRequestLock.WaitAsync(0))
        {
            return;
        }

        try
        {
            while (true)
            {
                var currentRequestId = _latestRenderRequestId;
                await RenderPreviewCoreAsync(currentRequestId);
                if (currentRequestId == _latestRenderRequestId)
                {
                    break;
                }
            }
        }
        finally
        {
            _renderRequestLock.Release();
        }
    }

    private async Task RenderPreviewCoreAsync(int requestId)
    {
        CancelPrefetch();

        if (!_pythonBridgeService.CanLocateBridge())
        {
            SetStatus("Python bridge が見つかりません。");
            return;
        }

        if (string.IsNullOrWhiteSpace(_selectedPreviewSourcePath) || !File.Exists(_selectedPreviewSourcePath))
        {
            ShowPreviewPlaceholder("入力フォルダを選ぶと、最初の画像をここへ表示します。");
            SetStatus("先に入力フォルダを選択してください。");
            return;
        }

        var selectedPreviewSourcePath = _selectedPreviewSourcePath;
        var selectedModelPath = _selectedModelPath;
        var previewParams = BuildPreviewParams();
        var classSettings = BuildClassSettings();
        _previewRequestVersion = requestId;
        var cacheKey = BuildPreviewCacheKey(
            selectedPreviewSourcePath,
            selectedModelPath,
            previewParams,
            classSettings
        );
        if (_previewBitmapCache.TryGetValue(cacheKey, out var cachedPreviewSource))
        {
            PreviewImage.Source = cachedPreviewSource;
            PreviewPlaceholderText.Visibility = Visibility.Collapsed;
            SetStatus($"preview キャッシュを表示 / source={Path.GetFileName(selectedPreviewSourcePath)}");
            UpdateImagePositionText();
            return;
        }

        await ShowBasePreviewAsync(selectedPreviewSourcePath, requestId);
        if (requestId != _latestRenderRequestId)
        {
            return;
        }

        if (await TryRenderLightweightPreviewAsync(
            requestId,
            cacheKey,
            selectedPreviewSourcePath,
            selectedModelPath,
            previewParams,
            classSettings))
        {
            return;
        }

        if (_previewCache.TryGetValue(cacheKey, out var cachedPreviewPath) && File.Exists(cachedPreviewPath))
        {
            await LoadPreviewImageAsync(cacheKey, cachedPreviewPath);
            SetStatus($"preview キャッシュを表示 / source={Path.GetFileName(selectedPreviewSourcePath)}");
            UpdateImagePositionText();
            return;
        }

        SetStatus("Python bridge で preview を生成中...");
        var previewPath = Path.Combine(
            Path.GetTempPath(),
            $"mosaic-remake-winui-preview-{Guid.NewGuid():N}.jpg"
        );

        var result = await _pythonBridgeService.RunPreviewAsync(
            new PreviewRequest
            {
                ImagePath = selectedPreviewSourcePath,
                OutputPreviewPath = previewPath,
                ModelPath = selectedModelPath,
                Params = previewParams,
                ClassSettings = classSettings,
            }
        );

        if (!result.Ok || string.IsNullOrWhiteSpace(result.PreviewPath) || !File.Exists(result.PreviewPath))
        {
            if (requestId != _latestRenderRequestId)
            {
                return;
            }
            ShowPreviewPlaceholder("preview の生成に失敗しました。");
            SetStatus(result.Message);
            return;
        }

        if (requestId != _latestRenderRequestId)
        {
            return;
        }

        _previewCache[cacheKey] = result.PreviewPath;
        await LoadPreviewImageAsync(cacheKey, result.PreviewPath);
        SetStatus($"{result.Message} / source={Path.GetFileName(selectedPreviewSourcePath)}");
        UpdateImagePositionText();
        SchedulePrefetch(requestId);
    }

    private async Task<bool> TryRenderLightweightPreviewAsync(
        int requestId,
        string cacheKey,
        string selectedPreviewSourcePath,
        string? selectedModelPath,
        Dictionary<string, object> previewParams,
        Dictionary<string, Dictionary<string, object>> classSettings)
    {
        var detectionCacheKey = BuildDetectionCacheKey(
            selectedPreviewSourcePath,
            selectedModelPath,
            previewParams,
            classSettings
        );
        if (!_previewMetadataCache.TryGetValue(detectionCacheKey, out var previewMetadata))
        {
            SetStatus("Python bridge で候補を取得中...");
            var detectionResult = await _pythonBridgeService.RunPreviewDetectionAsync(
                new PreviewDetectionRequest
                {
                    ImagePath = selectedPreviewSourcePath,
                    ModelPath = selectedModelPath,
                    Params = previewParams,
                    ClassSettings = classSettings,
                }
            );

            if (requestId != _latestRenderRequestId)
            {
                return true;
            }

            if (!detectionResult.Ok || detectionResult.Response is null)
            {
                return false;
            }

            previewMetadata = detectionResult.Response;
            CachePreviewMetadata(detectionCacheKey, previewMetadata);
        }

        var previewSource = await CreateLightweightPreviewSourceAsync(
            selectedPreviewSourcePath,
            previewMetadata,
            previewParams
        );
        if (requestId != _latestRenderRequestId)
        {
            return true;
        }

        if (previewSource is null)
        {
            return false;
        }

        CachePreviewBitmap(cacheKey, previewSource);
        PreviewImage.Source = previewSource;
        PreviewPlaceholderText.Visibility = Visibility.Collapsed;
        SetStatus($"簡易 preview を表示 / candidate_count={previewMetadata.CandidateCount} / source={Path.GetFileName(selectedPreviewSourcePath)}");
        UpdateImagePositionText();
        SchedulePrefetch(requestId);
        return true;
    }

    private async Task RequestRenderPreviewIfReadyAsync()
    {
        if (!string.IsNullOrWhiteSpace(_selectedPreviewSourcePath))
        {
            await RequestRenderPreviewAsync();
        }
    }

    private async Task ShowBasePreviewAsync(string imagePath, int requestId)
    {
        var basePreviewSource = await CreateBasePreviewSourceAsync(imagePath);
        if (requestId != _latestRenderRequestId || basePreviewSource is null)
        {
            return;
        }

        PreviewImage.Source = basePreviewSource;
        PreviewPlaceholderText.Visibility = Visibility.Collapsed;
        SetStatus($"原画像を先に表示中... / source={Path.GetFileName(imagePath)}");
        UpdateImagePositionText();
    }

    private void SchedulePreviewRefresh()
    {
        if (string.IsNullOrWhiteSpace(_selectedPreviewSourcePath))
        {
            return;
        }

        _previewDebounceTimer.Stop();
        CancelBackgroundWarmup();
        CancelPrefetch();
        _previewDebounceTimer.Start();
    }

    private async Task<ImageSource?> CreateLightweightPreviewSourceAsync(
        string imagePath,
        BridgePreviewMetadataResponse previewMetadata,
        Dictionary<string, object> previewParams)
    {
        try
        {
            var decodedSource = await GetOrCreateDecodedPreviewSourceAsync(imagePath);
            if (decodedSource is null)
            {
                return null;
            }

            var pixels = decodedSource.Pixels.ToArray();

            ApplyLightweightPreviewEffects(
                pixels,
                decodedSource.PixelWidth,
                decodedSource.PixelHeight,
                previewMetadata,
                previewParams
            );

            return await CreateWriteableBitmapAsync(decodedSource.PixelWidth, decodedSource.PixelHeight, pixels);
        }
        catch
        {
            return null;
        }
    }

    private async Task<ImageSource?> CreateBasePreviewSourceAsync(string imagePath)
    {
        try
        {
            var decodedSource = await GetOrCreateDecodedPreviewSourceAsync(imagePath);
            if (decodedSource is null)
            {
                return null;
            }

            return await CreateWriteableBitmapAsync(
                decodedSource.PixelWidth,
                decodedSource.PixelHeight,
                decodedSource.Pixels.ToArray()
            );
        }
        catch
        {
            return null;
        }
    }

    private async Task<DecodedPreviewSource?> GetOrCreateDecodedPreviewSourceAsync(string imagePath)
    {
        if (_decodedPreviewSourceCache.TryGetValue(imagePath, out var cachedSource))
        {
            return cachedSource;
        }

        var file = await StorageFile.GetFileFromPathAsync(imagePath);
        using var stream = await file.OpenAsync(FileAccessMode.Read);
        var decoder = await BitmapDecoder.CreateAsync(stream);

        var sourceWidth = (int)decoder.PixelWidth;
        var sourceHeight = (int)decoder.PixelHeight;
        var scale = sourceWidth > PreviewDecodePixelWidth
            ? (double)PreviewDecodePixelWidth / sourceWidth
            : 1.0;
        var targetWidth = Math.Max(1, (int)Math.Round(sourceWidth * scale));
        var targetHeight = Math.Max(1, (int)Math.Round(sourceHeight * scale));
        var transform = new BitmapTransform
        {
            ScaledWidth = (uint)targetWidth,
            ScaledHeight = (uint)targetHeight,
            InterpolationMode = BitmapInterpolationMode.Fant,
        };

        var softwareBitmap = await decoder.GetSoftwareBitmapAsync(
            BitmapPixelFormat.Bgra8,
            BitmapAlphaMode.Premultiplied,
            transform,
            ExifOrientationMode.RespectExifOrientation,
            ColorManagementMode.DoNotColorManage
        );

        var pixels = new byte[targetWidth * targetHeight * 4];
        softwareBitmap.CopyToBuffer(pixels.AsBuffer());
        var decodedSource = new DecodedPreviewSource(targetWidth, targetHeight, pixels);
        CacheDecodedPreviewSource(imagePath, decodedSource);
        return decodedSource;
    }

    private static async Task<WriteableBitmap> CreateWriteableBitmapAsync(int width, int height, byte[] pixels)
    {
        var bitmap = new WriteableBitmap(width, height);
        using var pixelStream = bitmap.PixelBuffer.AsStream();
        await pixelStream.WriteAsync(pixels, 0, pixels.Length);
        pixelStream.Seek(0, SeekOrigin.Begin);
        return bitmap;
    }

    private static void ApplyLightweightPreviewEffects(
        byte[] pixels,
        int pixelWidth,
        int pixelHeight,
        BridgePreviewMetadataResponse previewMetadata,
        Dictionary<string, object> previewParams)
    {
        var candidates = previewMetadata.Candidates ?? [];
        if (candidates.Count == 0)
        {
            return;
        }

        var maskType = previewParams.TryGetValue("mask_type", out var maskTypeValue)
            ? Convert.ToString(maskTypeValue, CultureInfo.InvariantCulture) ?? "pixel"
            : "pixel";
        var strength = previewParams.TryGetValue("strength", out var strengthValue)
            ? Math.Max(1, (int)Math.Round(Convert.ToDouble(strengthValue, CultureInfo.InvariantCulture)))
            : 20;
        var margin = previewParams.TryGetValue("margin", out var marginValue)
            ? Math.Max(0, (int)Math.Round(Convert.ToDouble(marginValue, CultureInfo.InvariantCulture)))
            : 18;
        var showBoxes = previewParams.TryGetValue("show_boxes", out var showBoxesValue) &&
            (showBoxesValue is bool boolValue
                ? boolValue
                : bool.TryParse(Convert.ToString(showBoxesValue, CultureInfo.InvariantCulture), out var parsedValue) && parsedValue);

        var sourceWidth = Math.Max(1, previewMetadata.ImageWidth);
        var sourceHeight = Math.Max(1, previewMetadata.ImageHeight);
        var scaleX = (double)pixelWidth / sourceWidth;
        var scaleY = (double)pixelHeight / sourceHeight;

        foreach (var candidate in candidates)
        {
            if (candidate.Xyxy is null || candidate.Xyxy.Count < 4)
            {
                continue;
            }

            var x1 = Math.Clamp((int)Math.Floor(candidate.Xyxy[0] * scaleX) - margin, 0, pixelWidth);
            var y1 = Math.Clamp((int)Math.Floor(candidate.Xyxy[1] * scaleY) - margin, 0, pixelHeight);
            var x2 = Math.Clamp((int)Math.Ceiling(candidate.Xyxy[2] * scaleX) + margin, 0, pixelWidth);
            var y2 = Math.Clamp((int)Math.Ceiling(candidate.Xyxy[3] * scaleY) + margin, 0, pixelHeight);

            if (x2 <= x1 || y2 <= y1)
            {
                continue;
            }

            ApplyRegionFilter(pixels, pixelWidth, pixelHeight, x1, y1, x2, y2, maskType, strength);

            if (showBoxes)
            {
                DrawBoundingBox(
                    pixels,
                    pixelWidth,
                    pixelHeight,
                    x1,
                    y1,
                    x2,
                    y2,
                    GetPreviewBoxColor(candidate.ClassId)
                );
            }
        }
    }

    private static void ApplyRegionFilter(
        byte[] pixels,
        int pixelWidth,
        int pixelHeight,
        int x1,
        int y1,
        int x2,
        int y2,
        string maskType,
        int strength)
    {
        _ = pixelHeight;
        switch (maskType)
        {
            case "black":
                FillRegion(pixels, pixelWidth, x1, y1, x2, y2, 0, 0, 0);
                return;
            case "white":
                FillRegion(pixels, pixelWidth, x1, y1, x2, y2, 255, 255, 255);
                return;
            case "blur":
                ApplyBlockAverage(pixels, pixelWidth, x1, y1, x2, y2, Math.Max(2, strength));
                return;
            default:
                ApplyPixelate(pixels, pixelWidth, x1, y1, x2, y2, Math.Max(1, strength));
                return;
        }
    }

    private static void FillRegion(
        byte[] pixels,
        int pixelWidth,
        int x1,
        int y1,
        int x2,
        int y2,
        byte red,
        byte green,
        byte blue)
    {
        for (var y = y1; y < y2; y++)
        {
            for (var x = x1; x < x2; x++)
            {
                var offset = ((y * pixelWidth) + x) * 4;
                pixels[offset] = blue;
                pixels[offset + 1] = green;
                pixels[offset + 2] = red;
                pixels[offset + 3] = 255;
            }
        }
    }

    private static void ApplyPixelate(byte[] pixels, int pixelWidth, int x1, int y1, int x2, int y2, int blockSize)
    {
        for (var blockY = y1; blockY < y2; blockY += blockSize)
        {
            for (var blockX = x1; blockX < x2; blockX += blockSize)
            {
                var blockEndX = Math.Min(x2, blockX + blockSize);
                var blockEndY = Math.Min(y2, blockY + blockSize);
                var sampleX = Math.Min(blockEndX - 1, blockX + ((blockEndX - blockX) / 2));
                var sampleY = Math.Min(blockEndY - 1, blockY + ((blockEndY - blockY) / 2));
                var sampleOffset = ((sampleY * pixelWidth) + sampleX) * 4;
                var blue = pixels[sampleOffset];
                var green = pixels[sampleOffset + 1];
                var red = pixels[sampleOffset + 2];

                for (var y = blockY; y < blockEndY; y++)
                {
                    for (var x = blockX; x < blockEndX; x++)
                    {
                        var offset = ((y * pixelWidth) + x) * 4;
                        pixels[offset] = blue;
                        pixels[offset + 1] = green;
                        pixels[offset + 2] = red;
                        pixels[offset + 3] = 255;
                    }
                }
            }
        }
    }

    private static void ApplyBlockAverage(byte[] pixels, int pixelWidth, int x1, int y1, int x2, int y2, int blockSize)
    {
        for (var blockY = y1; blockY < y2; blockY += blockSize)
        {
            for (var blockX = x1; blockX < x2; blockX += blockSize)
            {
                var blockEndX = Math.Min(x2, blockX + blockSize);
                var blockEndY = Math.Min(y2, blockY + blockSize);
                long blueTotal = 0;
                long greenTotal = 0;
                long redTotal = 0;
                long count = 0;

                for (var y = blockY; y < blockEndY; y++)
                {
                    for (var x = blockX; x < blockEndX; x++)
                    {
                        var offset = ((y * pixelWidth) + x) * 4;
                        blueTotal += pixels[offset];
                        greenTotal += pixels[offset + 1];
                        redTotal += pixels[offset + 2];
                        count++;
                    }
                }

                if (count == 0)
                {
                    continue;
                }

                var blue = (byte)(blueTotal / count);
                var green = (byte)(greenTotal / count);
                var red = (byte)(redTotal / count);
                for (var y = blockY; y < blockEndY; y++)
                {
                    for (var x = blockX; x < blockEndX; x++)
                    {
                        var offset = ((y * pixelWidth) + x) * 4;
                        pixels[offset] = blue;
                        pixels[offset + 1] = green;
                        pixels[offset + 2] = red;
                        pixels[offset + 3] = 255;
                    }
                }
            }
        }
    }

    private static void DrawBoundingBox(
        byte[] pixels,
        int pixelWidth,
        int pixelHeight,
        int x1,
        int y1,
        int x2,
        int y2,
        Windows.UI.Color color)
    {
        const int thickness = 2;
        for (var offset = 0; offset < thickness; offset++)
        {
            DrawHorizontalLine(pixels, pixelWidth, pixelHeight, x1, x2, y1 + offset, color);
            DrawHorizontalLine(pixels, pixelWidth, pixelHeight, x1, x2, y2 - 1 - offset, color);
            DrawVerticalLine(pixels, pixelWidth, pixelHeight, x1 + offset, y1, y2, color);
            DrawVerticalLine(pixels, pixelWidth, pixelHeight, x2 - 1 - offset, y1, y2, color);
        }
    }

    private static void DrawHorizontalLine(
        byte[] pixels,
        int pixelWidth,
        int pixelHeight,
        int x1,
        int x2,
        int y,
        Windows.UI.Color color)
    {
        if (y < 0 || y >= pixelHeight)
        {
            return;
        }

        for (var x = Math.Max(0, x1); x < Math.Min(pixelWidth, x2); x++)
        {
            var offset = ((y * pixelWidth) + x) * 4;
            pixels[offset] = color.B;
            pixels[offset + 1] = color.G;
            pixels[offset + 2] = color.R;
            pixels[offset + 3] = 255;
        }
    }

    private static void DrawVerticalLine(
        byte[] pixels,
        int pixelWidth,
        int pixelHeight,
        int x,
        int y1,
        int y2,
        Windows.UI.Color color)
    {
        if (x < 0 || x >= pixelWidth)
        {
            return;
        }

        for (var y = Math.Max(0, y1); y < Math.Min(pixelHeight, y2); y++)
        {
            var offset = ((y * pixelWidth) + x) * 4;
            pixels[offset] = color.B;
            pixels[offset + 1] = color.G;
            pixels[offset + 2] = color.R;
            pixels[offset + 3] = 255;
        }
    }

    private static Windows.UI.Color GetPreviewBoxColor(string classId)
    {
        return classId switch
        {
            "pussy" => Windows.UI.Color.FromArgb(255, 255, 95, 132),
            "penis" => Windows.UI.Color.FromArgb(255, 84, 181, 255),
            "testicles" => Windows.UI.Color.FromArgb(255, 128, 201, 100),
            "anus" => Windows.UI.Color.FromArgb(255, 255, 173, 69),
            "nipples" => Windows.UI.Color.FromArgb(255, 202, 117, 255),
            "breast" => Windows.UI.Color.FromArgb(255, 255, 120, 76),
            _ => Windows.UI.Color.FromArgb(255, 90, 160, 255),
        };
    }

    private async Task LoadPreviewImageAsync(string cacheKey, string previewPath)
    {
        if (_previewBitmapCache.TryGetValue(cacheKey, out var cachedBitmap))
        {
            PreviewImage.Source = cachedBitmap;
            PreviewPlaceholderText.Visibility = Visibility.Collapsed;
            return;
        }

        var file = await StorageFile.GetFileFromPathAsync(previewPath);
        using var stream = await file.OpenAsync(FileAccessMode.Read);
        var bitmap = new BitmapImage
        {
            DecodePixelWidth = PreviewDecodePixelWidth,
        };
        await bitmap.SetSourceAsync(stream);
        CachePreviewBitmap(cacheKey, bitmap);
        PreviewImage.Source = bitmap;
        PreviewPlaceholderText.Visibility = Visibility.Collapsed;
    }

    private void ShowPreviewPlaceholder(string message)
    {
        PreviewImage.Source = null;
        PreviewPlaceholderText.Text = message;
        PreviewPlaceholderText.Visibility = Visibility.Visible;
    }

    private void InitializePicker(object picker)
    {
        var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(this);
        WinRT.Interop.InitializeWithWindow.Initialize(picker, hwnd);
    }

    private async Task LoadInputImagesAsync(string folderPath, string statusPrefix)
    {
        CancelBackgroundWarmup();
        CancelPrefetch();
        _thumbnailLoadVersion++;
        _inputImagePaths.Clear();
        _inputImagePaths.AddRange(FindImagePaths(folderPath));
        PopulateImageList();
        _currentImageIndex = _inputImagePaths.Count > 0 ? 0 : -1;
        _selectedPreviewSourcePath = _currentImageIndex >= 0 ? _inputImagePaths[_currentImageIndex] : null;
        UpdateImagePositionText();
        UpdateNavigationButtons();
        UpdateImageListSelection();

        if (_selectedPreviewSourcePath is null)
        {
            ShowPreviewPlaceholder("入力フォルダに対応画像が見つかりません。");
            SetStatus("入力フォルダに preview 対象画像がありません。");
            return;
        }

        SetStatus($"{statusPrefix} レビュー表示で preview を生成します。");
        await RequestRenderPreviewAsync();
        _ = LoadImageListThumbnailsAsync(_thumbnailLoadVersion);
        _ = WarmupUpcomingPreviewDataAsync(_previewRequestVersion);
    }

    private async Task MovePreviewImageAsync(int delta)
    {
        if (_inputImagePaths.Count == 0)
        {
            return;
        }

        var nextIndex = Math.Clamp(_currentImageIndex + delta, 0, _inputImagePaths.Count - 1);
        if (nextIndex == _currentImageIndex)
        {
            return;
        }

        _currentImageIndex = nextIndex;
        _selectedPreviewSourcePath = _inputImagePaths[_currentImageIndex];
        UpdateImagePositionText();
        UpdateNavigationButtons();
        UpdateImageListSelection();
        await RequestRenderPreviewAsync();
        _ = WarmupUpcomingPreviewDataAsync(_previewRequestVersion);
    }

    private void UpdateImagePositionText()
    {
        var current = _currentImageIndex >= 0 ? _currentImageIndex + 1 : 0;
        ImagePositionText.Text = $"画像 {current} / {_inputImagePaths.Count}";
    }

    private void UpdateNavigationButtons()
    {
        PreviousImageButton.IsEnabled = _currentImageIndex > 0;
        NextImageButton.IsEnabled = _currentImageIndex >= 0 && _currentImageIndex < _inputImagePaths.Count - 1;
    }

    private void PopulateImageList()
    {
        _suppressImageListSelection = true;
        _imageListEntries.Clear();
        ImageListView.Items.Clear();
        for (var index = 0; index < _inputImagePaths.Count; index++)
        {
            var entry = CreateImageListEntry(index, _inputImagePaths[index]);
            _imageListEntries.Add(entry);
            ImageListView.Items.Add(entry.Item);
        }
        _suppressImageListSelection = false;
    }

    private void UpdateImageListSelection()
    {
        _suppressImageListSelection = true;
        ImageListView.SelectedIndex = _currentImageIndex;
        if (_currentImageIndex >= 0 && _currentImageIndex < ImageListView.Items.Count)
        {
            ImageListView.ScrollIntoView(ImageListView.Items[_currentImageIndex]);
        }
        _suppressImageListSelection = false;
    }

    private async Task OnImageListSelectionChangedAsync()
    {
        if (_suppressImageListSelection || ImageListView.SelectedIndex < 0)
        {
            return;
        }

        if (ImageListView.SelectedIndex == _currentImageIndex)
        {
            return;
        }

        _currentImageIndex = ImageListView.SelectedIndex;
        _selectedPreviewSourcePath = _inputImagePaths[_currentImageIndex];
        UpdateImagePositionText();
        UpdateNavigationButtons();
        await RequestRenderPreviewAsync();
        _ = WarmupUpcomingPreviewDataAsync(_previewRequestVersion);
    }

    private async Task LoadImageListThumbnailsAsync(int loadVersion)
    {
        foreach (var index in GetThumbnailLoadOrder())
        {
            if (loadVersion != _thumbnailLoadVersion || index < 0 || index >= _imageListEntries.Count)
            {
                return;
            }

            var entry = _imageListEntries[index];
            if (entry.ThumbnailImage.Source is not null)
            {
                continue;
            }

            entry.ThumbnailImage.Source = await CreateThumbnailAsync(entry.ImagePath);
        }
    }

    private IEnumerable<int> GetThumbnailLoadOrder()
    {
        if (_imageListEntries.Count == 0)
        {
            yield break;
        }

        var currentIndex = _currentImageIndex >= 0 ? _currentImageIndex : 0;
        var ordered = Enumerable
            .Range(0, _imageListEntries.Count)
            .OrderBy(index => Math.Abs(index - currentIndex))
            .ThenBy(index => index);

        foreach (var index in ordered)
        {
            yield return index;
        }
    }

    private static async Task<BitmapImage?> CreateThumbnailAsync(string imagePath)
    {
        try
        {
            var file = await StorageFile.GetFileFromPathAsync(imagePath);
            using var stream = await file.OpenAsync(FileAccessMode.Read);
            var bitmap = new BitmapImage
            {
                DecodePixelWidth = 96,
                DecodePixelHeight = 96,
            };
            await bitmap.SetSourceAsync(stream);
            return bitmap;
        }
        catch
        {
            return null;
        }
    }

    private static ImageListEntry CreateImageListEntry(int index, string imagePath)
    {
        var thumbnailImage = new Image
        {
            Width = 72,
            Height = 72,
            Stretch = Stretch.UniformToFill,
        };

        var thumbnailHost = new Grid
        {
            Width = 72,
            Height = 72,
        };
        thumbnailHost.Children.Add(new Border
        {
            Background = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 26, 32, 41)),
            BorderBrush = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 61, 70, 84)),
            BorderThickness = new Thickness(1),
            CornerRadius = new CornerRadius(8),
        });
        thumbnailHost.Children.Add(new FontIcon
        {
            Glyph = "\uE91B",
            FontSize = 20,
            Foreground = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 154, 164, 178)),
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center,
        });
        thumbnailHost.Children.Add(thumbnailImage);

        var content = new Border
        {
            Background = new SolidColorBrush(Windows.UI.Color.FromArgb(22, 33, 44, 54)),
            BorderBrush = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 61, 70, 84)),
            BorderThickness = new Thickness(1),
            CornerRadius = new CornerRadius(10),
            Padding = new Thickness(8),
            Margin = new Thickness(0, 0, 8, 0),
            Width = 180,
            Child = new Grid
            {
                ColumnSpacing = 8,
                ColumnDefinitions =
                {
                    new ColumnDefinition { Width = new GridLength(72) },
                    new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) },
                }
            }
        };

        var rootGrid = (Grid)content.Child;
        rootGrid.Children.Add(thumbnailHost);

        var textPanel = new StackPanel
        {
            Spacing = 4,
            VerticalAlignment = VerticalAlignment.Center,
        };
        Grid.SetColumn(textPanel, 1);
        textPanel.Children.Add(new TextBlock
        {
            Text = $"{index + 1:00}",
            Foreground = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 90, 160, 255)),
            FontSize = 12,
            FontWeight = Microsoft.UI.Text.FontWeights.SemiBold,
        });
        textPanel.Children.Add(new TextBlock
        {
            Text = Path.GetFileName(imagePath),
            TextWrapping = TextWrapping.WrapWholeWords,
            MaxLines = 2,
        });
        rootGrid.Children.Add(textPanel);

        var item = new ListViewItem
        {
            Padding = new Thickness(0),
            HorizontalContentAlignment = HorizontalAlignment.Stretch,
            Content = content,
        };

        return new ImageListEntry(imagePath, item, thumbnailImage);
    }

    private Dictionary<string, object> BuildPreviewParams()
    {
        return new Dictionary<string, object>
        {
            ["mask_type"] = GetComboBoxTag(MaskTypeComboBox, "pixel"),
            ["shape_type"] = GetComboBoxTag(ShapeTypeComboBox, "mask"),
            ["imgsz"] = int.Parse(GetComboBoxTag(ImageSizeComboBox, "960")),
            ["strength"] = StrengthSlider.Value,
            ["margin"] = MarginSlider.Value,
            ["show_boxes"] = ShowBoxesCheckBox.IsChecked == true,
        };
    }

    private Dictionary<string, Dictionary<string, object>> BuildClassSettings()
    {
        return new Dictionary<string, Dictionary<string, object>>
        {
            ["pussy"] = BuildClassSetting(PussyCheckBox, PussyConfSlider),
            ["penis"] = BuildClassSetting(PenisCheckBox, PenisConfSlider),
            ["testicles"] = BuildClassSetting(TesticlesCheckBox, TesticlesConfSlider),
            ["anus"] = BuildClassSetting(AnusCheckBox, AnusConfSlider),
            ["nipples"] = BuildClassSetting(NipplesCheckBox, NipplesConfSlider),
            ["breast"] = BuildClassSetting(BreastCheckBox, BreastConfSlider),
        };
    }

    private string BuildPreviewCacheKey()
    {
        return BuildPreviewCacheKey(
            _selectedPreviewSourcePath,
            _selectedModelPath,
            BuildPreviewParams(),
            BuildClassSettings()
        );
    }

    private static string BuildPreviewCacheKey(
        string? imagePath,
        string? modelPath,
        Dictionary<string, object> parameters,
        Dictionary<string, Dictionary<string, object>> classSettings)
    {
        return string.Join(
            "|",
            imagePath ?? "",
            modelPath ?? "",
            parameters["mask_type"],
            parameters["shape_type"],
            parameters["imgsz"],
            parameters["strength"],
            parameters["margin"],
            parameters["show_boxes"],
            SerializeClassSettingsKey(classSettings)
        );
    }

    private static string BuildDetectionCacheKey(
        string? imagePath,
        string? modelPath,
        Dictionary<string, object> parameters,
        Dictionary<string, Dictionary<string, object>> classSettings)
    {
        return string.Join(
            "|",
            imagePath ?? "",
            modelPath ?? "",
            parameters["imgsz"],
            SerializeClassSettingsKey(classSettings)
        );
    }

    private void SchedulePrefetch(int requestVersion)
    {
        _scheduledPrefetchVersion = requestVersion;
        _prefetchTimer.Stop();
        _prefetchTimer.Start();
    }

    private void CancelPrefetch()
    {
        _scheduledPrefetchVersion = -1;
        _prefetchTimer.Stop();
    }

    private async Task PrefetchNextPreviewIfIdleAsync(int requestVersion)
    {
        if (requestVersion != _previewRequestVersion || _currentImageIndex < 0 || _inputImagePaths.Count <= 1)
        {
            return;
        }

        var nextImagePath = FindNextPrefetchImagePath();
        if (nextImagePath is null)
        {
            return;
        }

        var previewParams = BuildPreviewParams();
        var classSettings = BuildClassSettings();
        var detectionCacheKey = BuildDetectionCacheKey(
            nextImagePath,
            _selectedModelPath,
            previewParams,
            classSettings
        );

        if (_previewMetadataCache.ContainsKey(detectionCacheKey))
        {
            SchedulePrefetch(requestVersion);
            return;
        }

            var detectionResult = await _pythonBridgeService.RunPreviewDetectionAsync(
                new PreviewDetectionRequest
                {
                    ImagePath = nextImagePath,
                    ModelPath = _selectedModelPath,
                    Params = previewParams,
                    ClassSettings = classSettings,
                },
                useBackgroundWorker: true
            );

        if (requestVersion != _previewRequestVersion)
        {
            return;
        }

        if (detectionResult.Ok && detectionResult.Response is not null)
        {
            CachePreviewMetadata(detectionCacheKey, detectionResult.Response);
        }

        SchedulePrefetch(requestVersion);
    }

    private string? FindNextPrefetchImagePath()
    {
        if (_currentImageIndex < 0 || _inputImagePaths.Count == 0)
        {
            return null;
        }

        var orderedIndexes = Enumerable
            .Range(0, _inputImagePaths.Count)
            .Where(index => index != _currentImageIndex)
            .OrderBy(index => Math.Abs(index - _currentImageIndex))
            .ThenBy(index => index);

        foreach (var neighborIndex in orderedIndexes)
        {
            var imagePath = _inputImagePaths[neighborIndex];
            var cacheKey = BuildDetectionCacheKey(
                imagePath,
                _selectedModelPath,
                BuildPreviewParams(),
                BuildClassSettings()
            );
            if (_previewMetadataCache.ContainsKey(cacheKey))
            {
                continue;
            }

            return imagePath;
        }

        return null;
    }

    private string BuildPreviewCacheKeyFor(string imagePath)
    {
        var parameters = BuildPreviewParams();
        var classSettings = BuildClassSettings();
        return string.Join(
            "|",
            imagePath,
            _selectedModelPath ?? "",
            parameters["mask_type"],
            parameters["shape_type"],
            parameters["imgsz"],
            parameters["strength"],
            parameters["margin"],
            parameters["show_boxes"],
            SerializeClassSettingsKey(classSettings)
        );
    }

    private async Task WarmupUpcomingPreviewDataAsync(int requestVersion)
    {
        CancelBackgroundWarmup();
        var cancellationTokenSource = new CancellationTokenSource();
        _backgroundWarmupCts = cancellationTokenSource;
        var cancellationToken = cancellationTokenSource.Token;

        if (requestVersion != _previewRequestVersion || _currentImageIndex < 0 || _inputImagePaths.Count == 0)
        {
            return;
        }

        try
        {
            await Task.Delay(250, cancellationToken);

            var previewParams = BuildPreviewParams();
            var classSettings = BuildClassSettings();
            var orderedImagePaths = GetWarmupImagePaths(_currentImageIndex);

            var warmedMetadata = 0;
            foreach (var imagePath in orderedImagePaths)
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (requestVersion != _previewRequestVersion || warmedMetadata >= InitialWarmupMetadataCount)
                {
                    break;
                }

                var detectionCacheKey = BuildDetectionCacheKey(
                    imagePath,
                    _selectedModelPath,
                    previewParams,
                    classSettings
                );
                if (_previewMetadataCache.ContainsKey(detectionCacheKey))
                {
                    continue;
                }

                var detectionResult = await _pythonBridgeService.RunPreviewDetectionAsync(
                    new PreviewDetectionRequest
                    {
                        ImagePath = imagePath,
                        ModelPath = _selectedModelPath,
                        Params = previewParams,
                        ClassSettings = classSettings,
                    },
                    cancellationToken,
                    useBackgroundWorker: true
                );

                if (requestVersion != _previewRequestVersion)
                {
                    return;
                }

                if (detectionResult.Ok && detectionResult.Response is not null)
                {
                    CachePreviewMetadata(detectionCacheKey, detectionResult.Response);
                    warmedMetadata++;
                }
            }

            var warmedDecodes = 0;
            foreach (var imagePath in orderedImagePaths)
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (requestVersion != _previewRequestVersion || warmedDecodes >= InitialWarmupDecodeCount)
                {
                    break;
                }

                if (_decodedPreviewSourceCache.ContainsKey(imagePath))
                {
                    continue;
                }

                var decodedSource = await GetOrCreateDecodedPreviewSourceAsync(imagePath);
                if (requestVersion != _previewRequestVersion)
                {
                    return;
                }

                if (decodedSource is not null)
                {
                    warmedDecodes++;
                }
            }
        }
        catch (OperationCanceledException)
        {
        }
        finally
        {
            if (ReferenceEquals(_backgroundWarmupCts, cancellationTokenSource))
            {
                _backgroundWarmupCts = null;
            }
            cancellationTokenSource.Dispose();
        }
    }

    private void CancelBackgroundWarmup()
    {
        if (_backgroundWarmupCts is null)
        {
            return;
        }

        try
        {
            _backgroundWarmupCts.Cancel();
        }
        catch
        {
        }

        _backgroundWarmupCts.Dispose();
        _backgroundWarmupCts = null;
    }

    private List<string> GetWarmupImagePaths(int centerIndex)
    {
        return Enumerable
            .Range(0, _inputImagePaths.Count)
            .OrderBy(index => Math.Abs(index - centerIndex))
            .ThenBy(index => index)
            .Select(index => _inputImagePaths[index])
            .ToList();
    }

    private static string GetComboBoxTag(ComboBox comboBox, string fallback)
    {
        return comboBox.SelectedItem is ComboBoxItem item && item.Tag is string tag
            ? tag
            : fallback;
    }

    private static List<string> FindImagePaths(string folderPath)
    {
        if (string.IsNullOrWhiteSpace(folderPath) || !Directory.Exists(folderPath))
        {
            return [];
        }

        string[] supportedExtensions = [".png", ".jpg", ".jpeg", ".bmp", ".webp"];
        return Directory
            .EnumerateFiles(folderPath)
            .Where(path => supportedExtensions.Contains(Path.GetExtension(path), StringComparer.OrdinalIgnoreCase))
            .OrderBy(path => path, StringComparer.OrdinalIgnoreCase)
            .ToList();
    }

    private static void OnModelDragOver(object sender, DragEventArgs e)
    {
        e.AcceptedOperation = DataPackageOperation.Copy;
    }

    private static void OnFolderDragOver(object sender, DragEventArgs e)
    {
        e.AcceptedOperation = DataPackageOperation.Copy;
    }

    private async void OnModelDrop(object sender, DragEventArgs e)
    {
        var path = await ResolveDroppedModelPathAsync(e);
        if (path is null)
        {
            SetStatus("ドロップされた項目は .pt モデルとして使えません。");
            return;
        }

        _selectedModelPath = path;
        ModelPathText.Text = _selectedModelPath;
        SetStatus("推論モデルをドロップで更新しました。");
        _ = _pythonBridgeService.RunWarmupAsync(_selectedModelPath);
        await RequestRenderPreviewAsync();
    }

    private async void OnInputDrop(object sender, DragEventArgs e)
    {
        var folderPath = await ResolveDroppedFolderPathAsync(e);
        if (folderPath is null)
        {
            SetStatus("入力にはフォルダまたは画像ファイルをドロップしてください。");
            return;
        }

        _selectedInputFolderPath = folderPath;
        InputPathText.Text = _selectedInputFolderPath;
        await LoadInputImagesAsync(_selectedInputFolderPath, "入力フォルダをドロップで更新しました。");
    }

    private async void OnOutputDrop(object sender, DragEventArgs e)
    {
        var folderPath = await ResolveDroppedFolderPathAsync(e);
        if (folderPath is null)
        {
            SetStatus("出力にはフォルダまたは画像ファイルをドロップしてください。");
            return;
        }

        _selectedOutputFolderPath = folderPath;
        OutputPathText.Text = _selectedOutputFolderPath;
        SetStatus("出力フォルダをドロップで更新しました。");
    }

    private static async Task<string?> ResolveDroppedModelPathAsync(DragEventArgs e)
    {
        if (!e.DataView.Contains(StandardDataFormats.StorageItems))
        {
            return null;
        }

        var items = await e.DataView.GetStorageItemsAsync();
        var file = items.OfType<StorageFile>().FirstOrDefault();
        if (file is null)
        {
            return null;
        }

        return string.Equals(Path.GetExtension(file.Path), ".pt", StringComparison.OrdinalIgnoreCase)
            ? file.Path
            : null;
    }

    private static async Task<string?> ResolveDroppedFolderPathAsync(DragEventArgs e)
    {
        if (!e.DataView.Contains(StandardDataFormats.StorageItems))
        {
            return null;
        }

        var items = await e.DataView.GetStorageItemsAsync();
        var firstItem = items.FirstOrDefault();
        if (firstItem is StorageFolder folder)
        {
            return folder.Path;
        }

        if (firstItem is StorageFile file && IsSupportedImagePath(file.Path))
        {
            return Path.GetDirectoryName(file.Path);
        }

        return null;
    }

    private static bool IsSupportedImagePath(string path)
    {
        string[] supportedExtensions = [".png", ".jpg", ".jpeg", ".bmp", ".webp"];
        return supportedExtensions.Contains(Path.GetExtension(path), StringComparer.OrdinalIgnoreCase);
    }

    private void ConfigureClassSettingsEvents()
    {
        foreach (var checkBox in GetClassSettingCheckBoxes())
        {
            checkBox.Checked += (_, _) => SchedulePreviewRefresh();
            checkBox.Unchecked += (_, _) => SchedulePreviewRefresh();
        }

        foreach (var slider in GetClassSettingSliders())
        {
            slider.ValueChanged += (_, _) =>
            {
                RefreshClassConfidenceTexts();
                SchedulePreviewRefresh();
            };
        }
    }

    private IEnumerable<CheckBox> GetClassSettingCheckBoxes()
    {
        yield return PussyCheckBox;
        yield return PenisCheckBox;
        yield return TesticlesCheckBox;
        yield return AnusCheckBox;
        yield return NipplesCheckBox;
        yield return BreastCheckBox;
    }

    private IEnumerable<Slider> GetClassSettingSliders()
    {
        yield return PussyConfSlider;
        yield return PenisConfSlider;
        yield return TesticlesConfSlider;
        yield return AnusConfSlider;
        yield return NipplesConfSlider;
        yield return BreastConfSlider;
    }

    private Dictionary<string, object> BuildClassSetting(CheckBox checkBox, Slider slider)
    {
        return new Dictionary<string, object>
        {
            ["enabled"] = checkBox.IsChecked == true,
            ["conf"] = slider.Value / 100.0,
        };
    }

    private static string SerializeClassSettingsKey(Dictionary<string, Dictionary<string, object>> classSettings)
    {
        return string.Join(
            ",",
            classSettings
                .OrderBy(entry => entry.Key, StringComparer.Ordinal)
                .Select(entry =>
                    $"{entry.Key}:{entry.Value["enabled"]}:{Convert.ToDouble(entry.Value["conf"], CultureInfo.InvariantCulture).ToString("0.00", CultureInfo.InvariantCulture)}")
        );
    }

    private void RefreshClassConfidenceTexts()
    {
        PussyConfValueText.Text = FormatConfidence(PussyConfSlider);
        PenisConfValueText.Text = FormatConfidence(PenisConfSlider);
        TesticlesConfValueText.Text = FormatConfidence(TesticlesConfSlider);
        AnusConfValueText.Text = FormatConfidence(AnusConfSlider);
        NipplesConfValueText.Text = FormatConfidence(NipplesConfSlider);
        BreastConfValueText.Text = FormatConfidence(BreastConfSlider);
    }

    private static string FormatConfidence(Slider slider)
    {
        return $"{slider.Value / 100.0:0.00}";
    }

    private void ApplyBridgeHealthResponse(BridgeHealthResponse response)
    {
        if (!string.IsNullOrWhiteSpace(response.ModelPath))
        {
            _selectedModelPath = response.ModelPath;
            ModelPathText.Text = response.ModelPath;
        }

        if (response.ClassSettings is null)
        {
            return;
        }

        ApplyClassSetting(response.ClassSettings, "pussy", PussyCheckBox, PussyConfSlider);
        ApplyClassSetting(response.ClassSettings, "penis", PenisCheckBox, PenisConfSlider);
        ApplyClassSetting(response.ClassSettings, "testicles", TesticlesCheckBox, TesticlesConfSlider);
        ApplyClassSetting(response.ClassSettings, "anus", AnusCheckBox, AnusConfSlider);
        ApplyClassSetting(response.ClassSettings, "nipples", NipplesCheckBox, NipplesConfSlider);
        ApplyClassSetting(response.ClassSettings, "breast", BreastCheckBox, BreastConfSlider);
        RefreshClassConfidenceTexts();
    }

    private static void ApplyClassSetting(
        IReadOnlyDictionary<string, BridgeClassSetting> settings,
        string key,
        CheckBox checkBox,
        Slider slider)
    {
        if (!settings.TryGetValue(key, out var classSetting))
        {
            return;
        }

        checkBox.IsChecked = classSetting.Enabled;
        slider.Value = Math.Clamp(classSetting.Conf * 100.0, slider.Minimum, slider.Maximum);
    }

    private void CachePreviewBitmap(string cacheKey, ImageSource bitmap)
    {
        if (_previewBitmapCache.ContainsKey(cacheKey))
        {
            _previewBitmapCache[cacheKey] = bitmap;
            return;
        }

        _previewBitmapCache[cacheKey] = bitmap;
        _previewBitmapCacheOrder.Enqueue(cacheKey);

        while (_previewBitmapCacheOrder.Count > MaxPreviewBitmapCacheCount)
        {
            var oldestKey = _previewBitmapCacheOrder.Dequeue();
            _previewBitmapCache.Remove(oldestKey);
        }
    }

    private void CachePreviewMetadata(string cacheKey, BridgePreviewMetadataResponse metadata)
    {
        if (_previewMetadataCache.ContainsKey(cacheKey))
        {
            _previewMetadataCache[cacheKey] = metadata;
            return;
        }

        _previewMetadataCache[cacheKey] = metadata;
        _previewMetadataCacheOrder.Enqueue(cacheKey);

        while (_previewMetadataCacheOrder.Count > MaxPreviewMetadataCacheCount)
        {
            var oldestKey = _previewMetadataCacheOrder.Dequeue();
            _previewMetadataCache.Remove(oldestKey);
        }
    }

    private void CacheDecodedPreviewSource(string imagePath, DecodedPreviewSource decodedSource)
    {
        if (_decodedPreviewSourceCache.ContainsKey(imagePath))
        {
            _decodedPreviewSourceCache[imagePath] = decodedSource;
            return;
        }

        _decodedPreviewSourceCache[imagePath] = decodedSource;
        _decodedPreviewSourceCacheOrder.Enqueue(imagePath);

        while (_decodedPreviewSourceCacheOrder.Count > MaxDecodedSourceCacheCount)
        {
            var oldestKey = _decodedPreviewSourceCacheOrder.Dequeue();
            _decodedPreviewSourceCache.Remove(oldestKey);
        }
    }
}

internal sealed record DecodedPreviewSource(int PixelWidth, int PixelHeight, byte[] Pixels);
internal sealed record ImageListEntry(string ImagePath, ListViewItem Item, Image ThumbnailImage);

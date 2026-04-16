using System.Collections.Generic;
using System.Diagnostics;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading;

namespace MosaicRemake.WinUI.Services;

public sealed class PythonBridgeService : IDisposable
{
    private static readonly JsonSerializerOptions RequestJsonOptions = new()
    {
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        WriteIndented = false,
    };

    private readonly WorkerChannel _foregroundWorker = new("foreground");
    private readonly WorkerChannel _backgroundWorker = new("background");

    public string? BridgeScriptPath => FindBridgeScriptPath("bridge_cli.py");
    public string? BridgeWorkerScriptPath => FindBridgeScriptPath("bridge_worker.py");

    public bool CanLocateBridge()
    {
        return BridgeScriptPath is not null;
    }

    public async Task<(bool Ok, string Message, BridgeHealthResponse? Response)> RunHealthAsync(CancellationToken cancellationToken = default)
    {
        var workerResult = await RunWorkerCommandAsync(
            "health",
            new Dictionary<string, object?>(),
            cancellationToken,
            useBackgroundWorker: false
        );
        if (workerResult.Ok)
        {
            return ParseHealthResponse(workerResult.Message);
        }

        var bridgeScriptPath = BridgeScriptPath;
        if (bridgeScriptPath is null)
        {
            return (false, "Python bridge が見つかりません。`mosaic-remake\\bridge_cli.py` の位置を確認してください。", null);
        }

        var cliResult = await RunPythonCliAsync(
            $"\"{bridgeScriptPath}\" health",
            cancellationToken
        );
        if (!cliResult.Ok)
        {
            return (false, cliResult.Message, null);
        }

        return ParseHealthResponse(cliResult.Message);
    }

    public async Task<(bool Ok, string Message)> RunWarmupAsync(string? modelPath, CancellationToken cancellationToken = default)
    {
        var workerPayload = new Dictionary<string, object?>
        {
            ["request"] = new Dictionary<string, object?>
            {
                ["model_path"] = modelPath,
            },
        };
        var workerResult = await RunWorkerCommandAsync("warmup", workerPayload, cancellationToken, useBackgroundWorker: false);
        if (workerResult.Ok)
        {
            return ParseWarmupResponse(workerResult.Message);
        }

        return (false, workerResult.Message);
    }

    public async Task<(bool Ok, string Message, BridgePreviewMetadataResponse? Response)> RunPreviewDetectionAsync(
        PreviewDetectionRequest request,
        CancellationToken cancellationToken = default,
        bool useBackgroundWorker = false
    )
    {
        var workerPayload = new Dictionary<string, object?>
        {
            ["request"] = request,
        };
        var workerResult = await RunWorkerCommandAsync("detect_preview", workerPayload, cancellationToken, useBackgroundWorker);
        if (!workerResult.Ok)
        {
            return (false, workerResult.Message, null);
        }

        return ParsePreviewDetectionResponse(workerResult.Message);
    }

    public async Task<(bool Ok, string Message, string? PreviewPath, int CandidateCount)> RunPreviewAsync(
        PreviewRequest request,
        CancellationToken cancellationToken = default
    )
    {
        var workerPayload = new Dictionary<string, object?>
        {
            ["request"] = request,
        };
        var workerResult = await RunWorkerCommandAsync("preview", workerPayload, cancellationToken, useBackgroundWorker: false);
        if (workerResult.Ok)
        {
            return ParsePreviewResponse(workerResult.Message);
        }

        var bridgeScriptPath = BridgeScriptPath;
        if (bridgeScriptPath is null)
        {
            return (false, "Python bridge が見つかりません。`mosaic-remake\\bridge_cli.py` の位置を確認してください。", null, 0);
        }

        var requestPath = Path.Combine(Path.GetTempPath(), $"mosaic-remake-preview-{Guid.NewGuid():N}.json");
        var previewPath = request.OutputPreviewPath;

        try
        {
            await File.WriteAllTextAsync(
                requestPath,
                JsonSerializer.Serialize(request, RequestJsonOptions),
                Encoding.UTF8,
                cancellationToken
            );

            var cliResult = await RunPythonCliAsync(
                $"\"{bridgeScriptPath}\" preview --request \"{requestPath}\"",
                cancellationToken
            );

            if (!cliResult.Ok)
            {
                return (false, cliResult.Message, null, 0);
            }

            return ParsePreviewResponse(cliResult.Message);
        }
        catch (Exception ex)
        {
            return (false, $"preview 呼び出しに失敗しました: {ex.Message}", null, 0);
        }
        finally
        {
            TryDeleteFile(requestPath);
            if (!string.IsNullOrWhiteSpace(previewPath) && !File.Exists(previewPath))
            {
                TryDeleteFile(previewPath);
            }
        }
    }

    private (bool Ok, string Message, BridgeHealthResponse? Response) ParseHealthResponse(string message)
    {
        try
        {
            using var document = JsonDocument.Parse(message);
            var root = document.RootElement;
            var modelLoaded = root.GetProperty("model_loaded").GetBoolean();
            var modelPath = root.GetProperty("model_path").GetString() ?? "";
            var classNames = root.GetProperty("class_names");
            var response = JsonSerializer.Deserialize<BridgeHealthResponse>(message);

            return (
                true,
                $"bridge 接続成功 / model_loaded={modelLoaded} / class_count={classNames.GetRawText()} / model_path={modelPath}"
                , response
            );
        }
        catch (Exception ex)
        {
            return (false, $"bridge の応答解析に失敗しました: {ex.Message}", null);
        }
    }

    private (bool Ok, string Message) ParseWarmupResponse(string message)
    {
        try
        {
            using var document = JsonDocument.Parse(message);
            var root = document.RootElement;
            if (!root.TryGetProperty("ok", out var okElement) || !okElement.GetBoolean())
            {
                var error = root.TryGetProperty("error", out var errorElement)
                    ? errorElement.GetString()
                    : "warmup failed";
                return (false, $"warmup 実行失敗: {error}");
            }

            return (true, "warmup 完了");
        }
        catch (Exception ex)
        {
            return (false, $"warmup の応答解析に失敗しました: {ex.Message}");
        }
    }

    private (bool Ok, string Message, string? PreviewPath, int CandidateCount) ParsePreviewResponse(string message)
    {
        try
        {
            using var document = JsonDocument.Parse(message);
            var root = document.RootElement;
            if (!root.TryGetProperty("ok", out var okElement) || !okElement.GetBoolean())
            {
                var error = root.TryGetProperty("error", out var errorElement)
                    ? errorElement.GetString()
                    : "preview failed";
                return (false, $"preview 実行失敗: {error}", null, 0);
            }

            var resolvedPreviewPath = root.GetProperty("preview_path").GetString();
            var candidateCount = root.TryGetProperty("candidate_count", out var countElement)
                ? countElement.GetInt32()
                : 0;

            return (
                true,
                $"preview 生成成功 / candidate_count={candidateCount}",
                resolvedPreviewPath,
                candidateCount
            );
        }
        catch (Exception ex)
        {
            return (false, $"preview の応答解析に失敗しました: {ex.Message}", null, 0);
        }
    }

    private (bool Ok, string Message, BridgePreviewMetadataResponse? Response) ParsePreviewDetectionResponse(string message)
    {
        try
        {
            using var document = JsonDocument.Parse(message);
            var root = document.RootElement;
            if (!root.TryGetProperty("ok", out var okElement) || !okElement.GetBoolean())
            {
                var error = root.TryGetProperty("error", out var errorElement)
                    ? errorElement.GetString()
                    : "detect preview failed";
                return (false, $"候補取得に失敗しました: {error}", null);
            }

            var response = JsonSerializer.Deserialize<BridgePreviewMetadataResponse>(message);
            return response is null
                ? (false, "候補取得結果の解析に失敗しました。", null)
                : (true, $"候補取得成功 / candidate_count={response.CandidateCount}", response);
        }
        catch (Exception ex)
        {
            return (false, $"候補取得結果の応答解析に失敗しました: {ex.Message}", null);
        }
    }

    private async Task<(bool Ok, string Message)> RunWorkerCommandAsync(
        string command,
        IDictionary<string, object?> payload,
        CancellationToken cancellationToken,
        bool useBackgroundWorker
    )
    {
        var worker = useBackgroundWorker ? _backgroundWorker : _foregroundWorker;
        await worker.Lock.WaitAsync(cancellationToken);
        try
        {
            var workerReady = await EnsureWorkerAsync(worker, cancellationToken);
            if (!workerReady.Ok)
            {
                return workerReady;
            }

            if (worker.Input is null || worker.Output is null)
            {
                return (false, "Python worker の入出力を確立できませんでした。");
            }

            var envelope = new Dictionary<string, object?>(payload)
            {
                ["command"] = command,
            };
            var line = JsonSerializer.Serialize(envelope, RequestJsonOptions);
            await worker.Input.WriteLineAsync(line);
            await worker.Input.FlushAsync();

            var responseLine = await worker.Output.ReadLineAsync(cancellationToken);
            if (string.IsNullOrWhiteSpace(responseLine))
            {
                return (false, $"Python worker から応答がありません。stderr={worker.ErrorLog}");
            }

            return (true, responseLine);
        }
        catch (Exception ex)
        {
            return (false, $"Python worker 実行失敗: {ex.Message}");
        }
        finally
        {
            worker.Lock.Release();
        }
    }

    private async Task<(bool Ok, string Message)> EnsureWorkerAsync(WorkerChannel worker, CancellationToken cancellationToken)
    {
        if (worker.Process is { HasExited: false } && worker.Input is not null && worker.Output is not null)
        {
            return (true, "worker ready");
        }

        CleanupWorker(worker);

        var workerScriptPath = BridgeWorkerScriptPath;
        if (workerScriptPath is null)
        {
            return (false, "Python worker が見つかりません。`mosaic-remake\\bridge_worker.py` の位置を確認してください。");
        }

        var startInfo = new ProcessStartInfo
        {
            FileName = "python",
            Arguments = $"\"{workerScriptPath}\"",
            RedirectStandardInput = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true,
            StandardInputEncoding = Encoding.UTF8,
            StandardOutputEncoding = Encoding.UTF8,
            StandardErrorEncoding = Encoding.UTF8,
        };

        var process = new Process { StartInfo = startInfo, EnableRaisingEvents = true };
        process.ErrorDataReceived += (_, args) =>
        {
            if (!string.IsNullOrWhiteSpace(args.Data))
            {
                lock (worker.ErrorLog)
                {
                    worker.ErrorLog.AppendLine(args.Data);
                }
            }
        };

        process.Start();
        process.BeginErrorReadLine();

        worker.Process = process;
        worker.Input = process.StandardInput;
        worker.Output = process.StandardOutput;

        var healthResult = await RunWorkerStartupHealthCheckAsync(worker, cancellationToken);
        if (!healthResult.Ok)
        {
            CleanupWorker(worker);
            return healthResult;
        }

        return (true, "worker ready");
    }

    private async Task<(bool Ok, string Message)> RunWorkerStartupHealthCheckAsync(WorkerChannel worker, CancellationToken cancellationToken)
    {
        if (worker.Input is null || worker.Output is null)
        {
            return (false, "worker の入出力が未初期化です。");
        }

        var line = JsonSerializer.Serialize(new Dictionary<string, object> { ["command"] = "health" }, RequestJsonOptions);
        await worker.Input.WriteLineAsync(line);
        await worker.Input.FlushAsync();

        var responseLine = await worker.Output.ReadLineAsync(cancellationToken);
        if (string.IsNullOrWhiteSpace(responseLine))
        {
            return (false, $"worker 起動直後の health 応答がありません。stderr={worker.ErrorLog}");
        }

        try
        {
            using var document = JsonDocument.Parse(responseLine);
            return document.RootElement.TryGetProperty("ok", out var okElement) && okElement.GetBoolean()
                ? (true, "worker health ok")
                : (false, responseLine);
        }
        catch
        {
            return (false, responseLine);
        }
    }

    private async Task<(bool Ok, string Message)> RunPythonCliAsync(
        string arguments,
        CancellationToken cancellationToken
    )
    {
        var startInfo = new ProcessStartInfo
        {
            FileName = "python",
            Arguments = arguments,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true,
            StandardOutputEncoding = Encoding.UTF8,
            StandardErrorEncoding = Encoding.UTF8,
        };

        using var process = new Process { StartInfo = startInfo };
        process.Start();

        var stdoutTask = process.StandardOutput.ReadToEndAsync(cancellationToken);
        var stderrTask = process.StandardError.ReadToEndAsync(cancellationToken);
        await process.WaitForExitAsync(cancellationToken);

        var stdout = await stdoutTask;
        var stderr = await stderrTask;

        if (process.ExitCode != 0)
        {
            var message = string.IsNullOrWhiteSpace(stderr) ? stdout : stderr;
            return (false, $"python bridge 実行失敗: {message.Trim()}");
        }

        return (true, stdout.Trim());
    }

    private string? FindBridgeScriptPath(string filename)
    {
        var baseDirectory = AppContext.BaseDirectory;
        var current = new DirectoryInfo(baseDirectory);

        for (var depth = 0; depth < 8 && current is not null; depth++)
        {
            var siblingPath = Path.Combine(current.FullName, "mosaic-remake", filename);
            if (File.Exists(siblingPath))
            {
                return siblingPath;
            }

            var nestedPath = Path.Combine(current.FullName, "projects", "mosaic-remake", filename);
            if (File.Exists(nestedPath))
            {
                return nestedPath;
            }

            current = current.Parent;
        }

        return null;
    }

    private void CleanupWorker(WorkerChannel worker)
    {
        try
        {
            worker.Input?.Dispose();
        }
        catch
        {
        }

        try
        {
            if (worker.Process is { HasExited: false })
            {
                worker.Process.Kill(true);
            }
        }
        catch
        {
        }

        try
        {
            worker.Process?.Dispose();
        }
        catch
        {
        }

        worker.Process = null;
        worker.Input = null;
        worker.Output = null;
        lock (worker.ErrorLog)
        {
            worker.ErrorLog.Clear();
        }
    }

    private static void TryDeleteFile(string? path)
    {
        if (string.IsNullOrWhiteSpace(path) || !File.Exists(path))
        {
            return;
        }

        try
        {
            File.Delete(path);
        }
        catch
        {
        }
    }

    public void Dispose()
    {
        CleanupWorker(_foregroundWorker);
        CleanupWorker(_backgroundWorker);
        _foregroundWorker.Lock.Dispose();
        _backgroundWorker.Lock.Dispose();
    }
}

internal sealed class WorkerChannel(string name)
{
    public string Name { get; } = name;
    public SemaphoreSlim Lock { get; } = new(1, 1);
    public StringBuilder ErrorLog { get; } = new();
    public Process? Process { get; set; }
    public StreamWriter? Input { get; set; }
    public StreamReader? Output { get; set; }
}

public sealed class PreviewRequest
{
    [JsonPropertyName("image_path")]
    public string ImagePath { get; init; } = "";

    [JsonPropertyName("output_preview_path")]
    public string OutputPreviewPath { get; init; } = "";

    [JsonPropertyName("model_path")]
    public string? ModelPath { get; init; }

    [JsonPropertyName("params")]
    public Dictionary<string, object>? Params { get; init; }

    [JsonPropertyName("class_settings")]
    public Dictionary<string, Dictionary<string, object>>? ClassSettings { get; init; }
}

public sealed class PreviewDetectionRequest
{
    [JsonPropertyName("image_path")]
    public string ImagePath { get; init; } = "";

    [JsonPropertyName("model_path")]
    public string? ModelPath { get; init; }

    [JsonPropertyName("params")]
    public Dictionary<string, object>? Params { get; init; }

    [JsonPropertyName("class_settings")]
    public Dictionary<string, Dictionary<string, object>>? ClassSettings { get; init; }
}

public sealed class BridgeHealthResponse
{
    [JsonPropertyName("model_path")]
    public string? ModelPath { get; init; }

    [JsonPropertyName("model_loaded")]
    public bool ModelLoaded { get; init; }

    [JsonPropertyName("class_settings")]
    public Dictionary<string, BridgeClassSetting>? ClassSettings { get; init; }
}

public sealed class BridgeClassSetting
{
    [JsonPropertyName("enabled")]
    public bool Enabled { get; init; }

    [JsonPropertyName("conf")]
    public double Conf { get; init; }
}

public sealed class BridgePreviewMetadataResponse
{
    [JsonPropertyName("candidate_count")]
    public int CandidateCount { get; init; }

    [JsonPropertyName("image_width")]
    public int ImageWidth { get; init; }

    [JsonPropertyName("image_height")]
    public int ImageHeight { get; init; }

    [JsonPropertyName("candidates")]
    public List<BridgePreviewCandidate>? Candidates { get; init; }
}

public sealed class BridgePreviewCandidate
{
    [JsonPropertyName("cls")]
    public string ClassId { get; init; } = "";

    [JsonPropertyName("conf")]
    public double Confidence { get; init; }

    [JsonPropertyName("xyxy")]
    public List<double>? Xyxy { get; init; }
}

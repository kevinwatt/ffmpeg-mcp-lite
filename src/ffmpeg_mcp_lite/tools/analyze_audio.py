"""Analyze audio dynamics/structure (loudness, energy envelope, spectrogram)."""

import asyncio
import re
from pathlib import Path
from typing import Optional

from ..config import config


async def _run(cmd: list[str]) -> tuple[Optional[int], bytes, bytes]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return proc.returncode, stdout, stderr


def _ffprobe_kv(text: str) -> dict[str, str]:
    """Parse ffprobe 'default=noprint_wrappers=1' output into a key/value dict."""
    result: dict[str, str] = {}
    for line in text.splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip()
    return result


def _last_tagged_value(text: str, label: str) -> Optional[str]:
    """Last '<label>: value' match where label starts the (trimmed) line.

    Matches the ebur128 Summary block (e.g. "    I:    -23.4 LUFS") while
    skipping per-frame log lines, which carry a "[Parsed_ebur128 @ ...]" prefix.
    """
    matches = re.findall(rf"^[ \t]*{label}:\s*(.+?)\s*$", text, re.MULTILINE)
    return matches[-1] if matches else None


def _last_astat(text: str, label: str) -> Optional[str]:
    """Last astats line containing label; value is everything after the final colon."""
    lines = [line for line in text.splitlines() if label.lower() in line.lower()]
    if not lines:
        return None
    return lines[-1].rsplit(":", 1)[-1].strip()


async def ffmpeg_analyze_audio(file_path: str, output_dir: Optional[str] = None) -> str:
    """Analyze audio dynamics/structure to judge build/drop vs. a flat loop.

    Runs EBU R128 loudness analysis, astats, an RMS energy envelope (the
    "shape" of the track over time), and renders a spectrogram + waveform
    image. Useful for judging whether a track is genuinely dynamic
    (build + drop) or a flat/repetitive vamp.

    Args:
        file_path: Path to the input audio (or video) file
        output_dir: Directory to write analysis artifacts to (default: "{output}/{stem}_analysis")

    Returns:
        Human-readable analysis report (also written to summary.txt in the output dir,
        alongside ebur128.log, astats.log, energy-envelope.csv, spectrogram.png, waveform.png)
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    outdir = (
        Path(output_dir).expanduser().resolve()
        if output_dir
        else config.ensure_output_dir() / f"{path.stem}_analysis"
    )
    outdir.mkdir(parents=True, exist_ok=True)

    ebur_log = outdir / "ebur128.log"
    astats_log = outdir / "astats.log"
    env_raw = outdir / ".energy-raw.txt"
    env_csv = outdir / "energy-envelope.csv"
    spectro = outdir / "spectrogram.png"
    wave = outdir / "waveform.png"
    summary_path = outdir / "summary.txt"

    # 1. Container / stream facts
    _, fmt_out, _ = await _run([
        config.ffprobe_path, "-v", "error",
        "-show_entries", "format=duration,bit_rate",
        "-of", "default=noprint_wrappers=1",
        str(path),
    ])
    fmt_info = _ffprobe_kv(fmt_out.decode(errors="replace"))
    duration = fmt_info.get("duration", "?")
    bitrate = fmt_info.get("bit_rate", "?")

    _, stream_out, _ = await _run([
        config.ffprobe_path, "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=sample_rate,channels",
        "-of", "default=noprint_wrappers=1",
        str(path),
    ])
    stream_info = _ffprobe_kv(stream_out.decode(errors="replace"))
    sample_rate = stream_info.get("sample_rate", "?")
    channels = stream_info.get("channels", "?")

    # 2. EBU R128 loudness (Integrated, LRA, True Peak)
    _, _, ebur_err = await _run([
        config.ffmpeg_path, "-hide_banner", "-nostats",
        "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-",
    ])
    ebur_text = ebur_err.decode(errors="replace")
    ebur_log.write_text(ebur_text)

    integrated = _last_tagged_value(ebur_text, "I")
    lra = _last_tagged_value(ebur_text, "LRA")
    true_peak = _last_tagged_value(ebur_text, "Peak")
    lra_num: Optional[float] = None
    if lra:
        match = re.match(r"[-0-9.]+", lra)
        if match:
            lra_num = float(match.group())

    # 3. astats overall (RMS, peak, crest/dynamic range, flatness)
    _, _, astats_err = await _run([
        config.ffmpeg_path, "-hide_banner", "-nostats",
        "-i", str(path), "-af", "astats=measure_perchannel=none", "-f", "null", "-",
    ])
    astats_text = astats_err.decode(errors="replace")
    astats_log.write_text(astats_text)

    rms_level = _last_astat(astats_text, "RMS level dB")
    peak_level = _last_astat(astats_text, "Peak level dB")
    dyn_range = _last_astat(astats_text, "Dynamic range")
    crest = _last_astat(astats_text, "Crest factor")
    flat = _last_astat(astats_text, "Flat factor")

    # 4. Energy envelope: RMS per 0.5s window -> CSV (the "shape" of the track)
    await _run([
        config.ffmpeg_path, "-hide_banner", "-nostats",
        "-i", str(path),
        "-af",
        "aresample=44100,asetnsamples=n=22050:p=0,astats=metadata=1:reset=1,"
        f"ametadata=print:key=lavfi.astats.Overall.RMS_level:file={env_raw}",
        "-f", "null", "-",
    ])

    envelope: list[tuple[float, float]] = []
    if env_raw.exists():
        current_t: Optional[float] = None
        for line in env_raw.read_text(errors="replace").splitlines():
            t_match = re.search(r"pts_time:\s*([0-9.]+)", line)
            if t_match:
                current_t = float(t_match.group(1))
                continue
            v_match = re.search(r"RMS_level=(-?inf|-?[0-9.]+)", line)
            if v_match and current_t is not None and v_match.group(1) != "-inf":
                envelope.append((current_t, float(v_match.group(1))))
        env_raw.unlink()

    env_csv.write_text(
        "time_s,rms_db\n" + "\n".join(f"{t:.2f},{v}" for t, v in envelope) + ("\n" if envelope else "")
    )

    # Variety signal computed over "active" windows only (RMS > -60 dB) so a
    # near-silent intro/outro fade doesn't masquerade as dynamics. sd of the
    # energy envelope is the signal: a flat loop has low sd; a track with
    # distinct build/drop sections has high sd.
    active = [v for _, v in envelope if v > -60]
    if active:
        n = len(active)
        mean = sum(active) / n
        sd = (sum(v * v for v in active) / n - mean * mean) ** 0.5
        env_min, env_max = min(active), max(active)
        variety = (
            "varied (distinct sections)" if sd >= 8
            else "some variation" if sd >= 4
            else "flat / repetitive"
        )
        env_stats = (
            f'windows={len(envelope)} active={n} min={env_min:.1f} max={env_max:.1f} '
            f'range={env_max - env_min:.1f} mean={mean:.1f} sd={sd:.1f} variety="{variety}"'
        )
    else:
        env_stats = "windows=0 active=0 variety=unknown"

    # 5. Spectrogram + waveform images
    spectro_rc, _, _ = await _run([
        config.ffmpeg_path, "-hide_banner", "-y",
        "-i", str(path), "-lavfi", "showspectrumpic=s=1280x480:legend=1",
        str(spectro),
    ])
    spectro_result = str(spectro) if spectro_rc == 0 else "(spectrogram failed)"

    wave_rc, _, _ = await _run([
        config.ffmpeg_path, "-hide_banner", "-y",
        "-i", str(path), "-filter_complex", "showwavespic=s=1280x240:colors=#3b82f6",
        str(wave),
    ])
    wave_result = str(wave) if wave_rc == 0 else "(waveform failed)"

    # 6. Verdict
    if lra_num is None:
        verdict = "unknown (LRA not parsed)"
    elif lra_num >= 8:
        verdict = f"DYNAMIC — strong build/drop (LRA {lra_num} LU)"
    elif lra_num >= 5:
        verdict = f"MODERATE — some movement (LRA {lra_num} LU)"
    else:
        verdict = f"FLAT — likely a loop/vamp (LRA {lra_num} LU)"

    # 7. Assemble + persist summary
    summary = f"""=== Audio analysis: {path} ===

-- Format --
duration_sec : {duration}
sample_rate  : {sample_rate}
channels     : {channels}
bit_rate     : {bitrate}

-- Loudness (EBU R128) --
integrated   : {integrated or "n/a"}
loudness_range (LRA) : {lra or "n/a"}   <- main dynamics metric; <5 flat, 8+ dynamic
true_peak    : {true_peak or "n/a"}

-- Overall (astats) --
rms_level_db : {rms_level or "n/a"}
peak_level_db: {peak_level or "n/a"}
dynamic_range: {dyn_range or "n/a"}
crest_factor : {crest or "n/a"}
flat_factor  : {flat or "n/a"}   <- high = sustained/flat

-- Energy envelope (0.5s windows) --
{env_stats}
csv          : {env_csv}
  (sd over active windows is the variety signal; sd<4 flat, 8+ varied. Near-silent fades excluded.)

-- Images --
spectrogram  : {spectro_result}
waveform     : {wave_result}

-- Verdict --
{verdict}

-- Raw logs --
ebur128.log  : {ebur_log}
astats.log   : {astats_log}
"""

    summary_path.write_text(summary)
    return summary

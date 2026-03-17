"""Tests for audioforge.core.ffmpeg progress parsing."""

from audioforge.core.ffmpeg import parse_progress


class TestParseProgress:
    def test_typical_line(self):
        line = "frame=    0 fps=0.0 q=-1.0 size=   256kB time=00:01:30.50 bitrate= 128.0kbits/s speed=5.2x"
        result = parse_progress(line, total_duration_ms=300_000)  # 5 minutes
        assert result is not None
        # 90.5 seconds = 90500ms out of 300000ms = ~30.17%
        assert abs(result - 30.17) < 0.1

    def test_zero_time(self):
        line = "size=       0kB time=00:00:00.00 bitrate=N/A speed=N/A"
        result = parse_progress(line, total_duration_ms=60_000)
        assert result == 0.0

    def test_near_end(self):
        line = "size=   1024kB time=00:04:59.90 bitrate= 128.0kbits/s speed=10x"
        result = parse_progress(line, total_duration_ms=300_000)  # 5 minutes
        assert result is not None
        assert result > 99.0
        assert result <= 100.0

    def test_exceeds_total_capped_at_100(self):
        line = "size=   2048kB time=00:06:00.00 bitrate= 128.0kbits/s"
        result = parse_progress(line, total_duration_ms=300_000)
        assert result == 100.0

    def test_no_time_in_line(self):
        line = "  Duration: 00:05:00.00, start: 0.000000, bitrate: 128 kb/s"
        result = parse_progress(line, total_duration_ms=300_000)
        assert result is None

    def test_empty_line(self):
        assert parse_progress("", total_duration_ms=300_000) is None

    def test_zero_total_duration(self):
        line = "size=   256kB time=00:01:00.00 bitrate= 128.0kbits/s"
        result = parse_progress(line, total_duration_ms=0)
        assert result == 0.0

    def test_hours_in_time(self):
        line = "size=   4096kB time=01:30:00.00 bitrate= 128.0kbits/s"
        result = parse_progress(line, total_duration_ms=7_200_000)  # 2 hours
        # 1h30m = 5400s = 5400000ms, out of 7200000ms = 75%
        assert result is not None
        assert abs(result - 75.0) < 0.1

    def test_fractional_seconds(self):
        line = "size=   128kB time=00:00:30.123 bitrate= 128.0kbits/s"
        result = parse_progress(line, total_duration_ms=60_000)
        assert result is not None
        # 30.123s = 30123ms out of 60000ms = ~50.2%
        assert abs(result - 50.2) < 0.1

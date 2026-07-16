"""Client-side local cache for Big QMT market data.

Pull bars from Big QMT once over RPC, persist them on the client, then read them
back with ``get_local_data`` without touching Big QMT again — for offline / local
analysis. One file per (period, dividend_type, code); incremental merge + dedupe
by time. Default storage is Parquet (columnar, compressed, cross-language); falls
back to pickle when pyarrow is unavailable. A cache written in one format is read
+ migrated transparently if the configured format changes.
"""

import os


# Candidate time-column names produced by the RPC market-data path.
_TIME_COLS = ("stime", "time", "index", "date", "datetime", "timetag")


def _time_col(df):
    """timecol。
    
    Args:
        df: df
    
    Returns:
         — 处理结果。
    """
    cols = list(getattr(df, "columns", []))
    for name in _TIME_COLS:
        if name in cols:
            return name
    return None


def _pad_end(value):
    """padend。
    
    Args:
        value: 值
    
    Returns:
         — 处理结果。
    """
    text = str(value)
    return text + "9" * (14 - len(text)) if 0 < len(text) < 14 else text


def _drop_placeholder_rows(df):
    """Big QMT fills dates it has no local data for with all-zero rows. A real bar
    never has close/open == 0, so drop those placeholders — the cache should hold
    only real bars, not 0-fill padding."""
    for col in ("close", "open", "price", "lastPrice"):
        if col in getattr(df, "columns", []):
            try:
                return df[df[col] != 0].reset_index(drop=True)
            except Exception:
                return df
    return df


def _pyarrow_available():
    """pyarrowavailable。
    
    Returns:
         — 处理结果。
    """
    try:
        import pyarrow  # noqa: F401

        return True
    except Exception:
        return False


def _resolve_format(fmt):
    """resolveformat。
    
    Args:
        fmt: fmt
    
    Returns:
         — 处理结果。
    """
    fmt = str(fmt or "auto").lower()
    if fmt in ("parquet", "pq"):
        return "parquet"
    if fmt in ("pkl", "pickle"):
        return "pkl"
    # auto / unknown
    return "parquet" if _pyarrow_available() else "pkl"


class LocalMarketCache:
    """LocalMarket缓存，提供 path, write, read, covered, stats 等方法。
    """
    def __init__(self, cache_dir=None, fmt="auto"):
        """初始化实例，设置内部状态和依赖项。
        
        Args:
            cache_dir: cachedir
            fmt: fmt
        """
        self.cache_dir = str(cache_dir or os.path.join(os.path.expanduser("~"), ".bigqmt_cache"))
        self.fmt = _resolve_format(fmt)

    def _ext(self):
        """ext。
        
        Returns:
             — 处理结果。
        """
        return ".parquet" if self.fmt == "parquet" else ".pkl"

    def path(self, code, period, dividend_type="none"):
        """path。
        
        Args:
            code: code
            period: period
            dividend_type: 除权除息type
        
        Returns:
             — 处理结果。
        """
        safe_code = str(code or "").replace("/", "_").replace("\\", "_")
        div = str(dividend_type or "none")
        return os.path.join(self.cache_dir, str(period or "1d"), div, safe_code + self._ext())

    def _existing_path(self, code, period, dividend_type):
        """Return the on-disk file for this key in the configured format, else the
        other format (so switching format still finds + migrates the old cache)."""
        primary = self.path(code, period, dividend_type)
        if os.path.isfile(primary):
            return primary
        base = primary[: -len(self._ext())]
        for ext in (".parquet", ".pkl"):
            alt = base + ext
            if os.path.isfile(alt):
                return alt
        return None

    @staticmethod
    def _read_file(path):
        """readfile。
        
        Args:
            path: path
        
        Returns:
             — 处理结果。
        """
        import pandas as pd

        # Read by actual file extension (an existing cache may be either format).
        if path.endswith(".pkl"):
            return pd.read_pickle(path)
        return pd.read_parquet(path)

    def _write_file(self, df, path):
        # Write in the configured format regardless of the path (the temp file ends
        # with ".tmp", not the format extension).
        """writefile。
        
        Args:
            df: df
            path: path
        """
        if self.fmt == "parquet":
            df.to_parquet(path, index=False)
        else:
            df.to_pickle(path)

    def write(self, code, period, df, dividend_type="none"):
        """Merge ``df`` into the cache for (code, period, dividend_type).

        Dedupe is by time keeping the LAST write, so re-pulling a range overwrites
        stale values — which is exactly what front-adjusted (前复权) data needs after
        a new dividend re-scales history. Returns total rows stored.
        """
        if df is None or not hasattr(df, "shape") or df.shape[0] == 0:
            return 0
        import pandas as pd

        incoming = _drop_placeholder_rows(df.copy())
        primary = self.path(code, period, dividend_type)
        existing = self._existing_path(code, period, dividend_type)
        if incoming.shape[0] == 0:
            # Nothing real to add (all 0-fill placeholders); keep existing cache.
            if existing:
                try:
                    return self._read_file(existing).shape[0]
                except Exception:
                    return 0
            return 0
        directory = os.path.dirname(primary)
        if directory and not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)
        merged = incoming
        tcol = _time_col(merged)
        if existing:
            try:
                old = self._read_file(existing)
                merged = pd.concat([old, merged], ignore_index=True)
            except Exception:
                pass
        if tcol and tcol in merged.columns:
            merged = merged.drop_duplicates(subset=[tcol], keep="last").sort_values(tcol).reset_index(drop=True)
        else:
            merged = merged.drop_duplicates().reset_index(drop=True)
        # Atomic-ish write (temp + replace) so a crash mid-write can't corrupt the file.
        tmp = primary + ".tmp"
        self._write_file(merged, tmp)
        os.replace(tmp, primary)
        # Migrated from the other format? drop the stale file.
        if existing and existing != primary:
            try:
                os.remove(existing)
            except Exception:
                pass
        return merged.shape[0]

    def read(self, code, period, start_time="", end_time="", count=-1, dividend_type="none"):
        """Return the cached DataFrame for (code, period, dividend_type), filtered."""
        existing = self._existing_path(code, period, dividend_type)
        if not existing:
            return None
        try:
            df = self._read_file(existing)
        except Exception:
            return None
        tcol = _time_col(df)
        if tcol and tcol in df.columns:
            series = df[tcol].astype(str)
            if start_time:
                df = df[series >= str(start_time)]
            if end_time:
                df = df[series <= _pad_end(end_time)]
            df = df.sort_values(tcol).reset_index(drop=True)
        try:
            n = int(count)
        except (TypeError, ValueError):
            n = -1
        if n > 0 and df.shape[0] > n:
            df = df.tail(n).reset_index(drop=True)
        return df

    def covered(self, code, period, dividend_type="none"):
        """Return (first_time, last_time, rows) for the cache, or None if empty."""
        df = self.read(code, period, dividend_type=dividend_type)
        if df is None or df.shape[0] == 0:
            return None
        tcol = _time_col(df)
        if not tcol:
            return (None, None, df.shape[0])
        series = df[tcol].astype(str)
        return (series.iloc[0], series.iloc[-1], df.shape[0])

    def stats(self):
        """Return (files, periods) currently cached across all dividend types."""
        files = 0
        periods = set()
        if os.path.isdir(self.cache_dir):
            for root, _dirs, fnames in os.walk(self.cache_dir):
                cached = [f for f in fnames if f.endswith(".parquet") or f.endswith(".pkl")]
                if cached:
                    files += len(cached)
                    rel = os.path.relpath(root, self.cache_dir)
                    periods.add(rel.split(os.sep)[0] if rel != "." else rel)
        return files, sorted(periods)

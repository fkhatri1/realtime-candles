import pytest, unittest, pandas as pd
from CandleSeries import CandleSeries

def test_ts_trunc():
    ts = "2021-12-08T16:35:15+00:00"
    expected = pd.to_datetime("2021-12-08T16:35:00+00:00")

    c = CandleSeries('BTC-PERP', 60)
    assert c._ts_trunc(ts) == expected

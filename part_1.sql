-- Assumes MySQL syntax and datatypes

-- Table for housing trade executions data
CREATE TABLE trades (
    exchange CHAR(20),
    pair CHAR(20),
    ts TIMESTAMP,
    price FLOAT,
    size FLOAT,
    side ENUM('buy', 'sell'),
    liquidation BINARY(1),  --true/false as 0 or 1
    PRIMARY KEY (exchange, pair, ts)  --sets up combination of these 3 fields as a primary key which must be unique
);

-- Table for housing historical ohlc data
CREATE TABLE ohlc (
    exchange CHAR(20),
    pair CHAR(20),
    interval_start TIMESTAMP,
    interval_duration INT,
    o FLOAT,
    h FLOAT,
    l FLOAT,
    c FLOAT,
    v FLOAT,
    PRIMARY KEY (exchange, pair, interval_start, interval_duration)  --sets up combination of these 4 fields as a primary key which must be unique
);

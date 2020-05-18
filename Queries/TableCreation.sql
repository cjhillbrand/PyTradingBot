CREATE table dailycryptodata (
	symbol	char(6),
	datetime timestamp,
	price 	real,
	PRIMARY KEY(symbol, datetime)
)
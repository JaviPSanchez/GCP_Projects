SELECT 
  data_element.tags
FROM 
  `gcp-native-v2.Test.Cryptos`,
  UNNEST(data) AS data_element
LIMIT 100;

SELECT column_name, data_type
FROM `gcp-native-v2.Test.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'Cryptos';

SELECT
  data_element.quote.USD.fully_diluted_market_cap,
  data_element.quote.USD.price,
  data_element.quote.USD.market_cap,
  data_element.quote.USD.percent_change_60d,
  data_element.quote.USD.percent_change_30d,
  data_element.quote.USD.percent_change_90d,
  data_element.quote.USD.volume_24h,
  data_element.symbol,
  data_element.name,
  status.timestamp
FROM `gcp-native-v2.Test.Cryptos`,
UNNEST(data) AS data_element
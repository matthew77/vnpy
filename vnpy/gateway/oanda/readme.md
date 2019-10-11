## Connection Limits

For new connections, we recommend you limit this to twice per second (2/s).

For an established connection, we recommend limiting this to one hundred per second (100/s).

Get a stream of Account Prices starting from when the request is made.
This pricing stream does not include every single price created for the Account, but instead will provide at most 4 prices per second (every 250 milliseconds) for each instrument being requested.
If more than one price is created for an instrument during the 250 millisecond window, only the price in effect at the end of the window is sent. This means that during periods of rapid price movement, subscribers to this stream will not be sent every price.
Pricing windows for different connections to the price stream are not all aligned in the same way (i.e. they are not all aligned to the top of the second). This means that during periods of rapid price movement, different subscribers may observe different prices depending on their alignment.

## Rate Limiting
### REST API
120 requests per second. Excess requests will receive HTTP 429 error. This restriction is applied against the requesting access token.

### Streaming API
20 active streams. Requests above this threshold will be rejected. This restriction is applied against the requesting access token.

### Connection Limiting
Client is allowed to make no more than 2 new connections per second. Excess connections will be rejected. 
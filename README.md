# Serverless WebSocket chat example

This is a Serverless project which creates a websocket chat backend. It's quite basic, but supports
some standard features including setting a nickname, multiple channels, and broadcasting messages
to channel members. The coolest this is that this is entirely serverless and in Python!

## Demo

[![asciicast](https://asciinema.org/a/O1ya9VitrkhH1lQVCqxbJsV6P.svg)](https://asciinema.org/a/O1ya9VitrkhH1lQVCqxbJsV6P)

## Getting started

This can all be deployed with AWS SAM.

```bash
$ sam build
$ sam deploy --guided
```

The final output will be a `wss` endpoint which you can connect to:

```
---------------------------------------------------------------------------------
Outputs
---------------------------------------------------------------------------------
Key                 WebSocketURI
Description         The WSS Protocol URI to connect to
Value               wss://abcd123.execute-api.us-west-2.amazonaws.com/Prod
```

Use `wscat` to connect and test:

- Install `wscat` by just running `yarn`
- In two different terminals: `./node_modules/.bin/wscat -c wss://YOUR_WS_ENDPOING`
- Now type a meesage and hit enter...you'll see messages from one window pop up into another.

## Commands

- `/name bz` - Change your display name to `bz`
- `/channel random` - Change to the `random` channel. Default channel is `general`
- `/help`

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

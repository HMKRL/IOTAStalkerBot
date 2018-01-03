# IOTA Stalker Bot
- A telegram bot that can monitor IOTA and other cryptocurrency coin status

## Bot command
- `rate` - Show crypto's exchange rate
- `track` - Track IOTA address
- `remind` - Remind you when exchange rate reached
- `confirm` - Notify when an IOTA transactions confirmed
- `donate` - Donate developer with IOTA

## State Machine
![](https://raw.githubusercontent.com/HMKRL/IOTAStalkerBot/master/state_diagram.png)

## Dependencies
- pip dependencies in `requirements.txt`
- you should setup an IOTA full node with [IRI](https://github.com/iotaledger/iri) on your host

## Notice
API KEY should be stored in enviroment variable `TG_BOT_KEY`    

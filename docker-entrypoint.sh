#!/bin/sh

anvil --steps-tracing --auto-impersonate --host 0.0.0.0 --fork-url https://base-mainnet.g.alchemy.com/v2/jznBIFv2-ZpI5PPfgrTQpikScTvE3awc --fork-block-number 29007455 &
ANVIL_PID=$!

sleep 3

cast send 0x3033C274D3Ccc8d12B4Ea567F6F94849507c37aE "grantRole(uint64,address,uint32)" 200 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 0 --rpc-url http://localhost:8545 --from 0xF6a9bd8F6DC537675D499Ac1CA14f2c55d8b5569 --unlocked

wait $ANVIL_PID
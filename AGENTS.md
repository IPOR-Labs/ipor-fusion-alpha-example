# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, Cursor, Gemini CLI, and others) working in this repository.
Codex and Cursor read it natively. Claude Code loads it through `CLAUDE.md`, Gemini CLI through
`.gemini/settings.json`. Keep this file the single source of truth, do not fork tool-specific copies, and keep it
well under 32 KiB (Codex's default `project_doc_max_bytes` cap on combined instruction files).

## What this is

Reference "alpha bot" for the IPOR Fusion SDK (`ipor-fusion`, pinned in `pyproject.toml`). Every cycle it reads the
Plasma Vault's wstETH balance on Base and, if non-zero, supplies all of it to Aave V3 through the `AaveV3SupplyFuse`
(`e_mode=1`). It is an example, not a production keeper: keep it small and readable.

## Commands

```bash
uv sync                                   # install (dev group included)
uv run python main.py                     # run the bot (needs .env, see below)
uv run pytest                             # run tests; CI runs `uv run pytest -v -s`
uv run pytest test_alpha_bot.py::test_alpha_bot -v -s   # single test
uv run ruff check .                       # lint (offline, no RPC needed)
uv run ruff format .                      # format; CI runs `ruff format --check`
docker compose up -d                      # anvil fork + bot sandbox (podman compose works too)
docker compose logs anvil                 # if the bot never starts, the role grant in docker-entrypoint.sh failed
```

CI (`.github/workflows/python-build.yml`) runs `uv sync --locked`, `ruff format --check`, `ruff check`, then
`pytest` with `PROVIDER_URL` injected from the `BASE_PROVIDER_URL` secret. Python is pinned to 3.11 in
`.python-version`, the Dockerfile, and the CI default. Keep `uv.lock` in sync with `pyproject.toml` or CI fails on
`--locked`. Without a `PROVIDER_URL` ruff is the only check you can run; the test fails fast instead of skipping.

## Conventions

- Commit subjects carry a bracketed prefix: `[fix]`, `[chore]`. Keep that style.
- No AI attribution anywhere: no `Co-Authored-By`, no "Generated with", no tool trailers in commits or PRs.
- Never print `.env` or `PRIVATE_KEY` into output, logs, or commit messages. Read single non-secret variables
  if you need them.
- Dependencies are pinned with `==` in `pyproject.toml`; do the same for new ones and run `uv lock`.

## Environment

`.env` (copy from `.env.example`) with `PROVIDER_URL`, `PRIVATE_KEY`, `PLASMA_VAULT_ADDRESS`. Tests and the compose
sandbox both need `PROVIDER_URL` to be a **Base archive RPC that supports `eth_simulateV1`** (Alchemy does);
`conftest.py` fails fast otherwise. The `.env.example` private key is anvil account #0 and is intentional, see below.

## Architecture

Four flat modules, no package:

- `main.py` validates env vars, builds `AlphaBot`, hands it to `Scheduler` (60 s interval).
- `scheduler.py` runs `do_fusion()` once immediately, then every `interval` seconds via `schedule`. Blocking loop.
- `alpha_bot.py` holds the strategy. `build_actions()` is the pure step (reads chain, returns `list[FuseAction]`,
  empty when nothing to do); `do_fusion()` wraps it with `vault.execute(actions).send()`. That split exists so the
  test can simulate the actions without sending a transaction. `do_fusion()` deliberately catches every exception
  and logs it so one failed cycle does not kill the scheduler loop.
- `logging_config.py` gives each component a non-propagating DEBUG logger named `Fusion Alpha - <component>`.

Strategy changes go in `AlphaBot.build_actions()`. Anything that produces `FuseAction`s belongs there, not in
`do_fusion()`.

### Test design (`test_alpha_bot.py`)

No anvil, no signing. The test pins `bot.ctx.default_block` to `PINNED_BLOCK`, then uses the SDK's `VaultSimulator`
to run one `eth_simulateV1` round-trip that: grants `ALPHA_ROLE` to the throwaway alpha wallet (impersonating the
`ATOMIST` address, which is allowed because simulation runs with `validation=false`), observes balances, executes
`build_actions()`, observes again. It asserts all wstETH left the vault and roughly the same amount of aWSTETH was
minted (10 wei tolerance for aToken rebasing). Follow the same pattern for new strategies: pin the block, grant
roles inside the simulation, assert on observed deltas.

### Compose sandbox (`docker-compose.yml`, `Dockerfile.anvil`, `docker-entrypoint.sh`)

The anvil container forks Base at the same pinned block using `.env`'s `PROVIDER_URL`; the bot container gets
`PROVIDER_URL` overridden to `http://anvil:8545/`. The entrypoint uses `cast send --unlocked` from the atomist to
grant `ALPHA_ROLE` (id `200`) to anvil account #0 on the vault's AccessManager. The compose healthcheck polls
`hasRole` for that grant and the bot only starts once it is healthy, because the bot's first cycle runs immediately
and would otherwise revert with `AccessManagedUnauthorized`.

### Hardcoded values that must stay consistent

| Value | Where |
|---|---|
| Pinned Base block `29007455` | `test_alpha_bot.py` (`PINNED_BLOCK`), `docker-entrypoint.sh` (`--fork-block-number`) |
| Vault `0xFe8b...2DE6` | `.env.example`, `test_alpha_bot.py` |
| Vault's AccessManager `0x3033...37aE` | `docker-entrypoint.sh`, `docker-compose.yml` healthcheck (the test derives it at runtime via `vault.get_access_manager_address()`) |
| Atomist `0xF6a9...5569` (role grantor) | `test_alpha_bot.py`, `docker-entrypoint.sh` |
| Anvil account #0 (`0xf39F...2266`, key in `.env.example`) | `docker-entrypoint.sh`, `docker-compose.yml` healthcheck |
| wstETH and Aave V3 supply fuse addresses (Base) | `AlphaBot` class constants; the aWSTETH address lives in the test |

Changing the vault, the block, or the sandbox wallet means updating every row that references it. The test's
"vault holds no wstETH at the pinned block" assertion is the canary for a bad block choice.

AI Token LaunchPad – Full-Stack Overview
=======================================

This repository contains a complete, production-ready AI token launch platform composed of:

- Smart Contracts (Foundry, Solidity 0.8.24)
- Backend API (Django + DRF, Web3 signature auth)
- Frontend (Next.js 15 + TypeScript, Ethers v6)

Users connect a wallet, sign a nonce to authenticate, configure a token launch with optional AI agents, deploy on-chain to the Core network, and manage their launches via a dashboard.


Repository Structure
--------------------

```
contracts/            # Foundry project with TokenFactory, FeeManager, tests
backend/AI_Launch_Pad # Django project with DRF APIs and Web3 signature auth
frontend/             # Next.js 15 app (app router), ethers v6, Tailwind UI
```


End-to-End Flow
---------------

1) Connect wallet on the frontend (EIP-1193 provider via MetaMask or compatible).
2) Obtain a nonce from the backend and sign it in the wallet.
3) Backend verifies signature and issues an API token (stored in localStorage).
4) User creates a “launch” via the backend API (metadata: name, symbol, supply, etc.).
5) Frontend calls the TokenFactory contract to deploy the token and parse the TokenCreated event.
6) Frontend attaches the transaction hash and token address back to the backend.
7) User is redirected to the dashboard to view the launch and track status.


Smart Contracts (contracts/)
----------------------------

- Tooling: Foundry (forge, cast)
- Language: Solidity 0.8.24
- Key contracts:
	- TokenFactory: Creates ERC-20 tokens and emits TokenCreated(launchId, tokenAddress, ...)
	- FeeManager: Computes and accounts for platform and AI service fees
- Network: Core DAO chain (chainId 1114). RPC and explorer configured in the frontend.

Common tasks
```
# Install foundry (if not yet installed)
# See https://book.getfoundry.sh/getting-started/installation

forge build
forge test -vv

# Example deployment (adjust RPC and private key via environment)
# forge script script/Deploy.s.sol --rpc-url $CORE_RPC --broadcast
```


Backend API (backend/AI_Launch_Pad)
-----------------------------------

- Framework: Django 4.2.x + Django REST Framework
- Auth: Web3 signature authentication using eth-account (nonce -> signed message -> token)
- DB: SQLite by default; Postgres recommended for production
- Caching/Rate Limit: Optional Redis, with LocMem fallback for local dev
- Notable endpoints:
	- GET /health/
	- POST /api/auth/web3/nonce/        { address } -> { nonce }
	- POST /api/auth/web3/verify/       { address, signature } -> { token }
	- GET/POST /api/launches/            create and list launches
	- POST /api/launches/<uuid>/attach_tx/  { tx_hash, token_address }

Local run (example)
```
cd backend/AI_Launch_Pad
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Environment configuration (examples)
```
DEBUG=1
ALLOWED_HOSTS=*
CORS_ALLOW_ALL_ORIGINS=true
USE_REDIS=0
# DATABASE_URL=postgres://user:pass@localhost:5432/ai_launch_pad
```


Frontend (frontend/)
--------------------

- Framework: Next.js 15 (App Router) + TypeScript
- Web3: Ethers v6, BrowserProvider, EIP-1193 provider
- UI: Tailwind CSS + framer-motion + lucide-react
- Key pages: Landing, LaunchPad, Dashboard, Governance, Community
- Shared hook: useWalletAuth for wallet connection and Web3 sign-in

Environment variables (examples)
```
NEXT_PUBLIC_API_BASE=http://localhost:8000
# Core DAO network configuration is defined in lib/constants.ts
```

Local run
```
cd frontend
npm install
npm run dev
# or
npm run build && npm run start
```


Configuration and Addresses
---------------------------

- Frontend chain and contract addresses live in `frontend/lib/constants.ts`:
	- CHAIN_CONFIG: chainId 1114 (Core), RPC URLs, explorer URL
	- CONTRACT_ADDRESSES: TokenFactory, FeeManager
- The frontend will attempt to switch/add the Core network automatically when connecting.


Development Notes
-----------------

- Web3 Auth flow is stateless on the client; the DRF token is stored in localStorage.
- The backend auto-assigns a default category to a launch if none is provided.
- The LaunchPad flow redirects to the dashboard on success.
- Health endpoint is AllowAny and unthrottled; Redis is optional (USE_REDIS=0 in local dev).


Testing and Verification
------------------------

- Contracts: `forge test` (add more tests in `contracts/test/` as needed)
- Backend: add DRF tests for auth and launches
- Frontend: use `npm run lint` and `npm run build` to ensure type-safety and production readiness


Troubleshooting
---------------

- If Next.js complains about async route props, ensure `params` and `searchParams` are treated as Promises in App Router pages and awaited.
- If rate limiting or cache errors occur locally, set `USE_REDIS=0` to use in-memory cache.
- If wallet connection fails, ensure a browser wallet is installed and the Core network RPC is reachable.


License
-------

This project includes third-party code under their respective licenses (e.g., OpenZeppelin). Review `contracts/lib/` and `contracts/openzeppelin-contracts/` for details. Add an explicit root license if distributing.


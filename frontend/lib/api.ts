const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        cache: "no-store",
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`API ${res.status}: ${text}`);
    }
    return res.json();
}

export async function health(): Promise<{ status: string; time: string }> {
    return request("/health/");
}

export async function getToken(username: string, password: string): Promise<{ token: string }> {
    return request("/api/auth/token/", {
        method: "POST",
        body: JSON.stringify({ username, password }),
    });
}

export async function web3GetNonce(address: string): Promise<{ nonce: string }> {
    return request("/api/auth/web3/nonce/", {
        method: "POST",
        body: JSON.stringify({ address }),
    });
}

export async function web3Verify(address: string, signature: string): Promise<{ token: string }> {
    return request("/api/auth/web3/verify/", {
        method: "POST",
        body: JSON.stringify({ address, signature }),
    });
}

export type CreateLaunchInput = {
    name: string;
    symbol: string;
    description?: string;
    category_id?: string; // UUID of a TokenCategory
    network?: string; // e.g. "ETHEREUM"
    total_supply?: number | string;
};

export async function createLaunch(token: string, data: CreateLaunchInput): Promise<{ id: string }> {
    return request("/api/launches/", {
        method: "POST",
        headers: { Authorization: `Token ${token}` },
        body: JSON.stringify(data),
    });
}

export type Launch = {
    id: string
    name: string
    symbol: string
    total_supply?: string | number
    network?: string
    created_at?: string
    updated_at?: string
}

export async function listLaunches(token: string): Promise<Launch[]> {
    return request<Launch[]>("/api/launches/", {
        headers: { Authorization: `Token ${token}` },
    })
}

export async function attachTx(token: string, launchId: string, tx_hash: string, contract_address?: string): Promise<{ id: string; tx_hash: string; contract_address?: string }> {
    return request(`/api/launches/${launchId}/attach_tx/`, {
        method: "POST",
        headers: { Authorization: `Token ${token}` },
        body: JSON.stringify({ tx_hash, contract_address }),
    });
}

// Example usage (in a React component):
// const token = (typeof window !== 'undefined') ? localStorage.getItem('authToken') : null;
// const launch = await createLaunch(token!, { name: 'MyToken', symbol: 'MYT', total_supply: '1000000', network: 'ETHEREUM' });
// const { success, txHash } = await contractService.createToken('MyToken', 'MYT', '1000000', [AI_AGENT_TYPES.MARKETING_AGENT]);
// if (success) await attachTx(token!, launch.id, txHash, deployedAddress);

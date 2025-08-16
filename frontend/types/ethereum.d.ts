export { }

declare global {
    // Minimal EIP-1193 provider interface we need
    interface Eip1193Provider {
        request(args: { method: string; params?: unknown[] }): Promise<unknown>
        on?(event: string, handler: (...args: unknown[]) => void): void
        removeListener?(event: string, handler: (...args: unknown[]) => void): void
    }

    interface Window {
        ethereum?: Eip1193Provider
    }
}

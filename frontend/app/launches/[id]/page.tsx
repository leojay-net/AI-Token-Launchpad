import Link from 'next/link'
import { CHAIN_CONFIG } from '@/lib/constants'

export default async function LaunchSuccess({ params, searchParams }: { params: Promise<{ id: string }>, searchParams: Promise<{ tx?: string, addr?: string }> }) {
    const { id } = await params
    const { tx, addr } = await searchParams
    const explorer = CHAIN_CONFIG.blockExplorerUrls[0]

    return (
        <main className="max-w-3xl mx-auto px-6 py-12">
            <h1 className="text-2xl font-bold mb-4">Launch Submitted</h1>
            <p className="text-neutral-700 mb-6">Your token launch has been linked and is processing on-chain.</p>

            <div className="space-y-3 mb-8">
                <div className="flex gap-2 items-center">
                    <span className="text-neutral-600 w-40">Launch ID</span>
                    <code className="text-sm">{id}</code>
                </div>
                {tx && (
                    <div className="flex gap-2 items-center">
                        <span className="text-neutral-600 w-40">Transaction</span>
                        <Link href={`${explorer}/tx/${tx}`} className="text-gold-600 underline" target="_blank" rel="noopener noreferrer">
                            {tx.slice(0, 10)}...{tx.slice(-8)}
                        </Link>
                    </div>
                )}
                {addr && (
                    <div className="flex gap-2 items-center">
                        <span className="text-neutral-600 w-40">Token Address</span>
                        <Link href={`${explorer}/address/${addr}`} className="text-gold-600 underline" target="_blank" rel="noopener noreferrer">
                            {addr}
                        </Link>
                    </div>
                )}
            </div>

            <div className="flex gap-3">
                <Link href="/" className="btn-secondary">Back Home</Link>
                <Link href="/dashboard" className="btn-secondary">Go to Dashboard</Link>
                {addr && explorer && (
                    <Link href={`${explorer}/address/${addr}`} className="btn-primary" target="_blank" rel="noopener noreferrer">
                        View on Explorer
                    </Link>
                )}
            </div>
        </main>
    )
}

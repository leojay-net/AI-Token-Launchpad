import Hero from '@/components/Hero'
import Features from '@/components/Features'
import Stats from '@/components/Stats'
import LaunchPad from '@/components/LaunchPad'
import Navigation from '@/components/Navigation'

export default function Home() {
    return (
        <main className="min-h-screen bg-white">
            <Navigation />
            <Hero />
            <Stats />
            <Features />
            <LaunchPad />
        </main>
    )
}

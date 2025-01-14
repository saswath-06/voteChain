import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '@/styles/globals.css'
import { ApolloProvider } from '../components/providers/ApolloProvider';
import { Web3Provider } from '../components/providers/Web3Provider';
import { client } from '@/lib/graphql/client'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'DAO Dashboard',
  description: 'Governance analytics platform for DAOs',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ApolloProvider>
          <Web3Provider>
            {children}
          </Web3Provider>
        </ApolloProvider>
      </body>
    </html>
  );
}

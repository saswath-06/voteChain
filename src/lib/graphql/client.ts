// src/lib/graphql/client.ts
import { ApolloClient, InMemoryCache, HttpLink } from '@apollo/client'

if (!process.env.NEXT_PUBLIC_SUBGRAPH_URL) {
  throw new Error('Missing NEXT_PUBLIC_SUBGRAPH_URL')
}

const httpLink = new HttpLink({
  uri: process.env.NEXT_PUBLIC_SUBGRAPH_URL
})

export const client = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          proposals: {
            keyArgs: ['where', 'orderBy', 'orderDirection'],
            merge(existing = [], incoming) {
              return [...existing, ...incoming]
            },
          },
        },
      },
    },
  }),
})

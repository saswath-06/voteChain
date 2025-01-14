import { ApolloProvider as BaseApolloProvider } from '@apollo/client';
import { client } from '@/lib/graphql/client';
import { PropsWithChildren } from 'react';

export function ApolloProvider({ children }: PropsWithChildren) {
  return (
    <BaseApolloProvider client={client}>
      {children}
    </BaseApolloProvider>
  );
}

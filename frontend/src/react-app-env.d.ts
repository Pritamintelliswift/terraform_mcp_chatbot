/// <reference types="react-scripts" />

declare module 'react' {
  export = React;
  export as namespace React;
}

declare namespace React {
  interface Element {}
  interface FC<P = {}> {
    (props: P & { children?: React.ReactNode }): React.ReactElement | null;
  }
  type ReactNode = ReactElement | string | number | boolean | null | undefined;
  interface ReactElement<P = any, T extends string | JSXElementConstructor<any> = string | JSXElementConstructor<any>> {
    type: T;
    props: P;
    key: Key | null;
  }
  type JSXElementConstructor<P> = ((props: P) => ReactElement | null);
  type Key = string | number;
}
declare module 'umi' {
  export const history: {
    push: (path: string) => void;
    replace: (path: string) => void;
    goBack: () => void;
  };
  
  export function useLocation(): {
    pathname: string;
    search: string;
    hash: string;
    state: any;
  };
}

// Umi define 注入的全局变量
declare const API_URL: string; 
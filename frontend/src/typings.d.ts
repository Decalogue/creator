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

// markdown-it-katex 类型声明
declare module 'markdown-it-katex' {
  import { PluginSimple } from 'markdown-it';
  const mk: PluginSimple;
  export default mk;
} 
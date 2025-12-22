import { defineConfig } from 'umi';
import { routes } from './routes';
export default defineConfig({
    esbuildMinifyIIFE: true,
    plugins: ['@umijs/plugins/dist/styled-components','@umijs/plugins/dist/antd'],
    styledComponents: {},
    antd:{},
    routes: routes,
    npmClient: 'pnpm',
    define:{
        'API_URL':'http://ngb1.dc.huixingyun.com:53115',
    },
});

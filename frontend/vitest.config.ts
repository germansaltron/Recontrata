import { defineConfig } from 'vitest/config'

// Config aislada para los tests unitarios (no carga los plugins de build/PWA de
// vite.config.ts). Entorno node: los tests que necesiten `navigator`/`window` lo
// stubean explícitamente con vi.stubGlobal.
export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
  },
})

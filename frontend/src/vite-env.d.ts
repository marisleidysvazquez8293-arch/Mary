/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string
  readonly VITE_PROXY_TARGET?: string
  readonly VITE_API_USER?: string
  readonly VITE_API_PASSWORD?: string
  readonly VITE_DEMO_CONJUNTO_PESOS_ID?: string
  /** Rol UI: analista | auditor | admin | administrador_tecnico */
  readonly VITE_SADE_ROLE?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

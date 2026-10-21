import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import { AppShell } from './layout/AppShell'
import { AhpPage } from './pages/AhpPage'
import { EscenariosPage } from './pages/EscenariosPage'
import { ExpedientePage } from './pages/ExpedientePage'
import { ReglasPage } from './pages/ReglasPage'
import { VisorPage } from './pages/VisorPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route index element={<VisorPage />} />
          <Route path="reglas" element={<ReglasPage />} />
          <Route path="ahp" element={<AhpPage />} />
          <Route path="escenarios" element={<EscenariosPage />} />
          <Route path="expediente" element={<ExpedientePage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

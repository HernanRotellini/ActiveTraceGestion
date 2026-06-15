## 1. Fix paginated list rendering — admin pages

- [x] 1.1 Fix `CohortesPage.tsx` — `carreras?.items.map(` → `carreras?.items?.map(` (line 75) and `data?.items.map(` → `data?.items?.map(` (line 133)
- [x] 1.2 Fix `MateriasPage.tsx` — three `.map()` calls: `carreras?.items` (80), `cohortes?.items` (94), `data?.items` (165)
- [x] 1.3 Fix `CarrerasPage.tsx` — `data?.items.map(` → `data?.items?.map(` (line 124)
- [x] 1.4 Fix `UsuariosPage.tsx` — `data?.items.map(` → `data?.items?.map(` (line 336)
- [x] 1.5 Fix `AuditoriaLogPage.tsx` — `data?.items.map(` → `data?.items?.map(` (line 54)

## 2. Fix paginated list rendering — feature pages

- [x] 2.1 Fix `EncuentrosListPage.tsx` — `data?.items.map(` → `data?.items?.map(` (line 74)
- [x] 2.2 Fix `TareasListPage.tsx` — `data?.items.map(` → `data?.items?.map(` (line 115)
- [x] 2.3 Fix `EquiposListPage.tsx` — `data?.items.map(` → `data?.items?.map(` (line 83)
- [x] 2.4 Fix `LiquidacionHistorialPage.tsx` — `data?.items.map(` → `data?.items?.map(` (line 28)
- [x] 2.5 Fix `SetupCuatrimestrePage.tsx` — `data?.items.map(` → `data?.items?.map(` (line 96)

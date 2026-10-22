# Business Analytics Dashboard

Aplicación web Full Stack para analizar datos comerciales: carga archivos CSV/Excel
con ventas, valida y procesa los datos, muestra indicadores calculados en tiempo real
y genera reportes CSV y PDF con gráficos.

> Los datos de demostración incluidos son **ficticios** y están etiquetados como tales
> (importación `DEMO-datos-ficticios.*`). No representan a ninguna empresa real.

---

## Índice

1. [Arquitectura](#arquitectura)
2. [Tecnologías](#tecnologías)
3. [Instalación y ejecución](#instalación-y-ejecución)
4. [Despliegue en la nube (Vercel + Render)](#despliegue-en-la-nube-vercel--render)
5. [Modelo de datos](#modelo-de-datos)
6. [Importación de datos](#importación-de-datos)
7. [Cálculos y decisiones](#cálculos-y-decisiones)
8. [Endpoints de la API](#endpoints-de-la-api)
9. [Pruebas](#pruebas)
10. [Variables de entorno](#variables-de-entorno)
11. [Datos de demostración](#datos-de-demostración)
12. [Limitaciones conocidas](#limitaciones-conocidas)

---

## Arquitectura

```
Business-Analytics-Dashboard/
├── backend/                 # API REST (FastAPI + SQLAlchemy + Pandas)
│   ├── app/
│   │   ├── main.py          # app factory, CORS, manejo centralizado de errores
│   │   ├── core/            # config, database, exceptions
│   │   ├── models/          # tablas SQLAlchemy (imports, sales)
│   │   ├── schemas/         # validación/serialización Pydantic
│   │   ├── repositories/    # consultas parametrizadas a la BD
│   │   ├── services/        # import, analytics, reports, demo
│   │   ├── routers/         # endpoints REST
│   │   └── utils/           # parsing de encabezados/fechas/números
│   └── tests/               # pytest (35 pruebas)
├── frontend/                # SPA (React + TypeScript + Vite + Tailwind + Recharts)
│   └── src/
│       ├── api/             # cliente HTTP tipado
│       ├── i18n/            # textos es/en + selector de idioma
│       ├── context/         # filtros globales sincronizados con la URL
│       ├── components/      # layout, filtros, KPIs, gráficos, estados, tabla
│       ├── pages/           # Dashboard, Importar, Datos, Reportes
│       └── hooks/           # carga asíncrona reutilizable
├── render.yaml              # blueprint de Render (backend + PostgreSQL)
├── .env.example
├── .gitignore
└── README.md
```

El backend separa responsabilidades: los **routers** solo orquestan, los **services**
contienen la lógica de negocio, los **repositories** ejecutan consultas mediante el ORM
(parametrizadas, sin SQL concatenado) y los **schemas** validan la entrada/salida.

## Tecnologías

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11, FastAPI 0.115, Pandas 2.2, Pydantic 2.10, SQLAlchemy 2.0 |
| Base de datos | SQLite (desarrollo) · PostgreSQL + psycopg2 (despliegue, misma capa ORM) |
| Frontend | React 18, TypeScript 5.7, Vite 6, Tailwind CSS 3.4, Recharts 2.13 |
| Reportes | ReportLab (PDF con gráficos nativos) + CSV |
| Pruebas | Pytest + httpx (backend) · Vitest + Testing Library (frontend) |
| Despliegue | Vercel (frontend) · Render (backend + PostgreSQL) |

## Instalación y ejecución

### Requisitos
- Python 3.11+
- Node.js 18+ y npm

### Backend

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/mac: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env      # o: cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000
- Documentación Swagger/OpenAPI: http://localhost:8000/docs

Las tablas se crean automáticamente al iniciar (SQLite por defecto).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

- App: http://localhost:5173
- El servidor de desarrollo de Vite hace **proxy** de `/api` hacia `http://localhost:8000`.

> **Windows con políticas de seguridad (WDAC/AppLocker):** si tu equipo bloquea el binario
> nativo de Rollup (`rollup.win32-x64-msvc.node`), Vercel/Vite no arrancarán con el error
> "An Application Control policy has blocked this file". El repo incluye
> `frontend/scripts/fix-rollup-wasm.mjs`, que se ejecuta automáticamente tras `npm install`
> (y en `predev`/`prebuild`/`pretest`) y redirige Rollup a su versión WebAssembly
> (`@rollup/wasm-node`), sin binario nativo. En equipos normales no cambia nada.

### Primeros pasos en la interfaz

1. Abre http://localhost:5173
2. Pulsa **Cargar datos de demostración** en el Dashboard (o sube tu propio archivo en *Importar*).
3. Usa la barra de filtros del encabezado (fechas, producto, categoría, granularidad, comparación).

## Despliegue en la nube (Vercel + Render)

Reparto de responsabilidades:

- **Frontend → Vercel** (estático, gratis, red global).
- **Backend + PostgreSQL → Render** (proceso persistente, necesario para Pandas, subida
  de archivos y una base de datos real).

> Por qué no todo en Vercel: sus funciones son *serverless* y efímeras. Pandas + openpyxl +
> ReportLab superan los límites prácticos de una función y su disco `/tmp` deja de ser fiable
> entre invocaciones, por lo que los datos importados se perderían.

### Paso 1 — Backend en Render

El repo incluye `render.yaml` (Infrastructure as Code). Opción rápida:

1. Crea una cuenta en https://render.com y conecta tu repositorio de GitHub.
2. Elige **New → Blueprint**, selecciona el repo. Render leerá `render.yaml` y creará:
   - un servicio web `ba-dashboard-api` (plan free),
   - una base de datos PostgreSQL `ba-dashboard-db` (plan free),
   - y enlazará `DATABASE_URL` automáticamente.
3. Cuando pregunte por `CORS_ORIGINS`, escribe la URL de tu frontend en Vercel
   (la tendrás en el Paso 2), por ejemplo: `https://tu-app.vercel.app`.
4. Tras el primer despliegue, copia la URL del backend, p. ej.
   `https://ba-dashboard-api.onrender.com`. Verifica `https://.../api/health`.

> El plan free de Render “duerme” el servicio tras unos minutos de inactividad; el primer
> acceso posterior tarda unos segundos en despertar. Es normal.

**Si prefieres configurarlo a mano** (sin Blueprint):

| Ajuste | Valor |
|--------|-------|
| Root directory | `backend` |
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health check path | `/api/health` |
| Env var | `DATABASE_URL` = cadena interna de tu PostgreSQL en Render |
| Env var | `UPLOAD_DIR` = `/tmp/uploads` |
| Env var | `CORS_ORIGINS` = URL de Vercel |
| Env var | `PYTHON_VERSION` = `3.11.9` |

### Paso 2 — Frontend en Vercel

1. Crea una cuenta en https://vercel.com e importa el repositorio.
2. En **Root Directory** selecciona `frontend`. Vercel detecta Vite automáticamente
   (configurado además en `frontend/vercel.json`).
3. Añade una variable de entorno:
   - `VITE_API_BASE` = `https://ba-dashboard-api.onrender.com/api` (tu URL de Render + `/api`).
4. Deploy. Copia la URL resultante (`https://tu-app.vercel.app`).
5. Vuelve a Render y actualiza `CORS_ORIGINS` con esa URL (y redeploy si hace falta).

Cualquier persona con el enlace de Vercel ya puede usar la aplicación.

### Notas de producción

- **Datos**: PostgreSQL gestionado por Render; el esquema se crea solo al arrancar.
- **Archivos subidos**: las filas aceptadas se guardan en la base de datos al analizar el
  archivo, así que la confirmación de una importación **no depende del disco**. Por eso el
  backend funciona aunque el filesystem sea efímero.
- **Sin autenticación**: cualquiera con el enlace ve y modifica los datos. Para uso público
  real, añade autenticación y filtra por usuario (ver *Limitaciones conocidas*).


## Modelo de datos

**`imports`** — trazabilidad de cada carga.

| Columna | Tipo | Notas |
|--------|------|-------|
| id | PK | |
| filename | varchar | nombre original |
| status | varchar | `pending` · `confirmed` · `failed` · `discarded` (indexado) |
| total_rows / accepted_rows / rejected_rows / duplicate_rows | int | resumen de la importación |
| errors_json | JSON | errores por fila (máx. 500 almacenados) |
| accepted_rows_json | JSON | filas aceptadas serializadas; permite confirmar sin depender del disco |
| checksum | varchar(64) | SHA-256 del archivo |
| stored_path | varchar | ruta del archivo para confirmar |
| is_demo | bool | identifica datos ficticios |
| created_at / confirmed_at | datetime | índice en `created_at` |

**`sales`** — registros de venta, relacionados con su importación de origen.

| Columna | Tipo | Notas |
|--------|------|-------|
| id | PK | |
| import_id | FK → imports.id | borrar la importación elimina sus ventas (cascade) |
| fecha | date | indexado |
| producto / categoria | varchar | indexados |
| cantidad | int | > 0 (validado en importación) |
| precio_unitario | numeric(12,2) | ≥ 0 (validado en importación) |
| total | numeric(14,2) | `cantidad × precio_unitario` |
| row_warnings | JSON | discrepancias detectadas (no se silencian) |
| created_at | datetime | |

Índices: `fecha`, `categoria`, `producto`, `import_id`.

## Importación de datos

Columnas esperadas (se aceptan alias en español e inglés):

| Columna | Alias aceptados |
|--------|-----------------|
| fecha | date, fecha_venta, dia |
| producto | product, item, articulo, nombre_producto |
| categoria | category, rubro |
| cantidad | quantity, qty, unidades |
| precio_unitario | precio, price, unit_price, precio_venta |
| ventas_totales *(opcional)* | total, total_sales, monto, importe |

**Flujo en dos fases (nada se borra en silencio):**

1. `POST /api/imports` — valida extensión, tamaño (≤ 5 MB) y **contenido real**
   (Pandas debe poder parsearlo), analiza fila por fila y crea una importación `pending`
   con el resumen: filas totales, aceptadas, rechazadas y duplicadas, más la lista de
   errores por fila (fila, campo, mensaje claro).
2. El usuario **revisa** los errores en la interfaz y decide:
   - `POST /api/imports/{id}/confirm` → inserta las filas aceptadas en una transacción.
   - `DELETE /api/imports/{id}` → descarta la importación pendiente.

**Validaciones por fila:** fecha inválida/vacía, producto o categoría vacíos,
cantidad no entera o ≤ 0, precio no numérico o negativo.

**Duplicados:** se detectan *dentro del archivo* con la clave
`(fecha, producto, categoría, cantidad, precio_unitario)`. Las repeticiones posteriores
a la primera se cuentan como `duplicate` y se reportan; **no** se insertan como ventas.

## Cálculos y decisiones

- **Total de una venta** = `cantidad × precio_unitario` (fuente de verdad). Si el archivo
  trae una columna de "ventas totales" cuya diferencia con el cálculo supera `0.01`, se
  conserva el valor calculado y se registra una **advertencia** visible en el detalle de
  la venta. No se descarta ni se corrige silenciosamente.
- **Ingresos totales** = Σ `total` de las ventas que cumplen los filtros activos.
- **Número de ventas** = conteo de filas filtradas.
- **Ticket promedio** = ingresos totales / número de ventas (0 si no hay ventas).
- **Producto más vendido** = producto con mayor Σ `total` en el conjunto filtrado.
- **Comparación de periodos**: el periodo anterior tiene la **misma duración** que el rango
  seleccionado y termina justo antes de su inicio. Las variaciones se expresan en %;
  si el periodo previo no tiene ingresos, la variación se muestra como `null` (sin división por cero).
- **Series temporales**: granularidad día/semana/mes. Las semanas usan el año-semana ISO.

## Endpoints de la API

Base: `/api`

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado de la API y de la base de datos |
| POST | `/imports` | Sube CSV/Excel → analiza y crea importación `pending` |
| GET | `/imports` | Historial paginado de importaciones |
| GET | `/imports/{id}` | Detalle de una importación + errores por fila |
| POST | `/imports/{id}/confirm` | Confirma y carga las ventas aceptadas |
| DELETE | `/imports/{id}` | Descartar/eliminar importación y sus ventas |
| GET | `/sales` | Ventas paginadas con filtros y orden |
| GET | `/sales/{id}` | Detalle de una venta |
| GET | `/analytics/summary` | KPIs + comparación opcional (`compare=true`) |
| GET | `/analytics/timeseries` | Serie temporal (`granularity=day\|week\|month`) |
| GET | `/analytics/categories` | Distribución de ingresos por categoría |
| GET | `/analytics/products` | Ranking de productos (`limit`) |
| GET | `/analytics/dimensions` | Productos y categorías disponibles para filtros |
| GET | `/reports/csv` | Descarga CSV de las ventas filtradas |
| GET | `/reports/pdf` | Reporte PDF (KPIs + tablas + gráficos) |
| POST | `/demo/seed` · DELETE `/demo/seed` | Cargar / eliminar datos de demostración |

**Filtros comunes** (en ventas, analítica y reportes): `date_from`, `date_to`,
`product`, `category`, `import_id`. Ventas añade `page`, `page_size`, `sort_by`, `sort_order`.

Errores: 400 (datos inválidos), 404 (no encontrado), 413 (archivo demasiado grande),
415 (tipo no admitido), 422 (parámetros inválidos). Las respuestas de error solo exponen
un mensaje `detail` legible; nunca trazas internas.

## Pruebas

### Backend (Pytest) — 35 pruebas

```bash
cd backend
python -m pytest
```

Cubren: estado de la API; importación CSV y Excel válidos; extensión no admitida;
archivo vacío; columnas faltantes; filas con fecha/producto/cantidad/precio inválidos;
duplicados; confirmación y conflicto al confirmar dos veces; borrado de importación y
sus ventas; paginación; filtros por fecha/producto/categoría; orden; detalle 404;
resultados vacíos; KPIs; comparación de periodos; series por día/mes; categorías y
productos; dataset vacío; reporte CSV (contenido y filtros); reporte PDF (cabecera `%PDF`);
datos demo (creación, idempotencia, etiqueta `is_demo`, reinicio).

Los archivos de prueba se generan en runtime (`tests/fixtures/build_files.py`), por lo que
el conjunto es reproducible y no depende de binarios versionados.

### Frontend (Vitest)

```bash
cd frontend
npm run test
```

Pruebas de componentes: `KpiCard` (etiqueta, valor, variación, hint), estados de interfaz
(`LoadingState`, `ErrorState`, `EmptyState`) y `FilterBar` (campos y captura de fecha).

## Variables de entorno

Copia `.env.example` a `.env`. **No contiene secretos reales.**

| Variable | Descripción | Por defecto |
|---------|-------------|-------------|
| `DATABASE_URL` | Cadena de conexión SQLAlchemy | `sqlite:///./dev.db` |
| `MAX_UPLOAD_MB` | Tamaño máximo de archivo | `5` |
| `CORS_ORIGINS` | Orígenes permitidos (coma) | `http://localhost:5173,...` |
| `UPLOAD_DIR` | Carpeta de archivos subidos | `uploads` |
| `VITE_API_BASE` | Base de la API en el frontend | `/api` |

Para usar PostgreSQL basta cambiar `DATABASE_URL` y añadir `psycopg2-binary`
(la capa ORM es idéntica; no requiere cambios de código).

## Datos de demostración

`POST /api/demo/seed` genera ~12 meses de ventas ficticias (varios productos y
categorías, precios y cantidades aleatorios reproducibles) bajo una importación
marcada con `is_demo=true` y nombre `DEMO-datos-ficticios.csv`. Es **idempotente**:
si ya existen datos demo no los duplica. `DELETE /api/demo/seed` los elimina.

En la interfaz, el Dashboard muestra un aviso permanente indicando que son datos
ficticios, y el historial de importaciones marca estas cargas con la etiqueta `DEMO`.

## Limitaciones conocidas

- **Sin autenticación** en esta versión: cualquiera con el enlace ve y modifica los datos.
  Si se añade multiusuario, cada usuario deberá acceder solo a sus propios datos
  (filtro por propietario en las consultas).
- **Sin Docker/Compose**: se incluye el despliegue gestionado en la nube (`render.yaml` +
  `frontend/vercel.json`) en lugar de contenedores.
- **Sin migraciones (Alembic)**: el esquema se crea con `create_all`. Para evolución
  del esquema en producción se recomienda añadir Alembic.
- **Sqlite por defecto en local**: para producción usar PostgreSQL cambiando `DATABASE_URL`
  (Render lo configura automáticamente vía `render.yaml`).
- **Plan free de Render**: el servicio se suspende tras unos minutos de inactividad; el
  primer acceso tarda unos segundos. La base PostgreSQL free tiene límite de almacenamiento.
- **Subidas de archivos en la nube**: el backend guarda las filas aceptadas en la base de
  datos, por lo que la confirmación no depende del disco. El archivo original en
  `UPLOAD_DIR` (por defecto `/tmp`) es solo respaldo y puede perderse al reiniciar.
- El reporte PDF usa gráficos nativos de ReportLab (no pixel-idénticos a los de Recharts),
  pero refleja los mismos datos filtrados.
- Los errores por importación se almacenan hasta un máximo de 500 por archivo.

## Licencia

Uso educativo / portafolio.

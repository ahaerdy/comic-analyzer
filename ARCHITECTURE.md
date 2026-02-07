# 🏗️ Comic Collection Manager - Architecture

> **Arquitetura completa do sistema de gerenciamento de coleções de comics**  
> Versão: 2.0 (Sistema Completo com Backend e Frontend)

---

## 📖 Índice

- [Visão Geral](#-visão-geral)
- [Estado Atual](#-estado-atual)
- [Arquitetura de 3 Camadas](#-arquitetura-de-3-camadas)
- [Decisões Técnicas](#-decisões-técnicas)
- [Backend API](#-backend-api)
- [Frontend Application](#-frontend-application)
- [Fluxo de Dados](#-fluxo-de-dados)
- [Estrutura de Diretórios](#-estrutura-de-diretórios)
- [Roadmap de Implementação](#-roadmap-de-implementação)
- [Considerações de Deploy](#-considerações-de-deploy)

---

## 🎯 Visão Geral

O Comic Collection Manager é um sistema de 3 camadas para catalogação, identificação e gerenciamento de grandes coleções de comics digitais (20k+ arquivos).

### Filosofia do Projeto

**Separação de Responsabilidades:**
- **Data Layer (Python)** → Constrói e mantém o banco de dados
- **Business Layer (Node.js)** → Expõe API REST
- **Presentation Layer (React)** → Interface visual

**Por que essa separação?**
1. Scripts Python rodam em batch (horas)
2. Backend serve dados rapidamente (ms)
3. Frontend atualiza sem reprocessar dados

---

## ✅ Estado Atual

### **Fase 1: Data Layer** (CONCLUÍDO - POC)

**Scripts Python desenvolvidos:**
- ✅ `comic_scanner.py` - Escaneia arquivos e cria inventário
- ✅ `comic_identifier.py` - Identifica via Comic Vine API
- ✅ `comic_enricher.py` - Busca metadados detalhados
- ✅ `comic_analyzer.py` - Análise e relatórios
- ✅ `comic_recleaner.py` - Re-processa nomes
- ✅ `comic_dbcheck.py` - Diagnóstico
- ✅ `comic_path_updater.py` - Sincroniza caminhos

**Resultado:**
- 📦 Banco SQLite com 32 campos
- 📊 22.021 comics catalogados
- ✅ ~90% identificados automaticamente
- 📚 Metadados completos (autores, sinopse, personagens)

### **Próximas Fases**

- 🚧 **Fase 2:** Backend API (Node.js + Express)
- 🔮 **Fase 3:** Frontend (React)
- 🔮 **Fase 4:** Features avançadas

---

## 🏛️ Arquitetura de 3 Camadas

```
┌─────────────────────────────────────────────────────────────────┐
│                   CAMADA 1: DATA LAYER                          │
│                      (Python Scripts)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Responsabilidades:                                             │
│  • Escanear sistema de arquivos                                 │
│  • Extrair metadados dos nomes de arquivo                       │
│  • Identificar comics via Comic Vine API                        │
│  • Enriquecer com dados detalhados                              │
│  • Manter integridade do banco de dados                         │
│                                                                 │
│  Tecnologias:                                                   │
│  • Python 3.8+                                                  │
│  • SQLite3 (built-in)                                           │
│  • requests (HTTP client)                                       │
│                                                                 │
│  Características:                                               │
│  • Batch processing (horas)                                     │
│  • Retomável (salva progresso)                                  │
│  • Rate limiting automático                                     │
│  • Resiliência a erros                                          │
│                                                                 │
│  Output:                                                        │
│  📦 comics_inventory.db (SQLite)                                │
│     └─ 32 campos x 20k+ registros                               │
│                                                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       │ SQLite Database
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                 CAMADA 2: BUSINESS LAYER                        │
│                   (Backend API - Node.js)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Responsabilidades:                                             │
│  • Expor API REST para frontend                                 │
│  • Consultas rápidas ao SQLite                                  │
│  • Servir capas de comics                                       │
│  • Integração com YACReader                                     │
│  • Business logic (favoritos, leitura, etc)                     │
│                                                                 │
│  Tecnologias:                                                   │
│  • Node.js 18+                                                  │
│  • Express (framework web)                                      │
│  • better-sqlite3 (SQLite driver)                               │
│  • CORS (cross-origin)                                          │
│                                                                 │
│  Características:                                               │
│  • Respostas em milissegundos                                   │
│  • RESTful API design                                           │
│  • Stateless (escalável)                                        │
│  • Cache inteligente                                            │
│                                                                 │
│  Endpoints:                                                     │
│  GET  /api/comics           - Lista comics                      │
│  GET  /api/comics/:id       - Detalhes                          │
│  GET  /api/series           - Lista séries                      │
│  GET  /api/search?q=...     - Busca                             │
│  POST /api/comics/:id/open  - Abre no YACReader                 │
│  GET  /api/covers/:id       - Serve capa                        │
│                                                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       │ HTTP/REST API
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│               CAMADA 3: PRESENTATION LAYER                      │
│                    (Frontend - React)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Responsabilidades:                                             │
│  • Interface visual do usuário                                  │
│  • Grid de comics com capas                                     │
│  • Busca e filtros avançados                                    │
│  • Visualização de detalhes                                     │
│  • Sistema de favoritos/lidos                                   │
│                                                                 │
│  Tecnologias:                                                   │
│  • React 18+                                                    │
│  • TypeScript (type safety)                                     │
│  • Tailwind CSS (styling)                                       │
│  • React Router (navegação)                                     │
│  • React Query (data fetching)                                  │
│  • react-window (virtualização)                                 │
│                                                                 │
│  Características:                                               │
│  • SPA (Single Page Application)                                │
│  • Virtualização (performance)                                  │
│  • Lazy loading de imagens                                      │
│  • Responsive design                                            │
│  • Cache local (React Query)                                    │
│                                                                 │
│  Principais Views:                                              │
│  • Home (grid de comics)                                        │
│  • Comic Detail (ficha completa)                                │
│  • Series View (edições da série)                               │
│  • Search Results                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🤔 Decisões Técnicas

### Por Que Python no Data Layer?

✅ **Vantagens:**
- Scripts simples e legíveis
- SQLite built-in
- Requests library (HTTP client robusto)
- Batch processing natural
- Fácil manutenção

❌ **Não é bom para:**
- API em tempo real (ms)
- Interface gráfica
- Concorrência alta

**Decisão:** Python perfeito para construir/manter banco. Não para servir dados.

---

### Por Que Node.js + Express no Backend?

#### **Opção 1: Node.js + Express** ✅ ESCOLHIDA

**Vantagens:**
- ✅ Desenvolvimento rápido (~100 linhas para API funcional)
- ✅ Mesma linguagem do frontend (JavaScript/TypeScript)
- ✅ SQLite integration excelente (better-sqlite3)
- ✅ Ecossistema rico (npm)
- ✅ Perfeito para POC e biblioteca pessoal
- ✅ Fácil deploy (PM2, Docker)

**Desvantagens:**
- ⚠️ Menos estruturado que Spring Boot
- ⚠️ Type safety requer TypeScript

**Quando usar:**
- 👤 Projeto pessoal
- 🚀 POC/MVP
- 📦 < 100k usuários
- 🏃 Desenvolvimento solo/pequeno time

#### **Opção 2: Spring Boot** ❌ NÃO ESCOLHIDA (para este projeto)

**Vantagens:**
- ✅ Enterprise-grade
- ✅ Type safety nativo (Java)
- ✅ Arquitetura muito estruturada
- ✅ Escalável para milhões

**Desvantagens:**
- ❌ Verboso (~500 linhas para mesma API)
- ❌ Curva de aprendizado íngreme
- ❌ Overkill para POC
- ❌ Build/deploy mais complexo

**Quando usar:**
- 🏢 Ambiente corporativo
- 👥 Time grande (10+ devs)
- 📈 Produto comercial
- 💰 Milhões de usuários

---

### Por Que React no Frontend?

✅ **Vantagens:**
- Maior ecossistema
- React Query (cache/data fetching)
- react-window (virtualização para 20k+ itens)
- Component reusability
- React Native (futuro mobile)

**Alternativas consideradas:**
- Vue.js - Bom, mas ecossistema menor
- Angular - Muito pesado para este caso
- Svelte - Muito novo, poucas libraries

---

## 🔌 Backend API

### Tecnologias

```json
{
  "dependencies": {
    "express": "^4.18.0",
    "better-sqlite3": "^9.0.0",
    "cors": "^2.8.5",
    "dotenv": "^16.0.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.0"
  }
}
```

---

### Estrutura do Backend

```
backend/
├── src/
│   ├── server.js              # Entry point
│   ├── config/
│   │   └── database.js        # SQLite connection
│   ├── routes/
│   │   ├── comics.js          # /api/comics
│   │   ├── series.js          # /api/series
│   │   ├── publishers.js      # /api/publishers
│   │   ├── search.js          # /api/search
│   │   └── covers.js          # /api/covers
│   ├── controllers/
│   │   ├── comicsController.js
│   │   ├── seriesController.js
│   │   └── searchController.js
│   ├── services/
│   │   ├── comicService.js    # Business logic
│   │   └── yacreaderService.js # YACReader integration
│   ├── middleware/
│   │   ├── errorHandler.js
│   │   └── validator.js
│   └── utils/
│       └── helpers.js
├── tests/
├── package.json
├── .env.example
└── README.md
```

---

### API Endpoints

#### **GET /api/comics**
Lista comics com paginação e filtros

**Query params:**
```javascript
?page=1              // Página (default: 1)
&limit=50            // Items por página (default: 50, max: 100)
&status=identified   // Filtro por status
&publisher=Marvel    // Filtro por editora
&series=Batman       // Filtro por série
&sort=volume_name    // Ordenação
&order=asc           // asc/desc
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "file_name": "Batman.001.cbr",
      "volume_name": "Batman (1940)",
      "issue_number": "1",
      "publisher": "DC Comics",
      "writers": "Bill Finger",
      "cover_url": "https://...",
      "status": "identified"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 19500,
    "pages": 390
  }
}
```

---

#### **GET /api/comics/:id**
Detalhes completos de um comic

**Response:**
```json
{
  "id": 1,
  "file_path": "/comics/Batman.001.cbr",
  "file_name": "Batman.001.cbr",
  "file_size": 45678900,
  "volume_name": "Batman (1940)",
  "issue_number": "1",
  "year": "1940",
  "publisher": "DC Comics",
  "description": "The first appearance of Batman...",
  "cover_date": "1940-05-01",
  "writers": "Bill Finger",
  "pencilers": "Bob Kane",
  "inkers": "Jerry Robinson",
  "colorists": "...",
  "characters": "Batman, Robin, Joker",
  "teams": "Dynamic Duo",
  "cover_url": "https://comicvine.gamespot.com/...",
  "site_detail_url": "https://comicvine.gamespot.com/batman-1-...",
  "status": "identified"
}
```

---

#### **GET /api/series**
Lista todas as séries

**Response:**
```json
{
  "data": [
    {
      "volume_name": "Batman (1940)",
      "publisher": "DC Comics",
      "count": 713,
      "first_issue": "1",
      "last_issue": "713",
      "year_start": "1940",
      "year_end": "2011"
    }
  ]
}
```

---

#### **GET /api/series/:name**
Comics de uma série específica

**Response:**
```json
{
  "series": {
    "volume_name": "Batman (1940)",
    "publisher": "DC Comics",
    "count": 85
  },
  "issues": [
    {
      "id": 1,
      "issue_number": "1",
      "cover_date": "1940-05-01",
      "writers": "Bill Finger",
      "cover_url": "..."
    }
  ]
}
```

---

#### **GET /api/search**
Busca por título

**Query params:**
```javascript
?q=batman            // Query de busca
&limit=20            // Limite de resultados
```

**Response:**
```json
{
  "query": "batman",
  "results": [
    {
      "id": 1,
      "volume_name": "Batman (1940)",
      "issue_number": "1",
      "cover_url": "..."
    }
  ],
  "count": 1250
}
```

---

#### **POST /api/comics/:id/open**
Abre comic no YACReader

**Response:**
```json
{
  "success": true,
  "message": "Comic opened in YACReader"
}
```

---

#### **GET /api/covers/:id/:size.jpg**
Serve capa do comic

**Params:**
- `:id` - ID do comic
- `:size` - `thumbnail` | `medium` | `original`

**Response:**
- Status 200 + imagem JPEG
- Status 404 + placeholder

---

#### **GET /api/stats**
Estatísticas gerais

**Response:**
```json
{
  "total_comics": 22021,
  "identified": 19950,
  "not_found": 100,
  "pending": 0,
  "publishers": {
    "Marvel": 8500,
    "DC Comics": 7200,
    "Image": 2100
  },
  "top_series": [
    {"name": "Batman (1940)", "count": 713},
    {"name": "Amazing Spider-Man", "count": 698}
  ]
}
```

---

### Exemplo de Implementação (server.js)

```javascript
const express = require('express');
const Database = require('better-sqlite3');
const cors = require('cors');
const { spawn } = require('child_process');

const app = express();
const db = new Database('../database/comics_inventory.db', { readonly: true });

app.use(cors());
app.use(express.json());

// GET /api/comics
app.get('/api/comics', (req, res) => {
  const page = parseInt(req.query.page) || 1;
  const limit = Math.min(parseInt(req.query.limit) || 50, 100);
  const offset = (page - 1) * limit;
  
  const { status, publisher, series } = req.query;
  
  let query = 'SELECT * FROM comics WHERE 1=1';
  const params = [];
  
  if (status) {
    query += ' AND status = ?';
    params.push(status);
  }
  
  if (publisher) {
    query += ' AND publisher = ?';
    params.push(publisher);
  }
  
  if (series) {
    query += ' AND volume_name LIKE ?';
    params.push(`%${series}%`);
  }
  
  query += ' ORDER BY volume_name, issue_number LIMIT ? OFFSET ?';
  params.push(limit, offset);
  
  const comics = db.prepare(query).all(...params);
  
  const totalQuery = 'SELECT COUNT(*) as count FROM comics WHERE 1=1' + 
    (status ? ' AND status = ?' : '') +
    (publisher ? ' AND publisher = ?' : '') +
    (series ? ' AND volume_name LIKE ?' : '');
  
  const countParams = [status, publisher, series && `%${series}%`].filter(Boolean);
  const total = db.prepare(totalQuery).get(...countParams);
  
  res.json({
    data: comics,
    pagination: {
      page,
      limit,
      total: total.count,
      pages: Math.ceil(total.count / limit)
    }
  });
});

// GET /api/comics/:id
app.get('/api/comics/:id', (req, res) => {
  const comic = db.prepare('SELECT * FROM comics WHERE id = ?').get(req.params.id);
  
  if (!comic) {
    return res.status(404).json({ error: 'Comic not found' });
  }
  
  res.json(comic);
});

// POST /api/comics/:id/open
app.post('/api/comics/:id/open', (req, res) => {
  const comic = db.prepare('SELECT file_path FROM comics WHERE id = ?').get(req.params.id);
  
  if (!comic) {
    return res.status(404).json({ error: 'Comic not found' });
  }
  
  // Abre no YACReader
  const child = spawn('yacreader', [comic.file_path], {
    detached: true,
    stdio: 'ignore'
  });
  child.unref();
  
  res.json({ success: true, message: 'Comic opened in YACReader' });
});

// GET /api/stats
app.get('/api/stats', (req, res) => {
  const stats = {
    total_comics: db.prepare('SELECT COUNT(*) as count FROM comics').get().count,
    identified: db.prepare('SELECT COUNT(*) as count FROM comics WHERE status = "identified"').get().count,
    not_found: db.prepare('SELECT COUNT(*) as count FROM comics WHERE status = "not_found"').get().count,
    pending: db.prepare('SELECT COUNT(*) as count FROM comics WHERE status = "pending"').get().count,
  };
  
  const publishers = db.prepare(`
    SELECT publisher, COUNT(*) as count 
    FROM comics 
    WHERE publisher IS NOT NULL 
    GROUP BY publisher 
    ORDER BY count DESC 
    LIMIT 10
  `).all();
  
  stats.publishers = Object.fromEntries(publishers.map(p => [p.publisher, p.count]));
  
  const topSeries = db.prepare(`
    SELECT volume_name, COUNT(*) as count 
    FROM comics 
    WHERE volume_name IS NOT NULL 
    GROUP BY volume_name 
    ORDER BY count DESC 
    LIMIT 20
  `).all();
  
  stats.top_series = topSeries;
  
  res.json(stats);
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`🚀 Backend API running on http://localhost:${PORT}`);
});
```

**~150 linhas** para um backend completo e funcional!

---

## ⚛️ Frontend Application

### Tecnologias

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@tanstack/react-query": "^5.0.0",
    "axios": "^1.6.0",
    "tailwindcss": "^3.3.0",
    "react-window": "^1.8.10"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0",
    "typescript": "^5.3.0"
  }
}
```

---

### Estrutura do Frontend

```
frontend/
├── public/
│   └── placeholder.jpg        # Capa padrão
├── src/
│   ├── components/
│   │   ├── ComicCard.tsx      # Card individual
│   │   ├── ComicGrid.tsx      # Grid virtualizado
│   │   ├── ComicDetail.tsx    # Ficha completa
│   │   ├── SearchBar.tsx      # Barra de busca
│   │   ├── Filters.tsx        # Filtros (editora, série)
│   │   ├── Navbar.tsx         # Menu de navegação
│   │   └── Pagination.tsx     # Paginação
│   ├── pages/
│   │   ├── Home.tsx           # Grid principal
│   │   ├── ComicPage.tsx      # Detalhes do comic
│   │   ├── SeriesPage.tsx     # Lista de séries
│   │   ├── SeriesView.tsx     # Edições de uma série
│   │   └── SearchResults.tsx  # Resultados de busca
│   ├── services/
│   │   └── api.ts             # Axios config + endpoints
│   ├── hooks/
│   │   ├── useComics.ts       # React Query hook
│   │   ├── useSeries.ts
│   │   └── useSearch.ts
│   ├── types/
│   │   └── Comic.ts           # TypeScript types
│   ├── utils/
│   │   └── helpers.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── tailwind.config.js
├── vite.config.ts
├── package.json
└── README.md
```

---

### Componentes Principais

#### **ComicCard.tsx**
Card individual para o grid

```tsx
interface Comic {
  id: number;
  volume_name: string;
  issue_number: string;
  cover_url?: string;
  publisher: string;
}

export function ComicCard({ comic }: { comic: Comic }) {
  const coverUrl = comic.cover_url 
    ? `/api/covers/${comic.id}/medium.jpg`
    : '/placeholder.jpg';
  
  return (
    <div className="group cursor-pointer">
      <div className="aspect-[2/3] overflow-hidden rounded-lg shadow-lg">
        <img 
          src={coverUrl}
          alt={`${comic.volume_name} #${comic.issue_number}`}
          loading="lazy"
          className="w-full h-full object-cover group-hover:scale-110 transition"
          onError={(e) => e.currentTarget.src = '/placeholder.jpg'}
        />
      </div>
      <div className="mt-2">
        <h3 className="font-semibold text-sm truncate">{comic.volume_name}</h3>
        <p className="text-xs text-gray-600">#{comic.issue_number}</p>
      </div>
    </div>
  );
}
```

---

#### **ComicGrid.tsx**
Grid virtualizado (performance para 20k+ items)

```tsx
import { FixedSizeGrid as Grid } from 'react-window';
import { useComics } from '../hooks/useComics';

export function ComicGrid() {
  const { data, isLoading } = useComics({ page: 1, limit: 1000 });
  
  if (isLoading) return <div>Loading...</div>;
  
  const COLUMN_COUNT = 5;
  const COLUMN_WIDTH = 200;
  const ROW_HEIGHT = 320;
  
  const Row = ({ columnIndex, rowIndex, style }: any) => {
    const index = rowIndex * COLUMN_COUNT + columnIndex;
    const comic = data?.data[index];
    
    if (!comic) return null;
    
    return (
      <div style={style}>
        <ComicCard comic={comic} />
      </div>
    );
  };
  
  return (
    <Grid
      columnCount={COLUMN_COUNT}
      columnWidth={COLUMN_WIDTH}
      height={800}
      rowCount={Math.ceil((data?.data.length || 0) / COLUMN_COUNT)}
      rowHeight={ROW_HEIGHT}
      width={COLUMN_COUNT * COLUMN_WIDTH}
    >
      {Row}
    </Grid>
  );
}
```

---

#### **ComicDetail.tsx**
Ficha completa do comic

```tsx
import { useParams } from 'react-router-dom';
import { useComic } from '../hooks/useComics';

export function ComicDetail() {
  const { id } = useParams();
  const { data: comic, isLoading } = useComic(id!);
  
  if (isLoading) return <div>Loading...</div>;
  if (!comic) return <div>Comic not found</div>;
  
  const handleOpen = async () => {
    await fetch(`/api/comics/${id}/open`, { method: 'POST' });
  };
  
  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="grid grid-cols-3 gap-8">
        {/* Capa */}
        <div>
          <img 
            src={comic.cover_url || '/placeholder.jpg'}
            alt={comic.volume_name}
            className="w-full rounded-lg shadow-2xl"
          />
          <button 
            onClick={handleOpen}
            className="w-full mt-4 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700"
          >
            📖 Abrir no YACReader
          </button>
        </div>
        
        {/* Detalhes */}
        <div className="col-span-2">
          <h1 className="text-4xl font-bold mb-2">{comic.volume_name}</h1>
          <p className="text-xl text-gray-600 mb-4">Issue #{comic.issue_number}</p>
          
          {comic.writers && (
            <div className="mb-4">
              <h2 className="font-semibold text-gray-700">Writers</h2>
              <p>{comic.writers}</p>
            </div>
          )}
          
          {comic.pencilers && (
            <div className="mb-4">
              <h2 className="font-semibold text-gray-700">Artists</h2>
              <p>{comic.pencilers}</p>
            </div>
          )}
          
          {comic.description && (
            <div className="mb-4">
              <h2 className="font-semibold text-gray-700 mb-2">Synopsis</h2>
              <div 
                className="prose"
                dangerouslySetInnerHTML={{ __html: comic.description }}
              />
            </div>
          )}
          
          {comic.characters && (
            <div className="mb-4">
              <h2 className="font-semibold text-gray-700">Characters</h2>
              <p>{comic.characters}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

#### **useComics.ts**
React Query hook

```tsx
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3001/api'
});

export function useComics(params: { page: number; limit: number }) {
  return useQuery({
    queryKey: ['comics', params],
    queryFn: async () => {
      const { data } = await api.get('/comics', { params });
      return data;
    },
    staleTime: 1000 * 60 * 5 // Cache por 5 minutos
  });
}

export function useComic(id: string) {
  return useQuery({
    queryKey: ['comic', id],
    queryFn: async () => {
      const { data } = await api.get(`/comics/${id}`);
      return data;
    }
  });
}
```

---

## 🔄 Fluxo de Dados

### Pipeline Completo

```
1. CONSTRUÇÃO DO BANCO (Python - uma vez)
   ↓
   [Arquivos CBR/CBZ] 
   → comic_scanner.py (5-10 min)
   → comic_identifier.py (10-15h)
   → comic_enricher.py (2-3h)
   ↓
   [comics_inventory.db] ← Banco pronto!

2. BACKEND SERVINDO (Node.js - sempre ativo)
   ↓
   [Express Server]
   → Lê SQLite (< 10ms por query)
   → Expõe REST API
   ↓
   [HTTP/JSON]

3. FRONTEND CONSUMINDO (React - browser)
   ↓
   [React App]
   → Chama API via Axios
   → React Query (cache)
   → Renderiza UI
   ↓
   [Usuário vê na tela]
```

### Exemplo de Request Completo

```
1. Usuário clica em "Batman" na busca
   ↓
2. React: GET /api/search?q=batman
   ↓
3. Express: SELECT * FROM comics WHERE volume_name LIKE '%batman%'
   ↓
4. SQLite: Retorna 1.250 resultados em 8ms
   ↓
5. Express: JSON response
   ↓
6. React Query: Cache local
   ↓
7. React: Renderiza grid com 1.250 cards
   ↓
8. react-window: Virtualiza (só renderiza 50 visíveis)
   ↓
9. Usuário vê Batman comics em 50ms total!
```

---

## 📁 Estrutura de Diretórios

### Projeto Completo

```
comic-collection-manager/
│
├── README.md                      # Guia de uso (scripts Python)
├── ARCHITECTURE.md                # Este documento
├── LICENSE
│
├── data-layer/                    # ✅ ATUAL (Python POC)
│   ├── comic_scanner.py
│   ├── comic_identifier.py
│   ├── comic_enricher.py
│   ├── comic_analyzer.py
│   ├── comic_recleaner.py
│   ├── comic_dbcheck.py
│   ├── comic_path_updater.py
│   ├── requirements.txt
│   └── README.md
│
├── backend/                       # 🚧 Fase 2
│   ├── src/
│   │   ├── server.js
│   │   ├── config/
│   │   ├── routes/
│   │   ├── controllers/
│   │   ├── services/
│   │   ├── middleware/
│   │   └── utils/
│   ├── tests/
│   ├── package.json
│   ├── .env.example
│   └── README.md
│
├── frontend/                      # 🔮 Fase 3
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   ├── package.json
│   └── README.md
│
├── database/                      # Compartilhado
│   └── comics_inventory.db        # Gerado pelos scripts Python
│
├── covers/                        # 🔮 Fase 4 (opcional)
│   ├── thumbnails/
│   ├── medium/
│   └── original/
│
└── docs/                          # Documentação extra
    ├── api-design.md
    ├── database-schema.md
    └── deployment.md
```

---

## 🗺️ Roadmap de Implementação

### **Fase 1: Data Layer** ✅ CONCLUÍDA

**Objetivo:** Construir banco de dados com metadados

- [x] Scanner de arquivos
- [x] Identificação via Comic Vine
- [x] Enriquecimento de metadados
- [x] Sistema de análise
- [x] Ferramentas de manutenção
- [x] Documentação completa

**Entrega:** 
- 22k comics catalogados
- 90%+ identificados
- Banco SQLite com 32 campos

**Tempo:** ~17 horas de processamento total

---

### **Fase 2: Backend API** 🚧 PRÓXIMA

**Objetivo:** Expor API REST para consumo

**Tasks:**
- [ ] Setup Node.js + Express
- [ ] Conexão com SQLite (better-sqlite3)
- [ ] Implementar endpoints básicos
  - [ ] GET /api/comics (lista)
  - [ ] GET /api/comics/:id (detalhes)
  - [ ] GET /api/series
  - [ ] GET /api/search
- [ ] Integração YACReader
  - [ ] POST /api/comics/:id/open
- [ ] Sistema de capas
  - [ ] GET /api/covers/:id/:size.jpg
- [ ] CORS configuration
- [ ] Error handling
- [ ] Logging
- [ ] Tests (Jest)
- [ ] Documentação API (Swagger)

**Entrega:**
- API funcional em localhost:3001
- 8+ endpoints
- Taxa de resposta < 50ms
- Integração YACReader

**Tempo estimado:** 2-3 semanas (part-time)

---

### **Fase 3: Frontend MVP** 🔮 FUTURO

**Objetivo:** Interface básica funcional

**Tasks:**
- [ ] Setup React + Vite
- [ ] Configurar React Query
- [ ] Configurar Tailwind CSS
- [ ] Implementar componentes base
  - [ ] ComicCard
  - [ ] ComicGrid (virtualizado)
  - [ ] Navbar
  - [ ] SearchBar
- [ ] Implementar páginas
  - [ ] Home (grid)
  - [ ] ComicDetail
  - [ ] SearchResults
- [ ] Integração com API
- [ ] Loading states
- [ ] Error handling
- [ ] Responsive design

**Entrega:**
- App React funcional
- Grid virtualizado (performance)
- Busca funcional
- Visualização de detalhes

**Tempo estimado:** 3-4 semanas (part-time)

---

### **Fase 4: Features Avançadas** 🔮 FUTURO

**Objetivos:** Melhorias e funcionalidades extras

**Backend:**
- [ ] Download automático de capas
- [ ] Sistema de favoritos
- [ ] Tracking de leitura
- [ ] Notas/ratings
- [ ] Classificação por gênero (Wikidata)
- [ ] Recomendações
- [ ] Autenticação (multi-usuário)

**Frontend:**
- [ ] Filtros avançados
- [ ] Listas customizadas
- [ ] Dark mode
- [ ] Estatísticas visuais (charts)
- [ ] Export de listas
- [ ] PWA (offline support)

**Tempo estimado:** Ongoing

---

## 🚀 Considerações de Deploy

### Development

```bash
# Backend
cd backend
npm install
npm run dev           # localhost:3001

# Frontend
cd frontend
npm install
npm run dev           # localhost:5173
```

---

### Production - Opção 1: Single Server

**Stack:**
- VPS (DigitalOcean, Linode, AWS EC2)
- Ubuntu 22.04
- Nginx (reverse proxy)
- PM2 (process manager)

**Estrutura:**
```
VPS (Ubuntu)
├── Nginx :80/:443
│   ├── /api → localhost:3001 (Backend)
│   └── / → localhost:5173 (Frontend build)
├── PM2
│   └── backend (Node.js)
└── SQLite DB
```

**Deploy:**
```bash
# Backend
cd backend
npm install --production
pm2 start src/server.js --name comic-api

# Frontend
cd frontend
npm run build
# Serve dist/ com nginx
```

---

### Production - Opção 2: Separado

**Backend:**
- Railway.app / Render.com
- SQLite embarcado
- Free tier disponível

**Frontend:**
- Vercel / Netlify
- Deploy automático (Git push)
- CDN global

---

### Docker (Recomendado)

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "3001:3001"
    volumes:
      - ./database:/app/database
      - ./covers:/app/covers
    environment:
      - NODE_ENV=production
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

**Deploy:**
```bash
docker-compose up -d
```

---

## 📊 Performance Esperada

### Backend (Node.js + SQLite)

| Endpoint | Registros | Tempo Esperado |
|----------|-----------|----------------|
| GET /api/comics | 50 | < 10ms |
| GET /api/comics/:id | 1 | < 5ms |
| GET /api/search | 100 | < 20ms |
| GET /api/stats | Agregado | < 50ms |

**Bottleneck:** Servir capas (se não cacheadas)

---

### Frontend (React)

| Ação | Tempo Esperado |
|------|----------------|
| Initial Load | < 2s |
| Navigate | < 100ms |
| Search | < 300ms (com debounce) |
| Open Detail | < 150ms |
| Scroll Grid | 60 FPS (react-window) |

**Bottleneck:** Download de imagens (lazy loading resolve)

---

## 🎓 Aprendizados

### Por Que Esta Arquitetura?

1. **Separação de concerns**
   - Python faz batch processing
   - Node.js serve dados rapidamente
   - React cuida da UI

2. **Performance**
   - SQLite é rápido para leitura (< 10ms)
   - React virtualiza grandes listas
   - Cache em múltiplas camadas

3. **Manutenibilidade**
   - Cada camada independente
   - Fácil substituir partes
   - TypeScript previne bugs

4. **Escalabilidade**
   - Backend pode ser replicado
   - Frontend em CDN
   - DB pode migrar para PostgreSQL se necessário

---

## 📚 Referências

### Tecnologias

- **Python:** https://docs.python.org/3/
- **Node.js:** https://nodejs.org/docs/
- **Express:** https://expressjs.com/
- **React:** https://react.dev/
- **SQLite:** https://www.sqlite.org/docs.html
- **React Query:** https://tanstack.com/query/latest

### APIs

- **Comic Vine API:** https://comicvine.gamespot.com/api/

### Tools

- **YACReader:** https://www.yacreader.com/

---

## 🤝 Contribuindo

Este projeto está em desenvolvimento ativo. Sugestões e contribuições são bem-vindas!

**Áreas que precisam de ajuda:**
- [ ] Testes automatizados
- [ ] Documentação da API (Swagger/OpenAPI)
- [ ] Classificação de gêneros (ML)
- [ ] Mobile app (React Native)
- [ ] Detecção de duplicatas

---

## 📄 Licença

MIT License

---

**Versão:** 2.0 (Arquitetura Completa)  
**Última atualização:** Fevereiro 2026  
**Autor:** Arthur Haerdy
**Status:** Data Layer completo | Backend/Frontend em planejamento

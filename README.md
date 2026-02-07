# 🎨 Comic Collection Manager

**Sistema de catalogação automatizada de comics usando Comic Vine API**  
Este projeto é uma **Prova de Conceito (POC)** dividido em vários módulos escritos em Python.

---

## 📖 Índice

- [O Que É](#-o-que-é)
- [Como Funciona](#-como-funciona)
- [Instalação](#-instalação)
- [Uso Passo a Passo](#-uso-passo-a-passo)
- [Scripts Disponíveis](#-scripts-disponíveis)
- [Estrutura do Banco](#-estrutura-do-banco)
- [Troubleshooting](#-troubleshooting)
- [Workflow Completo](#-workflow-completo)

---

## 🎯 O Que É

Transforma sua coleção desorganizada de comics digitais em um banco de dados completo e pesquisável com metadados do Comic Vine.

### Antes:
```
/comics/Batman.001.cbr
/comics/batman_002_2020_DCP_Digital.cbz  
/comics/BATMAN-003-Mephisto.cbr
```

### Depois:
```sql
ID: 1 | Batman (1940) #1 | DC Comics
  Roteiro: Bill Finger
  Arte: Bob Kane
  Personagens: Batman, Robin, Joker
  Sinopse: The first appearance of...
```

---

## 🔄 Como Funciona

```
┌─────────────────┐
│ 1. SCANNER      │  Varre pastas e cria inventário
│   (5-10 min)    │  22.000 arquivos → SQLite
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. IDENTIFIER   │  Identifica via Comic Vine API
│   (10-15 horas) │  Busca série + edição
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. ENRICHER     │  Enriquece com metadados
│   (2-3 horas)   │  Autores, sinopse, personagens
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. ANALYZER     │  Consulta e análise
│   (instantâneo) │  Relatórios, buscas, fichas
└─────────────────┘
```

**Total:** ~13-18 horas de processamento para 20k+ comics

---

## 🚀 Instalação

### 1. Pré-requisitos

```bash
# Python 3.8+
python3 --version

# Git (opcional)
git clone https://github.com/seu-usuario/comic-manager.git
cd comic-manager
```

### 2. Dependências

```bash
pip install requests --break-system-packages
```

### 3. API Key do Comic Vine

1. Acesse https://comicvine.gamespot.com/api/
2. Faça login/crie conta
3. Obtenha sua chave gratuita
4. Configure:

```bash
# Linux/Mac
export COMICVINE_API_KEY='sua_chave_aqui'

# Para tornar permanente, adicione ao ~/.bashrc
echo 'export COMICVINE_API_KEY="sua_chave_aqui"' >> ~/.bashrc
source ~/.bashrc

# Windows CMD
set COMICVINE_API_KEY=sua_chave_aqui

# Windows PowerShell
$env:COMICVINE_API_KEY='sua_chave_aqui'
```

---

## 📘 Uso Passo a Passo

### Passo 1: Escanear Coleção ⏱️ 5-10 min

```bash
# Escaneia pasta e cria banco de dados
python3 comic_scanner.py /caminho/dos/comics ~/Downloads
```

**O que acontece:**
- ✅ Cria `comics_inventory.db` em ~/Downloads
- ✅ Cataloga todos os .cbr, .cbz, .pdf
- ✅ Extrai título, edição e ano do nome
- ✅ Status: `pending` (aguardando identificação)

---

### Passo 2: Identificar Comics ⏱️ 10-15 horas

```bash
# SEMPRE teste primeiro com limite
python3 comic_identifier.py --db ~/Downloads/comics_inventory.db --limit 10

# Se tudo OK, processe todos
python3 comic_identifier.py --db ~/Downloads/comics_inventory.db

# Para rodar em background (recomendado)
nohup python3 comic_identifier.py --db ~/Downloads/comics_inventory.db > identification.log 2>&1 &

# Monitorar progresso
tail -f identification.log

# Interromper (se necessário)
# Ctrl+C ou: kill $(pgrep -f comic_identifier)
```

**Durante a execução:**
- ✅ Salva progresso a cada 10 registros
- ✅ Pode ser interrompido e retomado
- ✅ Gerencia rate limits automaticamente
- ✅ Mostra ETA e estatísticas em tempo real

---

### Passo 3: Enriquecer Metadados ⏱️ 2-3 horas

```bash
# Primeira vez: adicionar colunas extras
python3 comic_enricher.py --db ~/Downloads/comics_inventory.db --upgrade-db

# Enriquecer todos comics identificados
python3 comic_enricher.py --db ~/Downloads/comics_inventory.db
```

**Dados adicionados:**
- 📝 Sinopse completa
- ✍️ Roteiristas, desenhistas, coloristas, letristas
- 👥 Personagens, equipes, localizações
- 📖 Arcos de história
- 🎨 URL da capa
- 📅 Datas de publicação

---

### Passo 4: Consultar e Analisar ⏱️ Instantâneo

```bash
# Estatísticas gerais
python3 comic_analyzer.py --db ~/Downloads/comics_inventory.db stats

# Ficha completa de um comic
python3 comic_analyzer.py --db ~/Downloads/comics_inventory.db info 12345

# Buscar por título
python3 comic_analyzer.py --db ~/Downloads/comics_inventory.db search "Batman"

# Listar série completa
python3 comic_analyzer.py --db ~/Downloads/comics_inventory.db series "Amazing Spider-Man"

# Ver não identificados
python3 comic_analyzer.py --db ~/Downloads/comics_inventory.db not-found
```

---

## 🛠️ Scripts Disponíveis

### 📁 comic_scanner.py
**Escaneia diretórios e cria inventário inicial**

```bash
python3 comic_scanner.py <pasta_comics> <pasta_saida>

# Exemplos:
python3 comic_scanner.py /mnt/storage/Comics ~/Downloads
python3 comic_scanner.py . ~/Downloads
```

**O que faz:**
- Varre recursivamente pastas
- Suporta: .cbr, .cbz, .pdf, .cbt, .cb7
- Extrai título, edição e ano dos nomes
- Cria banco SQLite
- Ignora duplicatas automaticamente

---

### 🔍 comic_identifier.py
**Identifica comics via Comic Vine API**

```bash
# Ver status atual
python3 comic_identifier.py --db banco.db --status

# Processar com limite (teste)
python3 comic_identifier.py --db banco.db --limit 100

# Processar todos pendentes
python3 comic_identifier.py --db banco.db

# Exportar para CSV
python3 comic_identifier.py --db banco.db --export
```

**Status possíveis:**
- `pending` → Aguardando identificação
- `identified` → ✅ Identificado com sucesso
- `not_found` → ❌ Não encontrado no Comic Vine
- `error` → ⚠️ Erro durante processamento

---

### 📚 comic_enricher.py
**Enriquece com metadados detalhados**

```bash
# Preparar banco (apenas primeira vez)
python3 comic_enricher.py --db banco.db --upgrade-db

# Enriquecer todos identificados
python3 comic_enricher.py --db banco.db

# Com limite (teste)
python3 comic_enricher.py --db banco.db --limit 50

# Forçar re-enriquecimento
python3 comic_enricher.py --db banco.db --force
```

---

### 📊 comic_analyzer.py
**Análise e consultas do banco**

```bash
# Estatísticas gerais
python3 comic_analyzer.py --db banco.db stats

# Ficha completa
python3 comic_analyzer.py --db banco.db info <ID>

# Buscar título
python3 comic_analyzer.py --db banco.db search "texto"

# Listar série
python3 comic_analyzer.py --db banco.db series "Nome da Série"

# Por editora
python3 comic_analyzer.py --db banco.db publisher "Marvel"

# Não identificados
python3 comic_analyzer.py --db banco.db not-found

# Top 20 séries
python3 comic_analyzer.py --db banco.db top-series
```

---

### 🧹 comic_recleaner.py
**Re-processa nomes e corrige erros**

```bash
# Ver títulos problemáticos
python3 comic_recleaner.py --db banco.db --show-problems

# Re-processar todos os nomes
python3 comic_recleaner.py --db banco.db --reclean

# Resetar erros para 'pending'
python3 comic_recleaner.py --db banco.db --reset-failed

# Re-processar apenas erros
python3 comic_recleaner.py --db banco.db --reclean --status error
```

**Quando usar:**
- Melhoramos a lógica de limpeza
- Muitos comics não identificados
- Quer tentar novamente erros

---

### 🔧 comic_dbcheck.py
**Diagnóstico e verificação do banco**

```bash
# Verificar integridade
python3 comic_dbcheck.py --db banco.db

# Procurar bancos no sistema
python3 comic_dbcheck.py --find
```

---

### 🔄 comic_path_updater.py
**Sincroniza banco com arquivos renomeados/movidos**

```bash
# Ver arquivos órfãos (caminhos quebrados)
python3 comic_path_updater.py --db banco.db --list

# Corrigir automaticamente (por tamanho do arquivo)
python3 comic_path_updater.py --db banco.db --auto-fix /pasta/comics

# Atualizar um registro específico
python3 comic_path_updater.py --db banco.db --update-id 12345 --new-path /novo/caminho.cbr

# Remover registros órfãos
python3 comic_path_updater.py --db banco.db --delete
```

**Quando usar:**
- Renomeou arquivos
- Moveu para outras pastas
- Deletou arquivos
- Reorganizou coleção

**Como funciona:**
- Usa tamanho do arquivo como "impressão digital"
- Taxa de sucesso: ~95%
- Preserva TODOS os metadados do Comic Vine

---

## 💾 Estrutura do Banco

### Tabela: `comics`

**Campos Base (16 colunas):**
```sql
id                   INTEGER PRIMARY KEY
file_path            TEXT UNIQUE NOT NULL     -- Caminho completo
file_name            TEXT NOT NULL            -- Nome do arquivo
file_size            INTEGER                  -- Tamanho em bytes
file_ext             TEXT                     -- .cbr/.cbz/.pdf
clean_title          TEXT                     -- Título extraído
issue_number         TEXT                     -- Número da edição
year                 TEXT                     -- Ano
comicvine_volume_id  INTEGER                  -- ID da série no CV
comicvine_issue_id   INTEGER                  -- ID da edição no CV
volume_name          TEXT                     -- Nome da série
publisher            TEXT                     -- Editora
status               TEXT DEFAULT 'pending'   -- Status
error_message        TEXT                     -- Mensagem de erro
created_at           TIMESTAMP                -- Data criação
updated_at           TIMESTAMP                -- Última atualização
```

**Campos Enriquecidos (16 colunas adicionais):**
```sql
description          TEXT     -- Sinopse completa
cover_date           TEXT     -- Data da capa
store_date           TEXT     -- Data de venda
writers              TEXT     -- Roteiristas
pencilers            TEXT     -- Desenhistas/Arte
inkers               TEXT     -- Arte-finalistas
colorists            TEXT     -- Coloristas
letterers            TEXT     -- Letristas
editors              TEXT     -- Editores
cover_artists        TEXT     -- Artistas de capa
characters           TEXT     -- Personagens (até 10)
teams                TEXT     -- Equipes
locations            TEXT     -- Localizações (até 5)
story_arcs           TEXT     -- Arcos de história
cover_url            TEXT     -- URL da capa (medium)
site_detail_url      TEXT     -- Link para Comic Vine
```

**Total:** 32 campos

---

## 🔄 Gerenciamento de Arquivos

### O Que Fazer Quando Renomear/Mover/Deletar Comics

**Importante:** Seus metadados do Comic Vine **ficam salvos** no banco! Você só precisa atualizar os caminhos.

---

#### 📝 Cenário 1: Renomear Arquivo

```bash
# Antes: Batman.001.cbr
# Depois: Batman-Issue-001-1940.cbr

# Solução (automática):
python3 comic_path_updater.py --db $DB --auto-fix /pasta/comics

# O script usa TAMANHO do arquivo para identificar
# Taxa de sucesso: ~95%
```

---

#### 📂 Cenário 2: Mover para Outra Pasta

```bash
# Antes: /comics/Batman.001.cbr
# Depois: /comics/DC/Batman/Batman.001.cbr

# Solução (automática):
python3 comic_path_updater.py --db $DB --auto-fix /comics
```

---

#### 🗑️ Cenário 3: Deletar Arquivo

```bash
# Deletou o arquivo físico

# 1. Ver registros órfãos
python3 comic_path_updater.py --db $DB --list

# 2. Remover do banco
python3 comic_path_updater.py --db $DB --delete
```

---

#### 🔄 Cenário 4: Reorganização em Massa

```bash
# Reorganizou 5.000+ arquivos

# 1. SEMPRE faça backup primeiro!
cp $DB $DB.backup-$(date +%Y%m%d)

# 2. Mova os arquivos como quiser

# 3. Corrija automaticamente
python3 comic_path_updater.py --db $DB --auto-fix /comics

# 4. Verifique resultado
python3 comic_path_updater.py --db $DB --list

# 5. Limpe órfãos restantes (opcional)
python3 comic_path_updater.py --db $DB --delete
```

---

#### 💡 Fórmula Universal

Para **qualquer** modificação:

```bash
# 1. Listar problemas
python3 comic_path_updater.py --db $DB --list

# 2. Corrigir automaticamente
python3 comic_path_updater.py --db $DB --auto-fix /pasta/raiz

# 3. Limpar órfãos (se necessário)
python3 comic_path_updater.py --db $DB --delete
```

**✅ Seus metadados ficam intactos!** Apenas os caminhos são atualizados.

---

## ❓ Troubleshooting

### ❌ "COMICVINE_API_KEY não configurada"

```bash
# Verificar
echo $COMICVINE_API_KEY

# Se vazio, configurar
export COMICVINE_API_KEY='sua_chave_aqui'

# Tornar permanente
echo 'export COMICVINE_API_KEY="sua_chave"' >> ~/.bashrc
```

---

### ⚠️ Rate limit (erro 420)

**Não se preocupe!** O script gerencia automaticamente:
- Aguarda tempo necessário
- Usa exponential backoff
- Continua processando

**Nada a fazer!** Deixe rodando.

---

### ❌ Muitos "not_found"

```bash
# 1. Ver quais não foram encontrados
python3 comic_analyzer.py --db $DB not-found

# 2. Re-processar nomes (limpeza melhorada)
python3 comic_recleaner.py --db $DB --reclean

# 3. Resetar para 'pending'
python3 comic_recleaner.py --db $DB --reset-failed

# 4. Tentar identificar novamente
python3 comic_identifier.py --db $DB
```

**Taxa normal:** 85-95% de sucesso

---

### 🔄 Processo interrompido

**Pode retomar tranquilamente!**

```bash
# Ver status
python3 comic_identifier.py --db $DB --status

# Continuar de onde parou
python3 comic_identifier.py --db $DB
```

O progresso é salvo a cada 10 registros!

---

### 💾 Banco corrompido

```bash
# Diagnosticar
python3 comic_dbcheck.py --db $DB

# Última opção: recriar (PERDERÁ DADOS!)
rm $DB
python3 comic_scanner.py /pasta/comics ~/Downloads
```

---

## 🔄 Workflow Completo

### ✅ Setup Inicial

```bash
# 1. Definir variáveis (facilita comandos)
export DB=~/Downloads/comics_inventory.db
export COMICS_DIR=/mnt/storage_02/Comics
export COMICVINE_API_KEY='sua_chave_aqui'

# 2. Escanear coleção (5-10 min)
python3 comic_scanner.py $COMICS_DIR ~/Downloads
```

---

### 🔍 Identificação (10-15h)

```bash
# 1. SEMPRE testar primeiro!
python3 comic_identifier.py --db $DB --limit 10

# 2. Se OK, rodar em background
nohup python3 comic_identifier.py --db $DB > identification.log 2>&1 &

# 3. Monitorar
tail -f identification.log

# 4. Verificar status
python3 comic_identifier.py --db $DB --status
```

---

### 🔄 Correções (2-3h total)

```bash
# Após primeira rodada, corrigir erros

# 1. Ver quantos erros/não-encontrados
python3 comic_identifier.py --db $DB --status

# 2. Resetar para tentar novamente
python3 comic_recleaner.py --db $DB --reset-failed

# 3. Re-identificar
python3 comic_identifier.py --db $DB

# Repetir 2-3 vezes até atingir ~90% de sucesso
```

---

### 📚 Enriquecimento (2-3h)

```bash
# 1. Preparar banco (primeira vez)
python3 comic_enricher.py --db $DB --upgrade-db

# 2. Enriquecer
python3 comic_enricher.py --db $DB

# 3. Verificar
python3 comic_analyzer.py --db $DB info <ID_QUALQUER>
```

---

### 📊 Uso Diário

```bash
# Estatísticas
python3 comic_analyzer.py --db $DB stats

# Buscar comics
python3 comic_analyzer.py --db $DB search "Batman"

# Ver série completa
python3 comic_analyzer.py --db $DB series "X-Men"

# Top séries
python3 comic_analyzer.py --db $DB top-series
```

---

## 📊 Exemplo Real

### Coleção: 22.021 comics

**Fase 1 - Scanner (8 minutos):**
```
✅ 22.021 arquivos catalogados
⏳ pending: 22.021 (100.0%)
```

**Fase 2 - Identifier (12 horas):**
```
✅ identified: 19.500 (88.5%)
❌ not_found: 450 (2.0%)
⚠️ error: 71 (0.3%)
⏳ pending: 2.000 (9.1%)
```

**Correções (2 horas x 2 rodadas):**
```
✅ identified: 19.950 (90.6%)
❌ not_found: 100 (0.5%)
⚠️ error: 21 (0.1%)
```

**Fase 3 - Enricher (3 horas):**
```
📚 19.950 comics com metadados completos:
✍️ Roteiristas: 19.850
🎨 Desenhistas: 19.800
👥 Personagens: 18.500
📝 Sinopses: 19.900
🎨 Capas (URL): 19.920
```

**Total: ~17 horas de processamento**

---

## 💡 Dicas e Boas Práticas

### Performance
- ✅ Use `nohup` para processos longos
- ✅ Monitore com `tail -f`
- ✅ SEMPRE teste com `--limit` primeiro
- ✅ Use variável `$DB` para facilitar comandos

### Organização
```bash
# Adicione ao ~/.bashrc
export DB=~/Downloads/comics_inventory.db
export COMICVINE_API_KEY='sua_chave'
```

### Backup
```bash
# Backup regular do banco
cp $DB $DB.backup-$(date +%Y%m%d)

# Restaurar backup
cp $DB.backup-20260206 $DB
```

### Qualidade
- ~90% de identificação é **excelente**
- Comics muito antigos/obscuros podem não existir no CV
- Nomes muito diferentes precisam limpeza manual

---

## 🗺️ Roadmap

### ✅ Concluído (POC)
- [x] Scanner de arquivos
- [x] Identificação via Comic Vine
- [x] Enriquecimento de metadados
- [x] Sistema de análise
- [x] Retry automático
- [x] Sistema resiliente (retomável)

### 🚧 Próximos Passos
- [ ] Script de download de capas
- [ ] Classificação por gênero (Wikidata/Wikipedia)
- [ ] Sincronização de paths (renomeações)
- [ ] Backend API (Node.js + Express)
- [ ] Frontend React
- [ ] Integração YACReader

### 🔮 Futuro
- [ ] Detecção de duplicatas
- [ ] Organização automática de arquivos
- [ ] Sistema de favoritos/lidos/notas
- [ ] Recomendações por IA
- [ ] App mobile (React Native)

---

## 📝 Notas Técnicas

### Rate Limiting
- **Comic Vine:** 200 requisições/hora (gratuito)
- **Script:** 2 segundos entre requisições
- **Resultado:** ~1.800 comics/hora máximo
- **Gerenciamento:** Automático (exponential backoff)

### Precisão
- **Nome do arquivo → Título:** ~95%
- **Identificação Comic Vine:** ~85-95%
- **Enriquecimento completo:** ~99% dos identificados

### Performance
- **Scanner:** ~2.000 arquivos/minuto
- **Identifier:** ~1 comic/2 segundos
- **Enricher:** ~1 comic/2 segundos
- **Analyzer:** Instantâneo (queries em SQLite)

---

## 🙏 Créditos

- **Comic Vine API** - Metadados de comics
- **Python** - Linguagem base
- **SQLite** - Banco de dados
- **Requests** - Cliente HTTP

---

## 📄 Licença

MIT License

---

**Versão:** 1.0.0 (POC)  
**Última atualização:** Fevereiro 2026  
**Autor:** Arthur Haerdy

# 🎨 Comic Collection Manager

Este projeto é uma prova de conceito para demonstrar a viabilidade de catalogação automatizada de coleções. Sistema completo e robusto para identificar, catalogar e gerenciar coleções de comics usando a API do Comic Vine.

## 📋 Visão Geral

O sistema foi desenvolvido para processar **grandes coleções** de arquivos de comics (CBR, CBZ, PDF, CBT, CB7) e identificá-los automaticamente através da API do Comic Vine. Projetado para ser resiliente, eficiente e preparado para expansão futura com frontend React ou Spring Boot.

### ✨ Características Principais

- ✅ **Processa milhares de arquivos** sem travar ou perder progresso
- ✅ **Rate limiting inteligente** para respeitar limites da API
- ✅ **Retomável** - pode ser interrompido e continua de onde parou
- ✅ **SQLite local** - todos os dados ficam no seu computador
- ✅ **Limpeza avançada de nomes** - extrai título, edição e ano
- ✅ **Metadados completos** - sinopse, créditos, personagens, capas
- ✅ **Ferramentas de análise** - duplicatas, lacunas, estatísticas
- ✅ **Não modifica arquivos originais** - apenas consulta e cataloga
- ✅ **Preparado para frontend** - banco estruturado para integração

## 🛠️ Scripts Disponíveis

### 1. **comic_scanner.py** - Inventário Inicial
Escaneia todos os arquivos de comics e cria o banco de dados SQLite.

**Uso:**
```bash
# Configuração padrão (varre pasta atual, salva em ~/Downloads)
python3 comic_scanner.py

# Especificar pasta de varredura
python3 comic_scanner.py /caminho/para/comics

# Especificar pasta de varredura E pasta de saída
python3 comic_scanner.py /caminho/comics /caminho/saida

# Ver ajuda
python3 comic_scanner.py --help
```

**Características:**
- Varre recursivamente todas as subpastas
- Detecta: .cbr, .cbz, .pdf, .cbt, .cb7
- Extrai: título, número da edição, ano
- **Não abre ou modifica** os arquivos originais
- Tempo estimado: 1-2 minutos para 33.000 arquivos

**Saída:** `comics_inventory.db` no diretório especificado

---

### 2. **comic_identifier.py** - Identificação via API
Consulta a API do Comic Vine para identificar cada comic.

**Uso:**
```bash
# Processar todos os pendentes
python3 comic_identifier.py --db ~/Downloads/comics_inventory.db

# Testar com poucos arquivos primeiro (RECOMENDADO)
python3 comic_identifier.py --db ~/Downloads/comics_inventory.db --limit 50

# Ver apenas o status
python3 comic_identifier.py --db ~/Downloads/comics_inventory.db --status

# Exportar resultados para CSV
python3 comic_identifier.py --db ~/Downloads/comics_inventory.db --export
```

**Características:**
- Rate limiting: 2 segundos entre requisições (evita erro 420)
- Backoff exponencial em caso de rate limit
- Salva progresso a cada 10 registros
- Pode ser interrompido e retomado
- Identifica volume (série) e edição específica
- Tempo estimado: ~11 horas para 20.000 arquivos

**Dica:** Use `nohup` para rodar em background:
```bash
nohup python3 comic_identifier.py --db ~/Downloads/comics_inventory.db > log.txt 2>&1 &
```

---

### 3. **comic_analyzer.py** - Análise e Relatórios
Analisa a coleção identificada e gera relatórios.

**Uso:**
```bash
# Estatísticas detalhadas
python3 comic_analyzer.py --db ~/Downloads/comics_inventory.db stats

# Encontrar duplicatas
python3 comic_analyzer.py --db ~/Downloads/comics_inventory.db duplicates

# Encontrar lacunas nas séries
python3 comic_analyzer.py --db ~/Downloads/comics_inventory.db gaps

# Listar comics não encontrados
python3 comic_analyzer.py --db ~/Downloads/comics_inventory.db not-found

# Buscar um comic específico
python3 comic_analyzer.py --db ~/Downloads/comics_inventory.db search "Batman"

# Ver ficha completa de um comic (pelo ID)
python3 comic_analyzer.py --db ~/Downloads/comics_inventory.db info 1234
```

**Características:**
- Apenas lê o banco (não modifica nada)
- Estatísticas por editora, ano, formato
- Detecta duplicatas inteligentemente
- Identifica edições faltantes nas séries
- **Ficha completa** com todos os dados coletados e links para Comic Vine
- Toda saída é no terminal (sem arquivos)

---

### 4. **comic_enricher.py** - Enriquecimento de Metadados
Busca informações detalhadas da API do Comic Vine para comics já identificados.

**Uso:**
```bash
# Atualizar estrutura do banco (primeira vez)
python3 comic_enricher.py --db ~/Downloads/comics_inventory.db --upgrade-db

# Testar com poucos comics
python3 comic_enricher.py --db ~/Downloads/comics_inventory.db --limit 10

# Enriquecer todos os identificados
python3 comic_enricher.py --db ~/Downloads/comics_inventory.db

# Re-enriquecer todos (força atualização)
python3 comic_enricher.py --db ~/Downloads/comics_inventory.db --force

# Rodar em background
nohup python3 comic_enricher.py --db ~/Downloads/comics_inventory.db > enrich.log 2>&1 &
```

**O que busca:**
- ✅ **Sinopse completa** da edição
- ✅ **Créditos**: Roteiristas, desenhistas, arte-finalistas, coloristas, letristas, editores, capistas
- ✅ **Personagens** que aparecem
- ✅ **Equipes** (teams)
- ✅ **Localizações** da história
- ✅ **Arcos de história** (story arcs)
- ✅ **URL da capa** para download
- ✅ **Datas de publicação** (cover date, store date)

**Características:**
- Só processa comics já identificados com `comicvine_issue_id`
- Pula comics que já foram enriquecidos (use `--force` para re-enriquecer)
- Rate limiting: 2 segundos entre requisições
- Salva progresso a cada 10 registros
- Adiciona colunas automaticamente ao banco
- Tempo estimado: ~2 segundos por comic

**Quando usar:**
- Após identificar os comics com `comic_identifier.py`
- Quando quiser informações completas para uma biblioteca detalhada
- Para ter sinopses, créditos completos e metadados ricos

---

### 5. **comic_recleaner.py** - Re-processamento de Nomes
Re-processa os nomes dos arquivos com lógica de limpeza melhorada.

**Uso:**
```bash
# Ver nomes problemáticos (>40 caracteres)
python3 comic_recleaner.py --db ~/Downloads/comics_inventory.db --show-problems

# Re-processar TODOS os nomes
python3 comic_recleaner.py --db ~/Downloads/comics_inventory.db --reclean

# Re-processar apenas os não encontrados
python3 comic_recleaner.py --db ~/Downloads/comics_inventory.db --reclean --status not_found

# Ver mudanças enquanto re-processa
python3 comic_recleaner.py --db ~/Downloads/comics_inventory.db --reclean --show-changes

# Resetar erros para tentar novamente
python3 comic_recleaner.py --db ~/Downloads/comics_inventory.db --reset-failed
```

**Quando usar:**
- Após melhorias na lógica de limpeza de nomes
- Quando muitos comics não foram encontrados
- Para corrigir títulos muito longos ou mal formatados

---

### 6. **comic_dbcheck.py** - Diagnóstico do Banco
Verifica o estado e integridade do banco de dados.

**Uso:**
```bash
# Verificar banco específico
python3 comic_dbcheck.py --db ~/Downloads/comics_inventory.db

# Procurar bancos no sistema
python3 comic_dbcheck.py --find
```

**Características:**
- Verifica existência do arquivo
- Lista tabelas e estrutura
- Conta registros por status
- Útil para debug e diagnóstico

## 🚀 Guia de Início Rápido

### Configuração Inicial

1. **Instale as dependências:**
```bash
pip install requests
# SQLite já vem com Python 3
```

2. **Configure sua API Key do Comic Vine:**
   
   A API key é lida da variável de ambiente `COMICVINE_API_KEY`.
   
   **Obter a chave:**
   - Registre-se gratuitamente em https://comicvine.gamespot.com/api/
   - Copie sua chave de API
   
   **Configurar a variável:**
   
   ```bash
   # Linux/Mac (temporário - apenas nesta sessão)
   export COMICVINE_API_KEY='sua_chave_aqui'
   
   # Linux/Mac (permanente - adiciona ao ~/.bashrc)
   echo "export COMICVINE_API_KEY='sua_chave_aqui'" >> ~/.bashrc
   source ~/.bashrc
   
   # Windows (CMD)
   set COMICVINE_API_KEY=sua_chave_aqui
   
   # Windows (PowerShell)
   $env:COMICVINE_API_KEY='sua_chave_aqui'
   ```
   
   **Verificar se está configurada:**
   ```bash
   # Linux/Mac
   echo $COMICVINE_API_KEY
   
   # Windows (CMD)
   echo %COMICVINE_API_KEY%
   
   # Windows (PowerShell)
   echo $env:COMICVINE_API_KEY
   ```

3. **Defina variável DB para facilitar** (opcional mas recomendado):
```bash
# Temporário (apenas na sessão atual)
export DB=~/Downloads/comics_inventory.db

# Permanente (adiciona ao ~/.bashrc)
echo 'export DB=~/Downloads/comics_inventory.db' >> ~/.bashrc
source ~/.bashrc
```

---

### Fluxo Completo Recomendado

```bash
# Passo 1: Escanear coleção (1-2 min)
python3 comic_scanner.py /seu/diretorio/comics ~/Downloads

# Passo 2: Verificar se criou corretamente
python3 comic_dbcheck.py --db ~/Downloads/comics_inventory.db

# Passo 3: Teste pequeno (1-2 min)
python3 comic_identifier.py --db ~/Downloads/comics_inventory.db --limit 50

# Passo 4: Se OK, processar tudo (10-15 horas)
nohup python3 comic_identifier.py --db ~/Downloads/comics_inventory.db > identification.log 2>&1 &

# Passo 5: Monitorar progresso
tail -f identification.log
# ou
python3 comic_identifier.py --db ~/Downloads/comics_inventory.db --status

# Passo 6: Quando terminar, analisar resultados
python3 comic_analyzer.py --db ~/Downloads/comics_inventory.db stats
python3 comic_analyzer.py --db ~/Downloads/comics_inventory.db duplicates
python3 comic_analyzer.py --db ~/Downloads/comics_inventory.db gaps

# Passo 7: Exportar para CSV (opcional)
python3 comic_identifier.py --db ~/Downloads/comics_inventory.db --export
```

---

### Usando Variável $DB (Simplifica comandos)

Se você definiu a variável `DB`:

```bash
# Todos os comandos ficam mais curtos
python3 comic_analyzer.py --db $DB stats
python3 comic_analyzer.py --db $DB duplicates
python3 comic_analyzer.py --db $DB search "Batman"
python3 comic_identifier.py --db $DB --status
```

**Nota:** O `$DB` é apenas um atalho. `--db` sempre deve vir **antes** dos subcomandos!

## 📊 Estrutura do Banco de Dados

### Tabela `comics`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INTEGER | Chave primária |
| `file_path` | TEXT | Caminho completo do arquivo |
| `file_name` | TEXT | Nome original do arquivo |
| `file_size` | INTEGER | Tamanho em bytes |
| `file_ext` | TEXT | Extensão (.cbr, .cbz, etc) |
| `clean_title` | TEXT | Título limpo (sem tags) |
| `issue_number` | TEXT | Número da edição |
| `year` | TEXT | Ano de publicação |
| `comicvine_volume_id` | INTEGER | ID do volume no Comic Vine |
| `comicvine_issue_id` | INTEGER | ID da edição no Comic Vine |
| `volume_name` | TEXT | Nome oficial da série |
| `publisher` | TEXT | Editora |
| `status` | TEXT | Status do processamento |
| `error_message` | TEXT | Mensagem de erro (se houver) |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Última atualização |

**Campos adicionados pelo comic_enricher.py:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `description` | TEXT | Sinopse completa da edição |
| `cover_date` | TEXT | Data da capa |
| `store_date` | TEXT | Data de chegada nas lojas |
| `writers` | TEXT | Roteiristas |
| `pencilers` | TEXT | Desenhistas/Arte |
| `inkers` | TEXT | Arte-finalistas |
| `colorists` | TEXT | Coloristas |
| `letterers` | TEXT | Letristas |
| `editors` | TEXT | Editores |
| `cover_artists` | TEXT | Artistas de capa |
| `characters` | TEXT | Personagens que aparecem |
| `teams` | TEXT | Equipes |
| `locations` | TEXT | Localizações |
| `story_arcs` | TEXT | Arcos de história |
| `cover_url` | TEXT | URL da imagem da capa |
| `site_detail_url` | TEXT | Link para página no Comic Vine |

### Status possíveis

- **pending**: Ainda não processado pela API
- **identified**: Identificado com sucesso
- **not_found**: Não encontrado no Comic Vine
- **error**: Erro durante processamento

### Consultas SQL úteis

```sql
-- Total por status
SELECT status, COUNT(*) FROM comics GROUP BY status;

-- Top 10 editoras
SELECT publisher, COUNT(*) FROM comics 
WHERE publisher IS NOT NULL 
GROUP BY publisher 
ORDER BY COUNT(*) DESC 
LIMIT 10;

-- Séries com mais edições
SELECT volume_name, COUNT(*) as total
FROM comics 
WHERE volume_name IS NOT NULL
GROUP BY volume_name
ORDER BY total DESC
LIMIT 20;

-- Buscar comic específico
SELECT * FROM comics WHERE volume_name LIKE '%Batman%';
```

## 💡 Dicas e Boas Práticas

### 1. Sempre teste com amostra pequena primeiro
```bash
python3 comic_identifier.py --db $DB --limit 50
```
Verifique se a identificação está funcionando bem antes de processar tudo.

### 2. Use nohup ou screen para processos longos
```bash
# nohup - continua rodando mesmo se fechar o terminal
nohup python3 comic_identifier.py --db $DB > log.txt 2>&1 &

# screen - cria sessão destacável
screen -S comics
python3 comic_identifier.py --db $DB
# Ctrl+A, D para detach
# screen -r comics para voltar
```

### 3. Monitore o progresso
```bash
# Em outro terminal
watch -n 60 'python3 comic_identifier.py --db $DB --status'

# Ou veja o log em tempo real
tail -f log.txt
```

### 4. Faça backup do banco periodicamente
```bash
# Durante o processamento
cp ~/Downloads/comics_inventory.db ~/Downloads/comics_inventory.backup.db

# Ou use sqlite dump
sqlite3 ~/Downloads/comics_inventory.db .dump > backup.sql
```

### 5. Se muitos não forem encontrados
```bash
# 1. Veja quais estão problemáticos
python3 comic_recleaner.py --db $DB --show-problems

# 2. Re-limpe os nomes
python3 comic_recleaner.py --db $DB --reclean

# 3. Resete os não encontrados
python3 comic_recleaner.py --db $DB --reset-failed

# 4. Tente novamente
python3 comic_identifier.py --db $DB
```

### 6. Organize seus arquivos DEPOIS de identificar
**Não** reorganize a estrutura de pastas ANTES da identificação. 
Deixe como está, identifique tudo primeiro, depois organize.

### 7. Use aliases para comandos frequentes
Adicione ao `~/.bashrc`:
```bash
alias comics-status='python3 /path/comic_identifier.py --db ~/Downloads/comics_inventory.db --status'
alias comics-stats='python3 /path/comic_analyzer.py --db ~/Downloads/comics_inventory.db stats'
alias comics-search='python3 /path/comic_analyzer.py --db ~/Downloads/comics_inventory.db search'
```

### 8. Resultados esperados
Com base em coleções similares:
- **Taxa de identificação:** 85-95%
- **Não encontrados:** 5-15% (versões raras, scans antigos, nomes muito diferentes)
- **Erros:** <1%

Comics geralmente não encontrados:
- Revistas brasileiras não catalogadas no Comic Vine
- Scans muito antigos com nomes não padronizados
- Edições especiais ou promocionais
- Material não-oficial (fanzines, etc)

## 📋 Workflow Completo Atualizado

```bash
# ============================================
# FASE 1: PREPARAÇÃO
# ============================================

# Instalar dependências
pip install requests

# Configurar API Key (OBRIGATÓRIO)
export COMICVINE_API_KEY='sua_chave_do_comicvine'

# Verificar se está configurada
echo $COMICVINE_API_KEY

# Opcional: Salvar permanentemente no ~/.bashrc
echo "export COMICVINE_API_KEY='sua_chave'" >> ~/.bashrc
source ~/.bashrc

# ============================================
# FASE 2: INVENTÁRIO (1-2 min)
# ============================================

# Escanear a coleção
python3 comic_scanner.py /caminho/para/comics ~/Downloads

# Verificar se criou corretamente
python3 comic_dbcheck.py --db ~/Downloads/comics_inventory.db

# Definir variável para facilitar
DB=~/Downloads/comics_inventory.db

# ============================================
# FASE 3: TESTE (2-5 min)
# ============================================

# Teste pequeno para validar
python3 comic_identifier.py --db $DB --limit 50

# Ver estatísticas iniciais
python3 comic_analyzer.py --db $DB stats

# ============================================
# FASE 4: PROCESSAMENTO COMPLETO (10-15h)
# ============================================

# Rodar em background
nohup python3 comic_identifier.py --db $DB > identification.log 2>&1 &

# Salvar o PID para poder parar depois
echo $! > comic_process.pid

# ============================================
# FASE 5: MONITORAMENTO
# ============================================

# Ver progresso em tempo real
tail -f identification.log

# Ou ver status em outro terminal
watch -n 60 'python3 comic_identifier.py --db $DB --status'

# Ver se o processo ainda está rodando
ps aux | grep comic_identifier

# Parar o processo se necessário
kill $(cat comic_process.pid)

# ============================================
# FASE 6: CORREÇÕES (se necessário)
# ============================================

# Ver quantos não foram encontrados
python3 comic_analyzer.py --db $DB not-found

# Ver nomes problemáticos
python3 comic_recleaner.py --db $DB --show-problems

# Re-processar nomes
python3 comic_recleaner.py --db $DB --reclean

# Resetar não encontrados
python3 comic_recleaner.py --db $DB --reset-failed

# Tentar identificar novamente
python3 comic_identifier.py --db $DB

# ============================================
# FASE 7: ENRIQUECIMENTO (opcional mas recomendado)
# ============================================

# Atualizar banco (primeira vez)
python3 comic_enricher.py --db $DB --upgrade-db

# Testar com 10 comics
python3 comic_enricher.py --db $DB --limit 10

# Enriquecer todos (em background)
nohup python3 comic_enricher.py --db $DB > enrich.log 2>&1 &

# Monitorar progresso
tail -f enrich.log

# ============================================
# FASE 8: ANÁLISE FINAL
# ============================================

# Estatísticas completas
python3 comic_analyzer.py --db $DB stats

# Encontrar duplicatas
python3 comic_analyzer.py --db $DB duplicates

# Encontrar lacunas nas séries
python3 comic_analyzer.py --db $DB gaps

# Buscar séries específicas
python3 comic_analyzer.py --db $DB search "Batman"
python3 comic_analyzer.py --db $DB search "Homem-Aranha"

# ============================================
# FASE 9: EXPORTAÇÃO
# ============================================

# Exportar tudo para CSV
python3 comic_identifier.py --db $DB --export

# Fazer backup do banco
cp $DB ~/Downloads/comics_inventory.backup.db
```

## 📈 Resultados Esperados

Com base em coleções similares:
- **Taxa de identificação:** 85-95%
- **Não encontrados:** 5-15% (geralmente versões raras, scans antigos, ou nomes muito diferentes)
- **Erros:** <1%

Comics não encontrados geralmente são:
- Revistas brasileiras não catalogadas no Comic Vine
- Scans muito antigos com nomes não padronizados
- Edições especiais ou promocionais
- Material não-oficial

## 🛠️ Solução de Problemas

### "ERRO: API Key não configurada"

**Causa:** Variável de ambiente `COMICVINE_API_KEY` não está definida.

**Solução:**
```bash
# Configure a variável
export COMICVINE_API_KEY='sua_chave_aqui'

# Verifique se funcionou
echo $COMICVINE_API_KEY

# Para tornar permanente
echo "export COMICVINE_API_KEY='sua_chave'" >> ~/.bashrc
source ~/.bashrc
```

**Obter chave:** https://comicvine.gamespot.com/api/

---

### "sqlite3.OperationalError: no such table: comics"

**Causa:** Você não rodou o `comic_scanner.py` ainda, ou está apontando para o banco errado.

**Solução:**
```bash
# Verifique se o banco existe e está correto
python3 comic_dbcheck.py --db ~/Downloads/comics_inventory.db

# Se não existir, crie primeiro
python3 comic_scanner.py /seus/comics ~/Downloads

# Sempre use --db ANTES do subcomando
python3 comic_analyzer.py --db ~/Downloads/comics_inventory.db stats
```

---

### "error: unrecognized arguments: --db"

**Causa:** Ordem errada dos argumentos. O `--db` deve vir **antes** do subcomando.

**❌ Errado:**
```bash
python3 comic_analyzer.py stats --db ~/Downloads/comics_inventory.db
```

**✅ Correto:**
```bash
python3 comic_analyzer.py --db ~/Downloads/comics_inventory.db stats
```

---

### "420 Client Error" (Rate Limit Exceeded)

**Causa:** API do Comic Vine bloqueando por excesso de requisições.

**Solução:**
- O script já tem delay de 2 segundos e retry automático
- Se persistir, aumente `REQUEST_DELAY` em `comic_identifier.py`:
```python
REQUEST_DELAY = 3.0  # ou 4.0
```
- O script vai aguardar automaticamente e tentar novamente

---

### Muitos comics "not_found"

**Causa:** Nomes dos arquivos muito bagunçados ou mal formatados.

**Solução:**
```bash
# Ver quais nomes estão problemáticos
python3 comic_recleaner.py --db ~/Downloads/comics_inventory.db --show-problems

# Re-processar com lógica melhorada
python3 comic_recleaner.py --db ~/Downloads/comics_inventory.db --reclean

# Resetar os não encontrados
python3 comic_recleaner.py --db ~/Downloads/comics_inventory.db --reset-failed

# Tentar identificar novamente
python3 comic_identifier.py --db ~/Downloads/comics_inventory.db
```

---

### Script travou ou foi interrompido

**Solução:**
- Simplesmente rode novamente! O script é resiliente:
```bash
python3 comic_identifier.py --db ~/Downloads/comics_inventory.db
```
- Ele continua automaticamente de onde parou (processa apenas status 'pending')

---

### Não encontro o banco de dados

**Solução:**
```bash
# Procure no sistema
python3 comic_dbcheck.py --find

# Use o caminho encontrado
python3 comic_analyzer.py --db /caminho/encontrado/comics_inventory.db stats
```

---

### Processo muito lento

**Normal!** Com rate limit de 2 segundos:
- 1.000 arquivos ≈ 35 minutos
- 10.000 arquivos ≈ 6 horas
- 20.000 arquivos ≈ 11 horas

**Dicas:**
- Use `nohup` para rodar em background
- Use `screen` ou `tmux` para não perder a sessão
- Monitore com `--status` em outro terminal

## 📦 Dependências

```bash
pip install requests
```

SQLite já vem incluído no Python 3.

## 🔐 Segurança da API Key

A chave da API está hardcoded no `comic_identifier.py` para conveniência. Se preferir maior segurança:

```python
# No início do comic_identifier.py, substitua:
API_KEY = os.environ.get('COMICVINE_API_KEY', 'sua_chave_aqui')

# E rode:
export COMICVINE_API_KEY="sua_chave_aqui"
python3 comic_identifier.py
```

## 📤 Exportação e Uso dos Dados

Depois de identificar, você pode:

1. **Exportar para CSV:**
```bash
python3 comic_identifier.py --export
```
Resultado: `comics_identified.csv` com todos os dados

2. **Consultar direto no SQLite:**
```bash
sqlite3 comics_inventory.db
sqlite> SELECT * FROM comics WHERE publisher = 'Marvel';
sqlite> SELECT volume_name, COUNT(*) FROM comics GROUP BY volume_name;
```

3. **Usar em outros programas:**
- Importe o CSV no Excel/LibreOffice
- Use em softwares como Calibre, ComicRack, etc.
- Crie scripts próprios para organizar arquivos

## 🎯 Integração com Frontend (React/Spring Boot)

O sistema foi projetado para ser facilmente integrado com um frontend visual.

### Dados Disponíveis

O banco SQLite contém tudo necessário:
- ✅ **Caminho completo** de cada arquivo (`file_path`)
- ✅ **Metadados** oficiais do Comic Vine
- ✅ **IDs únicos** para buscar capas e sinopses
- ✅ **Relacionamentos** série/volume/edição

### Como Abrir Arquivos pelo Frontend

**Backend Node.js/Express:**
```javascript
const { exec } = require('child_process');

app.get('/api/comics/:id/open', async (req, res) => {
  const comic = await db.get('SELECT file_path FROM comics WHERE id = ?', req.params.id);
  
  // Abre com YACReader (ou qualquer leitor)
  exec(`yacreader "${comic.file_path}"`);
  
  res.json({ success: true });
});
```

**Backend Spring Boot:**
```java
@GetMapping("/api/comics/{id}/open")
public ResponseEntity<String> openComic(@PathVariable Long id) {
    Comic comic = repository.findById(id).orElseThrow();
    
    // Linux/Mac
    Runtime.getRuntime().exec(new String[]{"yacreader", comic.getFilePath()});
    
    // Windows
    Runtime.getRuntime().exec("cmd /c start YACReader \"" + comic.getFilePath() + "\"");
    
    return ResponseEntity.ok("Opened");
}
```

**Frontend React:**
```javascript
const openComic = async (comicId) => {
  await fetch(`/api/comics/${comicId}/open`);
};

<ComicCard 
  cover={comic.cover_url}
  title={comic.volume_name}
  issue={comic.issue_number}
  onClick={() => openComic(comic.id)}
/>
```

### Features Sugeridas

1. **Galeria Visual**
   - Grid de capas baixadas do Comic Vine
   - Filtros por editora, ano, série
   - Busca por título

2. **Gerenciamento de Leitura**
   - Marcar como lido/não lido
   - Tracking de progresso
   - Última página lida

3. **Análise de Coleção**
   - Gráficos de distribuição (por ano, editora)
   - Séries completas vs incompletas
   - Valor estimado da coleção

4. **Organização**
   - Renomear arquivos automaticamente
   - Mover para estrutura de pastas
   - Adicionar metadados ComicInfo.xml

### Endpoints REST Sugeridos

```
GET  /api/comics              # Lista todos
GET  /api/comics/:id          # Detalhes de um
GET  /api/comics/:id/open     # Abre o arquivo
GET  /api/series              # Lista séries
GET  /api/series/:id/issues   # Edições de uma série
GET  /api/publishers          # Lista editoras
GET  /api/stats               # Estatísticas gerais
POST /api/comics/:id/read     # Marca como lido
GET  /api/search?q=batman     # Busca
```

### Scripts Adicionais Futuros

Podemos criar:
- **comic_cover_downloader.py** - Baixa capas do Comic Vine
- **comic_organizer.py** - Move arquivos para estrutura organizada
- **comic_metadata_writer.py** - Adiciona ComicInfo.xml nos arquivos
- **comic_api_server.py** - API REST pronta para o frontend

---

## ❓ Perguntas Frequentes (FAQ)

### Os scripts modificam meus arquivos originais?
**NÃO!** Absolutamente nada é alterado. Os scripts apenas:
- Leem os nomes dos arquivos
- Consultam a API do Comic Vine
- Salvam informações no banco SQLite

Seus arquivos CBR/CBZ/PDF permanecem intocados.

### Posso rodar em várias máquinas?
Sim! Basta copiar o arquivo `comics_inventory.db` para outra máquina e continuar de onde parou.

### E se eu adicionar novos comics depois?
```bash
# Rode o scanner novamente - ele adiciona apenas os novos
python3 comic_scanner.py /novos/comics ~/Downloads
python3 comic_identifier.py --db ~/Downloads/comics_inventory.db
```

### Como exporto para outros programas?
```bash
# Exporta CSV com todos os dados
python3 comic_identifier.py --db $DB --export

# Ou consulte direto no SQLite
sqlite3 ~/Downloads/comics_inventory.db
```

### Funciona com mangás?
Sim, se estiverem catalogados no Comic Vine. Mangás japoneses podem ter taxa de identificação menor.

---

## 📞 Suporte

Se encontrar problemas:
1. Veja a seção "Solução de Problemas"
2. Rode `comic_dbcheck.py` para diagnóstico
3. Revise os logs de erro
4. Teste com amostra pequena primeiro

---

**Boa organização! 📚✨**

_Última atualização: Fevereiro 2025_

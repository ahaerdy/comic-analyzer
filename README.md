# 🎨 Sistema de Identificação de Comics

Sistema completo para identificar e catalogar uma coleção de comics usando a API do Comic Vine.

## 📋 Visão Geral

Este sistema processa milhares de arquivos de comics (CBR, CBZ, PDF, etc.) e os identifica automaticamente consultando o banco de dados do Comic Vine. O processo é dividido em fases para garantir resiliência e permitir retomada em caso de interrupção.

## 🚀 Como Usar

### Fase 1: Inventário (Escaneamento)

Primeiro, escaneie todos os arquivos e crie o banco de dados local:

```bash
# Escanear o diretório atual
python3 comic_scanner.py

# Ou escanear um diretório específico
python3 comic_scanner.py /caminho/para/seus/comics
```

**O que acontece:**
- ✓ Varre todas as subpastas recursivamente
- ✓ Identifica arquivos .cbr, .cbz, .pdf, .cbt, .cb7
- ✓ Limpa os nomes dos arquivos (remove tags de scan groups)
- ✓ Extrai título, número da edição e ano
- ✓ Armazena tudo em `comics_inventory.db`
- ✓ **Não usa a API** (fase rápida e gratuita)

**Tempo estimado:** 1-2 minutos para 33.000 arquivos

### Fase 2: Identificação via API

Depois do inventário, identifique os comics usando a API:

```bash
# Processar todos os arquivos pendentes
python3 comic_identifier.py

# Ou processar apenas alguns para testar (recomendado primeiro)
python3 comic_identifier.py --limit 50

# Ver apenas o status atual
python3 comic_identifier.py --status

# Exportar resultados para CSV
python3 comic_identifier.py --export
```

**O que acontece:**
- ✓ Processa arquivos com status 'pending'
- ✓ Busca cada título no Comic Vine
- ✓ Identifica volume (série) e edição específica
- ✓ Atualiza banco de dados com IDs oficiais
- ✓ Respeita rate limit da API (1 req/segundo)
- ✓ Salva progresso a cada 10 registros
- ✓ Pode ser interrompido e retomado

**Tempo estimado:** 
- ~10-15 horas para 33.000 arquivos
- Pode ser executado em segundo plano

**Dica:** Deixe rodando overnight ou em um terminal tmux/screen

### Fase 3: Análise e Relatórios

Analise sua coleção identificada:

```bash
# Ver estatísticas completas
python3 comic_analyzer.py stats

# Encontrar duplicatas
python3 comic_analyzer.py duplicates

# Encontrar lacunas nas séries (edições faltando)
python3 comic_analyzer.py gaps

# Listar comics não identificados
python3 comic_analyzer.py not-found

# Buscar um comic específico
python3 comic_analyzer.py search "Homem-Aranha"
```

## 📊 Estrutura do Banco de Dados

O arquivo `comics_inventory.db` contém uma tabela `comics` com:

| Campo | Descrição |
|-------|-----------|
| `file_path` | Caminho completo do arquivo |
| `file_name` | Nome original do arquivo |
| `clean_title` | Título limpo (sem tags) |
| `issue_number` | Número da edição |
| `year` | Ano de publicação |
| `comicvine_volume_id` | ID do volume no Comic Vine |
| `comicvine_issue_id` | ID da edição no Comic Vine |
| `volume_name` | Nome oficial da série |
| `publisher` | Editora |
| `status` | Status: pending, identified, not_found, error |

## 🔧 Status dos Arquivos

- **pending**: Ainda não processado
- **identified**: Identificado com sucesso
- **not_found**: Não encontrado no Comic Vine
- **error**: Erro durante processamento

## 💡 Dicas e Melhores Práticas

### 1. Teste Primeiro
```bash
# Sempre teste com poucos arquivos primeiro
python3 comic_identifier.py --limit 10
```

### 2. Rode em Background
```bash
# Use nohup para não interromper se o terminal fechar
nohup python3 comic_identifier.py > identification.log 2>&1 &

# Ou use screen/tmux
screen -S comics
python3 comic_identifier.py
# Ctrl+A, D para detach
```

### 3. Monitore o Progresso
```bash
# Em outro terminal, veja o status
watch -n 60 'python3 comic_identifier.py --status'

# Ou veja o log em tempo real
tail -f identification.log
```

### 4. Retome se Necessário
O script é resiliente - se parar, apenas rode novamente:
```bash
python3 comic_identifier.py
```
Ele continuará de onde parou (processa apenas status 'pending')

## 🎯 Fluxo Completo Recomendado

```bash
# 1. Inventário rápido (1-2 min)
python3 comic_scanner.py /seu/diretorio/de/comics

# 2. Teste com amostra pequena (1-2 min)
python3 comic_identifier.py --limit 50

# 3. Se tudo OK, processe tudo (10-15 horas)
nohup python3 comic_identifier.py > identification.log 2>&1 &

# 4. Monitore enquanto roda
tail -f identification.log
# ou
python3 comic_identifier.py --status

# 5. Quando terminar, analise os resultados
python3 comic_analyzer.py stats
python3 comic_analyzer.py duplicates
python3 comic_analyzer.py gaps

# 6. Exporte para CSV para uso externo
python3 comic_identifier.py --export
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

### "API rate limit exceeded"
- Normal. O script já implementa delays automáticos
- Se persistir, aumente `REQUEST_DELAY` em `comic_identifier.py`

### "Muitos comics não identificados"
- Revise o algoritmo de limpeza em `clean_filename()`
- Alguns nomes podem precisar de padrões adicionais
- Considere limpeza manual dos nomes mais problemáticos

### "Script travou"
- Verifique sua conexão com a internet
- Veja o log para mensagens de erro
- Simplesmente rode novamente (ele retoma)

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

## 🎨 Próximos Passos (Opcional)

Depois de identificar, você pode:

1. **Organizar arquivos fisicamente:**
   - Criar script para mover arquivos para estrutura `Editora/Série/Série #001.cbz`

2. **Adicionar metadados nos arquivos:**
   - Inserir `ComicInfo.xml` dentro dos CBZ
   - Facilita leitura em apps como Tachiyomi, Komga, etc.

3. **Criar biblioteca digital:**
   - Usar Komga, Kavita ou Ubooquity
   - Importar usando os IDs do Comic Vine

4. **Baixar capas:**
   - API do Comic Vine fornece URLs de capas
   - Pode adicionar script para download automático

## 📞 Suporte

Se encontrar problemas:
1. Veja a seção "Solução de Problemas"
2. Revise os logs de erro
3. Teste com amostra pequena primeiro
4. Ajuste os padrões de limpeza se necessário

## 📄 Licença

Scripts de uso pessoal. Use livremente para organizar sua coleção.

---

**Boa organização! 📚✨**

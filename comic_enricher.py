#!/usr/bin/env python3
"""
Comic Enricher - Enriquece o banco com metadados detalhados da API
Busca sinopse, autores, desenhistas, data de publicação, etc.
"""

import sqlite3
import requests
import time
import sys
import os
from datetime import datetime

API_KEY = os.environ.get('COMICVINE_API_KEY')
USER_AGENT = "ComicEnricher/1.0"
BASE_URL = "https://comicvine.gamespot.com/api"

REQUEST_DELAY = 2.0
MAX_RETRIES = 3
RETRY_DELAY = 5.0

def upgrade_database(db_path):
    """Adiciona colunas extras para metadados detalhados"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Lista de novas colunas a adicionar
    new_columns = [
        ('description', 'TEXT'),
        ('cover_date', 'TEXT'),
        ('store_date', 'TEXT'),
        ('writers', 'TEXT'),
        ('pencilers', 'TEXT'),
        ('inkers', 'TEXT'),
        ('colorists', 'TEXT'),
        ('letterers', 'TEXT'),
        ('editors', 'TEXT'),
        ('cover_artists', 'TEXT'),
        ('characters', 'TEXT'),
        ('teams', 'TEXT'),
        ('locations', 'TEXT'),
        ('story_arcs', 'TEXT'),
        ('cover_url', 'TEXT'),
        ('site_detail_url', 'TEXT'),
    ]
    
    # Verifica quais colunas já existem
    cursor.execute("PRAGMA table_info(comics)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    
    # Adiciona apenas as colunas que não existem
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            try:
                cursor.execute(f'ALTER TABLE comics ADD COLUMN {col_name} {col_type}')
                print(f"  ✓ Coluna '{col_name}' adicionada")
            except sqlite3.OperationalError:
                pass  # Coluna já existe
    
    conn.commit()
    conn.close()

class ComicVineAPI:
    """Wrapper para a API do Comic Vine"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        self.last_request_time = 0
    
    def _wait_for_rate_limit(self):
        """Garante que respeitamos o rate limit"""
        elapsed = time.time() - self.last_request_time
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint, params):
        """Faz requisição à API com retry e rate limiting"""
        params['api_key'] = self.api_key
        params['format'] = 'json'
        
        url = f"{BASE_URL}/{endpoint}/"
        
        for attempt in range(MAX_RETRIES):
            try:
                self._wait_for_rate_limit()
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 420:
                    wait_time = RETRY_DELAY * (2 ** attempt)
                    print(f"    ⚠️  Rate limit. Aguardando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                if data.get('status_code') == 1:
                    return data
                else:
                    return None
                    
            except requests.exceptions.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                else:
                    return None
        
        return None
    
    def get_issue_details(self, issue_id):
        """
        Obtém detalhes completos de uma edição
        """
        params = {
            'field_list': 'id,name,description,cover_date,store_date,person_credits,character_credits,team_credits,location_credits,story_arc_credits,image,site_detail_url'
        }
        
        data = self._make_request(f'issue/4000-{issue_id}', params)
        
        if not data or not data.get('results'):
            return None
        
        issue = data['results']
        
        # Processa créditos de pessoas
        writers = []
        pencilers = []
        inkers = []
        colorists = []
        letterers = []
        editors = []
        cover_artists = []
        
        for person in issue.get('person_credits', []):
            name = person.get('name', '')
            role = person.get('role', '').lower()
            
            if 'writer' in role:
                writers.append(name)
            if 'pencil' in role or 'artist' in role:
                pencilers.append(name)
            if 'ink' in role:
                inkers.append(name)
            if 'color' in role:
                colorists.append(name)
            if 'letter' in role:
                letterers.append(name)
            if 'editor' in role:
                editors.append(name)
            if 'cover' in role:
                cover_artists.append(name)
        
        # Processa outros créditos
        characters = [c.get('name') for c in issue.get('character_credits', []) if c.get('name')]
        teams = [t.get('name') for t in issue.get('team_credits', []) if t.get('name')]
        locations = [l.get('name') for l in issue.get('location_credits', []) if l.get('name')]
        story_arcs = [s.get('name') for s in issue.get('story_arc_credits', []) if s.get('name')]
        
        # URL da capa
        cover_url = None
        if issue.get('image'):
            cover_url = issue['image'].get('medium_url') or issue['image'].get('small_url')
        
        return {
            'description': issue.get('description', ''),
            'cover_date': issue.get('cover_date', ''),
            'store_date': issue.get('store_date', ''),
            'writers': ', '.join(writers) if writers else None,
            'pencilers': ', '.join(pencilers) if pencilers else None,
            'inkers': ', '.join(inkers) if inkers else None,
            'colorists': ', '.join(colorists) if colorists else None,
            'letterers': ', '.join(letterers) if letterers else None,
            'editors': ', '.join(editors) if editors else None,
            'cover_artists': ', '.join(cover_artists) if cover_artists else None,
            'characters': ', '.join(characters[:10]) if characters else None,  # Limita a 10
            'teams': ', '.join(teams) if teams else None,
            'locations': ', '.join(locations[:5]) if locations else None,
            'story_arcs': ', '.join(story_arcs) if story_arcs else None,
            'cover_url': cover_url,
            'site_detail_url': issue.get('site_detail_url', '')
        }

def enrich_comics(db_path, limit=None, force=False):
    """
    Enriquece comics identificados com metadados detalhados
    """
    
    # Valida API key
    if not API_KEY:
        print("\n❌ ERRO: Variável COMICVINE_API_KEY não configurada!")
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Conta quantos precisam de enriquecimento
    if force:
        # Força re-enriquecimento de todos identificados
        query = "SELECT COUNT(*) FROM comics WHERE status = 'identified' AND comicvine_issue_id IS NOT NULL"
    else:
        # Apenas os que ainda não têm descrição
        query = "SELECT COUNT(*) FROM comics WHERE status = 'identified' AND comicvine_issue_id IS NOT NULL AND (description IS NULL OR description = '')"
    
    cursor.execute(query)
    total_to_enrich = cursor.fetchone()[0]
    
    if total_to_enrich == 0:
        print("\n✅ Não há comics para enriquecer!")
        if not force:
            print("   Use --force para re-enriquecer todos")
        conn.close()
        return
    
    print(f"\n📊 {total_to_enrich} comics para enriquecer")
    
    if limit:
        print(f"   Processando apenas {limit} (limite especificado)")
        total_to_process = min(limit, total_to_enrich)
    else:
        total_to_process = total_to_enrich
    
    print(f"\n⏱️  Tempo estimado: {int(total_to_process * REQUEST_DELAY / 60)} minutos")
    print("=" * 70)
    
    # Busca comics para enriquecer
    if force:
        query = """
            SELECT id, volume_name, issue_number, comicvine_issue_id 
            FROM comics 
            WHERE status = 'identified' AND comicvine_issue_id IS NOT NULL
        """
    else:
        query = """
            SELECT id, volume_name, issue_number, comicvine_issue_id 
            FROM comics 
            WHERE status = 'identified' 
              AND comicvine_issue_id IS NOT NULL 
              AND (description IS NULL OR description = '')
        """
    
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    comics = cursor.fetchall()
    
    api = ComicVineAPI(API_KEY)
    
    processed = 0
    enriched = 0
    errors = 0
    
    start_time = time.time()
    
    for comic_id, volume_name, issue_num, issue_id in comics:
        processed += 1
        
        # Mostra progresso
        elapsed = time.time() - start_time
        rate = processed / elapsed if elapsed > 0 else 0
        eta_seconds = (total_to_process - processed) / rate if rate > 0 else 0
        eta_minutes = int(eta_seconds / 60)
        
        print(f"\n[{processed}/{total_to_process}] {volume_name} #{issue_num} | ETA: {eta_minutes}min")
        
        try:
            print(f"   🔍 Buscando detalhes da edição...", end='')
            details = api.get_issue_details(issue_id)
            
            if not details:
                print(" ❌ Não encontrado")
                errors += 1
                continue
            
            print(" ✓")
            
            # Mostra preview dos dados
            if details.get('writers'):
                print(f"   ✍️  Roteiro: {details['writers'][:50]}...")
            if details.get('pencilers'):
                print(f"   🎨 Arte: {details['pencilers'][:50]}...")
            
            # Atualiza banco de dados
            cursor.execute('''
                UPDATE comics 
                SET description = ?,
                    cover_date = ?,
                    store_date = ?,
                    writers = ?,
                    pencilers = ?,
                    inkers = ?,
                    colorists = ?,
                    letterers = ?,
                    editors = ?,
                    cover_artists = ?,
                    characters = ?,
                    teams = ?,
                    locations = ?,
                    story_arcs = ?,
                    cover_url = ?,
                    site_detail_url = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                details.get('description'),
                details.get('cover_date'),
                details.get('store_date'),
                details.get('writers'),
                details.get('pencilers'),
                details.get('inkers'),
                details.get('colorists'),
                details.get('letterers'),
                details.get('editors'),
                details.get('cover_artists'),
                details.get('characters'),
                details.get('teams'),
                details.get('locations'),
                details.get('story_arcs'),
                details.get('cover_url'),
                details.get('site_detail_url'),
                comic_id
            ))
            
            enriched += 1
            
            # Commit a cada 10
            if processed % 10 == 0:
                conn.commit()
                print(f"\n   💾 Progresso salvo ({enriched} enriquecidos)")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            errors += 1
    
    conn.commit()
    
    # Estatísticas finais
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 70)
    print("📊 RESULTADO FINAL:")
    print(f"   • Processados: {processed}")
    print(f"   • Enriquecidos: {enriched} ({enriched/processed*100:.1f}%)")
    print(f"   • Erros: {errors}")
    print(f"   • Tempo total: {int(elapsed_time/60)}min {int(elapsed_time%60)}s")
    print("=" * 70)
    
    conn.close()

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enriquece comics com metadados detalhados')
    parser.add_argument('--db', default='comics_inventory.db', help='Caminho do banco de dados')
    parser.add_argument('--limit', type=int, help='Limita número de comics a processar')
    parser.add_argument('--force', action='store_true', help='Re-enriquece todos (mesmo os que já têm dados)')
    parser.add_argument('--upgrade-db', action='store_true', help='Adiciona colunas extras ao banco')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("  📚 COMIC ENRICHER - Enriquecimento de Metadados")
    print("=" * 70)
    
    if not os.path.exists(args.db):
        print(f"\n❌ Banco de dados não encontrado: {args.db}")
        sys.exit(1)
    
    if args.upgrade_db:
        print("\n🔧 Atualizando estrutura do banco de dados...")
        upgrade_database(args.db)
        print("\n✅ Banco atualizado!")
        return
    
    # Garante que o banco tem as colunas necessárias
    upgrade_database(args.db)
    
    # Enriquece comics
    enrich_comics(args.db, limit=args.limit, force=args.force)

if __name__ == "__main__":
    main()

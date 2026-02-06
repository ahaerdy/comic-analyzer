#!/usr/bin/env python3
"""
Comic Identifier - Fase 2: Identificação via Comic Vine API
Processa arquivos do banco SQLite e identifica via API
"""

import sqlite3
import requests
import time
import sys
import os
from datetime import datetime

API_KEY = os.environ.get('COMICVINE_API_KEY')
USER_AGENT = "ComicIdentifier/1.0"
BASE_URL = "https://comicvine.gamespot.com/api"

# Configurações de rate limiting
REQUEST_DELAY = 2.0  # Segundos entre requisições (aumentado para evitar erro 420)
MAX_RETRIES = 3
RETRY_DELAY = 5.0  # Delay adicional após erro 420

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
                
                # Se receber 420 (rate limit), espera mais tempo
                if response.status_code == 420:
                    wait_time = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                    print(f"    ⚠️  Rate limit (420). Aguardando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                if data.get('status_code') == 1:
                    return data
                else:
                    error = data.get('error', 'Unknown error')
                    print(f"    ⚠️  API Error: {error}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"    ⚠️  Tentativa {attempt + 1}/{MAX_RETRIES} falhou: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return None
        
        return None
    
    def search_volume(self, title, year=None):
        """
        Busca um volume (série) no Comic Vine
        """
        params = {
            'query': title,
            'resources': 'volume',
            'limit': 10
        }
        
        data = self._make_request('search', params)
        
        if not data or not data.get('results'):
            return None
        
        volumes = data['results']
        
        # Se temos o ano, tenta encontrar match exato
        if year:
            for vol in volumes:
                vol_year = str(vol.get('start_year', ''))
                if vol_year == year:
                    return vol
        
        # Retorna o primeiro resultado (mais relevante)
        return volumes[0]
    
    def get_volume_issues(self, volume_id):
        """
        Obtém todas as edições de um volume
        """
        params = {
            'filter': f'volume:{volume_id}',
            'field_list': 'id,issue_number,name,volume',
            'limit': 100
        }
        
        data = self._make_request('issues', params)
        
        if not data or not data.get('results'):
            return []
        
        return data['results']
    
    def find_issue(self, volume_id, issue_number):
        """
        Encontra uma edição específica dentro de um volume
        """
        issues = self.get_volume_issues(volume_id)
        
        # Normaliza o número da edição para comparação
        issue_num_normalized = issue_number.lstrip('0') or '0'
        
        for issue in issues:
            api_issue_num = str(issue.get('issue_number', '')).lstrip('0') or '0'
            if api_issue_num == issue_num_normalized:
                return issue
        
        return None

def process_comics(db_path, limit=None, resume=True):
    """
    Processa arquivos pendentes do banco de dados
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Conta pendentes
    cursor.execute("SELECT COUNT(*) FROM comics WHERE status = 'pending'")
    total_pending = cursor.fetchone()[0]
    
    if total_pending == 0:
        print("✅ Não há arquivos pendentes para processar!")
        return
    
    print(f"\n📊 {total_pending} arquivos pendentes")
    
    if limit:
        print(f"   Processando apenas {limit} arquivos (limite especificado)")
        total_to_process = min(limit, total_pending)
    else:
        total_to_process = total_pending
    
    print(f"\n⏱️  Tempo estimado: {int(total_to_process * REQUEST_DELAY / 60)} minutos")
    print("=" * 60)
    
    # Busca arquivos pendentes
    query = "SELECT id, file_name, clean_title, issue_number, year FROM comics WHERE status = 'pending'"
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    comics = cursor.fetchall()
    
    api = ComicVineAPI(API_KEY)
    
    processed = 0
    identified = 0
    not_found = 0
    errors = 0
    
    start_time = time.time()
    
    for comic_id, filename, title, issue_num, year in comics:
        processed += 1
        
        # Mostra progresso
        elapsed = time.time() - start_time
        rate = processed / elapsed if elapsed > 0 else 0
        eta_seconds = (total_to_process - processed) / rate if rate > 0 else 0
        eta_minutes = int(eta_seconds / 60)
        
        print(f"\n[{processed}/{total_to_process}] {title}", end='')
        if issue_num:
            print(f" #{issue_num}", end='')
        if year:
            print(f" ({year})", end='')
        print(f" | ETA: {eta_minutes}min")
        
        try:
            # Busca o volume
            print(f"   🔍 Buscando volume...", end='')
            volume = api.search_volume(title, year)
            
            if not volume:
                print(" ❌ Não encontrado")
                cursor.execute('''
                    UPDATE comics 
                    SET status = 'not_found', 
                        error_message = 'Volume não encontrado',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (comic_id,))
                not_found += 1
                continue
            
            volume_id = volume['id']
            volume_name = volume['name']
            volume_year = volume.get('start_year')
            publisher = volume.get('publisher', {})
            publisher_name = publisher.get('name') if publisher else None
            
            print(f" ✓ {volume_name} ({volume_year})")
            
            # Se temos número da edição, busca a edição específica
            issue_id = None
            if issue_num:
                print(f"   🔍 Buscando edição #{issue_num}...", end='')
                issue = api.find_issue(volume_id, issue_num)
                if issue:
                    issue_id = issue['id']
                    print(f" ✓ Encontrada")
                else:
                    print(f" ⚠️  Edição não encontrada no volume")
            
            # Atualiza banco de dados
            cursor.execute('''
                UPDATE comics 
                SET comicvine_volume_id = ?,
                    comicvine_issue_id = ?,
                    volume_name = ?,
                    publisher = ?,
                    status = 'identified',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (volume_id, issue_id, volume_name, publisher_name, comic_id))
            
            identified += 1
            
            # Commit a cada 10 registros
            if processed % 10 == 0:
                conn.commit()
                print(f"\n   💾 Progresso salvo ({identified} identificados, {not_found} não encontrados)")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            cursor.execute('''
                UPDATE comics 
                SET status = 'error',
                    error_message = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (str(e), comic_id))
            errors += 1
    
    # Commit final
    conn.commit()
    
    # Estatísticas finais
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL:")
    print(f"   • Processados: {processed}")
    print(f"   • Identificados: {identified} ({identified/processed*100:.1f}%)")
    print(f"   • Não encontrados: {not_found} ({not_found/processed*100:.1f}%)")
    print(f"   • Erros: {errors}")
    print(f"   • Tempo total: {int(elapsed_time/60)}min {int(elapsed_time%60)}s")
    print("=" * 60)
    
    conn.close()

def show_status(db_path):
    """Mostra status atual do processamento"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n📊 STATUS ATUAL")
    print("=" * 60)
    
    cursor.execute('SELECT status, COUNT(*) FROM comics GROUP BY status')
    for status, count in cursor.fetchall():
        cursor.execute('SELECT COUNT(*) FROM comics')
        total = cursor.fetchone()[0]
        percentage = (count / total * 100) if total > 0 else 0
        print(f"   • {status}: {count} ({percentage:.1f}%)")
    
    print("=" * 60)
    
    conn.close()

def export_results(db_path, output_file='comics_identified.csv'):
    """Exporta resultados para CSV"""
    import csv
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT file_path, file_name, clean_title, issue_number, year,
               volume_name, publisher, comicvine_volume_id, comicvine_issue_id, status
        FROM comics
        ORDER BY volume_name, issue_number
    ''')
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Caminho', 'Arquivo', 'Título Limpo', 'Edição', 'Ano',
                        'Nome no Comic Vine', 'Editora', 'Volume ID', 'Issue ID', 'Status'])
        writer.writerows(cursor.fetchall())
    
    print(f"\n✅ Resultados exportados para: {output_file}")
    
    conn.close()

def main():
    """Função principal"""
    import argparse
    
    # Valida se a API key está configurada
    if not API_KEY:
        print("=" * 70)
        print("  ❌ ERRO: API Key não configurada")
        print("=" * 70)
        print("\n⚠️  A variável de ambiente COMICVINE_API_KEY não está definida.\n")
        print("Configure a chave antes de executar:\n")
        print("  # Linux/Mac:")
        print("  export COMICVINE_API_KEY='sua_chave_aqui'\n")
        print("  # Windows (CMD):")
        print("  set COMICVINE_API_KEY=sua_chave_aqui\n")
        print("  # Windows (PowerShell):")
        print("  $env:COMICVINE_API_KEY='sua_chave_aqui'\n")
        print("Obtenha sua chave gratuita em:")
        print("  https://comicvine.gamespot.com/api/\n")
        print("=" * 70)
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description='Identifica comics via Comic Vine API')
    parser.add_argument('--db', default='comics_inventory.db', help='Caminho do banco de dados')
    parser.add_argument('--limit', type=int, help='Limita número de arquivos a processar (para testes)')
    parser.add_argument('--status', action='store_true', help='Mostra apenas o status atual')
    parser.add_argument('--export', action='store_true', help='Exporta resultados para CSV')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  🎨 COMIC IDENTIFIER - Fase 2: Identificação")
    print("=" * 60)
    
    if args.status:
        show_status(args.db)
        return
    
    if args.export:
        export_results(args.db)
        return
    
    # Processa arquivos
    process_comics(args.db, limit=args.limit)
    
    # Oferece exportar
    response = input("\n📤 Deseja exportar os resultados para CSV? (s/n): ")
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        export_results(args.db)

if __name__ == "__main__":
    main()

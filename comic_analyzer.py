#!/usr/bin/env python3
"""
Comic Analyzer - Utilitário para análise e relatórios
"""

import sqlite3
import sys
from collections import Counter

def connect_db(db_path='comics_inventory.db'):
    """Conecta ao banco de dados"""
    try:
        return sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        sys.exit(1)

def show_detailed_stats(db_path):
    """Mostra estatísticas detalhadas"""
    conn = connect_db(db_path)
    cursor = conn.cursor()
    
    print("\n" + "=" * 70)
    print("  📊 ANÁLISE DETALHADA DA COLEÇÃO")
    print("=" * 70)
    
    # Estatísticas gerais
    cursor.execute('SELECT COUNT(*) FROM comics')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT status, COUNT(*) FROM comics GROUP BY status')
    status_counts = dict(cursor.fetchall())
    
    print(f"\n📚 TOTAL DE ARQUIVOS: {total}")
    print("\n📈 Por Status:")
    for status in ['pending', 'identified', 'not_found', 'error']:
        count = status_counts.get(status, 0)
        percentage = (count / total * 100) if total > 0 else 0
        bar = '█' * int(percentage / 2)
        print(f"   {status:15s}: {count:6d} ({percentage:5.1f}%) {bar}")
    
    # Top editoras
    print("\n🏢 Top 10 Editoras:")
    cursor.execute('''
        SELECT publisher, COUNT(*) as cnt 
        FROM comics 
        WHERE publisher IS NOT NULL 
        GROUP BY publisher 
        ORDER BY cnt DESC 
        LIMIT 10
    ''')
    for i, (publisher, count) in enumerate(cursor.fetchall(), 1):
        print(f"   {i:2d}. {publisher:30s}: {count:4d} arquivos")
    
    # Top séries
    print("\n📖 Top 10 Séries:")
    cursor.execute('''
        SELECT volume_name, COUNT(*) as cnt 
        FROM comics 
        WHERE volume_name IS NOT NULL 
        GROUP BY volume_name 
        ORDER BY cnt DESC 
        LIMIT 10
    ''')
    for i, (series, count) in enumerate(cursor.fetchall(), 1):
        print(f"   {i:2d}. {series:40s}: {count:4d} edições")
    
    # Anos
    print("\n📅 Distribuição por Ano:")
    cursor.execute('''
        SELECT year, COUNT(*) as cnt 
        FROM comics 
        WHERE year IS NOT NULL 
        GROUP BY year 
        ORDER BY year DESC 
        LIMIT 15
    ''')
    for year, count in cursor.fetchall():
        bar = '█' * (count // 50)
        print(f"   {year}: {count:4d} {bar}")
    
    # Formatos
    print("\n💾 Por Formato:")
    cursor.execute('SELECT file_ext, COUNT(*) FROM comics GROUP BY file_ext ORDER BY COUNT(*) DESC')
    for ext, count in cursor.fetchall():
        percentage = (count / total * 100) if total > 0 else 0
        print(f"   {ext:5s}: {count:6d} ({percentage:5.1f}%)")
    
    # Tamanho total
    cursor.execute('SELECT SUM(file_size) FROM comics')
    total_size = cursor.fetchone()[0] or 0
    total_gb = total_size / (1024**3)
    print(f"\n💿 Tamanho Total da Coleção: {total_gb:.2f} GB")
    
    print("=" * 70)
    
    conn.close()

def find_duplicates(db_path):
    """Encontra possíveis duplicatas"""
    conn = connect_db(db_path)
    cursor = conn.cursor()
    
    print("\n" + "=" * 70)
    print("  🔍 BUSCA DE DUPLICATAS")
    print("=" * 70)
    
    cursor.execute('''
        SELECT volume_name, issue_number, COUNT(*) as cnt, 
               GROUP_CONCAT(file_name, ' | ') as files
        FROM comics 
        WHERE volume_name IS NOT NULL AND issue_number IS NOT NULL
        GROUP BY volume_name, issue_number
        HAVING cnt > 1
        ORDER BY cnt DESC, volume_name
        LIMIT 50
    ''')
    
    results = cursor.fetchall()
    
    if not results:
        print("\n✅ Nenhuma duplicata encontrada!")
    else:
        print(f"\n⚠️  Encontradas {len(results)} possíveis duplicatas:\n")
        for series, issue, count, files in results:
            print(f"📚 {series} #{issue} - {count} cópias:")
            for filename in files.split(' | '):
                print(f"   • {filename}")
            print()
    
    conn.close()

def find_series_with_gaps(db_path):
    """Encontra séries com edições faltantes"""
    conn = connect_db(db_path)
    cursor = conn.cursor()
    
    print("\n" + "=" * 70)
    print("  🕳️  SÉRIES COM LACUNAS")
    print("=" * 70)
    
    cursor.execute('''
        SELECT volume_name, comicvine_volume_id, GROUP_CONCAT(issue_number) as issues
        FROM comics 
        WHERE volume_name IS NOT NULL 
          AND issue_number IS NOT NULL 
          AND comicvine_volume_id IS NOT NULL
        GROUP BY volume_name, comicvine_volume_id
        HAVING COUNT(*) >= 3
        ORDER BY COUNT(*) DESC
        LIMIT 20
    ''')
    
    print("\nAnalisando as 20 séries com mais edições...\n")
    
    gaps_found = False
    
    for series, vol_id, issues_str in cursor.fetchall():
        try:
            # Converte números de edições para inteiros
            issues = []
            for issue in issues_str.split(','):
                try:
                    issues.append(int(issue))
                except ValueError:
                    continue
            
            if not issues:
                continue
            
            issues.sort()
            
            # Encontra gaps
            gaps = []
            for i in range(len(issues) - 1):
                diff = issues[i + 1] - issues[i]
                if diff > 1:
                    gaps.append((issues[i], issues[i + 1]))
            
            if gaps:
                gaps_found = True
                print(f"📚 {series}")
                print(f"   Você tem: #{issues[0]} até #{issues[-1]} ({len(issues)} edições)")
                print(f"   Faltam:")
                for start, end in gaps:
                    missing = list(range(start + 1, end))
                    missing_str = ', '.join(f"#{n}" for n in missing)
                    print(f"      • {missing_str}")
                print()
        
        except Exception as e:
            continue
    
    if not gaps_found:
        print("✅ Não foram encontradas lacunas significativas nas principais séries!")
    
    print("=" * 70)
    
    conn.close()

def search_comics(db_path, query):
    """Busca comics no banco"""
    conn = connect_db(db_path)
    cursor = conn.cursor()
    
    print(f"\n🔍 Buscando: '{query}'")
    print("=" * 70)
    
    cursor.execute('''
        SELECT file_name, volume_name, issue_number, year, publisher, status, file_path
        FROM comics 
        WHERE file_name LIKE ? OR clean_title LIKE ? OR volume_name LIKE ?
        LIMIT 50
    ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
    
    results = cursor.fetchall()
    
    if not results:
        print("\n❌ Nenhum resultado encontrado.")
    else:
        print(f"\n✓ {len(results)} resultado(s):\n")
        for filename, vol_name, issue, year, publisher, status, path in results:
            info = vol_name or filename
            if issue:
                info += f" #{issue}"
            if year:
                info += f" ({year})"
            if publisher:
                info += f" - {publisher}"
            
            status_icon = {
                'identified': '✅',
                'pending': '⏳',
                'not_found': '❌',
                'error': '⚠️'
            }.get(status, '❓')
            
            print(f"{status_icon} {info}")
            print(f"   Arquivo: {filename}")
            print(f"   Caminho: {path}")
            print()
    
    print("=" * 70)
    
    conn.close()

def list_not_found(db_path):
    """Lista comics não encontrados"""
    conn = connect_db(db_path)
    cursor = conn.cursor()
    
    print("\n" + "=" * 70)
    print("  ❌ COMICS NÃO ENCONTRADOS")
    print("=" * 70)
    
    cursor.execute('''
        SELECT file_name, clean_title, issue_number, year
        FROM comics 
        WHERE status = 'not_found'
        ORDER BY clean_title
        LIMIT 100
    ''')
    
    results = cursor.fetchall()
    
    if not results:
        print("\n✅ Todos os comics foram identificados!")
    else:
        print(f"\n📋 {len(results)} comics não encontrados (mostrando até 100):\n")
        for filename, title, issue, year in results:
            info = title
            if issue:
                info += f" #{issue}"
            if year:
                info += f" ({year})"
            print(f"   • {info}")
            print(f"     Arquivo: {filename}\n")
    
    print("=" * 70)
    
    conn.close()

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Análise e relatórios da coleção de comics')
    parser.add_argument('--db', default='comics_inventory.db', help='Caminho do banco de dados')
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    subparsers.add_parser('stats', help='Mostra estatísticas detalhadas')
    subparsers.add_parser('duplicates', help='Busca duplicatas')
    subparsers.add_parser('gaps', help='Encontra lacunas nas séries')
    subparsers.add_parser('not-found', help='Lista comics não encontrados')
    
    search_parser = subparsers.add_parser('search', help='Busca comics')
    search_parser.add_argument('query', help='Termo de busca')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'stats':
        show_detailed_stats(args.db)
    elif args.command == 'duplicates':
        find_duplicates(args.db)
    elif args.command == 'gaps':
        find_series_with_gaps(args.db)
    elif args.command == 'not-found':
        list_not_found(args.db)
    elif args.command == 'search':
        search_comics(args.db, args.query)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Comic Scanner - Fase 1: Inventário
Escaneia todos os arquivos de comics e armazena em banco SQLite
"""

import sqlite3
import os
import re
from pathlib import Path
import sys

# Extensões de arquivos de comics suportadas
COMIC_EXTENSIONS = {'.cbr', '.cbz', '.pdf', '.cbt', '.cb7'}

def create_database(db_path='comics_inventory.db'):
    """Cria o banco de dados SQLite com a estrutura necessária"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE NOT NULL,
            file_name TEXT NOT NULL,
            file_size INTEGER,
            file_ext TEXT,
            clean_title TEXT,
            issue_number TEXT,
            year TEXT,
            comicvine_volume_id INTEGER,
            comicvine_issue_id INTEGER,
            volume_name TEXT,
            publisher TEXT,
            status TEXT DEFAULT 'pending',
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Índices para melhorar performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON comics(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_clean_title ON comics(clean_title)')
    
    conn.commit()
    return conn

def clean_filename(filename):
    """
    Limpa o nome do arquivo para extrair título, edição e ano
    """
    # Remove extensão
    name = os.path.splitext(filename)[0]
    
    # Substitui pontos e underscores por espaços
    name = name.replace(".", " ").replace("_", " ")
    
    # Remove tags entre parênteses e colchetes
    name = re.sub(r'\(.*?\)|\[.*?\]', '', name)
    
    # Remove números estranhos como 28 29 que aparecem no exemplo
    # (provavelmente artefatos de codificação)
    name = re.sub(r'\b\d{2}\s+\d{2}', '', name)
    
    # Remove tags comuns de scan groups e qualidade
    scan_tags = [
        'Digital', 'Mephisto', 'Empire', 'DCP', 'EvilTrash', 'GreenGiant',
        'Zone', 'bittertek', 'eclipse', 'c2c', 'Scan', 'HD', 'HQ',
        'Minutemen', 'Glorith', 'AnHeroGold', 'ScannerDarkly', 'Nemesis43',
        'CaptainMalcom', 'Archangel', 'BlackManta', 'Shadowcat', 'Oroboros',
        'Son of Ultron', 'digital', 'scans', 'retail', 'web', 'cbr', 'cbz',
        'complete', 'ongoing', 'fixed', 'proper', 'repost'
    ]
    
    for tag in scan_tags:
        name = re.sub(rf'\b{tag}\b', '', name, flags=re.IGNORECASE)
    
    # Extrai o ano (formato 19xx ou 20xx)
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', name)
    year = year_match.group(0) if year_match else None
    if year:
        name = name.replace(year, "")
    
    # Extrai número da edição ANTES de limpar mais
    # Padrões: 001, #01, v1, vol 1, 1-of-3, etc
    issue_patterns = [
        r'\b(\d{1,4})\s*(?:of|de)\s*\d{1,4}\b',  # 1-of-3, 1 of 3
        r'#\s*(\d{1,4})',  # #1, #001
        r'\bv(?:ol)?\.?\s*(\d{1,4})\b',  # vol 1, v1
        r'\b(\d{3,4})\b',  # 001, 0001
        r'\b(\d{1,2})\b'   # 1, 01 (última tentativa)
    ]
    
    issue_num = ""
    for pattern in issue_patterns:
        issue_match = re.search(pattern, name, re.IGNORECASE)
        if issue_match:
            issue_num = issue_match.group(1).lstrip('0') or '0'
            name = re.sub(pattern, '', name, count=1, flags=re.IGNORECASE)
            break
    
    # Remove palavras comuns que não são título
    noise_words = ['to', 'the', 'last', 'man', 'first', 'issue', 'part', 'chapter']
    # Mas APENAS se aparecerem no final ou sozinhas
    for word in noise_words:
        name = re.sub(rf'\s+{word}\s+\d+\s*$', '', name, flags=re.IGNORECASE)
    
    # Limpa espaços extras e hífens soltos
    title = re.sub(r'\s+', ' ', name).strip()
    title = re.sub(r'\s*-\s*$', '', title).strip()
    title = re.sub(r'^\s*-\s*', '', title).strip()
    
    # Se o título ficou muito longo (>50 chars), provavelmente tem lixo
    # Tenta pegar só as primeiras palavras
    if len(title) > 50:
        words = title.split()
        # Pega as primeiras 2-4 palavras capitalizadas
        clean_words = []
        for word in words[:6]:
            if word and (word[0].isupper() or word.lower() in ['the', 'a', 'an', 'of']):
                clean_words.append(word)
            else:
                break
        if clean_words:
            title = ' '.join(clean_words)
    
    return title, issue_num, year

def scan_directory(root_path, conn, progress_callback=None):
    """
    Escaneia recursivamente o diretório e adiciona arquivos ao banco
    """
    cursor = conn.cursor()
    
    total_found = 0
    total_added = 0
    total_skipped = 0
    
    print(f"\n🔍 Escaneando diretório: {root_path}")
    print("=" * 60)
    
    for root, dirs, files in os.walk(root_path):
        # Ignora diretórios ocultos
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            
            if ext in COMIC_EXTENSIONS:
                total_found += 1
                file_path = os.path.join(root, filename)
                
                try:
                    file_size = os.path.getsize(file_path)
                    clean_title, issue_num, year = clean_filename(filename)
                    
                    # Tenta inserir no banco
                    cursor.execute('''
                        INSERT OR IGNORE INTO comics 
                        (file_path, file_name, file_size, file_ext, 
                         clean_title, issue_number, year, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
                    ''', (file_path, filename, file_size, ext, 
                          clean_title, issue_num, year))
                    
                    if cursor.rowcount > 0:
                        total_added += 1
                        if total_added % 100 == 0:
                            print(f"  ✓ {total_added} arquivos adicionados...", end='\r')
                            conn.commit()
                    else:
                        total_skipped += 1
                        
                except Exception as e:
                    print(f"\n  ⚠️  Erro ao processar {filename}: {e}")
    
    conn.commit()
    
    print("\n" + "=" * 60)
    print(f"📊 Resultado do escaneamento:")
    print(f"   • Arquivos encontrados: {total_found}")
    print(f"   • Novos registros: {total_added}")
    print(f"   • Já existentes: {total_skipped}")
    print("=" * 60)
    
    return total_found, total_added, total_skipped

def show_statistics(conn):
    """Mostra estatísticas do banco de dados"""
    cursor = conn.cursor()
    
    print("\n📈 Estatísticas do Banco de Dados")
    print("=" * 60)
    
    # Total de arquivos
    cursor.execute('SELECT COUNT(*) FROM comics')
    total = cursor.fetchone()[0]
    print(f"   Total de arquivos: {total}")
    
    # Por status
    cursor.execute('SELECT status, COUNT(*) FROM comics GROUP BY status')
    print("\n   Por status:")
    for status, count in cursor.fetchall():
        percentage = (count / total * 100) if total > 0 else 0
        print(f"      • {status}: {count} ({percentage:.1f}%)")
    
    # Por extensão
    cursor.execute('SELECT file_ext, COUNT(*) FROM comics GROUP BY file_ext ORDER BY COUNT(*) DESC')
    print("\n   Por formato:")
    for ext, count in cursor.fetchall():
        print(f"      • {ext}: {count}")
    
    # Anos encontrados
    cursor.execute('SELECT year, COUNT(*) FROM comics WHERE year IS NOT NULL GROUP BY year ORDER BY year DESC LIMIT 10')
    results = cursor.fetchall()
    if results:
        print("\n   Top 10 anos:")
        for year, count in results:
            print(f"      • {year}: {count} arquivos")
    
    print("=" * 60)

def show_sample_records(conn, limit=10):
    """Mostra uma amostra dos registros"""
    cursor = conn.cursor()
    
    print(f"\n📋 Amostra de {limit} registros:")
    print("=" * 60)
    
    cursor.execute('''
        SELECT file_name, clean_title, issue_number, year, status 
        FROM comics 
        LIMIT ?
    ''', (limit,))
    
    for i, (filename, title, issue, year, status) in enumerate(cursor.fetchall(), 1):
        year_str = f"({year})" if year else ""
        issue_str = f"#{issue}" if issue else ""
        print(f"{i:2d}. {title} {issue_str} {year_str}")
        print(f"    Arquivo: {filename}")
        print(f"    Status: {status}")
        print()

def confirm_paths(scan_path, output_path):
    """Confirma os caminhos com o usuário"""
    print("\n" + "=" * 60)
    print("  ⚙️  CONFIGURAÇÃO")
    print("=" * 60)
    print(f"\n📂 Pasta de varredura: {os.path.abspath(scan_path)}")
    print(f"💾 Pasta de saída:     {os.path.abspath(output_path)}")
    print(f"\n📊 O banco de dados será criado em:")
    print(f"   {os.path.join(os.path.abspath(output_path), 'comics_inventory.db')}")
    print("\n" + "=" * 60)
    
    response = input("\n✓ Confirma estes caminhos? (s/n): ").strip().lower()
    
    return response in ['s', 'sim', 'y', 'yes']

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Comic Scanner - Escaneia e cataloga arquivos de comics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s                                    # Varre pasta atual, saída em ~/Downloads
  %(prog)s /path/comics                       # Varre /path/comics, saída em ~/Downloads
  %(prog)s /path/comics /path/output          # Especifica ambos os caminhos
  %(prog)s . ~/Documentos/Comics              # Varre pasta atual, saída customizada
        """
    )
    
    parser.add_argument(
        'scan_dir',
        nargs='?',
        default='.',
        help='Diretório para varrer (padrão: diretório atual)'
    )
    
    parser.add_argument(
        'output_dir',
        nargs='?',
        default=os.path.expanduser('~/Downloads'),
        help='Diretório de saída para o banco de dados (padrão: ~/Downloads)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  🎨 COMIC SCANNER - Fase 1: Inventário")
    print("=" * 60)
    
    # Expande ~ e resolve caminhos
    scan_path = os.path.expanduser(args.scan_dir)
    output_path = os.path.expanduser(args.output_dir)
    
    # Valida diretório de varredura
    if not os.path.exists(scan_path):
        print(f"\n❌ Erro: Diretório de varredura '{scan_path}' não encontrado!")
        sys.exit(1)
    
    if not os.path.isdir(scan_path):
        print(f"\n❌ Erro: '{scan_path}' não é um diretório!")
        sys.exit(1)
    
    # Cria diretório de saída se não existir
    if not os.path.exists(output_path):
        print(f"\n📁 Criando diretório de saída: {output_path}")
        try:
            os.makedirs(output_path, exist_ok=True)
        except Exception as e:
            print(f"❌ Erro ao criar diretório de saída: {e}")
            sys.exit(1)
    
    # Confirma com usuário se recebeu parâmetros
    if len(sys.argv) > 1:  # Recebeu ao menos 1 parâmetro
        if not confirm_paths(scan_path, output_path):
            print("\n❌ Operação cancelada pelo usuário.")
            sys.exit(0)
    else:
        # Mostra configuração padrão sem pedir confirmação
        print(f"\n📂 Pasta de varredura: {os.path.abspath(scan_path)}")
        print(f"💾 Pasta de saída:     {os.path.abspath(output_path)}")
    
    # Define caminho completo do banco de dados
    db_path = os.path.join(output_path, 'comics_inventory.db')
    
    # Cria/conecta ao banco de dados
    print("\n📁 Criando/conectando ao banco de dados...")
    conn = create_database(db_path)
    print(f"   ✓ Banco de dados: {db_path}")
    
    # Escaneia diretório
    scan_directory(scan_path, conn)
    
    # Mostra estatísticas
    show_statistics(conn)
    
    # Mostra amostra
    show_sample_records(conn, 10)
    
    print("\n✅ Inventário completo!")
    print(f"   📁 Banco de dados salvo em: {db_path}")
    print(f"\n   Próximo passo: executar 'comic_identifier.py --db {db_path}' para identificar via Comic Vine API")
    
    conn.close()

if __name__ == "__main__":
    main()

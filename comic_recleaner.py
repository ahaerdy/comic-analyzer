#!/usr/bin/env python3
"""
Comic Re-cleaner - Re-processa nomes de arquivos no banco de dados
Útil quando a lógica de limpeza é melhorada
"""

import sqlite3
import re
import os
import sys

def clean_filename(filename):
    """
    Limpa o nome do arquivo para extrair título, edição e ano
    (Versão melhorada)
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

def reclean_database(db_path, status_filter=None, show_changes=False):
    """
    Re-processa todos os nomes no banco com a nova lógica de limpeza
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Seleciona registros para re-processar
    if status_filter:
        cursor.execute('SELECT id, file_name, clean_title FROM comics WHERE status = ?', (status_filter,))
    else:
        cursor.execute('SELECT id, file_name, clean_title FROM comics')
    
    records = cursor.fetchall()
    
    print(f"\n🔄 Re-processando {len(records)} registros...")
    print("=" * 70)
    
    changed = 0
    unchanged = 0
    
    for record_id, filename, old_clean in records:
        new_title, new_issue, new_year = clean_filename(filename)
        
        if new_title != old_clean:
            changed += 1
            
            if show_changes:
                print(f"\n📝 Mudança detectada:")
                print(f"   Arquivo: {filename}")
                print(f"   Antes:   {old_clean}")
                print(f"   Depois:  {new_title}")
            
            # Atualiza banco
            cursor.execute('''
                UPDATE comics 
                SET clean_title = ?,
                    issue_number = ?,
                    year = ?,
                    status = CASE 
                        WHEN status = 'identified' THEN 'identified'
                        ELSE 'pending' 
                    END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_title, new_issue, new_year, record_id))
        else:
            unchanged += 1
        
        if (changed + unchanged) % 1000 == 0:
            print(f"   Processados: {changed + unchanged}/{len(records)}", end='\r')
            conn.commit()
    
    conn.commit()
    
    print("\n" + "=" * 70)
    print(f"✅ Processamento completo!")
    print(f"   • Alterados: {changed}")
    print(f"   • Sem mudanças: {unchanged}")
    print("=" * 70)
    
    conn.close()

def show_problem_names(db_path, min_length=40):
    """
    Mostra nomes que provavelmente estão problemáticos
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"\n🔍 Buscando títulos com mais de {min_length} caracteres...")
    print("=" * 70)
    
    cursor.execute('''
        SELECT file_name, clean_title, status 
        FROM comics 
        WHERE LENGTH(clean_title) > ?
        ORDER BY LENGTH(clean_title) DESC
        LIMIT 50
    ''', (min_length,))
    
    results = cursor.fetchall()
    
    if not results:
        print("✅ Nenhum título problemático encontrado!")
    else:
        print(f"\n⚠️  {len(results)} títulos longos/problemáticos:\n")
        for filename, title, status in results:
            print(f"[{len(title):3d} chars] {title}")
            print(f"           Arquivo: {filename}")
            print(f"           Status: {status}\n")
    
    print("=" * 70)
    conn.close()

def reset_failed_to_pending(db_path):
    """
    Reseta registros 'not_found' e 'error' para 'pending' para nova tentativa
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM comics WHERE status IN ('not_found', 'error')")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("\n✅ Não há registros com erro para resetar!")
        conn.close()
        return
    
    print(f"\n⚠️  {count} registros com status 'not_found' ou 'error'")
    response = input("Deseja resetá-los para 'pending' e tentar novamente? (s/n): ").strip().lower()
    
    if response in ['s', 'sim', 'y', 'yes']:
        cursor.execute('''
            UPDATE comics 
            SET status = 'pending',
                error_message = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE status IN ('not_found', 'error')
        ''')
        conn.commit()
        print(f"✅ {count} registros resetados para 'pending'")
    else:
        print("❌ Operação cancelada")
    
    conn.close()

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Re-processa nomes de arquivos no banco de dados',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--db', default='comics_inventory.db', help='Caminho do banco de dados')
    parser.add_argument('--reclean', action='store_true', help='Re-processa todos os nomes')
    parser.add_argument('--show-changes', action='store_true', help='Mostra as mudanças ao re-processar')
    parser.add_argument('--status', choices=['pending', 'not_found', 'error', 'identified'], 
                       help='Re-processa apenas registros com este status')
    parser.add_argument('--show-problems', action='store_true', help='Mostra títulos problemáticos')
    parser.add_argument('--reset-failed', action='store_true', help='Reseta registros com erro para pending')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("  🧹 COMIC RE-CLEANER - Limpeza de Nomes")
    print("=" * 70)
    
    if not os.path.exists(args.db):
        print(f"\n❌ Banco de dados não encontrado: {args.db}")
        sys.exit(1)
    
    if args.show_problems:
        show_problem_names(args.db)
    
    elif args.reset_failed:
        reset_failed_to_pending(args.db)
    
    elif args.reclean:
        reclean_database(args.db, status_filter=args.status, show_changes=args.show_changes)
        print("\n💡 Dica: Execute 'comic_identifier.py' novamente para re-identificar os registros atualizados")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

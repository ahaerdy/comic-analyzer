#!/usr/bin/env python3
"""
Comic Path Updater - Sincroniza banco de dados com arquivos renomeados/movidos
"""

import sqlite3
import os
import sys
from pathlib import Path

COMIC_EXTENSIONS = {'.cbr', '.cbz', '.pdf', '.cbt', '.cb7'}

def find_orphaned_records(db_path):
    """Encontra registros cujo arquivo não existe mais"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, file_path, file_name FROM comics')
    records = cursor.fetchall()
    
    orphaned = []
    
    print("\n🔍 Verificando arquivos...")
    for record_id, file_path, file_name in records:
        if not os.path.exists(file_path):
            orphaned.append((record_id, file_path, file_name))
    
    conn.close()
    
    return orphaned

def find_files_by_size(root_dir, target_size, extension):
    """Encontra arquivos por tamanho (para matching)"""
    
    matches = []
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            
            if ext == extension:
                filepath = os.path.join(root, filename)
                try:
                    size = os.path.getsize(filepath)
                    if abs(size - target_size) < 1024:  # Tolerância de 1KB
                        matches.append(filepath)
                except:
                    pass
    
    return matches

def auto_fix_paths(db_path, scan_dir):
    """
    Tenta corrigir automaticamente paths quebrados
    Usa tamanho do arquivo como identificador único
    """
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Encontra órfãos
    orphaned = find_orphaned_records(db_path)
    
    if not orphaned:
        print("\n✅ Nenhum arquivo órfão encontrado!")
        print("   Todos os caminhos estão corretos.")
        conn.close()
        return
    
    print(f"\n⚠️  {len(orphaned)} registros órfãos encontrados\n")
    
    fixed = 0
    not_found = 0
    
    print("🔧 Tentando corrigir automaticamente...\n")
    
    for record_id, old_path, old_name in orphaned:
        
        # Busca tamanho antigo
        cursor.execute('SELECT file_size, file_ext FROM comics WHERE id = ?', (record_id,))
        result = cursor.fetchone()
        
        if not result:
            continue
        
        old_size, old_ext = result
        
        print(f"[{record_id}] {old_name}")
        print(f"   Procurando arquivo com ~{old_size/(1024*1024):.1f}MB e extensão {old_ext}...")
        
        # Busca arquivos com mesmo tamanho e extensão
        candidates = find_files_by_size(scan_dir, old_size, old_ext)
        
        if len(candidates) == 1:
            # Match único - muito provável que seja o mesmo arquivo!
            new_path = candidates[0]
            new_name = os.path.basename(new_path)
            
            print(f"   ✓ Encontrado: {new_name}")
            
            # Atualiza banco
            cursor.execute('''
                UPDATE comics 
                SET file_path = ?,
                    file_name = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_path, new_name, record_id))
            
            fixed += 1
            
        elif len(candidates) > 1:
            print(f"   ⚠️  {len(candidates)} candidatos encontrados (ambíguo)")
            print("      Use modo manual para resolver")
            not_found += 1
        else:
            print(f"   ✗ Não encontrado")
            not_found += 1
        
        print()
    
    conn.commit()
    conn.close()
    
    # Resultado
    print("=" * 70)
    print("📊 RESULTADO:")
    print(f"   • Corrigidos automaticamente: {fixed}")
    print(f"   • Não encontrados/ambíguos: {not_found}")
    print("=" * 70)

def list_orphaned(db_path):
    """Lista registros órfãos"""
    
    orphaned = find_orphaned_records(db_path)
    
    if not orphaned:
        print("\n✅ Nenhum arquivo órfão!")
        return
    
    print(f"\n⚠️  {len(orphaned)} registros órfãos:\n")
    
    for record_id, file_path, file_name in orphaned[:50]:  # Limita a 50
        print(f"[ID: {record_id:5d}] {file_name}")
        print(f"             Caminho: {file_path}")
        print()
    
    if len(orphaned) > 50:
        print(f"... e mais {len(orphaned) - 50} registros")

def delete_orphaned(db_path, confirm=True):
    """Remove registros órfãos do banco"""
    
    orphaned = find_orphaned_records(db_path)
    
    if not orphaned:
        print("\n✅ Nenhum arquivo órfão para remover!")
        return
    
    print(f"\n⚠️  {len(orphaned)} registros órfãos encontrados\n")
    
    if confirm:
        print("⚠️  ATENÇÃO: Esta ação não pode ser desfeita!")
        response = input("\nDeseja realmente DELETAR estes registros? (s/n): ").strip().lower()
        
        if response not in ['s', 'sim', 'y', 'yes']:
            print("\n❌ Operação cancelada")
            return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    orphaned_ids = [r[0] for r in orphaned]
    
    # Delete em lote
    placeholders = ','.join('?' * len(orphaned_ids))
    cursor.execute(f'DELETE FROM comics WHERE id IN ({placeholders})', orphaned_ids)
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ {len(orphaned_ids)} registros órfãos removidos")

def update_path_by_id(db_path, record_id, new_path):
    """Atualiza caminho de um registro específico"""
    
    if not os.path.exists(new_path):
        print(f"\n❌ Arquivo não existe: {new_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    new_name = os.path.basename(new_path)
    new_size = os.path.getsize(new_path)
    
    cursor.execute('''
        UPDATE comics 
        SET file_path = ?,
            file_name = ?,
            file_size = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (new_path, new_name, new_size, record_id))
    
    if cursor.rowcount > 0:
        print(f"\n✅ Registro {record_id} atualizado")
        print(f"   Novo caminho: {new_path}")
    else:
        print(f"\n❌ Registro {record_id} não encontrado")
    
    conn.commit()
    conn.close()

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Sincroniza banco com arquivos renomeados/movidos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Listar arquivos órfãos
  %(prog)s --db comics.db --list

  # Corrigir automaticamente (por tamanho de arquivo)
  %(prog)s --db comics.db --auto-fix /caminho/dos/comics

  # Remover órfãos do banco
  %(prog)s --db comics.db --delete

  # Atualizar um registro específico
  %(prog)s --db comics.db --update-id 12345 --new-path /novo/caminho/arquivo.cbr
        """
    )
    
    parser.add_argument('--db', required=True, help='Caminho do banco de dados')
    parser.add_argument('--list', action='store_true', 
                       help='Lista registros órfãos')
    parser.add_argument('--auto-fix', metavar='SCAN_DIR',
                       help='Tenta corrigir automaticamente buscando em SCAN_DIR')
    parser.add_argument('--delete', action='store_true',
                       help='Remove registros órfãos do banco')
    parser.add_argument('--update-id', type=int, metavar='ID',
                       help='Atualiza um registro específico')
    parser.add_argument('--new-path', metavar='PATH',
                       help='Novo caminho (usado com --update-id)')
    parser.add_argument('--no-confirm', action='store_true',
                       help='Não pede confirmação')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("  🔧 COMIC PATH UPDATER")
    print("=" * 70)
    
    if not os.path.exists(args.db):
        print(f"\n❌ Banco de dados não encontrado: {args.db}")
        sys.exit(1)
    
    if args.list:
        list_orphaned(args.db)
    
    elif args.auto_fix:
        if not os.path.exists(args.auto_fix):
            print(f"\n❌ Diretório não encontrado: {args.auto_fix}")
            sys.exit(1)
        auto_fix_paths(args.db, args.auto_fix)
    
    elif args.delete:
        delete_orphaned(args.db, confirm=not args.no_confirm)
    
    elif args.update_id:
        if not args.new_path:
            print("\n❌ --new-path é obrigatório quando usar --update-id")
            sys.exit(1)
        update_path_by_id(args.db, args.update_id, args.new_path)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

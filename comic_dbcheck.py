#!/usr/bin/env python3
"""
Database Diagnostics - Verifica o estado do banco de dados
"""

import sqlite3
import os
import sys

def check_database(db_path):
    """Verifica o estado do banco de dados"""
    
    print("=" * 70)
    print("  🔍 DIAGNÓSTICO DO BANCO DE DADOS")
    print("=" * 70)
    
    # Verifica se o arquivo existe
    print(f"\n📁 Verificando: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ Arquivo não encontrado!")
        print("\n💡 Solução:")
        print("   Execute primeiro: python3 comic_scanner.py")
        return False
    
    print(f"✅ Arquivo existe ({os.path.getsize(db_path)} bytes)")
    
    # Tenta conectar
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lista tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📋 Tabelas encontradas: {len(tables)}")
        
        if not tables:
            print("⚠️  Banco vazio (sem tabelas)")
            print("\n💡 Solução:")
            print("   Execute: python3 comic_scanner.py")
            return False
        
        for table in tables:
            print(f"   • {table[0]}")
        
        # Verifica se a tabela 'comics' existe
        table_names = [t[0] for t in tables]
        
        if 'comics' not in table_names:
            print("\n❌ Tabela 'comics' não encontrada!")
            print("\n💡 Solução:")
            print("   Execute: python3 comic_scanner.py")
            return False
        
        # Mostra estrutura da tabela comics
        cursor.execute("PRAGMA table_info(comics)")
        columns = cursor.fetchall()
        
        print("\n📊 Estrutura da tabela 'comics':")
        for col in columns:
            print(f"   • {col[1]} ({col[2]})")
        
        # Conta registros
        cursor.execute("SELECT COUNT(*) FROM comics")
        count = cursor.fetchone()[0]
        
        print(f"\n📈 Total de registros: {count}")
        
        if count == 0:
            print("⚠️  Banco vazio (sem registros)")
            print("\n💡 Solução:")
            print("   Execute: python3 comic_scanner.py /caminho/dos/seus/comics")
        else:
            # Mostra estatísticas por status
            cursor.execute("SELECT status, COUNT(*) FROM comics GROUP BY status")
            print("\n📊 Por status:")
            for status, cnt in cursor.fetchall():
                print(f"   • {status}: {cnt}")
        
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ Banco de dados OK!")
        print("=" * 70)
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Erro ao acessar banco: {e}")
        return False

def find_databases():
    """Procura por bancos de dados no sistema"""
    
    print("\n🔍 Procurando por arquivos comics_inventory.db...")
    print("=" * 70)
    
    common_paths = [
        '.',
        os.path.expanduser('~'),
        os.path.expanduser('~/Downloads'),
        os.path.expanduser('~/Documents'),
        os.path.expanduser('~/Documentos'),
    ]
    
    found = []
    
    for path in common_paths:
        if not os.path.exists(path):
            continue
        
        for root, dirs, files in os.walk(path, topdown=True):
            # Limita profundidade
            dirs[:] = [d for d in dirs if not d.startswith('.')][:5]
            
            if 'comics_inventory.db' in files:
                db_path = os.path.join(root, 'comics_inventory.db')
                size = os.path.getsize(db_path)
                found.append((db_path, size))
    
    if not found:
        print("❌ Nenhum banco encontrado nos locais comuns")
    else:
        print(f"✅ {len(found)} banco(s) encontrado(s):\n")
        for db_path, size in found:
            size_mb = size / (1024 * 1024)
            print(f"   📁 {db_path}")
            print(f"      Tamanho: {size_mb:.2f} MB\n")
    
    print("=" * 70)

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Diagnóstico do banco de dados')
    parser.add_argument('--db', default='comics_inventory.db', help='Caminho do banco')
    parser.add_argument('--find', action='store_true', help='Procura bancos no sistema')
    
    args = parser.parse_args()
    
    if args.find:
        find_databases()
    else:
        check_database(args.db)

if __name__ == "__main__":
    main()

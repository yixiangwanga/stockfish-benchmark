import time
import chess
import chess.engine
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURAZIONE ---
ENGINE_PATH = "C:/Users/yixia/Desktop/stockfish/stockfish-windows-x86-64-universal.exe"                          
HASH_SIZES = [16, 128, 512]                                        

def run_benchmark():
    results = []
    board = chess.Board("r1bq1rk1/pp2ppbp/2np1np1/8/3NP3/2N1BP2/PPPQ2PP/R3KB1R w KQ - 3 9")
    
    with chess.engine.SimpleEngine.popen_uci(ENGINE_PATH) as engine:
        engine.configure({"Threads": 1})
        
        for hash_mb in HASH_SIZES:
            engine.configure({"Hash": hash_mb})
            engine.protocol.send_line("ucinewgame")

            info = engine.analyse(board, chess.engine.Limit(depth=22))
            # hashfull è espresso in per mille: 1000 = 100%
            hashfull_pct = info.get("hashfull", 0) / 10.0
            
            results.append({
                "Hash_MB": str(hash_mb) + " MB",
                "Tempo_s": info.get("time", 0), 2),
                "Hashfull_pct": round(hashfull_pct, 1),
                "Nodi": info.get("nodes", 0)
            })
            
    return pd.DataFrame(results)

def plot_results(df):
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(f"Impatto della Hash Size (Profondità Fissa: {FIXED_DEPTH})", fontsize=14, fontweight='bold')
    
    colors = ['#e74c3c', '#f39c12', '#2ecc71']
    
    # Grafico 1: Tempo impiegato
    bars1 = ax1.bar(df["Hash_MB"], df["Tempo_s"], color=colors, edgecolor='black')
    ax1.set_title("Tempo di Calcolo (secondi)")
    ax1.set_ylabel("Secondi")
    ax1.grid(axis='y', linestyle='--', alpha=0.6)
    ax1.bar_label(bars1, fmt='%.2f s', padding=3)
    
    # Grafico 2: Saturazione Hash (Hashfull)
    bars2 = ax2.bar(df["Hash_MB"], df["Hashfull_pct"], color=colors, edgecolor='black')
    ax2.set_title("Saturazione Tabella (Hashfull %)")
    ax2.set_ylabel("Percentuale di riempimento (%)")
    ax2.set_ylim(0, 110)
    ax2.grid(axis='y', linestyle='--', alpha=0.6)
    ax2.bar_label(bars2, fmt='%.1f%%', padding=3)
    
    # Grafico 3: Nodi esplorati
    bars3 = ax3.bar(df["Hash_MB"], df["Nodi"] / 1_000_000, color=colors, edgecolor='black')
    ax3.set_title("Nodi Esplorati (Milioni)")
    ax3.set_ylabel("Milioni di nodi")
    ax3.grid(axis='y', linestyle='--', alpha=0.6)
    ax3.bar_label(bars3, fmt='%.2f M', padding=3)
    
    plt.tight_layout()
    plt.savefig("impatto_hash_size.png", dpi=300)
    print("Grafico salvato come 'impatto_hash_size.png'")
    plt.show()

if __name__ == "__main__":
    df_risultati = run_benchmark()
    print("--- RIEPILOGO DATI ---")
    print(df_risultati.to_string(index=False))
    plot_results(df_risultati)
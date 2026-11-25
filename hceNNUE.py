import chess
import chess.engine
import matplotlib.pyplot as plt
import numpy as np

STOCKFISH_PATH = "C:/Users/yixia/Desktop/stockHCE/stockfish/stockfish-windows-x86-64-avx2"

# Posizioni di test (Apertura, Mediogioco complesso, Finale)
TEST_POSITIONS = {
    "Posizione Iniziale": chess.STARTING_FEN,
    "Mediogioco (Siciliana)": "r1bq1rk1/pp2ppbp/2np1np1/8/3NP3/2N1BP2/PPPQ2PP/R3KB1R w KQ - 3 9",
    "Finale complesso": "8/p4p1p/5kp1/1p6/8/3b2P1/PPp2P1P/2R3K1 w - - 0 34"
}

def run_benchmark(engine_path, positions):
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    engine.configure({"Threads": 1, "Hash": 128})
    
    results = {"HCE": {}, "NNUE": {}}

    for mode, use_nnue in [("HCE", False), ("NNUE", True)]:
        engine.configure({"Use NNUE": use_nnue})
        
        for name, fen in positions.items():
            board = chess.Board(fen)
            # Pulizia della hash table prima di ogni analisi
            engine.configure({"Clear Hash": None})
            
            info = engine.analyse(board, chess.engine.Limit(time=3.0))
            nps = info.get("nps", 0)
            nodes = info.get("nodes", 0)
            depth = info.get("depth", 0)
            
            results[mode][name] = {
                "nps": nps,
                "nodes": nodes,
                "depth": depth
            }
            print(f"[{name}] NPS: {nps:,} | Nodi totali: {nodes:,} | Profondità: {depth}")

    engine.quit()
    return results

def plot_results(results):
    positions = list(TEST_POSITIONS.keys())
    hce_nps = [results["HCE"][p]["nps"] / 1_000 for p in positions]   # In kN/s
    nnue_nps = [results["NNUE"][p]["nps"] / 1_000 for p in positions] # In kN/s

    x = np.arange(len(positions))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, hce_nps, width, label='HCE (Valutazione Classica)', color='#3498db')
    rects2 = ax.bar(x + width/2, nnue_nps, width, label='NNUE (Rete Neurale)', color='#e74c3c')

    ax.set_ylabel('Nodi al Secondo (kN/s)', fontsize=11)
    ax.set_title('Confronto Velocità di Calcolo: Stockfish 16 HCE vs NNUE (1 Thread)', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(positions, fontsize=10)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    # Aggiunge i valori e la differenza percentuale sopra le barre
    for i in range(len(positions)):
        ax.annotate(f'{hce_nps[i]:.0f} kN/s',
                    xy=(x[i] - width/2, hce_nps[i]),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        diff_pct = ((nnue_nps[i] - hce_nps[i]) / hce_nps[i]) * 100
        ax.annotate(f'{nnue_nps[i]:.0f} kN/s\n({diff_pct:+.1f}%)',
                    xy=(x[i] + width/2, nnue_nps[i]),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color='#c0392b')

    plt.tight_layout()
    plt.savefig("confronto_nps_sf16.png", dpi=300)
    print("\nGrafico salvato come 'confronto_nps_sf16.png'")
    plt.show()

if __name__ == "__main__":
    dati = run_benchmark(STOCKFISH_PATH, TEST_POSITIONS)
    plot_results(dati)
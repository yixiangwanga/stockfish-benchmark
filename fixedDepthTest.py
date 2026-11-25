import chess
import chess.engine
import matplotlib.pyplot as plt

ENGINE_PATH = "C:/Users/yixia/Desktop/stockfish/stockfish-windows-x86-64-universal.exe"
MOVETIME_SEC = 5.0          # Tempo fisso in secondi per ogni test
HASH_MB = 512
THREAD_LIST = [1, 2, 4, 8]

def run_benchmark():
    nps_results = []
    depth_results = []
    board = chess.Board("r1bq1rk1/pp2ppbp/2np1np1/8/3NP3/2N1BP2/PPPQ2PP/R3KB1R w KQ - 3 9")

    # Avvia Stockfish
    with chess.engine.SimpleEngine.popen_uci(ENGINE_PATH) as engine:
        for threads in THREAD_LIST:
            # Configurazione motore
            engine.configure({
                "Threads": threads,
                "Hash": HASH_MB
            })

	    # Pulisce la memoria Hash per evitare contaminazioni dal test precedente
            engine.protocol.send_line("ucinewgame")
	    # Analizza la posizione impostata per 5 secondi
            info = engine.analyse(board, chess.engine.Limit(time=MOVETIME_SEC))
            
            nps_results.append(info.get("nps", 0))
            depth_results.append(info.get("depth", 0))

    return nps_results, depth_results

def plot_results(threads_list, nps_list, depths_list):
    mnps_list = [nps / 1_000_000 for nps in nps_list]

    fig, ax1 = plt.subplots(figsize=(11, 6))

    # --- ASSE SINISTRO: MN/s (Velocità) ---
    color_nps = '#1f77b4' # Blu
    ax1.set_xlabel("Numero di Thread", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Mega-Nodi al Secondo (MN/s)", color=color_nps, fontsize=12, fontweight='bold')
    
    line1 = ax1.plot(threads_list, mnps_list, marker='o', linewidth=2.5, color=color_nps, label='Velocità (MN/s)')
    ax1.tick_params(axis='y', labelcolor=color_nps)
    ax1.set_xticks(threads_list)
    ax1.grid(True, linestyle=':', alpha=0.6)

    # Etichette valori MN/s
    for i, val in enumerate(mnps_list):
        ax1.annotate(f"{val:.2f} MN/s",
                     (threads_list[i], val),
                     textcoords="offset points",
                     xytext=(0, 10),
                     ha='center',
                     fontsize=9,
                     color=color_nps,
                     fontweight='bold')

    # --- ASSE DESTRO: Profondità (Depth) ---
    ax2 = ax1.twinx()
    color_depth = '#d62728' # Rosso
    ax2.set_ylabel("Profondità Raggiunta (Depth)", color=color_depth, fontsize=12, fontweight='bold')
    
    line2 = ax2.plot(threads_list, depths_list, marker='s', linewidth=2.5, linestyle='-.', color=color_depth, label='Profondità (Ply)')
    ax2.tick_params(axis='y', labelcolor=color_depth)
    
    min_d = min(depths_list) - 2
    max_d = max(depths_list) + 3
    ax2.set_ylim(min_d, max_d)

    # Unisce le due legende in un unico riquadro
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True, shadow=True)

    plt.title(f"Benchmark Motore: Velocità (MN/s) vs Profondità ({MOVETIME_SEC}s)", fontsize=14, pad=15, fontweight='bold')
    fig.tight_layout()

    output_file = "benchmark_nps_depth.png"
    plt.savefig(output_file, dpi=300)
    print(f"Grafico salvato con successo in: {output_file}")
    plt.show()

if __name__ == "__main__":

    nps_data, depth_data = run_benchmark()
    plot_results(THREAD_LIST, nps_data, depth_data)
import subprocess
import re
import matplotlib.pyplot as plt

STOCKFISH_PATH = "C:/Users/yixia/Desktop/stockfish/stockfish-windows-x86-64-universal.exe" 
THREADS_LIST = [1, 2, 4, 8]
HASH_SIZE_MB = 128
DEPTH_LIMIT = 13

def stockfish_bench(sf_path, hash_mb, threads, depth):

    # Comando CLI: stockfish bench [hash] [threads] [limit]
    cmd = [sf_path, "bench", str(hash_mb), str(threads), str(depth)]
    print(f"Esecuzione test con {threads} thread(s) (Hash: {hash_mb}MB, Depth: {depth})...")

    # Esecuzione comando e stampa dei risultati del benchmark su stderr
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Estrazione tramite Regex dei valori finali
    nps = int(re.search(r"Nodes/second\s*:\s*(\d+)", result.stderr).group(1))
    time_ms = int(re.search(r"Total time \(ms\)\s*:\s*(\d+)", result.stderr).group(1))

    return nps, time_ms

def plot_results(threads_list, nps_list, time_list):
    # Convertiamo NPS in Mega-Nodi al secondo (MN/s) per una lettura più pulita
    mnps_list = [nps / 1_000_000 for nps in nps_list]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle(f"Benchmark Stockfish (Hash: {HASH_SIZE_MB}MB | Depth: {DEPTH_LIMIT})", fontsize=14, fontweight='bold')

    # --- Grafico 1: Mega-Nodes Per Second (MN/s) ---
    bars = ax1.bar([str(t) for t in threads_list], mnps_list, color='#2b5c8f', width=0.5)
    ax1.set_title("Velocità di Calcolo (MN/s)", fontsize=12)
    ax1.set_xlabel("Numero di Thread", fontsize=10)
    ax1.set_ylabel("Mega-Nodi al Secondo (MN/s)", fontsize=10)
    ax1.grid(axis='y', linestyle='--', alpha=0.6)

    # Aggiunge le etichette numeriche sopra ogni barra
    for bar in bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + (max(mnps_list)*0.02), f"{yval:.2f} M", ha='center', va='bottom', fontweight='bold')

    # --- Grafico 2: Tempo totale di esecuzione (Secondi) ---
    time_sec = [t / 1000.0 for t in time_list]
    ax2.plot([str(t) for t in threads_list], time_sec, marker='o', color='#d9534f', linewidth=2.5, markersize=8)
    ax2.set_title("Tempo Totale Esecuzione", fontsize=12)
    ax2.set_xlabel("Numero di Thread", fontsize=10)
    ax2.set_ylabel("Tempo (Secondi)", fontsize=10)
    ax2.grid(True, linestyle='--', alpha=0.6)

    for i, txt in enumerate(time_sec):
        ax2.annotate(f"{txt:.2f}s", (str(threads_list[i]), time_sec[i]), textcoords="offset points", xytext=(0,10), ha='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig("stockfish_benchmark.png", dpi=150)
    print("Grafico salvato come 'stockfish_benchmark.png'")
    plt.show()

if __name__ == "__main__":
    valid_threads = []
    nps_results = []
    time_results = []

    for t in THREADS_LIST:
        nps, time_ms = stockfish_bench(STOCKFISH_PATH, HASH_SIZE_MB, t, DEPTH_LIMIT)

        valid_threads.append(t)
        nps_results.append(nps)
        time_results.append(time_ms)

    plot_results(valid_threads, nps_results, time_results)
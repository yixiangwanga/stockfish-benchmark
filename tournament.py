import subprocess
import re
import matplotlib.pyplot as plt
import numpy as np

# Configurazione file e parametri del torneo
CUTECHESS_EXE = "./cutechess-cli.exe"
STOCKFISH_EXE = "./stockfish-windows-x86-64-avx2"
OPENINGS_FILE = "./aperture.epd"      
TIME_CONTROL = "5+0.05"  
CONCURRENCY = 4         
	
def run_cutechess_and_parse():
    cmd = [
        CUTECHESS_EXE,
        "-engine", "name=SF16_NNUE", f"cmd={STOCKFISH_EXE}", "option.Use NNUE=true",
        "-engine", "name=SF16_HCE", f"cmd={STOCKFISH_EXE}", "option.Use NNUE=false",
        "-each", "proto=uci", f"tc={TIME_CONTROL}", "option.Threads=1", "option.Hash=64",
        "-openings", f"file={OPENINGS_FILE}", "format=epd", "order=random",
        "-repeat",
        "-games", "100",
        "-concurrency", str(CONCURRENCY),
    ]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Regex per leggere l'output standard di cutechess-cli
    score_pattern = re.compile(r"Score of SF16_NNUE vs SF16_HCE:\s+(\d+)\s+-\s+(\d+)\s+-\s+(\d+)\s+\[[\d.]+\]\s+(\d+)")
    elo_pattern = re.compile(r"Elo difference:\s+([+-]?\d+\.\d+)\s+\+/-\s+(\d+\.\d+),\s+LOS:\s+(\d+\.\d+)\s+%")

    # Liste per tracciare l'andamento partita dopo partita
    game_numbers = [0]
    cumulative_score_diff = [0.0]  # Differenza punti netta (NNUE - HCE)
    
    wins, losses, draws = 0, 0, 0
    elo_diff, elo_err, los = 0.0, 0.0, 0.0

    for line in process.stdout:
        line = line.strip()
        
        # Cattura l'aggiornamento del punteggio
        score_match = score_pattern.search(line)
        if score_match:
            w, l, d, total = map(int, score_match.groups())
            wins, losses, draws = w, l, d
            game_numbers.append(total)
            # Ogni vittoria vale +1, ogni sconfitta -1, patta 0
            cumulative_score_diff.append(w - l)
            print(f"Partita {total}/{NUM_GAMES} -> NNUE: {w} | HCE: {l} | Patte: {d}")

        # Cattura il calcolo statistico Elo e LOS
        elo_match = elo_pattern.search(line)
        if elo_match:
            elo_diff = float(elo_match.group(1))
            elo_err = float(elo_match.group(2))
            los = float(elo_match.group(3))

    process.wait()
    print(f"Risultato finale (NNUE vs HCE): +{wins} -{losses} ={draws}")
    print(f"Differenza Elo: {elo_diff:+.1f} ± {elo_err:.1f} (LOS: {los:.1f}%)")

    return {
        "games": game_numbers,
        "score_diff": cumulative_score_diff,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "elo_diff": elo_diff,
        "elo_err": elo_err,
        "los": los
    }

def generate_thesis_plots(data):
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

    # --- GRAFICO 1: Andamento cumulativo del vantaggio (Random Walk) ---
    ax1.plot(data["games"], data["score_diff"], color='#2c3e50', linewidth=2, label='Vantaggio netto NNUE (Vittorie - Sconfitte)')
    ax1.axhline(0, color='#e74c3c', linestyle='--', linewidth=1.2, label='Parità teorica (0)')
    ax1.fill_between(data["games"], data["score_diff"], 0, where=(np.array(data["score_diff"]) >= 0), color='#27ae60', alpha=0.15)
    
    ax1.set_title("Progressione del Vantaggio nel Torneo", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Numero di Partite Giocate", fontsize=10)
    ax1.set_ylabel("Differenza Punti Netta (NNUE - HCE)", fontsize=10)
    ax1.legend(loc='upper left', fontsize=9)

    # --- GRAFICO 2: Distribuzione Esiti e Stima Elo ---
    categories = ['Vittorie NNUE', 'Patte', 'Vittorie HCE']
    counts = [data["wins"], data["draws"], data["losses"]]
    colors = ['#27ae60', '#95a5a6', '#c0392b']

    bars = ax2.bar(categories, counts, color=colors, width=0.55)
    ax2.set_title("Distribuzione degli Esiti", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Numero di Partite", fontsize=10)
    ax2.set_ylim(0, max(counts) * 1.2)

    # Aggiunge etichette numeriche e percentuali sopra le barre
    total_games = sum(counts)
    for bar in bars:
        yval = bar.get_height()
        pct = (yval / total_games) * 100 if total_games > 0 else 0
        ax2.text(bar.get_x() + bar.get_width()/2, yval + (max(counts)*0.02),
                 f"{yval}\n({pct:.1f}%)", ha='center', va='bottom', fontsize=9.5, fontweight='bold')

    # Box informativo con Elo e LOS per la tesi
    stats_text = (
        f"Differenza Elo: {data['elo_diff']:+.1f} ± {data['elo_err']:.1f}\n"
        f"LOS (Prob. Superiorità): {data['los']:.1f}%\n"
        f"Cadenza: {TIME_CONTROL}s | Threads: 1"
    )
    ax2.text(0.95, 0.92, stats_text, transform=ax2.transAxes, fontsize=9.5,
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8f9fa', edgecolor='#bdc3c7'))

    plt.suptitle("Confronto Forza di Gioco: Stockfish 16 NNUE vs HCE", fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    output_filename = "risultati_torneo_tesi.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"\nGrafico salvato ad alta risoluzione come '{output_filename}'")
    plt.show()

if __name__ == "__main__":
    risultati = run_cutechess_and_parse()
    generate_thesis_plots(risultati)
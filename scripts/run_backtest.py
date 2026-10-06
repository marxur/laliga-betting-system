"""Ejecuta el backtest reproducible y escribe outputs/reports/backtest_actual.md."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import ejecutar


def main():
    Path("outputs/logs").mkdir(parents=True, exist_ok=True)
    Path("outputs/reports").mkdir(parents=True, exist_ok=True)
    informe = ejecutar(escribir=True)
    cartera = informe["cartera"]
    print(f"Partidos: {informe['partidos']} train={informe['train']} test={informe['test']}")
    print(f"Cartera test: {cartera['aciertos']}/{cartera['disparos']} ROI={cartera['roi']:.1%}")
    print(f"Edge: {informe['edge_cartera']['mensaje']}")
    print(f"Informe: {informe['informe']}")


if __name__ == "__main__":
    main()

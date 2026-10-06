"""Pipeline reproducible de La Liga a partir de los CSV locales."""

import pandas as pd

from src.config import DATA_CONFIG, BASE_DIR
from src.data.cleaner import DataCleaner
from src.data.feature_engineering import FeatureEngineer
from src.rules.laliga_rules import crear_reglas_laliga
from src.backtest.engine import BacktestEngine
from src.backtest.validation import DataValidator


def cargar_laliga_local() -> pd.DataFrame:
    global_dir = BASE_DIR / "data" / "global"
    raw_dir = DATA_CONFIG.raw_dir
    files = sorted(global_dir.glob("SP1_*.csv"))
    if not files:
        files = sorted(raw_dir.glob("SP1_*.csv"))
    if not files:
        raise FileNotFoundError("No hay CSV SP1 en data/global ni en data/raw")

    frames = []
    for path in files:
        df = pd.read_csv(path, encoding="latin1")
        temporada = path.stem.split("_")[-1]
        df["Temporada"] = f"20{temporada[:2]}-{temporada[2:]}"
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def preparar() -> pd.DataFrame:
    raw = cargar_laliga_local()
    limpio = DataCleaner.limpiar(raw)
    return FeatureEngineer().generar_todas_features(limpio)


def aplicar_confianza_de_train(reglas, resultados_train, minimo=30):
    for regla in reglas:
        res = resultados_train.get(regla.nombre)
        if not res or res["disparos"] < minimo:
            regla.activa = False
            continue
        regla.confianza_esperada = res["win_rate"]
        regla.activa = True
    return reglas


def ejecutar(escribir=True):
    df = preparar()
    validator = DataValidator()
    train, test = validator.split_temporal(df)
    reglas = crear_reglas_laliga()

    train_res = BacktestEngine(train, reglas).ejecutar(verbose=False)
    test_res = BacktestEngine(test, reglas).ejecutar(verbose=False)
    aplicar_confianza_de_train(reglas, train_res)
    cartera = BacktestEngine(test, reglas).ejecutar_cartera(verbose=False)
    edge_cartera = validator.validar_contra_cuota(cartera.get("partidos") or [])

    filas = []
    for regla in reglas:
        res = test_res[regla.nombre]
        edge = validator.validar_contra_cuota(res.get("partidos") or [])
        filas.append({
            "regla": regla.nombre,
            "activa_tras_train": regla.activa,
            "confianza_train": regla.confianza_esperada,
            "disparos_test": res["disparos"],
            "win_rate_test": res["win_rate"],
            "roi_test": res["roi"],
            "drawdown_test": res["max_drawdown"],
            "omitidos": res["omitidos_sin_cuota"],
            "edge": edge["mensaje"],
            "valida": validator.validar_regla(res),
        })

    informe = {
        "partidos": len(df),
        "train": len(train),
        "test": len(test),
        "filas": filas,
        "cartera": cartera,
        "edge_cartera": edge_cartera,
    }
    if escribir:
        path = BASE_DIR / "outputs" / "reports" / "backtest_actual.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_markdown(informe), encoding="utf-8")
        informe["informe"] = str(path)
    return informe


def _markdown(informe) -> str:
    lineas = [
        "# Backtest generado por el motor actual",
        "",
        "Estas cifras salen de `src/pipeline.py` sobre `data/global/SP1_*.csv`.",
        "No son las de la tabla antigua del README.",
        "",
        f"- Partidos: {informe['partidos']}",
        f"- Train: {informe['train']}",
        f"- Test: {informe['test']}",
        "",
        "| Regla | Confianza train | Disparos test | Win rate | ROI | Drawdown | Edge |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for fila in informe["filas"]:
        lineas.append(
            f"| {fila['regla']} | {fila['confianza_train']:.1%} | {fila['disparos_test']} | "
            f"{fila['win_rate_test']:.1%} | {fila['roi_test']:.1%} | "
            f"{fila['drawdown_test']:.2f}u | {fila['edge']} |"
        )
    cartera = informe["cartera"]
    edge = informe["edge_cartera"]
    lineas += [
        "",
        "## Cartera en test",
        "",
        "Una apuesta por partido. La confianza es el win rate de train, no el número escrito a mano.",
        f"- Disparos: {cartera['disparos']}",
        f"- Aciertos: {cartera['aciertos']}",
        f"- ROI: {cartera['roi']:.1%}",
        f"- Ganancia: {cartera['ganancia_total']:.2f} unidades",
        f"- Drawdown: {cartera['max_drawdown']:.2f} unidades",
        f"- Edge: {edge['mensaje']}",
        "",
        "Si el edge no es significativo, la regla no está validada aunque el ROI puntual sea positivo.",
    ]
    return "\n".join(lineas) + "\n"

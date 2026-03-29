from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).resolve().parent / "rf_depenses.joblib"
_model = None


def get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def statut_to_features(statut: str):
    s = (statut or "").upper()
    statut_retraite = 1 if s == "RETRAITE" else 0
    statut_salarie = 1 if s == "SALARIE" else 0
    return statut_retraite, statut_salarie


def predict_depense(age: int, salaire_mensuel: float, statut: str) -> float:
    model = get_model()
    statut_retraite, statut_salarie = statut_to_features(statut)

    X = [[age, float(salaire_mensuel), statut_retraite, statut_salarie]]
    y_pred = model.predict(X)[0]
    return float(y_pred)

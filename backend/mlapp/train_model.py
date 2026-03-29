import joblib 

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

df = pd.read_csv("dataset_ml_normalise.csv")

X = df[["age", "salaire_mensuel", "statut_retraite", "statut_salarie"]]
y = df["depense_totale"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("MAE :", mean_absolute_error(y_test, y_pred), "€")
print("R²  :", r2_score(y_test, y_pred))

# =========================
# SAUVEGARDE DU MODELE
# =========================
joblib.dump(model, "rf_depenses.joblib")

print(" Modèle sauvegardé : rf_depenses.joblib")

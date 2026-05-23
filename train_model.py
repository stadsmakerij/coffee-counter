import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

VAL_RATIO = 0.2
RANDOM_STATE = 42

data = pd.read_csv('power_log.csv')
data = data[data['coffee_brewed'].isin(['yes', 'no'])]
data['coffee_brewed'] = data['coffee_brewed'].map({'yes': 1, 'no': 0})

# cup_id increments on every 0->1 transition; idle rows after a cup share its id
data['cup_id'] = (data['coffee_brewed'].diff() == 1).cumsum().astype(int)
total_cups = int(data['cup_id'].max())

data['timestamp'] = pd.to_datetime(data['timestamp'])
data = data.set_index('timestamp')

data['mean_30s'] = data['power'].rolling('30s').mean()
data['max_30s'] = data['power'].rolling('30s').max()
data['min_30s'] = data['power'].rolling('30s').min()
data['std_30s'] = data['power'].rolling('30s').std().fillna(0)

data = data.dropna()

X = data[['power', 'mean_30s', 'max_30s', 'min_30s', 'std_30s']]
y = data['coffee_brewed']
groups = data['cup_id']

splitter = GroupShuffleSplit(n_splits=1, test_size=VAL_RATIO, random_state=RANDOM_STATE)
train_idx, val_idx = next(splitter.split(X, y, groups=groups))

X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
groups_val = groups.iloc[val_idx]

train_cups = sorted({c for c in groups.iloc[train_idx].unique() if c > 0})
val_cups = sorted({c for c in groups_val.unique() if c > 0})

model = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE)
model.fit(X_train, y_train)

y_pred = model.predict(X_val)

cups_detected = 0
for cup in val_cups:
    cup_mask = (groups_val == cup) & (y_val == 1)
    if cup_mask.any() and y_pred[cup_mask.values].sum() > 0:
        cups_detected += 1

print(f"Total labeled cups: {total_cups}")
print(f"Train: {len(train_cups)} cups / {len(X_train)} rows")
print(f"Val:   {len(val_cups)} cups / {len(X_val)} rows")
print()
print(f"Row-level accuracy: {(y_pred == y_val).mean():.3f}")
print()
print("Classification report:")
print(classification_report(y_val, y_pred, target_names=['no', 'yes'], zero_division=0))
print("Confusion matrix (rows = actual, cols = predicted):")
print(confusion_matrix(y_val, y_pred))
print()
print(f"Cup-level detection: {cups_detected}/{len(val_cups)} validation cups detected")

joblib.dump(model, 'coffee_model.pkl')
print(f"\nModel saved as 'coffee_model.pkl' (trained on {len(train_cups)} cups).")

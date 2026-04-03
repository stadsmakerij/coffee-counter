import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

data = pd.read_csv('power_log.csv')

data = data[data['coffee_brewed'].isin(['yes', 'no'])]

data['coffee_brewed'] = data['coffee_brewed'].map({'yes': 1, 'no': 0})

coffee_count = int((data['coffee_brewed'].diff() == 1).sum())

data['timestamp'] = pd.to_datetime(data['timestamp'])
data = data.set_index('timestamp')

data['mean_30s'] = data['power'].rolling('30s').mean()
data['max_30s'] = data['power'].rolling('30s').max()
data['min_30s'] = data['power'].rolling('30s').min()
data['std_30s'] = data['power'].rolling('30s').std().fillna(0)

data = data.dropna()

X = data[['power', 'mean_30s', 'max_30s', 'min_30s', 'std_30s']]
y = data['coffee_brewed']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
joblib.dump(model, 'coffee_model.pkl')
print(f"Trained model has been saved as 'coffee_model.pkl' (trained on {coffee_count} cups of coffee).")

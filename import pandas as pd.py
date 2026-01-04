import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc, confusion_matrix, ConfusionMatrixDisplay

# --- STEP 1: CREATE MOCK DATA (Simulating your London Logistics Scenario) ---
# In your real project, you would load your CSVs here instead.
np.random.seed(42) # Consistent results
n_samples = 1000

data = pd.DataFrame({
    'Rainfall_mm': np.random.exponential(scale=2, size=n_samples), # Skewed rain data
    'Rush_Hour': np.random.choice([0, 1], size=n_samples),         # 0=No, 1=Yes
    'Is_Weekend': np.random.choice([0, 1], size=n_samples),        # 0=Weekday, 1=Weekend
    'Retail_Index': np.random.normal(100, 10, size=n_samples)      # Economic activity
})

# Create a realistic "Target" variable (Did a delay happen?)
# Logic: If it rains heavily OR (rush hour AND high retail activity) -> Delay likely
data['Delay_Risk'] = (
    (data['Rainfall_mm'] > 3) * 0.6 + 
    (data['Rush_Hour'] * 0.5) + 
    (data['Is_Weekend'] * -0.3) + 
    np.random.normal(0, 0.2, size=n_samples)
)
data['Was_Delayed'] = (data['Delay_Risk'] > 0.6).astype(int) # 1 = Delayed, 0 = On Time

# --- STEP 2: TRAIN THE MODEL ---
X = data[['Rainfall_mm', 'Rush_Hour', 'Is_Weekend', 'Retail_Index']]
y = data['Was_Delayed']

# Split data (Chronological split is best for time-series, but we use random here for demo)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Initialize Decision Tree (Max depth 3 to keep the diagram readable)
clf = DecisionTreeClassifier(max_depth=3, random_state=42)
clf.fit(X_train, y_train)

# --- STEP 3: GENERATE THE GRAPHS ---

# Figure 1: Feature Importance (The Business Insight)
plt.figure(figsize=(10, 5))
plt.barh(X.columns, clf.feature_importances_, color='#1f77b4')
plt.xlabel('Importance Score')
plt.title('Figure 1: Feature Importance - What Causes Delays?')
plt.show()

# Figure 2: ROC Curve (The Validation)
y_prob = clf.predict_proba(X_test)[:, 1]
fpr, tpr, _ = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Figure 2: Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc="lower right")
plt.show()

# Figure 3: Confusion Matrix (Accuracy Breakdown)
y_pred = clf.predict(X_test)
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['On Time', 'Delayed'])
disp.plot(cmap='Blues')
plt.title('Figure 3: Confusion Matrix')
plt.show()

# Figure 4: The Tree Diagram (Transparency/gdpr)
plt.figure(figsize=(20, 10))
plot_tree(clf, feature_names=X.columns, class_names=['On Time', 'Delayed'], filled=True, rounded=True)
plt.title('Figure 4: Decision Tree Logic Flow')
plt.show()
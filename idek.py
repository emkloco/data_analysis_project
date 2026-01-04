# classification_model.py

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
from sklearn import tree

def prepare_classification_data(df):
    """
    Prepare data for market positioning classification.
    
    Features: regional economic indicators
    Target: best-performing retail segment
    """
    features = [
        'gini_coefficient',
        'median_income',
        'p90_p10_ratio',
        'discretionary_income',
        'population_density'
    ]
    
    X = df[features]
    y = df['optimal_segment']  # Budget/Mid/Premium
    
    return X, y

def train_decision_tree(X, y):
    """
    Train decision tree classifier for market segmentation.
    
    Returns model and performance metrics.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    model = DecisionTreeClassifier(
        max_depth=4,  # Keep interpretable
        min_samples_split=10,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    cv_scores = cross_val_score(model, X, y, cv=10)
    
    return model, {
        'train_accuracy': train_score,
        'test_accuracy': test_score,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std()
    }

def visualize_tree(model, feature_names, class_names):
    """
    Create publication-quality decision tree visualization.
    """
    plt.figure(figsize=(20, 10))
    tree.plot_tree(
        model,
        feature_names=feature_names,
        class_names=class_names,
        filled=True,
        rounded=True,
        fontsize=10
    )
    plt.tight_layout()
    return plt.gcf()

def feature_importance_analysis(model, feature_names):
    """
    Analyze which features matter most for classification.
    """
    importances = model.feature_importances_
    return pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=False)
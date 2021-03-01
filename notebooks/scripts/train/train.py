import argparse
import os
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing
from sklearn.model_selection import StratifiedKFold, cross_val_score, GridSearchCV


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Hyperparameters are described here. In this simple example we are just including one hyperparameter.
    parser.add_argument('--max_leaf_nodes', type=int, default=-1)

    # Sagemaker specific arguments. Defaults are set in the environment variables.
    parser.add_argument('--output-data-dir', type=str, default=os.environ['SM_OUTPUT_DATA_DIR'])
    parser.add_argument('--model-dir', type=str, default=os.environ['SM_MODEL_DIR'])
    parser.add_argument('--train', type=str, default=os.environ['SM_CHANNEL_TRAIN'])
    
    args = parser.parse_args()
    train_path = os.path.join(args.train, 'train.csv')
    train = pd.read_csv(train_path)
        
    X_train, y_train = train.drop(['Survived'], axis=1), train['Survived']
    y_train = y_train.astype({"Survived": int})
    
    rf = RandomForestClassifier(n_estimators=100, n_jobs=-1)

    param_grid =  {
        "criterion": ["gini", "entropy"],
        "max_depth":[i for i in range(1, 5)]
                  }

    stratifiedkfold = StratifiedKFold(n_splits=3)
    grid_search = GridSearchCV(rf, param_grid, cv=stratifiedkfold, refit=True, scoring='f1')
    grid_search.fit(X_train, y_train)
    joblib.dump(grid_search, os.path.join(args.model_dir, "model.joblib"))


def model_fn(model_dir):
    """Deserialized and return fitted model

    Note that this should have the same name as the serialized model in the main method
    """
    clf = joblib.load(os.path.join(model_dir, "model.joblib"))
    return clf
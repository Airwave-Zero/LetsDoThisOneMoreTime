import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib

def create_email_categorizer(csv_path = '../email_data/email_training_data.csv',
                             model_path = 'email_judge_model.pkl'):
    ''' Use LogisticRegression for easy implementation and high speed
    Could be improved to RandomForest or BERT but requires more resources
    Ultimately choosing this as a starting point'''
    # Import all the emails from the correct folder
    df = pd.read_csv(csv_path, encoding='ISO-8859-1')
    df = df.dropna(subset=['body', 'label'])

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(df['body'], df['label'], test_size=0.2, random_state=42)

    # Build pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_df=0.95,
            min_df=2
        )),('clf', LogisticRegression(max_iter=1000))
    ])

    # Train model
    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))

    # Save model
    joblib.dump(pipeline, 'email_judge_model.pkl')

def load_model(model_path='email_judge_model.pkl'):
    return joblib.load(model_path)

def classify_email(subject, body):
    text = f"{subject} {body}"
    model = load_model()
    return model.predict([text])[0]

create_email_categorizer()

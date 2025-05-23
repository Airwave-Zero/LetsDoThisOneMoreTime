import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib

# Import all the emails from the correct folder
df = pd.read_csv('../email_data/email_training_data.csv')

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(df['content'], df['label'], test_size=0.2, random_state=42)

# Build pipeline
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2),
        max_df=0.95,
        min_df=2
    )),
    ''' Use LogisticRegression for easy implementation and high speed
        Could be improved to RandomForest or BERT but requires more resources
        Ultimately choosing this as a starting point'''
    ('clf', LogisticRegression(max_iter=1000))
])

# Train model
pipeline.fit(X_train, y_train)

# Evaluate
y_pred = pipeline.predict(X_test)
print(classification_report(y_test, y_pred))

# Save model
joblib.dump(pipeline, 'email_judger_model.pkl')

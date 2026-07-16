import os
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.metrics import accuracy_score

def train():
    # Path to news.csv in the workspace directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(os.path.dirname(current_dir))
    csv_path = os.path.join(workspace_dir, 'news.csv')
    print(f"Loading dataset from: {csv_path}")
    
    # Read the dataset
    df = pd.read_csv(csv_path, encoding='latin-1')
    
    # Drop rows where critical columns are missing
    df = df.dropna(subset=['text', 'label'])
    
    # Combine title and text
    df['title'] = df['title'].fillna('')
    df['combined_text'] = df['title'] + " " + df['text']
    
    # Filter only REAL and FAKE labels
    df = df[df['label'].isin(['REAL', 'FAKE'])]
    
    X = df['combined_text']
    y = df['label']
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Vectorizing text using TF-IDF...")
    # Initialize TF-IDF Vectorizer
    tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
    
    # Fit and transform
    X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
    X_test_tfidf = tfidf_vectorizer.transform(X_test)
    
    print("Training PassiveAggressiveClassifier...")
    # Initialize PassiveAggressiveClassifier
    pac = PassiveAggressiveClassifier(max_iter=50)
    pac.fit(X_train_tfidf, y_train)
    
    # Predict and calculate accuracy
    y_pred = pac.predict(X_test_tfidf)
    score = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {score:.2%}")
    
    # Save the model and vectorizer
    model_path = os.path.join(current_dir, 'model.pkl')
    vectorizer_path = os.path.join(current_dir, 'vectorizer.pkl')
    
    print(f"Saving model to {model_path}...")
    with open(model_path, 'wb') as f:
        pickle.dump(pac, f)
        
    print(f"Saving vectorizer to {vectorizer_path}...")
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(tfidf_vectorizer, f)
        
    print("Training finished successfully!")

if __name__ == '__main__':
    train()

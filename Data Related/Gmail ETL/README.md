Gmail ETL Pipeline — Job Application Tracker

This project is a backend-focused ETL pipeline designed to automate the classification and analysis of job application emails from Gmail. By extracting relevant emails, transforming them into a structured format, and visualizing insights, the system helps track the job search journey over time. 

Also, it was extended to help get my finances on track and reduce spending/understanding my bad spending habits.

Project Overview
===============
The pipeline handles the full lifecycle of data collection and analysis:

Extract job-related and financial emails using the Gmail API with OAuth 2.0 authentication
Transform raw email content through normalization and classification
Load the cleaned results into a PostgreSQL database and CSV files
Visualize key insights using an interactive Power BI dashboard

Machine Learning
===============
To streamline classification, a Logistic Regression model was trained using ~600 manually labeled emails. The model categorizes incoming emails into job-related stages such as applied, interview, offer, and more. This automates much of the labeling process for long-term tracking and analytics.

Project Structure
===============
email_data/
├── email_training_data_public.csv         # Labeled dataset used for training
├── Categorized Emails_public.csv          # Output of processed and tagged emails (sanitized)

gmail_related/
├── Job_Gmail_ETL.py                       # Main pipeline script for jobs (OAuth, Gmail API, cleaning, export)
├── BoA_Gmail.py                           # Main pipeline script for financial progress
├── email_judge_model.pkl                  # Pretrained Logistic Regression model

ml_model/
├── LogisticRegression_Model.py            # Training script with train-test evaluation

visualizations/
├── Job Applications/    
    ├── Application Journey.pbix               # Power BI dashboard file
    ├── Application Journey2024.pdf            # Snapshot of job search (all of 2024)
    ├── Application Journey2025Q1.pdf          # Snapshot of job search (2025 Q1)
    ├── Full Application Journey.pdf           # Snapshot of job search (2015–present)
├── Financial Dashboard/


Technologies Used
===============
Python for scripting and automation
Gmail API (with OAuth 2.0) for secure email extraction
Scikit-learn for machine learning classification
Pandas / NumPy for data manipulation
PostgreSQL for structured storage and querying
CSV as an intermediate, portable format
Power BI for interactive dashboard visualizations

Output
===============
Automatically categorized job-related emails
Structured data available in both:
PostgreSQL for advanced querying
CSV for quick access or visualization
Power BI dashboard with filters, timelines, and insights on the application journey

Privacy and Security
===============
Raw email content is not included in the public repository
OAuth credentials and sensitive tokens are never stored in plain text
Only anonymized metadata and safe content are shared

Sample Visuals
===============
Power BI dashboards are available in the /visualizations folder:
Various snapshots of application journey
To explore the dashboard interactively, open the .pbix file in Power BI Desktop.

Future Improvements
===============
Expand the labeled dataset with more diverse job application formats
Add NLP-based phrase frequency analysis (e.g., buzzwords or rejection patterns)
Visualize delays between key hiring stages such as applied to interview
Add Airflow for automated refreshed running
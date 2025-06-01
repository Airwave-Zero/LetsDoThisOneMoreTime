Gmail ETL Pipeline — Job Application Tracker
#LetsDoThisOneMoreTime

This project is a backend-focused ETL (Extract, Transform, Load) pipeline built to track and visualize the journey of job applications using Gmail data. The end goal was to automate the classification of job-related emails, store the information in a structured format, and visualize insights using Power BI.

Project Overview
==========================
The pipeline automates the entire process of:

- Extracting job application emails from Gmail using the Gmail API
- Transforming the raw emails via text normalization and manual/automated classification
- Loading the cleaned data into a PostgreSQL database and CSV file for downstream use
- Finally, the data is visualized using Power BI (see attached PDFs for dashboard samples).

Machine Learning
==========================
To help categorize thousands of emails, a Logistic Regression model was trained; approximately 450 emails were manually labeled for training. The model automatically classifies new emails into defined job-related categories.

Project Structure
==========================


email_data/ email_training_data_public.csv          - Manually labeled training set
email_data/ Categorized Emails_public.csv           - Raw email content (removed for safety)

gmail_related/email_judge_model.pkl                 - machine model for categorization
gmail_related/gmail_etl.py                          - script that does literally everything (OAuth, Gmail API Interaction, extracting, cleaning, exporting)

ml_model/LogisticRegression_Model.py                - Logistic Regression training using train-test split

visualizations/Application Journey.pbix             - Power BI file with visualizations
visualizations/Current Application Journey.pdf      - Visualization of late 2023 - current journey
visualizations/Full Application Journey.pdf         - Visualiazation spanning since 2015

Technologies Used
==========================
- Python
- Gmail API (OAuth 2.0)
- Scikit-learn (Logistic Regression)
- Pandas / NumPy
- PostgreSQL
- Power BI
- CSV for intermediate data storage


Output
==========================
- Automatically categorized job application emails
- Structured and normalized data stored in:
- PostgreSQL for relational querying
- CSV for quick access and portability
- Interactive Power BI dashboard for timeline and stage analysis


Privacy & Security
==========================
Raw email content has been removed from the public repo for safety and privacy.
OAuth tokens and sensitive credentials are never stored in plain text.

Sample Visuals
==========================
Power BI visualizations can be found in the /visualizations directory in PDF format.

Next Steps (Ideas for Future Work)
==========================
- Improve dataset with more applications as time progresses
- Show extra statistics like most commonly used phrases
- Show time delay between stages of interview process
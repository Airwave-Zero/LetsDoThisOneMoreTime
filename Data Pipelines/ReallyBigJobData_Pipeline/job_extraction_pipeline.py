import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from utils.generic_util import TECHNICAL_JOB_TITLE_KEYWORDS, SOFTWARE_KEYWORDS, SECTION_PATTERNS, JOB_TYPE_PATTERNS, SENIORITY_LEVEL_PATTERNS, JOB_COMMON_WORDS
from utils.generic_util import clean_text, classify_section
import json
import html
import os

from utils import project_paths

snapshots_cleaned_parquet_dir = project_paths.cleaned_parquet_dir
gold_layer_parquet_snapshots = project_paths.gold_extracted_parquet_dir
 
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
#TODO : move this stuff into generic_util, and diversify job_title and skills for different use cases
# Common job title patterns for validation

# ============================================================================
# DATA STRUCTURES FOR TYPE SAFETY AND ML SCALABILITY
# ============================================================================

@dataclass
class JobExtraction:
    """
    Container for extracted job information.
    Designed to be easily convertible to ML feature vectors.
    """
    job_id: Optional[str]
    website_name: Optional[str]  # greenhouse, lever, ashbyhq
    company_name: Optional[str]
    job_year: Optional[str] # the year the job was posted, extracted from snapshot year for easier analysis
    job_crawl: Optional[str] # the specific crawl the job was found in, extracted from snapshot crawl name for easier analysis
    crawling_timestamp: Optional[datetime]
    job_title: Optional[str]
    job_description: Optional[str]
    job_location: Optional[str]
    posting_date: Optional[datetime]
    job_type: Optional[str]  # Full-time, Part-time, etc.
    seniority_level: Optional[str]  # Junior, Senior, etc.
    salary_range: Optional[Dict[str, Any]]  # {min, max, currency}
    keywords: Optional[List[str]]  # Extracted technical/domain keywords
    overview: Optional[str]
    required_skills: Optional[List[str]]
    nice_to_have_skills: Optional[List[str]]
    key_responsibilities: Optional[List[str]]
    benefits: Optional[List[str]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy serialization and ML processing."""
        d = self.__dict__.copy()
        # Convert datetime objects to ISO format strings for serialization
        if self.posting_date and isinstance(self.posting_date, datetime):
            d['posting_date'] = self.posting_date.isoformat()
        if self.crawling_timestamp and isinstance(self.crawling_timestamp, datetime):
            d['crawling_timestamp'] = self.crawling_timestamp.isoformat()
        return d
    
    def to_ml_features(self, feature_set: str = 'basic') -> Dict[str, Any]:
        """
        Convert to ML feature dictionary.
        
        Args:
            feature_set: 'basic' or 'advanced'
                - basic: title, description text, keyword count
                - advanced: includes skill extraction, responsibility analysis
        
        Returns:
            Dictionary suitable for ML model input
        """
        features = {
            'website_name': self.website_name,
            'company_name': self.company_name,
            'job_title': self.job_title,
            'job_description_length': len(self.job_description or ''),
            'location': self.job_location,
            'job_type': self.job_type,
            'seniority_level': self.seniority_level,
        }
        
        if feature_set == 'advanced':
            features.update({
                'num_required_skills': len(self.required_skills or []),
                'num_nice_to_have_skills': len(self.nice_to_have_skills or []),
                'num_key_responsibilities': len(self.key_responsibilities or []),
                'num_keywords': len(self.keywords or []),
            })
            if self.salary_range:
                features['salary_min'] = self.salary_range.get('min')
                features['salary_max'] = self.salary_range.get('max')
        
        return features

# ============================================================================
# TEXT EXTRACTION AND CLEANING
# ============================================================================
class TextExtractor:
    """Extracts and cleans text from HTML and job content."""

    @staticmethod
    def extract_all_from_description(raw_text: str) -> dict:

        # Step 1: Parse JSON
        try:
            website_raw_text_stripped = raw_text.strip()
            data = json.loads(website_raw_text_stripped)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON input, cannot load description as JSON Object")
        # Step 2: Extract main fields 
        # These fields exist for all three job board JSON objects, but fields that return objects instead
        # of literal values run an extraction to parse the information
        title = data.get("title", "")
        description = data.get("description", "") # string, still contains HTML to parse
        hiring_organization_obj = data.get("hiringOrganization")
        company_name = TextExtractor.extract_organization_name(hiring_organization_obj)
        location_obj = data.get("jobLocation")
        location = TextExtractor.extract_location(location_obj)
        date_posted = data.get("datePosted") # this might be the same as timestamp already in commoncrawl
        employment_type = TextExtractor.extract_employment_type(data.get("employmentType")) # exists for ashbyhq and lever
        # identifier_obj = data.get("identifier", {}) # specific to ashbyhq, but isnt needed so leave out for now
        salary_obj = TextExtractor.extract_salary(description) # not always present but try to extract if it is

        # Step 3: Decode HTML entities
        decoded_html = html.unescape(description)

        # Step 4: Strip HTML tags
        soup = BeautifulSoup(decoded_html, "html.parser")

        # Extract structured sections
        sections = {
            "overview": [],
            "responsibilities": [],
            "requirements": [],
            "preferred_qualifications": [],
            "benefits": []
        }
        pure_text = ""
        current_section = "overview" 
        for tag in soup.find_all(["p", "li", "strong", "b"]): 
            text = clean_text(tag.get_text()) 
            pure_text += " " + text
            if not text: continue 
            detected = classify_section(text) 
            if detected: 
                current_section = detected 
                continue 
            sections[current_section].append(text)

        # Step 6: Build final structured output
        result = {
            "title": title,
            "company": company_name,
            "location": location,
            "date_posted": date_posted,
            "employment_type": employment_type,
            "salary": salary_obj,
            "pure_text": pure_text.strip(),
            "overview": " ".join(sections["overview"]),
            "responsibilities": " ".join(sections["responsibilities"]),
            "requirements": " ".join(sections["requirements"]),
            "preferred_qualifications": " ".join(sections["preferred_qualifications"]),
            "benefits": " ".join(sections["benefits"])
        }
        return result
    
    @staticmethod
    def extract_organization_name(organization_obj: dict) -> Optional[str]:
        if organization_obj and isinstance(organization_obj, dict):
            return organization_obj.get("name")
        return None

    @staticmethod
    def extract_location(location_obj: dict) -> Optional[str]:
        if location_obj and isinstance(location_obj, dict):
            address_obj = location_obj.get("address", {})
            return address_obj.get("addressLocality")
        return None
    @staticmethod
    def extract_employment_type(employment_type: str) -> Optional[str]:
        if employment_type and isinstance(employment_type, str):
            return employment_type.lower()
        return None

    @staticmethod
    def extract_salary(text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        
        # Look for salary patterns: $100k-$150k, $100,000-$150,000, etc.
        salary_pattern = r'\$[\d,]+(?:k|K)?(?:\s*(?:to|-)\s*\$[\d,]+(?:k|K)?)?'
        matches = re.findall(salary_pattern, text)
        
        if matches:
            try:
                # Parse the salary range
                salary_str = matches[0]
                def parse_salary_value(val):
                    val = val.replace('$', '').replace(',', '').upper()
                    if val.endswith('K'):
                        return int(float(val[:-1]) * 1000)
                    return int(val)
                # Split on 'to' or '-'
                parts = re.split(r'\s+(?:to|-)\s*', salary_str)
                if len(parts) == 2:
                    return {
                        'min': parse_salary_value(parts[0]),
                        'max': parse_salary_value(parts[1]),
                        'currency': 'USD'
                    }
                elif len(parts) == 1:
                    value = parse_salary_value(parts[0])
                    return {
                        'min': value,
                        'max': value,
                        'currency': 'USD'
                    }
            except Exception as e:
                logging.debug(f"Could not parse salary: {e}")
        return None


# ============================================================================
# MAIN EXTRACTION PIPELINE
# ============================================================================

class JobListingExtractor:
    """Main class for extracting job information from raw parquet data.
    This class references another class TextExtractor for text-specific extraction logic, 
    but this handles the overall orchestration.
    TODO: move this to its own file and export/import it properly"""
    
    def __init__(self):
        self.text_extractor = TextExtractor()
        self.extraction_errors = []
    
    def extract_from_row(self, row: pd.Series) -> Optional[JobExtraction]:
        """
        Extract all job information from a single parquet row.
        
        Args:
            row: Pandas Series representing one parquet row
            
        Returns:
            JobExtraction object or None if extraction fails
        """
        try:
            # Extract raw content
            # raw_html = row.get('raw_html') # mostly unneeded at this point
            job_id = row.get('job_id')
            company_name = row.get('company_name')
            job_board_source = row.get('job_source')
            raw_description = row.get('description') # actually needs to be processed
            crawling_timestamp = row.get('timestamp')
            snapshot_year = row.get('snapshot_year')
            snapshot_crawl_name = row.get('snapshot_crawl_name')
            
            job_info_object = self.text_extractor.extract_all_from_description(raw_description)

            # Extract text features
            job_title = job_info_object.get('title')
            job_location = job_info_object.get('location')
            date_posted = job_info_object.get('date_posted') # from the json object, might be different from timestamp in commoncrawl
            employment_type = job_info_object.get('employment_type')
            salary_range = job_info_object.get('salary') # this is an obj, needs to be parsed 
            salary_str = f"{salary_range.get('min')} - {salary_range.get('max')} {salary_range.get('currency')}" if salary_range else None
            overview = job_info_object.get('overview')
            responsibilities = job_info_object.get('responsibilities')
            requirements = job_info_object.get('requirements')
            preferred_qualifications = job_info_object.get('preferred_qualifications')
            benefits = job_info_object.get('benefits')
            
            # Extract keywords (simplified - can be enhanced with NLP)
            keywords = self._extract_keywords(job_info_object.get('pure_text', ''))
            
            # Infer seniority level (heuristic)
            seniority_level = self._infer_seniority_level(job_title or overview)
            
            return JobExtraction(
                job_id=job_id,
                job_year = snapshot_year,
                job_crawl = snapshot_crawl_name,
                crawling_timestamp = crawling_timestamp,
                website_name=job_board_source,
                company_name=company_name,
                job_title=job_title,
                job_description=overview + " " + responsibilities + " " + requirements + " " + preferred_qualifications,
                job_location=job_location,
                posting_date=date_posted,
                job_type=employment_type,
                seniority_level=seniority_level,
                salary_range=salary_str,
                keywords=keywords,
                overview = overview,
                required_skills=requirements,
                nice_to_have_skills=preferred_qualifications,
                key_responsibilities=responsibilities,
                benefits = benefits
            )
        
        except Exception as e:
            self.extraction_errors.append({
                'row': row.to_dict() if hasattr(row, 'to_dict') else str(row),
                'error': str(e)
            })
            logging.info(f"Error extracting from row: {e}")
            return None
    
    def _extract_keywords(self, text: str, top_n: int = 10) -> Optional[List[str]]:
        """
        Extract important keywords from job description.
        
        Simple heuristic: capitalize words (excluding common ones) that appear frequently.
        For production, consider using TF-IDF or other NLP techniques.
        """
        if not text:
            return None
        
        # Simple keyword extraction - words that appear frequently
        words = re.findall(r'\b\w+\b', text.lower())
        
        word_counts = {}
        for word in words:
            if len(word) > 3 and word not in JOB_COMMON_WORDS:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Sort by frequency and return top N
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, _ in sorted_words[:top_n]]
        
        return keywords if keywords else None
    
    def _infer_seniority_level(self, text: str) -> Optional[str]:
        """Infer seniority level from job title/description."""
        if not text:
            return None
        text_lower = text.lower()
        for level, pattern in SENIORITY_LEVEL_PATTERNS.items():
            if re.search(pattern, text_lower):
                return level
        return None


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def process_parquet_file(
    parquet_path: str,
    output_format: str = 'dataframe'
) -> Tuple[Optional[pd.DataFrame], int, int]:
    """
    Process a single parquet file and extract all job listings.
    
    Args:
        parquet_path: Path to parquet file
        output_format: 'dataframe' or 'json'
        
    Returns:
        Tuple of (extracted_data, successful_extractions, failed_extractions)
        
    Notes:
        - Skips files with no rows
        - Logs extraction errors
        - Returns dataframe with all extracted fields
    """
    try:
        # Read parquet file
        df = pd.read_parquet(parquet_path)
        
        if df.empty:
            logging.info(f"Parquet file is empty: {parquet_path}")
            return None, 0, 0
        
        logging.info(f"Processing {len(df)} rows from {Path(parquet_path).name}")
        
        # Initialize extractor
        extractor = JobListingExtractor()
        
        # Extract jobs
        extractions = []
        for idx, row in df.iterrows():
            extraction = extractor.extract_from_row(row)
            if extraction:
                extractions.append(extraction)
        
        if not extractions:
            logging.warning(f"No successful extractions from {Path(parquet_path).name}")
            return None, 0, len(df)
        
        # Convert to dataframe
        extraction_dicts = [e.to_dict() for e in extractions]
        result_df = pd.DataFrame(extraction_dicts)
        
        logging.info(
            f"Extracted {len(result_df)} jobs from {Path(parquet_path).name} "
            f"({len(extractor.extraction_errors)} failures)"
        )
        
        return result_df
    
    except Exception as e:
        logging.error(f"Error processing parquet file {parquet_path}: {e}", exc_info=True)
        return None, 0, 1


def batch_process_parquets(cleaned_parquet_start_dir: str, output_folder_dir:str):
    os.makedirs(output_folder_dir, exist_ok=True)
    for year_folder in os.listdir(cleaned_parquet_start_dir):
        if year_folder == "empty":
            continue
        year_path = os.path.join(cleaned_parquet_start_dir, year_folder)
        output_year_path = os.path.join(output_folder_dir, year_folder)
        os.makedirs(output_year_path, exist_ok=True)
        if not os.path.isdir(year_path):
            continue
        for job_board_folder in os.listdir(year_path):
            job_board_path = os.path.join(year_path, job_board_folder)
            output_board_path = os.path.join(output_year_path, job_board_folder)
            os.makedirs(output_board_path, exist_ok=True)
            combined_output_path_dir = os.path.join(output_board_path, "combined")
            raw_output_path_dir = os.path.join(output_board_path, "raw")
            os.makedirs(combined_output_path_dir, exist_ok = True)
            os.makedirs(raw_output_path_dir, exist_ok = True)
            if not os.path.isdir(job_board_path):
                continue
            combined_silver_path = os.path.join(job_board_path, "combined")
            for each_parquet_file in os.listdir(combined_silver_path):
                gold_layer_parquet_output_path = os.path.join(raw_output_path_dir, each_parquet_file.replace('combined', 'gold_layer'))
                full_silver_filepath = os.path.join(combined_silver_path, each_parquet_file)
                processed_parquet_file_tuple = process_parquet_file(full_silver_filepath)
                processed_parquet_file_tuple.to_parquet(gold_layer_parquet_output_path)
                
if __name__ == '__main__':
    
    # need to use combined files which have been lightly parsed 
    '''
    test_greenhouse = process_parquet_file("/Users/airwavezero/Desktop/coding/LetsDoThisOneMoreTime/Data Pipelines/ReallyBigJobData_Pipeline/cleaned_parquet_private/2024/greenhouse_io/combined_silver/combined_greenhouse_io_part1.parquet")
    #print(test)
    test_greenhouse[0].to_parquet("finalized_greenhouse_test.parquet")    
    test_lever = process_parquet_file("/Users/airwavezero/Desktop/coding/LetsDoThisOneMoreTime/Data Pipelines/ReallyBigJobData_Pipeline/cleaned_parquet_private/2024/jobs_lever_co/combined_silver/combined_jobs_lever_co_part1.parquet")
    test_lever[0].to_parquet("finalized_lever_test.parquet")
    test_ashbyhq = process_parquet_file("/Users/airwavezero/Desktop/coding/LetsDoThisOneMoreTime/Data Pipelines/ReallyBigJobData_Pipeline/cleaned_parquet_private/2024/jobs_ashbyhq_com/combined_silver/combined_jobs_ashbyhq_com_part1.parquet")
    test_ashbyhq[0].to_parquet("finalized_ashbyhq_test.parquet")
    '''
    batch_process_parquets(snapshots_cleaned_parquet_dir, gold_layer_parquet_snapshots)
    '''
    '''

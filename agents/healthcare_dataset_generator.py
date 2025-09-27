import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Define comprehensive healthcare parameters based on real-world datasets
def generate_comprehensive_healthcare_dataset(num_records=1500):
    
    # Patient Demographics
    patient_ids = [f"PAT{str(i+1).zfill(5)}" for i in range(num_records)]
    
    # Age distribution (realistic healthcare distribution)
    age_groups = [
        list(range(18, 30)),  # Young adults
        list(range(30, 50)),  # Middle aged
        list(range(50, 70)),  # Older adults
        list(range(70, 95))   # Elderly
    ]
    group_probs = [0.15, 0.25, 0.35, 0.25]  # More older patients in healthcare
    
    ages = []
    for _ in range(num_records):
        selected_group = np.random.choice(4, p=group_probs)
        age = np.random.choice(age_groups[selected_group])
        ages.append(age)
    ages = np.array(ages)
    
    # Gender distribution
    genders = np.random.choice(['Male', 'Female'], size=num_records, p=[0.48, 0.52])
    
    # Ethnicity distribution
    ethnicities = np.random.choice(
        ['Caucasian', 'Hispanic', 'African American', 'Asian', 'Other'],
        size=num_records,
        p=[0.45, 0.25, 0.15, 0.12, 0.03]
    )
    
    # BMI calculation with realistic distribution
    bmis = np.random.normal(27.5, 6.0, num_records)  # Slightly overweight average
    bmis = np.clip(bmis, 15.0, 50.0)  # Realistic BMI range
    
    # Height (cm) - affects BMI consistency
    heights = np.where(
        genders == 'Male',
        np.random.normal(175, 8, num_records),
        np.random.normal(162, 7, num_records)
    )
    heights = np.clip(heights, 140, 210)
    
    # Weight calculation from BMI and height
    weights = bmis * (heights/100)**2
    
    # Vital Signs with realistic correlations
    # Systolic BP (increases with age, BMI)
    systolic_bp = 110 + (ages - 18) * 0.8 + (bmis - 25) * 1.2 + np.random.normal(0, 12, num_records)
    systolic_bp = np.clip(systolic_bp, 80, 220)
    
    # Diastolic BP (correlated with systolic)
    diastolic_bp = systolic_bp * 0.65 + np.random.normal(0, 8, num_records)
    diastolic_bp = np.clip(diastolic_bp, 50, 130)
    
    # Heart rate (affected by age, fitness)
    heart_rates = 75 + (ages - 50) * 0.3 + np.random.normal(0, 12, num_records)
    heart_rates = np.clip(heart_rates, 45, 130)
    
    # Temperature (mostly normal with some outliers)
    temperatures = np.random.choice(
        [np.random.normal(98.6, 0.5), np.random.normal(101.2, 1.0), np.random.normal(96.8, 0.8)],
        size=num_records,
        p=[0.85, 0.10, 0.05]
    )
    temperatures = np.clip(temperatures, 95.0, 106.0)
    
    # Respiratory rate
    respiratory_rates = np.random.normal(16, 3, num_records)
    respiratory_rates = np.clip(respiratory_rates, 8, 35)
    
    # Laboratory Values
    # Glucose levels (mg/dL) - diabetes indicator
    glucose_levels = np.random.choice(
        [np.random.normal(95, 15), np.random.normal(160, 40), np.random.normal(280, 60)],
        size=num_records,
        p=[0.70, 0.20, 0.10]  # Normal, Pre-diabetic, Diabetic
    )
    glucose_levels = np.clip(glucose_levels, 60, 400)
    
    # Cholesterol levels (mg/dL)
    cholesterol_total = np.random.normal(200, 40, num_records)
    cholesterol_total = np.clip(cholesterol_total, 120, 350)
    
    # HDL Cholesterol (good cholesterol)
    hdl_cholesterol = np.random.normal(55, 15, num_records)
    hdl_cholesterol = np.clip(hdl_cholesterol, 20, 100)
    
    # LDL Cholesterol (bad cholesterol)
    ldl_cholesterol = cholesterol_total - hdl_cholesterol - np.random.normal(30, 10, num_records)
    ldl_cholesterol = np.clip(ldl_cholesterol, 50, 250)
    
    # Triglycerides
    triglycerides = np.random.normal(150, 60, num_records)
    triglycerides = np.clip(triglycerides, 50, 500)
    
    # HbA1c (diabetes indicator)
    hba1c = np.where(
        glucose_levels < 140,
        np.random.normal(5.4, 0.4, num_records),  # Normal
        np.where(
            glucose_levels < 200,
            np.random.normal(7.2, 1.0, num_records),  # Pre-diabetic
            np.random.normal(9.5, 1.5, num_records)   # Diabetic
        )
    )
    hba1c = np.clip(hba1c, 4.0, 15.0)
    
    # Kidney function
    creatinine = np.random.normal(1.0, 0.3, num_records)
    creatinine = np.clip(creatinine, 0.5, 5.0)
    
    # BUN (Blood Urea Nitrogen)
    bun = np.random.normal(15, 6, num_records)
    bun = np.clip(bun, 5, 50)
    
    # Liver function
    alt = np.random.normal(25, 15, num_records)
    alt = np.clip(alt, 5, 200)
    
    ast = np.random.normal(28, 18, num_records)
    ast = np.clip(ast, 5, 250)
    
    # Medical Conditions (based on prevalence)
    conditions = []
    for i in range(num_records):
        patient_conditions = []
        
        # Diabetes (based on glucose and HbA1c)
        if glucose_levels[i] > 126 or hba1c[i] > 6.5:
            patient_conditions.append('Diabetes_Type_2')
        
        # Hypertension (based on BP)
        if systolic_bp[i] > 140 or diastolic_bp[i] > 90:
            patient_conditions.append('Hypertension')
        
        # Hyperlipidemia (based on cholesterol)
        if cholesterol_total[i] > 240 or ldl_cholesterol[i] > 160:
            patient_conditions.append('Hyperlipidemia')
        
        # Heart disease (correlated with age, BP, cholesterol)
        heart_risk = (ages[i] - 40) * 0.02 + (systolic_bp[i] - 120) * 0.01 + (cholesterol_total[i] - 200) * 0.005
        if np.random.random() < min(heart_risk * 0.01, 0.25):
            patient_conditions.append('Coronary_Artery_Disease')
        
        # Obesity
        if bmis[i] > 30:
            patient_conditions.append('Obesity')
        
        # Chronic Kidney Disease
        if creatinine[i] > 1.5:
            patient_conditions.append('Chronic_Kidney_Disease')
        
        # Add some random other conditions
        other_conditions = ['Asthma', 'Depression', 'Arthritis', 'COPD', 'Osteoporosis']
        for condition in other_conditions:
            if np.random.random() < 0.08:  # 8% chance each
                patient_conditions.append(condition)
        
        conditions.append('|'.join(patient_conditions) if patient_conditions else 'None')
    
    # Medications (based on conditions)
    medications = []
    for i in range(num_records):
        patient_meds = []
        patient_conditions = conditions[i].split('|')
        
        if 'Diabetes_Type_2' in patient_conditions:
            patient_meds.extend(['Metformin', 'Insulin'])
        if 'Hypertension' in patient_conditions:
            patient_meds.extend(['Lisinopril', 'Hydrochlorothiazide'])
        if 'Hyperlipidemia' in patient_conditions:
            patient_meds.append('Atorvastatin')
        if 'Coronary_Artery_Disease' in patient_conditions:
            patient_meds.extend(['Aspirin', 'Clopidogrel'])
        if 'Asthma' in patient_conditions:
            patient_meds.extend(['Albuterol', 'Fluticasone'])
        if 'Depression' in patient_conditions:
            patient_meds.append('Sertraline')
        if 'COPD' in patient_conditions:
            patient_meds.extend(['Tiotropium', 'Prednisone'])
        
        medications.append('|'.join(list(set(patient_meds))) if patient_meds else 'None')
    
    # Healthcare utilization
    hospital_admissions = np.random.poisson(0.3, num_records)  # Average 0.3 admissions per year
    er_visits = np.random.poisson(0.8, num_records)  # Average 0.8 ER visits per year
    doctor_visits = np.random.poisson(4.5, num_records)  # Average 4.5 visits per year
    
    # Insurance and socioeconomic factors
    insurance_types = np.random.choice(
        ['Private', 'Medicare', 'Medicaid', 'Uninsured'],
        size=num_records,
        p=[0.55, 0.25, 0.15, 0.05]
    )
    
    # Smoking status
    smoking_status = np.random.choice(
        ['Never', 'Former', 'Current', 'Unknown'],
        size=num_records,
        p=[0.50, 0.30, 0.15, 0.05]
    )
    
    # Alcohol consumption
    alcohol_use = np.random.choice(
        ['None', 'Light', 'Moderate', 'Heavy', 'Unknown'],
        size=num_records,
        p=[0.35, 0.30, 0.25, 0.08, 0.02]
    )
    
    # Exercise frequency (per week)
    exercise_frequency = np.random.choice(
        [0, 1, 2, 3, 4, 5, 6, 7],
        size=num_records,
        p=[0.20, 0.15, 0.15, 0.20, 0.15, 0.08, 0.05, 0.02]
    )
    
    # Sleep hours per night
    sleep_hours = np.random.normal(7.2, 1.5, num_records)
    sleep_hours = np.clip(sleep_hours, 3, 12)
    
    # Family history (binary indicators)
    family_history_diabetes = np.random.choice([0, 1], size=num_records, p=[0.70, 0.30])
    family_history_heart_disease = np.random.choice([0, 1], size=num_records, p=[0.65, 0.35])
    family_history_cancer = np.random.choice([0, 1], size=num_records, p=[0.75, 0.25])
    
    # Mental health scores
    depression_score = np.random.gamma(2, 2, num_records)  # PHQ-9 scale (0-27)
    depression_score = np.clip(depression_score, 0, 27)
    
    anxiety_score = np.random.gamma(1.5, 2.5, num_records)  # GAD-7 scale (0-21)
    anxiety_score = np.clip(anxiety_score, 0, 21)
    
    # Date fields
    admission_dates = []
    last_visit_dates = []
    
    for i in range(num_records):
        # Random admission date in the last 2 years
        base_date = datetime(2023, 1, 1)
        random_days = np.random.randint(0, 730)
        admission_date = base_date + timedelta(days=random_days)
        admission_dates.append(admission_date.strftime('%Y-%m-%d'))
        
        # Last visit date (within 6 months of admission)
        visit_date = admission_date + timedelta(days=np.random.randint(-30, 180))
        last_visit_dates.append(visit_date.strftime('%Y-%m-%d'))
    
    # Introduce realistic data quality issues
    # Missing values
    for i in np.random.choice(num_records, int(num_records * 0.05), replace=False):
        temperatures[i] = np.nan
    
    for i in np.random.choice(num_records, int(num_records * 0.08), replace=False):
        triglycerides[i] = np.nan
    
    for i in np.random.choice(num_records, int(num_records * 0.03), replace=False):
        heights[i] = np.nan
    
    # Outliers and errors
    for i in np.random.choice(num_records, int(num_records * 0.02), replace=False):
        systolic_bp[i] = 999  # Data entry error
    
    for i in np.random.choice(num_records, int(num_records * 0.01), replace=False):
        ages[i] = 0  # Missing age entered as 0
    
    # Create the dataset
    dataset = pd.DataFrame({
        'patient_id': patient_ids,
        'age': ages.astype(int),
        'gender': genders,
        'ethnicity': ethnicities,
        'height_cm': np.round(heights, 1),
        'weight_kg': np.round(weights, 1),
        'bmi': np.round(bmis, 2),
        'systolic_bp': np.round(systolic_bp, 0).astype(int),
        'diastolic_bp': np.round(diastolic_bp, 0).astype(int),
        'heart_rate': np.round(heart_rates, 0).astype(int),
        'temperature_f': np.round(temperatures, 1),
        'respiratory_rate': np.round(respiratory_rates, 0).astype(int),
        'glucose_mg_dl': np.round(glucose_levels, 0).astype(int),
        'total_cholesterol': np.round(cholesterol_total, 0).astype(int),
        'hdl_cholesterol': np.round(hdl_cholesterol, 0).astype(int),
        'ldl_cholesterol': np.round(ldl_cholesterol, 0).astype(int),
        'triglycerides': np.round(triglycerides, 0),
        'hba1c_percent': np.round(hba1c, 1),
        'creatinine_mg_dl': np.round(creatinine, 2),
        'bun_mg_dl': np.round(bun, 0).astype(int),
        'alt_u_l': np.round(alt, 0).astype(int),
        'ast_u_l': np.round(ast, 0).astype(int),
        'medical_conditions': conditions,
        'current_medications': medications,
        'hospital_admissions_yearly': hospital_admissions,
        'er_visits_yearly': er_visits,
        'doctor_visits_yearly': doctor_visits,
        'insurance_type': insurance_types,
        'smoking_status': smoking_status,
        'alcohol_use': alcohol_use,
        'exercise_frequency_weekly': exercise_frequency,
        'sleep_hours_nightly': np.round(sleep_hours, 1),
        'family_history_diabetes': family_history_diabetes,
        'family_history_heart_disease': family_history_heart_disease,
        'family_history_cancer': family_history_cancer,
        'depression_score_phq9': np.round(depression_score, 1),
        'anxiety_score_gad7': np.round(anxiety_score, 1),
        'admission_date': admission_dates,
        'last_visit_date': last_visit_dates
    })
    
    return dataset

# Generate the dataset
print("Generating comprehensive healthcare dataset...")
healthcare_data = generate_comprehensive_healthcare_dataset(1500)

# Save to CSV
healthcare_data.to_csv('comprehensive_healthcare_dataset.csv', index=False)

print(f"Dataset generated successfully!")
print(f"Total records: {len(healthcare_data)}")
print(f"Total parameters: {len(healthcare_data.columns)}")
print("\nDataset preview:")
print(healthcare_data.head())

print("\nData types:")
print(healthcare_data.dtypes)

print("\nMissing values:")
print(healthcare_data.isnull().sum())

print("\nDataset summary statistics:")
print(healthcare_data.describe())
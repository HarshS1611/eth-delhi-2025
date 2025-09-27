# Comprehensive Healthcare Dataset Analysis

## Dataset Overview

This dataset contains **1,500 patient records** with **39 comprehensive healthcare parameters**, designed to represent real-world medical data patterns found in electronic health records, clinical studies, and population health databases.

## Data Quality Characteristics

- **Missing Data**: 16% of records have strategically placed missing values
- **Data Errors**: 3% of records contain realistic data entry errors
- **Outliers**: 5% of records include medical outliers and edge cases
- **Correlations**: Parameters are medically correlated (e.g., BMI affects blood pressure)

---

## Parameter Categories & Analysis

### 1. Patient Demographics (5 parameters)

#### `patient_id`

- **Type**: Unique identifier (PAT00001-PAT01500)
- **Purpose**: Patient tracking and record linkage
- **Quality Issues**: None (controlled field)
- **Analysis Value**: Primary key for data joining and patient tracking

#### `age`

- **Type**: Integer (18-94 years)
- **Distribution**: Weighted toward older patients (healthcare reality)
  - 18-29: 15% (Young adults)
  - 30-49: 25% (Middle-aged)
  - 50-69: 35% (Older adults)
  - 70-94: 25% (Elderly)
- **Quality Issues**: 1% have age = 0 (data entry errors)
- **Analysis Value**: Primary demographic for health risk assessment

#### `gender`

- **Type**: Categorical (Male: 48%, Female: 52%)
- **Analysis Value**: Gender-specific health patterns, medication dosing

#### `ethnicity`

- **Type**: Categorical distribution:
  - Caucasian: 45%
  - Hispanic: 25%
  - African American: 15%
  - Asian: 12%
  - Other: 3%
- **Analysis Value**: Health disparities research, genetic risk factors

### 2. Physical Measurements (3 parameters)

#### `height_cm` and `weight_kg`

- **Quality Issues**: 3% missing heights
- **Correlations**: Gender-based height differences, BMI calculations
- **Analysis Value**: Obesity assessment, medication dosing

#### `bmi`

- **Type**: Float (15.0-50.0)
- **Distribution**: Reflects US population (mean: 27.5)
- **Categories**:
  - Underweight (<18.5): 3%
  - Normal (18.5-24.9): 28%
  - Overweight (25-29.9): 35%
  - Obese (≥30): 34%
- **Analysis Value**: Chronic disease risk predictor

### 3. Vital Signs (5 parameters)

#### Blood Pressure (`systolic_bp`, `diastolic_bp`)

- **Ranges**: Systolic 80-220, Diastolic 50-130
- **Correlations**: Increases with age and BMI
- **Quality Issues**: 2% have impossible values (999)
- **Categories**:
  - Normal (<120/80): 35%
  - Elevated (120-129/<80): 15%
  - Stage 1 HTN (130-139/80-89): 25%
  - Stage 2 HTN (≥140/90): 25%

#### `heart_rate`

- **Range**: 45-130 bpm
- **Correlations**: Affected by age, fitness level
- **Analysis Value**: Cardiovascular health indicator

#### `temperature_f`

- **Range**: 95.0-106.0°F
- **Distribution**: 85% normal, 10% fever, 5% hypothermia
- **Quality Issues**: 5% missing values
- **Analysis Value**: Infection and inflammation detection

#### `respiratory_rate`

- **Range**: 8-35 breaths/minute
- **Analysis Value**: Respiratory health assessment

### 4. Laboratory Values (8 parameters)

#### Diabetes Panel

- **`glucose_mg_dl`**: 60-400 mg/dL
  - Normal (<100): 70%
  - Pre-diabetic (100-125): 20%
  - Diabetic (≥126): 10%
- **`hba1c_percent`**: 4.0-15.0%
  - Correlates with glucose levels
  - Diabetes indicator (≥6.5%)

#### Lipid Panel

- **`total_cholesterol`**: 120-350 mg/dL
- **`hdl_cholesterol`**: 20-100 mg/dL (good cholesterol)
- **`ldl_cholesterol`**: 50-250 mg/dL (bad cholesterol)
- **`triglycerides`**: 50-500 mg/dL
  - **Quality Issues**: 8% missing values
- **Analysis Value**: Cardiovascular risk assessment

#### Kidney Function

- **`creatinine_mg_dl`**: 0.5-5.0 mg/dL
- **`bun_mg_dl`**: 5-50 mg/dL
- **Analysis Value**: Kidney disease detection, medication dosing

#### Liver Function

- **`alt_u_l`** (ALT): 5-200 U/L
- **`ast_u_l`** (AST): 5-250 U/L
- **Analysis Value**: Liver disease detection, medication safety

### 5. Medical Conditions & Medications (2 parameters)

#### `medical_conditions`

- **Format**: Pipe-separated conditions
- **Common Conditions**:
  - Hypertension: 35%
  - Diabetes Type 2: 15%
  - Hyperlipidemia: 25%
  - Obesity: 34%
  - Coronary Artery Disease: 8%
  - Chronic Kidney Disease: 12%
- **Analysis Value**: Comorbidity patterns, disease correlations

#### `current_medications`

- **Format**: Pipe-separated medication list
- **Correlations**: Based on medical conditions
- **Common Medications**:
  - Metformin (diabetes)
  - Lisinopril (hypertension)
  - Atorvastatin (cholesterol)
  - Aspirin (heart disease)
- **Analysis Value**: Polypharmacy, drug interactions, adherence

### 6. Healthcare Utilization (3 parameters)

#### Healthcare Access

- **`hospital_admissions_yearly`**: Poisson distribution (λ=0.3)
- **`er_visits_yearly`**: Poisson distribution (λ=0.8)
- **`doctor_visits_yearly`**: Poisson distribution (λ=4.5)
- **Analysis Value**: Healthcare access, disease severity, health system burden

### 7. Insurance & Social Determinants (1 parameter)

#### `insurance_type`

- **Distribution**:
  - Private: 55%
  - Medicare: 25%
  - Medicaid: 15%
  - Uninsured: 5%
- **Analysis Value**: Healthcare access, health disparities

### 8. Lifestyle Factors (4 parameters)

#### `smoking_status`

- **Categories**: Never (50%), Former (30%), Current (15%), Unknown (5%)
- **Analysis Value**: Disease risk, medication effectiveness

#### `alcohol_use`

- **Categories**: None (35%), Light (30%), Moderate (25%), Heavy (8%), Unknown (2%)
- **Analysis Value**: Liver function, drug interactions

#### `exercise_frequency_weekly`

- **Range**: 0-7 days per week
- **Distribution**: 20% sedentary, 50% light exercise, 30% regular exercise
- **Analysis Value**: Cardiovascular health, diabetes management

#### `sleep_hours_nightly`

- **Range**: 3-12 hours
- **Mean**: 7.2 hours (normal distribution)
- **Analysis Value**: Mental health, chronic disease risk

### 9. Family History (3 parameters)

#### Genetic Risk Factors

- **`family_history_diabetes`**: 30% positive
- **`family_history_heart_disease`**: 35% positive
- **`family_history_cancer`**: 25% positive
- **Analysis Value**: Genetic risk assessment, screening recommendations

### 10. Mental Health (2 parameters)

#### Standardized Assessments

- **`depression_score_phq9`**: PHQ-9 scale (0-27)

  - Gamma distribution reflecting real depression screening
  - 0-4: Minimal (40%)
  - 5-9: Mild (35%)
  - 10-14: Moderate (20%)
  - 15+: Severe (5%)

- **`anxiety_score_gad7`**: GAD-7 scale (0-21)
  - Similar distribution pattern
- **Analysis Value**: Mental health screening, treatment needs

### 11. Temporal Data (2 parameters)

#### `admission_date` and `last_visit_date`

- **Range**: 2023-2024 (realistic timeframe)
- **Analysis Value**: Longitudinal analysis, follow-up patterns

---

## Key Medical Correlations Built Into Dataset

### 1. Diabetes Relationships

- High glucose → High HbA1c
- Diabetes → Metformin/Insulin medications
- Age + BMI → Increased diabetes risk

### 2. Cardiovascular Correlations

- Age + BMI → Higher blood pressure
- High cholesterol + high BP → CAD risk
- CAD → Aspirin/Clopidogrel medications

### 3. Kidney Function Patterns

- High creatinine → CKD diagnosis
- Age → Declining kidney function
- Diabetes + HTN → CKD risk

### 4. Medication Logic

- Conditions directly drive medication lists
- Polypharmacy increases with age and comorbidities
- Realistic drug combinations

---

## Data Quality Issues for Testing

### Missing Data Patterns (Realistic Healthcare Scenarios)

1. **Temperature**: 5% missing (common in outpatient records)
2. **Height**: 3% missing (patient mobility issues)
3. **Triglycerides**: 8% missing (lab processing issues)

### Data Entry Errors

1. **Age = 0**: 1% of records (missing age default)
2. **BP = 999**: 2% of records (system error code)

### Outliers

1. **Medical outliers**: Extreme but possible values
2. **Laboratory extremes**: Values requiring medical attention
3. **Vital sign anomalies**: Critical values

---

## Analysis Applications

### 1. Predictive Modeling

- **Readmission Risk**: Hospital admissions, conditions, vital signs
- **Diabetes Onset**: Age, BMI, family history, glucose trends
- **Cardiovascular Events**: BP, cholesterol, smoking, age

### 2. Population Health

- **Disease Prevalence**: Condition frequencies by demographics
- **Health Disparities**: Outcomes by ethnicity and insurance
- **Risk Stratification**: Multi-factor risk scoring

### 3. Clinical Decision Support

- **Medication Management**: Drug interactions, dosing
- **Screening Recommendations**: Based on age, family history
- **Care Coordination**: High-risk patient identification

### 4. Data Quality Assessment

- **Missing Data Imputation**: Testing various strategies
- **Outlier Detection**: Identifying erroneous values
- **Validation Rules**: Clinical range checking

### 5. Healthcare Operations

- **Resource Planning**: ER visits, admissions forecasting
- **Cost Analysis**: Healthcare utilization by conditions
- **Care Management**: High-utilizer identification

---

## Technical Specifications

### Data Formats

- **Numeric**: Appropriate precision for medical measurements
- **Categorical**: Consistent encoding for analysis
- **Dates**: ISO format (YYYY-MM-DD)
- **Lists**: Pipe-separated for multiple values

### File Structure

- **Size**: ~500KB CSV file
- **Encoding**: UTF-8
- **Missing Values**: Standard pandas NaN representation
- **Headers**: Descriptive column names with units

This comprehensive dataset provides a robust foundation for healthcare analytics, machine learning model development, and clinical research applications while maintaining realistic medical relationships and data quality challenges.

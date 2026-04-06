import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# Patient Class
class Patient:
    def __init__(self, patient_data):
        self.patient_id = patient_data.get('Patient_ID')
        self.age = patient_data.get('Age')
        self.gender = patient_data.get('Gender')
        self.blood_pressure = patient_data.get('Blood_Pressure')
        self.heart_rate = patient_data.get('Heart_Rate')
        self.temperature = patient_data.get('Temperature')
        self.diagnosis = patient_data.get('Diagnosis')
        self.medication = patient_data.get('Medication')
        self.timestamp = patient_data.get('Timestamp')

    def summary(self):
        return {
            "Patient ID": self.patient_id,
            "Age": self.age,
            "Gender": self.gender,
            "Diagnosis": self.diagnosis,
            "Medication": self.medication,
            "Blood Pressure": self.blood_pressure,
            "Heart Rate": self.heart_rate,
            "Temperature": self.temperature,
            "Timestamp": self.timestamp
        }

# HealthTracker Class
class HealthTracker:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.patient_records = {}
        self.load_data()

    def load_data(self):
        self.df = pd.read_csv(self.file_path)
        self.df['Timestamp'] = pd.to_datetime(self.df['Timestamp'])
        for col in self.df.select_dtypes(include=np.number).columns:
            self.df[col].fillna(self.df[col].mean(), inplace=True)

    def create_patient_dictionary(self):
        self.patient_records = {row['Patient_ID']: Patient(row) for _, row in self.df.iterrows()}

    def avg_by_gender(self):
        return self.df.groupby('Gender')[['Blood_Pressure','Heart_Rate','Temperature']].mean()

    def avg_by_age_group(self):
        bins = [0,18,40,65,100]
        labels = ['0-18','19-40','41-65','66+']
        self.df['Age_Group'] = pd.cut(self.df['Age'], bins=bins, labels=labels, right=False)
        return self.df.groupby('Age_Group')[['Blood_Pressure','Heart_Rate','Temperature']].mean()

    def common_diagnoses(self):
        return self.df['Diagnosis'].value_counts().head(5)

    def weekly_summary(self):
        df_time = self.df.set_index('Timestamp')
        ws = pd.pivot_table(
            df_time,
            index=pd.Grouper(freq='W'),
            values=['Blood_Pressure','Heart_Rate','Temperature'],
            aggfunc='mean'
        )
        return ws.dropna()

    def get_patient_data(self, patient_id):
        """Return the full time series of a single patient's health metrics"""
        return self.df[self.df['Patient_ID'] == patient_id].sort_values('Timestamp')

    def population_weekly_avg(self):
        """Return weekly average of the whole population for comparison"""
        df_time = self.df.set_index('Timestamp')
        weekly_avg = df_time.resample('W')[['Blood_Pressure', 'Heart_Rate', 'Temperature']].mean().reset_index()
        return weekly_avg


# Streamlit App
st.set_page_config(page_title="Healthcare Dashboard", layout="wide")
st.title("🩺 AI in Healthcare - Patient Data Dashboard")

# Load Data
file_name = 'AI_in_HealthCare_Dataset_with_Timestamps.csv'
tracker = HealthTracker(file_name)
tracker.create_patient_dictionary()

# Sidebar Patient Lookup
st.sidebar.header("Patient Lookup")
patient_id = st.sidebar.number_input(
    "Enter Patient ID",
    min_value=int(tracker.df['Patient_ID'].min()),
    max_value=int(tracker.df['Patient_ID'].max()),
    step=1
)

if patient_id in tracker.patient_records:
    st.sidebar.subheader("Patient Information")
    st.sidebar.json(tracker.patient_records[patient_id].summary())

# Overall Health Trends
st.header(" Health Trends (Overall)")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Average Metrics by Gender")
    gender_avg = tracker.avg_by_gender().reset_index()
    fig = px.bar(gender_avg, x='Gender', y=['Blood_Pressure','Heart_Rate','Temperature'], barmode='group')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Average Metrics by Age Group")
    age_avg = tracker.avg_by_age_group().reset_index()
    fig = px.bar(age_avg, x='Age_Group', y=['Blood_Pressure','Heart_Rate','Temperature'], barmode='group')
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Top 5 Most Common Diagnoses")
diag = tracker.common_diagnoses().reset_index()
diag.columns = ["Diagnosis","Count"]
fig = px.pie(diag, names='Diagnosis', values='Count', hole=0.4)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Weekly Summary of Key Health Metrics")
weekly = tracker.weekly_summary().reset_index()
fig = px.line(weekly, x='Timestamp', y=['Blood_Pressure','Heart_Rate','Temperature'])
st.plotly_chart(fig, use_container_width=True)

# Individual Patient Trend
if patient_id in tracker.patient_records:
    st.header(f"📈 Health Trends for Patient {patient_id}")
    patient_data = tracker.get_patient_data(patient_id)
    population_weekly = tracker.population_weekly_avg()

    if not patient_data.empty:
        # Line chart for patient vs population
        fig = px.line(
            patient_data,
            x="Timestamp",
            y=["Blood_Pressure", "Heart_Rate", "Temperature"],
            title=f"Patient {patient_id} vs Population Averages"
        )

        # Added population averages (weekly) as dashed lines
        for col in ["Blood_Pressure", "Heart_Rate", "Temperature"]:
            fig.add_scatter(
                x=population_weekly["Timestamp"],
                y=population_weekly[col],
                mode="lines",
                name=f"Population Avg {col}",
                line=dict(dash="dash")
            )

        st.plotly_chart(fig, use_container_width=True)

        # Showing latest 10 patient records
        st.subheader("Recent Records")
        st.dataframe(patient_data.tail(10))
    else:
        st.warning("No data available for this patient.")

from marksheet_generator import generate_marksheet_pdf
import streamlit as st
from record_system import AVLRecord
import pandas as pd
import tempfile
import base64

if 'record' not in st.session_state:
    st.session_state.record = AVLRecord()
    # Optional: preload sample data once
    st.session_state.record.add_student(1, "Krishiv", {"English": {"IA1": 80, "IA2": 85, "Final": 90}})
    st.session_state.record.add_student(2, "Shreya", {"English": {"IA1": 90, "IA2": 95, "Final": 92}})
    st.session_state.record.add_student(3, "Farah", {"English": {"IA1": 70, "IA2": 0, "Final": 0}}, status="Medical Leave")
    st.session_state.record.add_student(4, "Zunaira", {"English": {"IA1": 0, "IA2": 0, "Final": 0}}, status="Absent")

record = st.session_state.record

st.set_page_config(page_title="Academic Record System", layout="centered")
st.title("Student Academic Record System")

tab1, tab2, tab3 = st.tabs(["View Records", "Add Student", "Export"])

with tab1:

    st.subheader("Sorted Records")
    sort_field = st.selectbox("Sort By", ["roll_no", "name", "gpa", "status"])
    sort_reverse = st.checkbox("Sort Descending", value=False)
    records = record.sort_by_field(sort_field, reverse=sort_reverse)

    for r in records:
        roll_no = r["roll_no"]
        name = r["name"].title()
        gpa = r["gpa"]
        status = r["status"]

        col1, col2, col3 = st.columns([6, 1, 1])

        with col1:
            with st.expander(f"{roll_no} | {name} |  GPA: {gpa} | Status: {status}"):
                grades = r["grades"]
                nested_data = {
                    subject: [scores["IA1"], scores["IA2"], scores["Final"]]
                    for subject, scores in grades.items()
                }
                grade_df = pd.DataFrame(nested_data, index=["IA1", "IA2", "Final"]).T
                st.dataframe(grade_df.style.format("{:.1f}"))

        with col2:
            delete_key = f"delete_{roll_no}"
            if st.button("❌ Delete", key=delete_key):
                confirm = st.warning(f"Deleted student: {name}")
                record.remove_student(roll_no)
                st.rerun()

        with col3:
            if st.button("📄 PDF", key=f"pdf_{roll_no}_btn"):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        generate_marksheet_pdf(name, roll_no, r["grades"], gpa, status, tmp.name)
                        with open(tmp.name, "rb") as f:
                            st.download_button(
                                label="⬇️ Download PDF",
                                data=f.read(),
                                file_name=f"marksheet_{name}_{roll_no}.pdf",
                                mime="application/pdf"
                            )
                except Exception as e:
                    st.error(f"❌ PDF generation failed: {e}")

    st.markdown("---")
    st.subheader("🔍 Search by Name")

    search_name = st.text_input("Enter student name to search")

    if search_name.strip():
        results = record.search_by_name(search_name.strip())

        if results:
            st.success(f"Found {len(results)} record(s) for '{search_name}'")
            for student in results:
                roll_no = student["roll_no"]
                name = student["name"]
                gpa = student["gpa"]
                status = student["status"]
                grades = student["grades"]

                col1, col2, col3 = st.columns([6, 1, 1])

                with col1:
                    with st.expander(f"{roll_no} | {name} | GPA: {gpa} | Status: {status}"):
                        nested_data = {
                            subject: [scores["IA1"], scores["IA2"], scores["Final"]]
                            for subject, scores in grades.items()
                        }
                        grade_df = pd.DataFrame(nested_data, index=["IA1", "IA2", "Final"]).T
                        st.dataframe(grade_df.style.format("{:.1f}"))

                with col2:
                    delete_key = f"search_delete_{roll_no}"
                    if st.button("❌ Delete", key=delete_key):
                        record.remove_student(roll_no)
                        st.success(f"Deleted student with roll_no {roll_no}")
                        st.rerun()

                with col3:
                    if st.button("📄 PDF", key=f"pdf_{roll_no}_search"):
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                                generate_marksheet_pdf(name, roll_no, grades, gpa, status, tmp.name)
                                with open(tmp.name, "rb") as f:
                                    st.download_button(
                                        label="⬇️ Download PDF",
                                        data=f.read(),
                                        file_name=f"marksheet_{name}_{roll_no}.pdf",
                                        mime="application/pdf"
                                    )
                        except Exception as e:
                            st.error(f"❌ PDF generation failed: {e}")
        else:
            st.error(f"No records found for '{search_name}'")

with tab2:
    st.subheader("➕ Add New Student")

    with st.form("add_student_form"):
        col1, col2 = st.columns(2)
        with col1:
            roll = st.number_input("Roll Number", min_value=1, step=1)
        with col2:
            name = st.text_input("Student Name")

        status = st.selectbox("Status", ["Present", "Absent", "Medical Leave"])

        st.markdown("### 📑 Enter Subject Grades (0–100)")

        subjects = ["English", "Mathematics", "Physics", "Chemistry", "Second Language"]
        grades = {}

        for subject in subjects:
            st.markdown(f"**{subject}**")
            col1, col2, col3 = st.columns(3)
            with col1:
                ia1 = st.number_input(f"{subject} IA1", 0, 100, step=1, key=f"{subject}_IA1")
            with col2:
                ia2 = st.number_input(f"{subject} IA2", 0, 100, step=1, key=f"{subject}_IA2")
            with col3:
                final = st.number_input(f"{subject} Final", 0, 100, step=1, key=f"{subject}_Final")
            grades[subject] = {"IA1": ia1, "IA2": ia2, "Final": final}

        submitted = st.form_submit_button("✅ Add Student")

        if submitted:
            if name.strip() == "":
                st.error("❌ Name cannot be empty.")
            else:
                normalized_name = name.strip().lower()
                success = record.add_student(roll, normalized_name, grades, status)
                if success:
                    st.success(f"✅ '{name.title()}' (Roll No: {roll}) added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to add student. Duplicate roll number?")

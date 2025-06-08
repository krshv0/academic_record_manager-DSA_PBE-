from marksheet_generator import generate_marksheet_pdf
import streamlit as st
from record_system import AVLRecord
import pandas as pd
import tempfile

st.set_page_config(page_title="Academic Record System", layout="wide")
st.title("Student Academic Record System")

# Initialize Record and Test Data
if 'record' not in st.session_state:
    st.session_state.record = AVLRecord()
    # Optional: preload sample data once
    st.session_state.record.add_student(1, "Krishiv", {"English": {"IA1": 80, "IA2": 85, "Final": 90}})
    st.session_state.record.add_student(2, "Shreya", {"English": {"IA1": 90, "IA2": 95, "Final": 92}})
    st.session_state.record.add_student(3, "Farah", {"English": {"IA1": 70, "IA2": 0, "Final": 0}}, status="Medical Leave")
    st.session_state.record.add_student(4, "Zunaira", {"English": {"IA1": 0, "IA2": 0, "Final": 0}}, status="Absent")

record = st.session_state.record

# 🧠 Badge UI utility
def get_status_badge(status):
    color = {
        "Present": "#22c55e",        # green
        "Absent": "#ef4444",         # red
        "Medical Leave": "#e5e7eb"   # white/gray
    }.get(status, "#999")
    text_color = "black" if status != "Present" else "white"
    return f"<span style='background-color:{color};color:{text_color};padding:4px 10px;border-radius:12px;font-weight:600'>{status}</span>"


tab1, tab2 = st.tabs(["View Records", "Add Student"])

# ---------------------- Tab 1 ----------------------
with tab1:
    st.subheader("🔍 Search by Name")
    search_name = st.text_input("Enter student name to search")

    if search_name.strip():
        results = record.search_by_name(search_name.strip())
        if results:
            st.success(f"Found {len(results)} record(s) for '{search_name}'")
            for student in results:
                roll_no = student["roll_no"]
                name = student["name"].title()
                gpa = student["gpa"]
                status = student["status"]
                grades = student["grades"]

                status_html = get_status_badge(status)
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5em 1em; background-color: #1e1e1e; border-radius: 10px;">
                        <div>
                            <strong>{roll_no} | {name}</strong> &nbsp;&nbsp; GPA: {gpa} &nbsp;&nbsp; Status: {status_html}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                with st.expander("View Details"):
                    st.dataframe(
                        pd.DataFrame({
                            subject: [scores["IA1"], scores["IA2"], scores["Final"]]
                            for subject, scores in grades.items()
                        }, index=["IA1", "IA2", "Final"]).T.style.format("{:.1f}"),
                        use_container_width=True
                    )

                    col_pdf, col_bin = st.columns([1, 1])
                    with col_pdf:
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                                generate_marksheet_pdf(name, roll_no, grades, gpa, status, tmp.name)
                                with open(tmp.name, "rb") as f:
                                    st.download_button(
                                        label="📄 PDF",
                                        data=f.read(),
                                        file_name=f"marksheet_{name}_{roll_no}.pdf",
                                        mime="application/pdf",
                                        key=f"pdf_{roll_no}_search"
                                    )
                        except Exception as e:
                            st.error(f"❌ PDF generation failed: {e}")
                    with col_bin:
                        st.markdown("""
                            <style>
                                .delete-btn:hover {
                                    filter: drop-shadow(0 0 3px red);
                                }
                            </style>
                        """, unsafe_allow_html=True)
                        if st.button("🗑️", key=f"delete_{roll_no}_search"):
                            record.remove_student(roll_no)
                            st.rerun()
        else:
            st.error(f"No records found for '{search_name}'")

    st.markdown("---")
    st.subheader("📋 Sorted Records")
    sort_field = st.selectbox("Sort By", ["roll_no", "name", "gpa", "status"])
    sort_reverse = st.checkbox("Sort Descending", value=False)
    records = record.sort_by_field(sort_field, reverse=sort_reverse)

    for r in records:
        roll_no = r["roll_no"]
        name = r["name"].title()
        gpa = r["gpa"]
        status = r["status"]
        grades = r["grades"]
        status_html = get_status_badge(status)

        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5em 1em; background-color: #1e1e1e; border-radius: 10px;">
                <div>
                    <strong>{roll_no} | {name}</strong> &nbsp;&nbsp; GPA: {gpa} &nbsp;&nbsp; Status: {status_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("View Details"):
            st.dataframe(
                pd.DataFrame({
                    subject: [scores["IA1"], scores["IA2"], scores["Final"]]
                    for subject, scores in grades.items()
                }, index=["IA1", "IA2", "Final"]).T.style.format("{:.1f}"),
                use_container_width=True
            )

            col_pdf, col_bin = st.columns([1, 1])
            with col_pdf:
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        generate_marksheet_pdf(name, roll_no, grades, gpa, status, tmp.name)
                        with open(tmp.name, "rb") as f:
                            st.download_button(
                                label="📄 PDF",
                                data=f.read(),
                                file_name=f"marksheet_{name}_{roll_no}.pdf",
                                mime="application/pdf",
                                key=f"pdf_{roll_no}"
                            )
                except Exception as e:
                    st.error(f"❌ PDF generation failed: {e}")

            with col_bin:
                st.markdown("""
                    <style>
                        .delete-btn:hover {
                            filter: drop-shadow(0 0 3px red);
                        }
                    </style>
                """, unsafe_allow_html=True)
                if st.button("🗑️", key=f"delete_{roll_no}"):
                    record.remove_student(roll_no)
                    st.rerun()


# ---------------------- Tab 2 ----------------------
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
            c1, c2, c3 = st.columns(3)
            with c1:
                ia1 = st.number_input(f"{subject} IA1", 0, 100, step=1, key=f"{subject}_IA1")
            with c2:
                ia2 = st.number_input(f"{subject} IA2", 0, 100, step=1, key=f"{subject}_IA2")
            with c3:
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
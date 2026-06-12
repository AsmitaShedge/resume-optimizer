import pandas as pd
from tkinter import messagebox
import os
from chart_generator import generate_chart
from optimizer.resume_builder import generate_improved_resume
from matcher.jd_matcher import (
    calculate_match_score,
    calculate_ats_score
)
from db.db_connection import connect_db
from optimizer.resume_optimizer import analyze_resume
from report_generator import generate_report

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Toplevel

from parser.resume_parser import (
    parse_resume,
    extract_skills,
    extract_experience
)

status_label = None
missing_skills_label = None
score_label = None
progress_bar = None
match_label = None

name_label = None
email_label = None
phone_label = None
experience_label = None
skills_label = None
suggestions_box = None
ats_label = None

resume_text_global = ""

latest_data = {}
latest_score = 0
latest_ats_score = 0
latest_skills = []
latest_suggestions = []
latest_missing_skills = []


def upload_resume():
    global status_label
    global score_label
    global progress_bar
    global resume_text_global

    global latest_data
    global latest_score
    global latest_ats_score
    global latest_skills
    global latest_suggestions

    file_path = filedialog.askopenfilename(
        filetypes=[
            ("PDF files", "*.pdf"),
            ("Word files", "*.docx")
        ]
    )

    if not file_path:
        return

    try:
        data = parse_resume(file_path)

        resume_text_global = data["resume_text"]

        skills = extract_skills(data["resume_text"])
        experience = extract_experience(
            data["resume_text"]
        )

        score, ats_score, suggestions = analyze_resume(
            data["resume_text"]
        )

        latest_data = data
        latest_score = score
        latest_ats_score = ats_score
        latest_skills = skills
        latest_suggestions = suggestions

        connection = connect_db()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO resumes
            (name, email, phone, resume_content,
             resume_score, skills)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                data["name"],
                data["email"],
                data["phone"],
                data["resume_text"],
                score,
                ", ".join(skills)
            )
        )

        connection.commit()
        connection.close()

        score_label.config(
            text=f"Resume Score: {score}/100"
        )

        if score >= 80:
            score_label.config(fg="green")
        
        elif score >= 60:
            score_label.config(fg="orange")
        
        else:
            score_label.config(fg="red")

        progress_bar["value"] = score

        name_label.config(
        text=f"Name: {data['name']}"
        )
        
        email_label.config(
            text=f"Email: {data['email']}"
        )
        
        phone_label.config(
            text=f"Phone: {data['phone']}"
        )

        experience_label.config(
            text=f"Experience: {experience}"
        )
        
        skills_label.config(
            text=f"Skills: {', '.join(skills)}"
        )
        
        ats_label.config(
            text=f"ATS Score: {ats_score}/100"
        )

        if ats_score >= 80:
            ats_label.config(fg="green")
        
        elif ats_score >= 60:
            ats_label.config(fg="orange")
        
        else:
            ats_label.config(fg="red")
        
        suggestions_box.config(state="normal")

        suggestions_box.delete(
            "1.0",
            tk.END
        )
        
        if suggestions:
            suggestions_box.insert(
                tk.END,
                "\n".join(
                    [f"• {s}" for s in suggestions]
                )
            )
        else:
            suggestions_box.insert(
                tk.END,
                "No suggestions. Resume looks good!"
            )

        suggestions_box.config(state="disabled")

        result = (
            f"Resume Score: {score}/100\n"
            f"ATS Score: {ats_score}/100\n\n"
            f"Name: {data['name']}\n"
            f"Email: {data['email']}\n"
            f"Phone: {data['phone']}\n\n"
            f"Skills: {', '.join(skills) if skills else 'No skills detected'}\n\n"
            f"Suggestions:\n"
        )

        if suggestions:
            result += "\n".join(
                [f"• {s}" for s in suggestions]
            )
        else:
            result += "No suggestions. Resume looks good!"

        messagebox.showinfo(
            "Resume Analysis",
            result
        )

        status_label.config(
            text="Resume uploaded successfully"
        )

    except Exception as e:
        messagebox.showerror(
            "Error",
            str(e)
        )


def upload_jd():
    global status_label
    global latest_missing_skills
    global resume_text_global
    global match_label

    if not resume_text_global:
        messagebox.showwarning(
            "Warning",
            "Please upload a resume first."
        )
        return

    jd_file = filedialog.askopenfilename(
        filetypes=[("Text Files", "*.txt")]
    )

    if not jd_file:
        return

    try:
        with open(jd_file, "r", encoding="utf-8") as file:
            jd_text = file.read()

        match_score = calculate_match_score(
            resume_text_global,
            jd_text
        )

        connection = connect_db()
        cursor = connection.cursor()
        
        cursor.execute(
            """
            UPDATE resumes
            SET jd_match_score = %s
            WHERE id = (
                SELECT MAX(id) FROM resumes
            )
            """,
            (match_score,)
        )
        
        connection.commit()
        connection.close()

        generate_chart(
            latest_score,
            latest_ats_score,
            match_score
        )
    
        ats_score, matched_skills, missing_skills = (
            calculate_ats_score(
                resume_text_global,
                jd_text
            )
        )

        latest_missing_skills = missing_skills
        
        match_label.config(
            text=f"Match Score: {match_score}%"
        )

        if match_score >= 80:
            match_label.config(fg="green")
        
        elif match_score >= 60:
            match_label.config(fg="orange")
        
        else:
            match_label.config(fg="red")

        resume_skills = set(
            extract_skills(resume_text_global)
        )
        
        jd_skills = set(
            extract_skills(jd_text)
        )
        
        missing_skills = list(
            jd_skills - resume_skills
        )
        
        if missing_skills:
            missing_skills_label.config(
                text="Missing Skills: " +
                ", ".join(missing_skills)
            )
        else:
            missing_skills_label.config(
                text="Missing Skills: None"
            )
        
        ats_label.config(
            text=f"ATS Score: {ats_score}%"
        )
        
        suggestions_box.config(state="normal")
        
        suggestions_box.delete(
            "1.0",
            tk.END
        )
        
        result_text = (
            "MATCHED SKILLS\n\n"
        )
        
        if matched_skills:
        
            for skill in matched_skills:
                result_text += f"✓ {skill}\n"
        
        else:
            result_text += "No matched skills\n"
        
        result_text += "\n\nMISSING SKILLS\n\n"
        
        if missing_skills:
        
            for skill in missing_skills:
                result_text += f"✗ {skill}\n"
        
        else:
            result_text += "No missing skills"
        
        suggestions_box.insert(
            tk.END,
            result_text
        )
        
        suggestions_box.config(state="disabled")
        
        messagebox.showinfo(
            "JD Match Result",
            f"Match Score: {match_score}%\n\n"
            f"ATS Score: {ats_score}%"
        )

        status_label.config(
            text="JD uploaded successfully"
        )

    except Exception as e:
        messagebox.showerror(
            "Error",
            str(e)
        )


def download_report():
    global latest_data
    global latest_score
    global latest_ats_score
    global latest_skills
    global latest_suggestions

    if not latest_data:
        messagebox.showwarning(
            "Warning",
            "Please upload a resume first."
        )
        return

    filename = (
        f"reports/{latest_data['name']}_Report.pdf"
    )

    generate_report(
        filename,
        latest_data["name"],
        latest_data["email"],
        latest_data["phone"],
        latest_score,
        latest_ats_score,
        latest_skills,
        latest_suggestions
    )

    messagebox.showinfo(
        "Success",
        f"Report saved:\n{filename}"
    )


def generate_resume():
    try:
        global latest_data
        global latest_skills
        global latest_missing_skills

        if not latest_data:
            messagebox.showwarning(
                "Warning",
                "Please upload a resume first."
            )
            return

        os.makedirs(
            "improved_resumes",
            exist_ok=True
        )
        
        output_file = (
            f"improved_resumes/"
            f"{latest_data['name']}_Updated.docx"
        )

        generate_improved_resume(
            latest_data["name"],
            latest_data["email"],
            latest_data["phone"],
            latest_skills,
            latest_missing_skills,
            latest_data["resume_text"],
            output_file
        )

        os.startfile(os.path.abspath(output_file))

        messagebox.showinfo(
            "Success",
            f"Resume saved:\n{output_file}"
        )

    except Exception as e:
        messagebox.showerror(
            "Error",
            str(e)
        )
        print("Generate Resume Error:", e)


def view_records():
    try:
        connection = connect_db()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
            id,
            name,
            email,
            phone,
            resume_score,
            jd_match_score,
            created_at
            FROM resumes
            """
        )

        records = cursor.fetchall()

        connection.close()

        window = Toplevel()

        window.title("Saved Records")

        window.geometry("700x400")

        text = tk.Text(window)

        text.pack(
            fill="both",
            expand=True
        )

        for row in records:
            text.insert(
                tk.END,
                f"ID: {row[0]}\n"
                f"Name: {row[1]}\n"
                f"Email: {row[2]}\n"
                f"Phone: {row[3]}\n"
                f"Resume Score: {row[4]}\n"
                f"JD Match Score: {row[5]}\n"
                f"Created At: {row[6]}\n"
                "-----------------------------\n"
            )

    except Exception as e:
        messagebox.showerror(
            "Error",
            str(e)
        )

def view_chart():

    chart_path = "reports/analysis_chart.png"

    if os.path.exists(chart_path):

        os.startfile(os.path.abspath(chart_path))

    else:

        messagebox.showwarning(
            "Warning",
            "Chart file not found."
        )


def export_excel():

    connection = connect_db()

    query = """
    SELECT name, email, phone, resume_score
    FROM resumes
    """

    df = pd.read_sql(query, connection)

    file_path = "reports/resume_records.xlsx"

    df.to_excel(file_path, index=False)

    connection.close()

    os.startfile(os.path.abspath(file_path))

    messagebox.showinfo(
        "Success",
        f"Excel exported:\n{file_path}"
    )

def launch_upload_ui():
    global status_label
    global missing_skills_label
    global score_label
    global progress_bar
    global match_label
    global name_label
    global email_label
    global phone_label
    global experience_label
    global skills_label
    global suggestions_box
    global ats_label

    root = tk.Tk()

    root.title("Resume Optimizer")

    root.geometry("800x600")
    root.configure(bg="white")

    header = tk.Label(
        root,
        text="Resume Optimizer",
        font=("Arial", 22, "bold"),
        bg="#0A4DA3",
        fg="white",
        pady=10
    )

    header.pack(fill="x")

    info_frame = tk.LabelFrame(
        root,
        text="Candidate Information",
        padx=10,
        pady=10
    )
    
    info_frame.pack(
        fill="x",
        padx=20,
        pady=5
    )

    name_label = tk.Label(
        info_frame,
        text="Name: ",
        font=("Arial", 12)
    )
    name_label.pack(anchor="w", pady=1)
    
    email_label = tk.Label(
        info_frame,
        text="Email: ",
        font=("Arial", 12)
    )
    email_label.pack(anchor="w", pady=1)
    
    phone_label = tk.Label(
        info_frame,
        text="Phone: ",
        font=("Arial", 12)
    )
    phone_label.pack(anchor="w", pady=1)
    
    experience_label = tk.Label(
        info_frame,
        text="Experience: Fresher",
        font=("Arial", 12)
    )
    experience_label.pack(anchor="w", pady=1)
    
    skills_label = tk.Label(
        info_frame,
        text="Skills: ",
        font=("Arial", 12)
    )
    skills_label.pack(anchor="w", pady=1)
    
    button_frame = tk.Frame(root, bg="white")
    button_frame.pack(pady=20)

    button_color="#0A4DA3"
    
    tk.Button(
        button_frame,
        text="Upload Resume",
        command=upload_resume,
        width=15,
        bg=button_color,
        fg="white",
        font=("Arial", 10, "bold")
    ).grid(row=0, column=0, padx=5)
    
    tk.Button(
        button_frame,
        text="Upload JD",
        command=upload_jd,
        width=15,
        bg=button_color,
        fg="white",
        font=("Arial", 10, "bold")
    ).grid(row=0, column=1, padx=5)
    
    tk.Button(
        button_frame,
        text="Download PDF",
        command=download_report,
        width=15,
       bg=button_color,
        fg="white",
        font=("Arial", 10, "bold")
    ).grid(row=0, column=2, padx=5)
    
    tk.Button(
        button_frame,
        text="Generate Resume",
        command=generate_resume,
        width=15,
        bg=button_color,
        fg="white",
        font=("Arial", 10, "bold")
    ).grid(row=1, column=0, padx=5, pady=5)
    
    tk.Button(
        button_frame,
        text="View Records",
        command=view_records,
        width=15,
        bg=button_color,
        fg="white",
        font=("Arial", 10, "bold")
    ).grid(row=1, column=1, padx=5, pady=5)

    tk.Button(
        button_frame,
        text="View Chart",
        command=view_chart,
        width=15,
        bg=button_color,
        fg="white",
        font=("Arial", 10, "bold")
    ).grid(row=2, column=1, pady=5)

    tk.Button(
        button_frame,
        text="Export Excel",
        command=export_excel,
        width=15,
        bg=button_color,
        fg="white",
        font=("Arial", 10, "bold")
    ).grid(row=1, column=2, padx=5, pady=5)

    score_frame = tk.LabelFrame(
        root,
        text="Resume Analysis",
        padx=10,
        pady=10
    )
    
    score_frame.pack(
        fill="x",
        padx=20,
        pady=10
    )
    
    score_label = tk.Label(
        score_frame,
        text="Resume Score: 0/100",
        font=("Arial", 12, "bold"),
        fg="green"
    )
    
    score_label.grid(
        row=0,
        column=0,
        padx=20
    )
    
    ats_label = tk.Label(
        score_frame,
        text="ATS Score: 0/100",
        font=("Arial", 12, "bold"),
        fg="blue"
    )
    
    ats_label.grid(
        row=0,
        column=1,
        padx=20
    )
    
    match_label = tk.Label(
        score_frame,
        text="Match Score: 0%",
        font=("Arial", 12, "bold"),
        fg="red"
    )
    
    match_label.grid(
        row=0,
        column=2,
        padx=20
    )

    missing_skills_label = tk.Label(
        root,
        text="Missing Skills: None",
        font=("Helvetica", 11, "bold")
    )

    missing_skills_label.pack(pady=5)

    progress_bar = ttk.Progressbar(
        root,
        orient="horizontal",
        length=700,
        mode="determinate",
        maximum=100
    )

    progress_bar.pack(pady=20)

    
    suggestion_frame = tk.LabelFrame(
        root,
        text="Suggestions",
        padx=10,
        pady=10
    )
    
    suggestion_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )
    
    scrollbar = tk.Scrollbar(suggestion_frame)
    scrollbar.pack(side="right", fill="y")
    
    suggestions_box = tk.Text(
        suggestion_frame,
        height=8,
        width=100,
        wrap="word",
        yscrollcommand=scrollbar.set
    )
    
    suggestions_box.pack(side="left", fill="both", expand=True)
    
    scrollbar.config(command=suggestions_box.yview)

    suggestions_box.config(state="disabled")
    

    status_label = tk.Label(
        root,
        text="Ready",
        bd=1,
        relief="sunken",
        anchor="w"
    )
    
    status_label.pack(
        side="bottom",
        fill="x"
    )

    footer = tk.Label(
        root,
        text="Resume Optimizer | AIML Project",
        fg="gray",
        font=("Arial", 9)
    )

    footer.pack(pady=5)

    root.mainloop()


if __name__ == "__main__":
    launch_upload_ui()
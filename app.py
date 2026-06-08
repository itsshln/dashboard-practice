import streamlit as st
import pandas as pd
import plotly.express as px

from database import engine
from queries import *
from io import BytesIO


#Настройка страницы

st.set_page_config(
    page_title="Практика студентов | FESCO",
    page_icon="📊",
    layout="wide"
)

#CSS

try:
    with open("style.css", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )
except:
    pass

#SIDEBAR

with st.sidebar:

    try:
        st.image(
            "assets/fesco_logo.png",
            use_container_width=True
        )
    except:
        pass

    st.markdown("## Практика студентов")

    st.markdown("---")

    period = st.selectbox(
        "Период",
        [
            "2025 год",
            "I квартал",
            "II квартал",
            "III квартал",
            "IV квартал"
        ]
    )
    departments_filter = pd.read_sql(
        """
        SELECT name 
        FROM departments
        ORDER BY name
        """,
        engine
    )
    
    department = st.selectbox(
        "Подразделение",
        ["Все"] + departments_filter["name"].tolist()
    )

    students_filter = pd.read_sql(
        """
        SELECT student_id, full_name
        FROM public.students
        ORDER BY student_id
        """,
        engine
    )

    selected_student = st.sidebar.selectbox(
        "Студент",
        ["Все студенты"] + students_filter["full_name"].tolist()
    )

    status = st.selectbox(
    "Статус",
    [
        "Все статусы",
        "Новая заявка",
        "На рассмотрении HR",
        "На согласовании подразделения",
        "Наставник назначен",
        "Практика активна",
        "Практика завершена",
        "Отказ"
    ]
    )

    st.markdown("---")

    st.markdown(
        """
        **Разделы**

        • KPI и эффективность

        • Воронка процесса

        • SLA и сроки

        • Аналитика заявок

        • Подразделения

        • Наставники

        • Реестр студентов
        """
    )

#HEADER

left, right = st.columns([5, 2])

with left:

    st.title("Практика студентов")

    st.caption(
        "Аналитический дашборд бизнес-процессов организации практики студентов"
    )

with right:

    st.write("")
    st.info("👤 HR-менеджер")

st.divider()

#KPI

total_students = get_total_students(selected_student).iloc[0, 0]
total_requests = get_total_requests(period, department, selected_student, status).iloc[0, 0]

active = get_active_practices(period, department, selected_student).iloc[0, 0]
completed = get_completed_practices(period, department, selected_student).iloc[0, 0]

avg_days = get_avg_processing_time(period, department, selected_student).iloc[0, 0]

returns = get_document_return_rate(period, department, selected_student, status).iloc[0, 0]

student_sat = get_student_satisfaction(period, department, selected_student, status).iloc[0, 0]
department_sat = get_department_satisfaction(period, department, selected_student, status).iloc[0, 0]

mentor_rating = get_mentor_rating(period, department, selected_student).iloc[0, 0]

reserve = get_reserve_conversion(period, department, selected_student, status).iloc[0, 0]

hr_queue = get_hr_queue(period, department, selected_student).iloc[0, 0]

#Округление метрик

student_sat = round(student_sat or 0, 2)

department_sat = round(department_sat or 0, 2)

mentor_rating = round(mentor_rating or 0, 2)

reserve = round(reserve or 0, 2)

returns = round(returns or 0, 2)

avg_days = round(avg_days or 0, 1)

#KPI ряд 1

st.subheader("Операционная эффективность")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Всего заявок",
    total_requests
)

c2.metric(
    "Активные практики",
    active,
    delta=f"{active} в работе"
)

c3.metric(
    "Завершено",
    completed,
    delta="успешно"
)

c4.metric(
    "Среднее оформление",
    f"{avg_days} дн.",
    delta="в среднем"
)

c5.metric(
    "Очередь HR",
    hr_queue,
    delta="в очереди"
)

#KPI ряд 2

c6, c7, c8, c9, c10 = st.columns(5)

c6.metric(
    "Всего студентов",
    total_students
)

c7.metric(
    "Возвраты документов",
    f"{returns}%"
)

c8.metric(
    "Оценка студентов",
    student_sat
)

c9.metric(
    "Оценка подразделений",
    department_sat
)

c10.metric(
    "Оценка наставников",
    mentor_rating
)

st.divider()

#KPI HR

st.subheader("Кадровый результат")

c11, c12 = st.columns(2)

c11.metric(
    "Конверсия в кадровый резерв",
    f"{reserve}%"
)

c12.metric(
    "Завершенные практики",
    completed
)

st.divider()

#Воронка процессов

st.subheader("Воронка процессов")

funnel = get_process_funnel(period, department, selected_student, status)

fig = px.funnel(
    funnel,
    x="cnt",
    y="stage",
    labels={
        "cnt": "Количество заявок",
        "stage": "Этап бизнес-процессов практики"
    }
)

fig.update_layout(
    height=500,
    xaxis_title="Количество заявок",
    yaxis_title="Этап бизнес-процессов практики"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

#Время этапов

st.subheader(
    "Среднее время прохождения этапов"
)

stage = get_stage_duration(period, department, selected_student)

fig = px.bar(
    stage,
    x="avg_days",
    y="status_name",
    orientation="h",
    text="avg_days",
    labels={
        "avg_days": "Среднее время (дни)",
        "status_name": "Этап бизнес-процессов практики"
    }
)

fig.update_layout(
    height=500,
    xaxis_title="Среднее время (дни)",
    yaxis_title="Этап бизнес-процессов практики"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

#Динамика + статусы

left, right = st.columns(2)
with left:

    st.subheader("Динамика заявок")

    month = get_requests_by_month(period, department, selected_student, status)

    month.columns = [
        "Месяц",
        "Количество заявок"
    ]

    months_ru = {
        "January": "Январь",
        "February": "Февраль",
        "March": "Март",
        "April": "Апрель",
        "May": "Май",
        "June": "Июнь",
        "July": "Июль",
        "August": "Август",
        "September": "Сентябрь",
        "October": "Октябрь",
        "November": "Ноябрь",
        "December": "Декабрь"
    }

    month["Месяц"] = pd.to_datetime(
        month["Месяц"]
    ).dt.strftime("%B").replace(months_ru)

    fig = px.line(
        month,
        x="Месяц",
        y="Количество заявок",
        markers=True
    )

    fig.update_layout(
        height=400,
        xaxis_title="Месяц",
        yaxis_title="Количество заявок"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right:

    st.subheader("Статусы заявок")

    status = get_status_distribution(period, department, selected_student, status)
    status.columns = [
    "Статус заявки",
    "Количество"
    ]

    fig = px.pie(
        status,
        values="Количество",
        names="Статус заявки",
        hole=0.55
    )

    fig.update_layout(
    height=400,
    legend_title="Статус заявки"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

#Кадровый резерв

st.subheader(
    "Кадровый резерв"
)

reserve_chart = get_reserve_chart(period, department, selected_student, status)
reserve_chart.columns = [
    "Статус",
    "Количество"
]

fig = px.pie(
    reserve_chart,
    values="Количество",
    names="Статус",
    hole=0.6
)

fig.update_layout(
    height=450,
    legend_title="Результат"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

#Университеты + подразделения

left, right = st.columns(2)

with left:

    st.subheader(
        "Топ университетов"
    )

    university = get_university_distribution(selected_student)

    university.columns = [
        "Университет",
        "Количество студентов"
    ]

    fig = px.bar(
        university.head(10),
        x="Количество студентов",
        y="Университет",
        orientation="h"
    )

    fig.update_layout(
        height=450
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right:

    st.subheader(
        "Подразделения"
    )

    departments = get_department_distribution(period, department, selected_student, status)
    departments.columns = [
    "Подразделение",
    "Количество практикантов"
    ]

    st.dataframe(
        departments,
        use_container_width=True,
        hide_index=True
    )

st.divider()

#Рейтинг подразделений

left, right = st.columns(2)

with left:

    st.subheader(
        "Рейтинг подразделений"
    )

    dep_rating = get_department_rating(period, department, selected_student, status)
    dep_rating.columns = [
    "Подразделение",
    "Студентов",
    "Средняя оценка"
    ]

    st.dataframe(
        dep_rating,
        use_container_width=True,
        hide_index=True
    )

with right:

    st.subheader(
        "Рейтинг наставников"
    )

    mentor_table = get_mentor_rating_table(period, department, selected_student, status)
    mentor_table.columns = [
    "Наставник",
    "Студентов",
    "Средняя оценка"
    ]

    st.dataframe(
        mentor_table,
        use_container_width=True,
        hide_index=True
    )

st.divider()

#Реестр студентов

st.subheader(
    "Реестр студентов"
)

students = pd.read_sql(
    f"""

    SELECT

        s.student_id,
        s.full_name,
        s.university,
        s.speciality,

        d.name,

        p.current_status,
        p.practice_start,
        p.practice_end

    FROM students s

    LEFT JOIN practice_requests p
        ON s.student_id = p.student_id

    LEFT JOIN departments d
        ON p.department_id = d.department_id

    WHERE {build_student_condition(selected_student)}
      AND {build_department_condition(department)}
      AND {build_status_condition(status)}

    ORDER BY s.student_id

    """,
    engine
)

students.columns = [
    "ID",
    "ФИО",
    "Университет",
    "Специальность",
    "Подразделение",
    "Статус",
    "Начало практики",
    "Окончание практики"
]

students["Начало практики"] = pd.to_datetime(
    students["Начало практики"]
).dt.strftime("%d.%m.%Y")

students["Окончание практики"] = pd.to_datetime(
    students["Окончание практики"]
).dt.strftime("%d.%m.%Y")

st.dataframe(
    students,
    use_container_width=True,
    hide_index=True
)

#Экспорт в Excel
st.divider()

st.subheader("Экспорт данных")

output = BytesIO()

with pd.ExcelWriter(
    output,
    engine="openpyxl"
) as writer:

    students.to_excel(
        writer,
        sheet_name="Студенты",
        index=False
    )

    university.to_excel(
        writer,
        sheet_name="Университеты",
        index=False
    )

    departments.to_excel(
        writer,
        sheet_name="Подразделения",
        index=False
    )

    dep_rating.to_excel(
        writer,
        sheet_name="Рейтинг подразделений",
        index=False
    )

    mentor_table.to_excel(
        writer,
        sheet_name="Наставники",
        index=False
    )

output.seek(0)

st.download_button(
    "📥 Скачать отчет Excel",
    data=output,
    file_name="FESCO_Практика_студентов.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
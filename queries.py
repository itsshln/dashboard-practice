import pandas as pd
from database import engine

def build_period_condition(period):

    if period == "I квартал":
        return "EXTRACT(QUARTER FROM created_at)=1"

    elif period == "II квартал":
        return "EXTRACT(QUARTER FROM created_at)=2"

    elif period == "III квартал":
        return "EXTRACT(QUARTER FROM created_at)=3"

    elif period == "IV квартал":
        return "EXTRACT(QUARTER FROM created_at)=4"

    return "1=1"

def build_department_condition(department):

    if department == "Все":
        return "1=1"

    return f"d.name = '{department}'"

def build_student_condition(student):

    if student == "Все студенты":
        return "1=1"

    return f"s.full_name = '{student}'"

def build_status_condition(status):

    if status == "Все статусы":
        return "1=1"

    return f"p.current_status = '{status}'"

#KPI

def get_total_students(student):

    query = f"""
    SELECT COUNT(*) AS total_students

    FROM students s

    WHERE {build_student_condition(student)}
    """

    return pd.read_sql(query, engine)


def get_total_requests(period, department, student, status):

    query = f"""
    SELECT COUNT(*) AS total_requests

    FROM practice_requests p

    LEFT JOIN departments d
        ON p.department_id = d.department_id

    LEFT JOIN students s
        ON p.student_id = s.student_id

    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND {build_status_condition(status)}
    """

    return pd.read_sql(query, engine)


def get_active_practices(period, department, student):

    query = f"""
    SELECT COUNT(*) AS active_count

    FROM practice_requests p

    LEFT JOIN departments d
        ON p.department_id = d.department_id

    LEFT JOIN students s
        ON p.student_id = s.student_id

    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND p.current_status='Практика активна'
    """

    return pd.read_sql(query, engine)


def get_completed_practices(period, department, student):

    query = f"""
    SELECT COUNT(*) AS completed_count

    FROM practice_requests p

    LEFT JOIN departments d
        ON p.department_id = d.department_id

    LEFT JOIN students s
        ON p.student_id = s.student_id

    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND p.current_status='Практика завершена'
    """

    return pd.read_sql(query, engine)


def get_avg_processing_time(period, department, student):

    query = f"""
    SELECT
        COALESCE(
            ROUND(
                AVG(
                    approved_at::date - created_at::date
                )::numeric,
                2
            ),
            0
        ) AS avg_days

    FROM practice_requests p

    LEFT JOIN departments d
        ON p.department_id=d.department_id

    LEFT JOIN students s
        ON p.student_id = s.student_id

    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND approved_at IS NOT NULL
    """

    return pd.read_sql(query, engine)


def get_document_return_rate(period, department, student, status):

    query = f"""
    SELECT
        COALESCE(
            ROUND(
                (
                    COUNT(*) FILTER (
                        WHERE doc.is_valid = FALSE
                    ) * 100.0
                    /
                    NULLIF(COUNT(*),0)
                )::numeric,
                2
            ),
            0
        ) AS return_rate

    FROM documents doc

    JOIN practice_requests p
        ON doc.request_id = p.request_id

    JOIN departments d
        ON p.department_id = d.department_id

    JOIN students s
        ON p.student_id = s.student_id

    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND {build_status_condition(status)}
    """

    return pd.read_sql(query, engine)


def get_student_satisfaction(period, department, student, status):

    query = f"""
    SELECT
        COALESCE(
            ROUND(
                AVG(pr.student_score)::numeric,
                2
            ),
            0
        ) AS student_satisfaction

    FROM practice_results pr

    JOIN practice_requests r
        ON pr.request_id=r.request_id

    JOIN departments d
        ON r.department_id=d.department_id

    JOIN students s
        ON r.student_id=s.student_id

    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND {build_status_condition(status)}
    """

    return pd.read_sql(query, engine)


def get_department_satisfaction(period, department, student, status):

    query = f"""
    SELECT
        COALESCE(
            ROUND(
                AVG(pr.department_score)::numeric,
                2
            ),
            0
        ) AS department_satisfaction

    FROM practice_results pr

    JOIN practice_requests r
        ON pr.request_id=r.request_id

    JOIN departments d
        ON r.department_id=d.department_id

    JOIN students s
        ON r.student_id=s.student_id

    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND {build_status_condition(status)}
    """

    return pd.read_sql(query, engine)


def get_mentor_rating(period, department, student):

    query = f"""
    SELECT
        COALESCE(
            ROUND(
                AVG(pr.mentor_score)::numeric,
                2
            ),
            0
        ) AS mentor_rating

    FROM practice_results pr

    JOIN practice_requests r
        ON pr.request_id=r.request_id

    JOIN departments d
        ON r.department_id=d.department_id

    JOIN students s
        ON r.student_id=s.student_id

    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
    """

    return pd.read_sql(query, engine)


def get_reserve_conversion(period, department, student, status):

    query = f"""
    SELECT
        COALESCE(
            ROUND(
                (
                    COUNT(*) FILTER (
                        WHERE reserve_recommendation = TRUE
                    ) * 100.0 /
                    NULLIF(COUNT(*),0)
                )::numeric,
                2
            ),
            0
        ) AS reserve_conversion

    FROM practice_results pr

    JOIN practice_requests r
        ON pr.request_id=r.request_id

    JOIN departments d
        ON r.department_id=d.department_id

    JOIN students s
        ON r.student_id=s.student_id

    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND {build_status_condition(status)}
    """

    return pd.read_sql(query, engine)


def get_hr_queue(period, department, student):

    query = f"""
    SELECT COUNT(*) AS hr_queue

    FROM practice_requests p

    LEFT JOIN departments d
        ON p.department_id=d.department_id

    LEFT JOIN students s
        ON p.student_id=s.student_id

    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND current_status NOT IN (
            'Практика завершена',
            'Отказ'
      )
    """

    return pd.read_sql(query, engine)

#Воронка процессов

def get_process_funnel(period, department, student, status):

    query = f"""

    SELECT
        'Подана заявка' AS stage,
        COUNT(*) AS cnt
    FROM practice_requests p
    LEFT JOIN departments d
        ON p.department_id = d.department_id
    LEFT JOIN students s
        ON p.student_id = s.student_id
    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND {build_status_condition(status)}
      
    UNION ALL

    SELECT
        'Рассмотрение HR' AS stage,
        COUNT(*) AS cnt
    FROM practice_requests p
    LEFT JOIN departments d
        ON p.department_id = d.department_id
    LEFT JOIN students s
        ON p.student_id = s.student_id
    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND {build_status_condition(status)}
      AND current_status <> 'Новая заявка'

    UNION ALL

    SELECT
        'Наставник назначен' AS stage,
        COUNT(*) AS cnt
    FROM practice_requests p
    LEFT JOIN departments d
        ON p.department_id = d.department_id
    LEFT JOIN students s
        ON p.student_id = s.student_id
    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND {build_status_condition(status)}
      AND mentor_id IS NOT NULL

    UNION ALL

    SELECT
        'Практика активна' AS stage,
        COUNT(*) AS cnt
    FROM practice_requests p
    LEFT JOIN departments d
        ON p.department_id = d.department_id
    LEFT JOIN students s
        ON p.student_id = s.student_id
    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND {build_status_condition(status)}
      AND current_status IN (
            'Практика активна',
            'Практика завершена'
      )

    UNION ALL

    SELECT
        'Практика завершена' AS stage,
        COUNT(*) AS cnt
    FROM practice_requests p
    LEFT JOIN departments d
        ON p.department_id = d.department_id
    LEFT JOIN students s
        ON p.student_id = s.student_id
    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND {build_status_condition(status)}
      AND current_status = 'Практика завершена'

    """

    return pd.read_sql(query, engine)

#Время прохождения этапов

def get_stage_duration(period, department, student):

    query = f"""

    WITH events AS (

        SELECT
            sh.request_id,
            sh.status_name,
            sh.changed_at,

            LEAD(sh.changed_at)
            OVER(
                PARTITION BY sh.request_id
                ORDER BY sh.changed_at
            ) AS next_time

        FROM status_history sh

        JOIN practice_requests p
            ON sh.request_id = p.request_id

        JOIN departments d
            ON p.department_id = d.department_id

        JOIN students s
            ON p.student_id = s.student_id

        WHERE {build_period_condition(period)}
          AND {build_department_condition(department)}
          AND {build_student_condition(student)}
    )

    SELECT
        status_name,

        ROUND(
            AVG(
                EXTRACT(
                    EPOCH FROM (
                        next_time - changed_at
                    )
                ) / 86400
            )::numeric,
            2
        ) AS avg_days

    FROM events

    WHERE next_time IS NOT NULL

    GROUP BY status_name

    ORDER BY avg_days DESC

    """

    return pd.read_sql(query, engine)

#Диаграммы

def get_status_distribution(period, department, student, status):

    query = f"""
    SELECT
        current_status,
        COUNT(*) AS cnt

    FROM practice_requests p

    LEFT JOIN departments d
        ON p.department_id=d.department_id
    
    LEFT JOIN students s
        ON p.student_id=s.student_id    

    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND {build_status_condition(status)}
    GROUP BY current_status
    ORDER BY cnt DESC
    """

    return pd.read_sql(query, engine)


def get_requests_by_month(period, department, student, status):

    query = f"""
    SELECT
        DATE_TRUNC('month', created_at) AS month,
        COUNT(*) AS requests_count

    FROM practice_requests p

    LEFT JOIN departments d
        ON p.department_id=d.department_id
    
    LEFT JOIN students s
        ON p.student_id=s.student_id

    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND {build_status_condition(status)}

    GROUP BY month
    ORDER BY month
    """

    return pd.read_sql(query, engine)


def get_reserve_chart(period, department, student, status):

    query = f"""
    SELECT
        CASE
            WHEN reserve_recommendation=TRUE
                THEN 'Рекомендован'
            ELSE 'Не рекомендован'
        END AS reserve_status,

        COUNT(*) AS cnt

    FROM practice_results pr

    JOIN practice_requests r
        ON pr.request_id=r.request_id

    JOIN departments d
        ON r.department_id=d.department_id
    
    JOIN students s
        ON r.student_id=s.student_id

    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND {build_status_condition(status)}
    GROUP BY reserve_status
    """

    return pd.read_sql(query, engine)

#Университеты

def get_university_distribution(student):

    query = f"""
    SELECT
        university,
        COUNT(*) AS cnt

    FROM students s

    WHERE {build_student_condition(student)}

    GROUP BY university
    ORDER BY cnt DESC
    """

    return pd.read_sql(query, engine)

#Подразделения

def get_department_distribution(period, department, student, status):

    query = f"""
    SELECT
        d.name,
        COUNT(*) AS cnt

    FROM practice_requests p

    JOIN departments d
        ON p.department_id=d.department_id
    
    JOIN students s
        ON p.student_id=s.student_id

    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND {build_status_condition(status)}
    GROUP BY d.name
    ORDER BY cnt DESC
    """

    return pd.read_sql(query, engine)


def get_department_rating(period, department, student, status):

    query = f"""
    SELECT
        d.name,
        COUNT(*) AS students,

        ROUND(
            AVG(pr.department_score)::numeric,
            2
        ) AS avg_score

    FROM practice_results pr

    JOIN practice_requests r
        ON pr.request_id=r.request_id

    JOIN departments d
        ON r.department_id=d.department_id
    
    JOIN students s
        ON r.student_id=s.student_id

    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND {build_status_condition(status)}
    GROUP BY d.name
    ORDER BY avg_score DESC
    """

    return pd.read_sql(query, engine)

#Наставники

def get_mentor_rating_table(period, department, student, status):

    query = f"""
    SELECT
        m.full_name,
        COUNT(*) AS students,

        ROUND(
            AVG(pr.mentor_score)::numeric,
            2
        ) AS avg_score

    FROM practice_results pr

    JOIN practice_requests r
        ON pr.request_id=r.request_id

    JOIN mentors m
        ON r.mentor_id=m.mentor_id

    JOIN departments d
        ON r.department_id=d.department_id
    
    JOIN students s
        ON r.student_id=s.student_id

    WHERE {build_period_condition(period)}
      AND {build_department_condition(department)}
      AND {build_student_condition(student)}
      AND {build_status_condition(status)}
    GROUP BY m.full_name
    ORDER BY avg_score DESC
    """

    return pd.read_sql(query, engine)
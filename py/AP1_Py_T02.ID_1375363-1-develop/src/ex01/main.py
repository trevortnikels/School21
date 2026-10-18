import time
import random
from multiprocessing import Process, Queue
from prettytable import PrettyTable

from questions import Question
from students import Student
from examiners import Examiner
from typing import List


def files():
    with open('examiners.txt', 'r', encoding='utf-8') as f:
        examiners = [line.strip().split() for line in f.readlines() if line.strip()]

    with open('students.txt', 'r', encoding='utf-8') as f:
        students = [line.strip().split() for line in f.readlines() if line.strip()]

    with open('questions.txt', 'r', encoding='utf-8') as f:
        questions = [line.strip() for line in f.readlines() if line.strip()]

    return examiners, students, questions


def process_of_exam(examiner: Examiner, students_queue: Queue, results: Queue, questions: List[Question]):
    personal_start = time.time()

    while not students_queue.empty():
        try:
            if time.time() - personal_start > 30:
                print(f"{examiner.name} на обеде")
                time.sleep(random.uniform(12, 18))
                personal_start = time.time()

            student: Student = students_queue.get(timeout=1.0)

            examiner.cur_student = student
            results.put(("start", examiner.name, student.name))

            examiner.exam_process(student, questions)

            results.put((
                "finish",
                examiner.name,
                student.name,
                student.state,
                getattr(student, 'exam_time', None),
                examiner.total_students,
                examiner.failed_students,
                examiner.work_time
            ))

            examiner.cur_student = None

        except Exception:
            continue


def print_process(students, examiners, cur_time: float):
    # УБРАЛИ clear_screen() — чтобы избежать ошибки в PowerShell
    print("\n" + "="*80)

    # Таблица студентов
    stu_table = PrettyTable(["Студент", "Статус"])
    for student in sorted(students, key=lambda s: ("Очередь", "Сдал", "Провалил").index(s.state)):
        stu_table.add_row([student.name, student.state])
    print(stu_table)

    # Таблица экзаменаторов
    ex_table = PrettyTable(["Экзаменатор", "Текущий студент", "Всего студентов", "Завалил", "Время работы"])
    for ex in examiners:
        current = ex.cur_student.name if ex.cur_student else "-"
        ex_table.add_row([
            ex.name,
            current,
            ex.total_students,
            ex.failed_students,
            f"{ex.work_time:.2f}"
        ])
    print(ex_table)

    queue_count = sum(1 for s in students if s.state == "Очередь")
    print(f"\nОсталось в очереди: {queue_count} из {len(students)}")
    print(f"Время с момента начала экзамена: {cur_time:.2f}")
    print("="*80)


def print_res(students, examiners, questions, total_time: float):
    print("\n" + "="*80 + "\nФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ\n" + "="*80)

    # Финальная таблица студентов
    stu_table = PrettyTable(["Студент", "Статус"])
    for student in sorted(students, key=lambda s: ("Сдал", "Провалил").index(s.state)):
        stu_table.add_row([student.name, student.state])
    print(stu_table)

    # Финальная таблица экзаменаторов
    ex_table = PrettyTable(["Экзаменатор", "Всего студентов", "Завалил", "Время работы"])
    for ex in examiners:
        ex_table.add_row([ex.name, ex.total_students, ex.failed_students, f"{ex.work_time:.2f}"])
    print(ex_table)

    print(f"\nВремя экзамена: {total_time:.2f} секунд")

    # Лучшие студенты
    passed = [s for s in students if s.state == "Сдал" and s.exam_time is not None]
    if passed:
        min_time = min(s.exam_time for s in passed)
        best = [s.name for s in passed if abs(s.exam_time - min_time) < 0.01]
        print(f"Имена лучших студентов: {', '.join(best)}")
    else:
        print("Имена лучших студентов: нет")

    # Лучшие экзаменаторы
    if examiners:
        min_rate = min((e.failed_students / e.total_students if e.total_students > 0 else 1.0) for e in examiners)
        best_ex = [e.name for e in examiners 
                   if e.total_students > 0 and abs(e.failed_students / e.total_students - min_rate) < 0.001]
        print(f"Имена лучших экзаменаторов: {', '.join(best_ex) if best_ex else 'нет'}")

    # Студенты на отчисление
    failed = [s for s in students if s.state == "Провалил" and s.exam_time is not None]
    if failed:
        min_time = min(s.exam_time for s in failed)
        to_expell = [s.name for s in failed if abs(s.exam_time - min_time) < 0.01]
        print(f"Имена студентов на отчисление: {', '.join(to_expell)}")

    # Лучшие вопросы
    if questions:
        max_correct = max((q.correct_ans for q in questions), default=0)
        best_q = [q.questions for q in questions if q.correct_ans == max_correct]
        print(f"Лучшие вопросы: {', '.join(best_q)}")

    passed_count = sum(1 for s in students if s.state == "Сдал")
    success_rate = passed_count / len(students) if students else 0
    if success_rate > 0.85:
        print("\nВывод: Экзамен удался")
    else:
        print("\nВывод: Экзамен не удался")


def main():
    ex_data, stu_data, quest_data = files()

    examiners = [Examiner(name, gender) for name, gender in ex_data]
    students = [Student(name, gender) for name, gender in stu_data]
    questions = [Question(text) for text in quest_data]

    students_queue = Queue()
    for student in students:
        students_queue.put(student)

    results_queue = Queue()

    processes = []
    for examiner in examiners:
        p = Process(target=process_of_exam,
                    args=(examiner, students_queue, results_queue, questions))
        p.start()
        processes.append(p)

    start_time = time.time()

    try:
        while any(p.is_alive() for p in processes) or not results_queue.empty():
            cur_time = time.time() - start_time

            while not results_queue.empty():
                try:
                    data = results_queue.get(timeout=0.1)
                    if data[0] == "finish":
                        _, ex_name, stu_name, state, exam_time, total, failed, work_time = data

                        for s in students:
                            if s.name == stu_name:
                                s.state = state
                                s.exam_time = exam_time
                                break

                        for e in examiners:
                            if e.name == ex_name:
                                e.total_students = total
                                e.failed_students = failed
                                e.work_time = work_time
                                break
                except:
                    break

            print_process(students, examiners, cur_time)
            time.sleep(0.3)   # чуть больше задержка 

    finally:
        for p in processes:
            if p.is_alive():
                p.terminate()

    final_time = time.time() - start_time
    print_res(students, examiners, questions, final_time)


if __name__ == "__main__":
    main()
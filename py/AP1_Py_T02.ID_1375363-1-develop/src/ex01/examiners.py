import random
import time
from students import Student
from questions import Question
from typing import List


class Examiner:
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender
        self.total_students = 0
        self.failed_students = 0
        self.work_time = 0.0
        self.cur_student: Student = None
        self.break_time = False

    def mood(self, correct: int) -> bool:
        mood = random.choices(["Bad", "Normal", "Good"],
                              weights=[1/8, 5/8, 1/4], k=1)[0]
        if mood == "Bad":
            return False
        elif mood == "Good":
            return True
        # Neutral: passed if more than half correct ( > 1.5 → at least 2 out of 3)
        return correct > 1.5

    def exam_process(self, student: Student, questions: List[Question]):
        self.total_students += 1
        exam_time = random.uniform(len(self.name) - 1, len(self.name) + 1)
        time.sleep(exam_time)

        self.work_time += exam_time
        student.exam_time = exam_time

        correct_answers = 0

        # Выбираем 3 случайных вопроса
        for idx in random.sample(range(len(questions)), 3):
            question = questions[idx]
            stu_answer = question.student_answer(student.gender)
            ex_answers = question.examiners_answer(self.gender)

            if stu_answer in ex_answers:
                correct_answers += 1
                question.correct_ans += 1   # +1 только за этот вопрос!

        # Решение по настроению
        passed = self.mood(correct_answers)
        if passed:
            student.state = "Сдал"
        else:
            self.failed_students += 1
            student.state = "Провалил"
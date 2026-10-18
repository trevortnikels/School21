import random


class Question:
    phi = (1 + 5 ** 0.5) / 2

    def __init__(self, question):
        self.questions = question
        self.words = question.split()
        self.correct_ans = 0

    def probability_for_answer(self, gender):
        n = len(self.words)
        if n == 0:
            return []
        if n == 1:
            return [1.0]

        probs = []
        remaining = 1.0
        phi = self.phi

        for i in range(n):
            if i == n - 1:
                probs.append(remaining)
            else:
                p = remaining / phi
                probs.append(p)
                remaining -= p

        if gender == 'Ж':
            probs.reverse()

        total = sum(probs)
        if total > 0:
            probs = [p / total for p in probs]

        return probs

    def student_answer(self, gender):
        prob = self.probability_for_answer(gender)
        return random.choices(self.words, weights=prob, k=1)[0]

    def examiners_answer(self, gender):
        """Экзаменатор выбирает одно или несколько правильных слов.
        После каждого выбора с вероятностью 1/3 продолжает выбирать ещё."""
        prob = self.probability_for_answer(gender)
        words_left = list(range(len(self.words)))
        correct = []

        while words_left:
            idx = random.choices(words_left, 
                                 weights=[prob[i] for i in words_left], 
                                 k=1)[0]
            correct.append(self.words[idx])
            words_left.remove(idx)

            # Вероятность 1/3 продолжить, иначе остановиться
            if random.random() > 1/3 or len(words_left) == 0:
                break

        return correct
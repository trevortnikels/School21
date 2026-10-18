CC = gcc
OS = $(shell uname)
CFLAGS = -Wall -Werror -Wextra -g -std=c11

STRING_FUNC = $(wildcard ./string_functions/*.c)
SPRINTF_FUNC = $(wildcard ./sprintf_function/s21_sprintf.c)
SOURCE_TESTS_FUNC = $(wildcard ./test_function/*.c *.h)

TEST_EXEC = s21_test_string
REPORT_DIR = ./report

ifeq ($(OS), Ilya)
	det_OS = -lcheck
	GCOV_FLAGS = -fprofile-arcs -ftest-coverage
else
	det_OS = -lcheck -lm -pthread 
endif

all: s21_string.a s21_sprintf gcov_report

rebuild: clean all

test:
	@$(CC) $(CFLAGS) $(det_OS) --coverage $(SOURCE_TESTS_FUNC) $(STRING_FUNC) $(SPRINTF_FUNC) s21_string.a -o s21_test_string
	./s21_test_string

gcov_report: test
	@lcov -t "test_s21_string" -o test.info --no-external -c -d .
	@genhtml -o report test.info
	open report/index.html
	rm -rf *.gcno *gcda *.gco

s21_string.a:
	@$(CC) $(CFLAGS) $(STRING_FUNC) $(GCOV_FLAGS) -c
	ar rc s21_string.a *.o
	ranlib s21_string.a

s21_sprintf:
	@$(CC) $(CFLAGS) $(SPRINTF_FUNC) $(GCOV_FLAGS) -c

clean:
	rm -rf test *.gcda *.gcno *.o *.info *.a *.h.gch tests/*.gcno report 
	rm -rf s21_test_string.dSYM s21_test_string
	rm -rf tests/*.h.gch 

style:
	@cp ../materials/linters/.clang-format ../src
	clang-format -n -style=google *.h $(STRING_FUNC) $(SOURCE_TESTS_FUNC) $(SPRINTF_FUNC)
	@rm -rf .clang-format

style_repair:
	@cp ../materials/linters/.clang-format ../src
	@clang-format -i -style=google *.h $(STRING_FUNC) $(SOURCE_TESTS_FUNC) $(SPRINTF_FUNC)
	@rm -rf .clang-format

leaks:
	leaks -atExit -- ./s21_test_string

cppcheck:
	cppcheck *.h $(STRING_FUNC) $(SOURCE_TESTS_FUNC) $(SPRINTF_FUNC)

install_brew:
	cd ~
	curl -fsSL https://rawgit.com/kube/42homebrew/master/install.sh | zsh
	brew install lcov

CC=gcc
CFLAGS = -std=c11 -Wall -Wextra -Werror -pedantic 
GCOVFLAGS = -fprofile-arcs -ftest-coverage
LD_FLAGS= -lcheck -lsubunit -lm

HEADERS =  s21_decimal.h s21_arithmetic_lib.h s21_additional_func.h
SRC_C = s21_additional_func.c s21_arithmetic_lib.c
SOURCE_TESTS_FUNC = $(wildcard ./tests/*.c)
SOURCES_ALL = $(wildcard ./arithmetic/*.c) 	\
	$(wildcard ./convertors/*.c)			\
	$(wildcard ./comparison/*.c)			\
	$(wildcard ./other/*.c) 				\


OBJ_LIBRARY := $(patsubst %.c, %.o, $(SOURCES_ALL) $(SRC_C))

%.o: %.c $(HEADERS)
	gcc $(CFLAGS) -c $< -o $@


all: s21_decimal.a test gcov_report

s21_decimal.a: $(OBJ_LIBRARY) $(HEADERS)
	ar rcs s21_decimal.a $(OBJ_LIBRARY)
	ranlib s21_decimal.a
	rm -rf ./*/*.o *.o

test: s21_decimal.a tests/tests_suite.c
	gcc $(CFLAGS) tests/tests_suite.c s21_decimal.a -o test.out $(LD_FLAGS)
	./test.out

gcov_report: s21_decimal.a tests/tests_suite.c
	gcc $(GCOVFLAGS) tests/tests_suite.c $(SOURCES_ALL) $(SRC_C) -o report.out $(LD_FLAGS)
	./report.out
	lcov -t "gcov_report" -o Coverage_Report.info -c -d .
	genhtml -o ./report Coverage_Report.info
	rm -f *.o *.a *.gcno *.gcda *.info *.out *.gcov *.gch
	open ./report/index-sort-f.html
	
check:
	@cp ../materials/linters/.clang-format ../src
	clang-format -n -style=google *.h $(SOURCES_ALL) $(SRC_C) $(SOURCE_TESTS_FUNC)
	@rm -rf .clang-format


clang:
	@cp ../materials/linters/.clang-format ../src
	@clang-format -i -style=google *.h $(SOURCES_ALL) $(SRC_C) $(SOURCE_TESTS_FUNC)
	@rm -rf .clang-format


rebuild: clean all

clean:
	rm -f *.o *.a *.gcno *.gcda *.info *.out *.gcov *.gch
	rm -rf ./report

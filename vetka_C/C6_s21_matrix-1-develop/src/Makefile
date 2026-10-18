TARGET = s21_matrix.a
CC = gcc
CFLAGS = -Wall -Werror -Wextra -std=c11
OS = $(shell uname)
MODULES = $(wildcard modules/*.c)
OBJECTS = $(patsubst %.c, %.o, $(MODULES))
TEST_TARGET = testing_exe

ifeq ($(OS), Linux)
	LDLIBS = -lcheck_pic -pthread -lrt -lm -lsubunit
else
	LDLIBS = -lcheck
endif

all: clean $(TARGET) test gcov_report

build: $(TARGET)

rebuild: clean $(TARGET)

$(TARGET): $(OBJECTS)
	@ar rcs $(TARGET) $(wildcard objects/*.o)

%.o: %.c
	@mkdir -p objects
	@$(CC) -c $(CFLAGS) $< $(LDLIBS) -o $(patsubst modules%, objects%, $@)

test: $(TARGET)
	@$(CC) $(CFLAGS) $(wildcard tests/*.c) $(LDLIBS) -L. $(TARGET) -o ./tests/$(TEST_TARGET)
	@./tests/$(TEST_TARGET)

gcov_report: $(TARGET)
	@echo "┏=========================================┓"
	@echo "┃     Generating your html report ...     ┃"
	@echo "┗=========================================┛"
	@$(CC) --coverage $(CFLAGS) $(wildcard tests/*.c) $(LDLIBS) $(MODULES) -o ./tests/$(TEST_TARGET)
	@./tests/$(TEST_TARGET)
	@lcov -t "test_coverage" -o test_coverage.info -c -d .
	@genhtml -o report test_coverage.info
	@open report/index.html
	@rm -rf *.gcda *.gcno tests/$(TEST_TARGET) report/test_coverage.info

style_check:
	@echo "┏=========================================┓"
	@echo "┃  Checking your code for Google Style    ┃"
	@echo "┗=========================================┛"
	@cp ../materials/linters/.clang-format .
	@clang-format -n **/*.c **/*.h *.h
	@rm ./.clang-format

format_style:
	@echo "┏=========================================┓"
	@echo "┃  Formatting your code for Google Style  ┃"
	@echo "┗=========================================┛"
	@cp ../materials/linters/.clang-format .
	@clang-format -i **/*.c **/*.h *.h
	@rm ./.clang-format


valgrind_check: test
	@CK_FORK=no valgrind --vgdb=no --leak-check=full \
	--show-leak-kinds=all --track-origins=yes --log-file="valgrind.log" -v --verbose -q --quiet -s tests/$(TEST_TARGET)

clean:
	@echo "Deleting unnecessary files..."
	@rm -rf objects *.a tests/$(TEST_TARGET) *.dSYM **/*.dSYM *.log **/*.log report test_coverage.info


.PHONY: all build rebuild clean test gcov_report style_check valgrind_check
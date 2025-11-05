# https://just.systems

target := './include ./src -regex ".*\.\(c\|h\|cpp\|hpp\)"'

lint:
    find {{ target }} -exec clang-tidy -p ./build {} +;

format:
    find {{ target }} -exec clang-format -i {} +;

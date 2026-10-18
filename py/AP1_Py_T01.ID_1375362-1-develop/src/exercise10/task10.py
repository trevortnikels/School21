def get_first_line() -> tuple[int, int]:
    N, T = map(int, input().strip().split())

    if N <= 0 or T <= 0:
        raise ValueError

    return (N, T)


def get_data_from_input(N: int) -> dict:
    data = {}
    for _ in range(N):
        year, cost, time = map(int, input().strip().split())

        if year <= 0 or cost <= 0 or time <= 0:
            raise ValueError

        data.setdefault(year, []).append((cost, time))
    return data


def find_best(data: dict, T: int) -> int | None:
    best_cost = None
    for year, maschines in data.items():
        best_for_time = {}
        for cost, time in maschines:
            needed_time = T - time

            if needed_time in best_for_time:
                total_cost = cost + best_for_time[needed_time]

                if best_cost is None or best_cost > total_cost:
                    best_cost = total_cost

            if time not in best_for_time or best_for_time[time] > cost:
                best_for_time[time] = cost

    return best_cost


def main():
    try:
        N, T = get_first_line()
        data = get_data_from_input(N)
        print(find_best(data, T))
    except Exception:
        print("Ошибка ввода")
        return


if __name__ == "__main__":
    main()

import pandas as pd


def split_df(df: pd.DataFrame, num_parts: int | None = None, part_size: int | None = None) -> list[pd.DataFrame]:
    if df.empty:
        return []

    if num_parts:
        avg_size = len(df) // num_parts
        remainder = len(df) % num_parts

        result = []
        start = 0
        for i in range(num_parts):
            end = start + avg_size + (1 if i < remainder else 0)
            result.append(df.iloc[start:end])
            start = end
        return result

    elif part_size:
        return [df.iloc[i:i + part_size] for i in range(0, len(df), part_size)]

    else:
        raise ValueError(
            f"Either num_parts: {num_parts!r} or part_size: {part_size!r} must be provided"
        )


if __name__ == '__main__':
    def main():
        df = pd.DataFrame({"A": range(1, 101), "B": range(101, 201)})
        # dfs = split_df(df, num_parts=2)
        dfs = split_df(df, part_size=50)
        for df in dfs:
            print(df)


    main()

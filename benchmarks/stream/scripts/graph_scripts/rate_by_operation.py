import argparse
import os

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd

from utils import file_exists, int_to_human, smooth_line


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create graphs from previously generated CSV files"
    )

    parser.add_argument(
        "-c", "--csv_file", type=file_exists, help="CSV file to process"
    )

    parser.add_argument(
        "-o", "--output", type=str, help="Directory to dump all the graphs into"
    )

    parser.add_argument(
        "-a",
        "--array-sizes",
        type=int,
        nargs="+",
        help="The array sizes to be filtered",
    )

    parser.add_argument(
        "-f", "--functions", type=str, nargs="+", help="The functions to be filtered"
    )

    args = parser.parse_args()

    csv_file, directory = args.csv_file, args.output

    if not os.path.isdir(directory):
        os.makedirs(directory)

    df = pd.read_csv(csv_file).iloc[:, 0:4]

    array_sizes = (
        args.array_sizes if args.array_sizes else df["ArraySize"].drop_duplicates()
    )
    functions = args.functions if args.functions else df["Function"].drop_duplicates()

    for array_size in array_sizes:
        filtered = df[df["ArraySize"] == array_size]

        fig = plt.figure()
        ax = plt.subplot(111)

        for func in functions:
            tmp_df: pd.DataFrame = (
                # https://stackoverflow.com/a/27975230 (Filtering by row value)
                filtered[filtered["Function"] == func]
                .drop(columns=["Function"])
                .groupby(["Threads"])["BestRateMBs"]
                .mean()
            )

            x, y = smooth_line(tmp_df.index, tmp_df.values)
            ax.plot(x, y, label=func)

        # https://stackoverflow.com/a/4701285 (setting legend outside plot)
        box = ax.get_position()
        ax.set_position(
            [box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9]
        )
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.125),
            fancybox=True,
            shadow=True,
            ncol=5,
        )

        ax.yaxis.set_major_formatter(
            FuncFormatter(
                lambda x, _: int_to_human(x)
                if x < 1_000_000
                else int_to_human(x, fmt="%.1f")
            )
        )

        human_array_size = int_to_human(array_size, replace_long=False)

        ax.set_xlabel("Threads")
        ax.set_ylabel("Best Rate (MB/s)")
        ax.set_title(f"Array size: {human_array_size}")

        f = directory + f"{human_array_size.replace(' ', '')}.png"
        fig.savefig(f)
        fig.clf()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3

"""
DeCompression of a file holding a compressed CSV table

The compressed file holds a conversion map followed by the compressed representation of the table.

The algorithm is:
    1 - Load the conversion map from file to RAM.
    2 - Read the compressed table and replace each coded string with its matching original value.
    3 - Save each modified row in CSV format to the output file
"""

import argparse
import csv
import json
import time


def decompress_file_and_save(compressed_file, output_file):
    """
    Decompress a CSV table using a conversion map and save it to the output file
    :param compressed_file: Path to a file containing a conversion map and a compressed CSV table
    :param output_file: Path to save the decompressed CSV table
    """
    with open(compressed_file, 'r', newline='') as comp_file:
        conversion_map = json.loads(comp_file.readline())
        with open(output_file, 'w', newline='') as output:
            table = csv.reader(comp_file)
            csv_writer = csv.writer(output)
            for row in table:
                for index, column_value in enumerate(row):
                    # Only perform operation for relevant cells:
                    if str(column_value).startswith('&'):
                        # Get the relevant column's list
                        conversion_list = conversion_map[str(index)]
                        # Parse the coded string
                        pos = int(column_value[1:])
                        # Find the original table's text
                        sub_text = conversion_list[pos]
                        row[index] = sub_text
                csv_writer.writerow(row)


def main():
    # Command line arguments parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("compressedFile", help="Path to a compressed file")
    parser.add_argument("outputFile", help="Path to where the decompressed file will be saved")

    args = parser.parse_args()
    compressed_file = args.compressedFile
    output_file = args.outputFile

    try:
        start_time = time.time()
        decompress_file_and_save(compressed_file, output_file)
        end_time = time.time()
        print("Decompression completed.")
        print("Time elapsed: {time} seconds".format(time=round(end_time-start_time, 3)))
    except FileNotFoundError as e:
        print("Error: File not found.", e.strerror)
        exit(1)
    except IOError:
        print("Error: Could not read file.")
        exit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3

"""
Compression of a CSV file holding a table

Assumption is that many of the table values repeats themselves.
    We gain compression by:
        Replacing similar values with a shorter string;
        Results in less data that needs to be writen to the file;
        Smaller file size!
    The short string (A.K.A 'coded string') chosen is the symbol '&' followed by number.
    That number is the index of the original value in a predefined array.
    Predefined arrays (A.K.A 'conversion map') holds the original table's values and used for decompression.

    The compressed file holds a conversion map followed by the compressed representation of the table.

The algorithm is:
    1 - Create a conversion map that will be used to substitute values from the table:
        1.1 - Scan through the table, count all cells' values occurrences into a nested dictionary.
            Dictionary layout is {int, dictionary} where:
            int is the index number of a column from the table, starting from 0.
            Inner dictionary holds all the values of that column.
                Layout is {string, int} where:
                  string is the original value from the column.
                  int is a counter which holds the number of occurrences of that value.
                Example:{ 0: {phrase_A: counter, phrase_B: counter},
                          ...
                          n: {phrase_X: counter, phrase_Y: counter} }
            Optimization note -
                Based on the coded string - the shortest representation of a compressed value
                  is 2 characters long - "&x" (where x is a single digit);
                Trying to compress values that are 2 characters long or less will impact both
                  execution time and the compressed file's size.
                Therefore - those values are skipped.
    1.2 - Sort each inner dictionary by the frequency of phrases in a descending order.
          The higher the value's counter - the more frequent it is.
    1.3 - Drop the frequency counters and save the phrases in a list.
            Since the frequency counters are no longer needed - this step helps to save space in the compressed file.
    2 - Create the compressed representation of the table.
        That is done by replacing phrases with their coded strings using the conversion map.
    3 - Save the conversion map and the compressed table into an output file.
"""

from collections import defaultdict
import operator
import argparse
import csv
import json
import time
import os


def get_conversion_map(input_file):
    """
    Create a conversion map that will be used to substitute values from the table
    :param input_file: path to CSV file which will be compressed
    :return: dictionary of lists - the conversion map
    """
    # Dictionary of dictionaries for counting table values occurrences
    columns_counter = defaultdict(dict)

    # Dictionary of lists for saving table values, sorted by number of occurrences in a descending order.
    # Dictionary keys are columns numbers, values are lists
    # Example:   { 0: [most_frequent_phrase_in_column_0, ..., most_rare_phrase_in_column_0],
    #              ... ,
    #              n: [most_frequent_phrase_in_column_n, ..., most_rare_phrase_in_column_n] }
    columns_sorted = defaultdict(list)
    with open(input_file, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            # Count the occurrences of all column values into a dictionary of dictionaries
            for index, column_value in enumerate(row):
                # Optimization - ignoring values shorter than 3 characters
                if len(column_value) <= 2:
                    continue
                if column_value in columns_counter[index]:
                    columns_counter[index][column_value] += 1
                else:
                    (columns_counter[index])[column_value] = 1

    # For each of the inner dictionaries:
    for index, column in columns_counter.items():
        # Sort by values in reversed order (most frequent phrase will be first in order)
        sorted_column = sorted(column.items(), key=operator.itemgetter(1), reverse=True)
        # Create a list from the sorted phrases (excluding the empty strings) and add it to a dictionary
        columns_sorted[index] = [x[0] for x in sorted_column if x[0] is not '']
    return columns_sorted


def compress_csv_and_save(input_file, output_file):
    """
    Compresses a CSV table from input file and save it along with the conversion table in the output file
    :param input_file: Path to CSV file which will be compressed
    :param output_file: Path to save the compressed output file
    """
    conversion_map = get_conversion_map(input_file)

    # Save data to file
    json.dump(conversion_map, open(output_file, 'w'))

    with open(input_file, 'r', newline='') as csv_file:
        with open(output_file, 'a', newline='') as output:
            table = csv.reader(csv_file)
            csv_writer = csv.writer(output)
            csv_writer.writerow('')
            for row in table:
                for index, column_value in enumerate(row):
                    # Optimization - ignoring values shorter than 3 characters
                    if len(column_value) <= 2:
                        continue
                    sub_text = '&' + str(conversion_map[index].index(column_value))
                    row[index] = sub_text
                csv_writer.writerow(row)


def main():
    # Command line arguments parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("csvFilePath", help="Path to a CSV file to be compressed")
    parser.add_argument("outputFile", help="Path to which the compressed file will be saved")

    args = parser.parse_args()
    input_file = args.csvFilePath
    output_file = args.outputFile

    try:
        start_time = time.time()
        compress_csv_and_save(input_file, output_file)
        end_time = time.time()
        original_file_size = os.path.getsize(input_file)
        compressed_file_size = os.path.getsize(output_file)
        print("Compression completed.")
        print("Original file size:  ", original_file_size, "Bytes")
        print("Compressed file size:", compressed_file_size, "Bytes")
        print("Compression ratio:    {ratio}:1".format(ratio=round(original_file_size / compressed_file_size, 1)))
        print("Time elapsed:         {time} Seconds".format(time=round(end_time - start_time, 3)))
    except FileNotFoundError:
        print("Error: File not found.")
        exit(1)
    except IOError:
        print("Error: Could not read file.")
        exit(1)
    except OSError:
        print("Error: Could not reach the output file. Compression ratio caculation failed.")
        exit(1)


if __name__ == '__main__':
    main()

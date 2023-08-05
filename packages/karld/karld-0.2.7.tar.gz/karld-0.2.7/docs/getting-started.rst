Getting Started with karld
===========================

You have some things you want to do with some data you have.
Maybe it's in a couple of files, or one big file and you
need to clean it up and extract just part of it or maybe you also
need to merge multiple kinds of files based on a common part such
as an email address.
It's not already indexed in a database either so you can't
just do a SQL statement to get the results.
You could manipulate it with python, but putting
all the data in big dictionaries with email as the key
and then iterating over one doing lookups on the other
proves to be slow and can only be done with limited
size data.

karld is here to help. First off, the name karld was chosen
because it sounds like knarled, but it's knot.

Examples
==============================

Split data
++++++++++++++++++++++
From the example directory available by cloning the repository at https://github.com/johnwlockwood/karl_data.

Once cloned to your local system, cd into the karld project directory and run

    python setup.py install

This will install karld. Then cd into the example directory and run:

    python split_multiline.py

This will read multiline/data.csv and produce split_data_ml and split_data_ml_pipe.
Run it and compare the input and output. Checkout the source.

Split csv files
----------------------

Use split_file to split up your data files or use split_csv_file to split up
csv files which may have multi-line fields to ensure they are not broken up.::

    import os

    import karld

    big_file_names = [
        "bigfile1.csv",
        "bigfile2.csv",
        "bigfile3.csv"
    ]

    data_path = os.path.join('path','to','data', 'root')


    def main():
        for filename in big_file_names:
            # Name the directory to write the split files into based
            # on the name of the file.
            out_dir = os.path.join(data_path, 'split_data', filename.replace('.csv', ''))

            # Split the file, with a default max_lines=200000 per shard of the file.
            karld.io.split_csv_file(os.path.join(data_path, filename), out_dir)


    if __name__ == "__main__":
        main()


When you're generating data and want to shard it out to files based on quantity, use
one of the split output functions such as ``split_file_output_csv``, ``split_file_output`` or
``split_file_output_json``::

    import os
    import pathlib

    import karld


    def main():
        """
        Python 2 version
        """

        items = (str(x) + os.linesep for x in range(2000))

        out_dir = pathlib.Path('shgen')
        karld.io.ensure_dir(str(out_dir))

        karld.io.split_file_output('big_data', items, str(out_dir))


    if __name__ == "__main__":
        main()

CSV serializable data
---------------------------
::

    import pathlib

    import karld


    def main():
        """
        From a source of data, shard it to csv files.
        """
        if karld.is_py3():
            third = chr
        else:
            third = unichr

        # Your data source
        items = ((x, x + 1, third(x + 10)) for x in range(2000))

        out_dir = pathlib.Path('shard_out_csv')

        karld.io.ensure_dir(str(out_dir))

        karld.io.split_file_output_csv('big_data.csv', items, str(out_dir))


    if __name__ == "__main__":
        main()


Rows of json serializable data
------------------------------------
::

    import pathlib

    import karld


    def main():
        """
        From a source of data, shard it to csv files.
        """
        if karld.is_py3():
            third = chr
        else:
            third = unichr

        # Your data source
        items = ((x, x + 1, third(x + 10)) for x in range(2000))

        out_dir = pathlib.Path('shard_out_json')

        karld.io.ensure_dir(str(out_dir))

        karld.io.split_file_output_json('big_data.json', items, str(out_dir))


    if __name__ == "__main__":
        main()


Consume data
++++++++++++++++++++++
Consume the contents of a csv file iteratively.
--------------------------------------------------
::

        from __future__ import print_function
        from operator import itemgetter

        import pathlib

        import karld


        def main():
            """
            Iterate over a the row of a csv file, extracting the data
            you desire.
            """
            data_file_path = pathlib.Path('test_data/things_kinds/data_0.csv')

            rows = karld.io.i_get_csv_data(str(data_file_path))

            kinds = set(map(itemgetter(1), rows))

            for kind in kinds:
                print(kind)


        if __name__ == "__main__":
            main()


Consume many csv files iteratively as one stream.
--------------------------------------------------
::

        from __future__ import print_function
        from itertools import chain

        try:
            from itertools import imap
        except ImportError:
            # if python 3
            imap = map

        import karld

        from karld.path import i_walk_csv_paths


        def main():
            """
            Consume many csv files as if one.
            """
            import pathlib

            input_dir = pathlib.Path('test_data/things_kinds')

            # # Use a generator expression
            # iterables = (karld.io.i_get_csv_data(data_path)
            #              for data_path in i_walk_csv_paths(str(input_dir)))

            # # or a generator map.
            iterables = imap(karld.io.i_get_csv_data,
                             i_walk_csv_paths(str(input_dir)))

            items = chain.from_iterable(iterables)

            for item in items:
                print(item[0], item[1])


        if __name__ == "__main__":
            main()

The clean.py example shows processing multiple csv files in parallel.

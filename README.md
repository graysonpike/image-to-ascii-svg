# image-to-ascii-svg
An image to ascii converter which outputs to SVG format for poster printing. Inspired by [CodingTrain's Coding Challenge #166](https://thecodingtrain.com/challenges/166-image-to-ascii) and [Karthik Iyer's similar implementation](https://github.com/KarthikRIyer/image2ascii) in Rust.

## Run it yourself

You can run this project by installing the dependencies with a Python virtual environment:
```shell
python3.12 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Place input PNG and/or JPG files into the `input/` directory.

Then, run the script:
```shell
python image2ascii.py
```

Your converted images will be saved to the `output/` directory. Existing files with the same name in `output/` will be overwritten.


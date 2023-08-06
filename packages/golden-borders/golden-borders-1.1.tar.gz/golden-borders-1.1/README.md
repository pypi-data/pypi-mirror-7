# Computing dimensions for a perfect print


## The Purpose

I like to print my photographs. I'm also too cheap to frame them, however
I do “mat” them.

In case you don't know, normally a print is:

1. printed
2. a *mat* is cut, the mat is bigger than the print, and has a window through which you can see the print (that window can be bigger or smaller than the print)
3. the print is mounted between the mat and a cardboard
4. a window is put in *front* of the mat (the mat can draw attention to the print, but its main purpose is to put space between the print and the window so they don't touch)
5. all that stuff is placed in the frame
6. the frame is stuck on a wall.

So sometimes I do steps 1, 2, 3 and 6, sometimes 1, 3 and 6, and sometimes just 1. Depends on how I feel :)

Anyway, so each time I print something, I have to decide on a border.

Then there the optical illusion of the print "sinking" into the frame, requiring a wider bottom border to compensate.

And then there's the top border.. I think it's ugly when it's smaller than the side borders.

And so this little piece of code does just that.. compute everything so I don't have to think.

## Border sizes

We find the "golden ratio" in many places, including in theories for choosing a mat size.

To choose the dimensions of a mat, some people multiply the width and the height of the print by the golden ratio. Some think it adds way too much border. And for landscapes.. this causes the top border to be smaller than the size borders.

Others compute the *surface* of the print, multiply by the golden ratio, and use that for the size of the mat.

Personnally, what I do is to compute the *surface* of the mat using the *surface* of the print multiplied by some factor (mostly the golden ratio times its square root). Then I keep this surface constant and compute the borders so I obtain:

1. top, left and right borders of equal size
2. bottom border bigger to "optically center" the print

See a [small document I made about this](reflections/doc.pdf) to organize my thoughts.

## Installation

    pip install golden-borders

## Usage

`golden-borders` takes these arguments:

    golden-borders [OPTIONS] PRINT_DIMS

where `PRINT_DIMS` is a dimension pair representing either the size of the *mat*, or the size of the *print* (default = print).

The `OPTIONS` may be:

`--units TEXT` (default, `mm`)
: The units. This represents the default for all inputs, and also the units for the output. The units may be `mm`, `cm`, `dm`, `in`, `ft`.

`--mat` / `--print` (default: `print`)
: If `mat`, then the `PRINT_DIMS` are the dimensions of the mat, else the dimensions of the print.

`--paper TEXT`
: If specified, this is the dimensions of the paper. Print is assumed to be centered.

`--overlap TEXT`
: The overlap of the window over the print. TEXT can be a single or a pair of dimensions. This dimension represents the overlap on *each side*. (e.g. 2x3 means 2mm each size, 3mm top/bottom)

`--border TEXT`
: Specify the value to use for the top, left and right borders. The bottom border is still computed.

`--factor TEXT`
: This is the multiplicator for the area computation. May be a number, or `golden` to use the golden ratio. The default is `golden`.

`--exp TEXT`
: This is the exponent of the factor. Simply a convenience for the golden ratio. The default is `1`, except for `factor = golden`, in which case it's `1.5`.


# License

This is released under a [BSD 3-Clause License](http://opensource.org/licenses/BSD-3-Clause). This basically means:

- You can do what you want with it, as long as the copyright notice, the conditions and the disclaimer stay.
- You cannot use the name of the copyright holder or contributors to endorse or promote derived products.
